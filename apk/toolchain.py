# apk/toolchain.py

from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import zipfile

from alpha_pipeline import alpha_pipeline
from apk.project import render_manifest
from apk.resources import AndroidResources, resources_from_mapping, resources_from_program
from emit.smali_activity import emit_activity_wrapper_smali, emit_click_listener_smali


def _class_desc_from_smali(smali_text: str) -> str:
    for line in smali_text.splitlines():
        line = line.strip()
        if line.startswith(".class "):
            parts = line.split()
            return parts[-1]
    raise RuntimeError("Could not find .class descriptor in Smali")


def _class_desc_to_path(desc: str) -> Path:
    if desc.startswith("L") and desc.endswith(";"):
        desc = desc[1:-1]
    return Path(*desc.split("/"))


def _activity_name_from_desc(desc: str, application_id: str) -> str:
    if desc.startswith("L") and desc.endswith(";"):
        desc = desc[1:-1]
    fqcn = desc.replace("/", ".")
    if fqcn.startswith(application_id + "."):
        return "." + fqcn[len(application_id) + 1 :]
    return fqcn


def _find_default_launcher_icon() -> Path | None:
    candidates = [
        Path.cwd() / "anali_launcher_icon.png",
        Path(__file__).resolve().parents[1] / "anali_launcher_icon.png",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _detect_launcher_icon_ref(res_dir: Path) -> str | None:
    if not res_dir.exists():
        return None
    for path in res_dir.rglob("ic_launcher.*"):
        if not path.is_file():
            continue
        for part in path.parts:
            if part.startswith("mipmap"):
                return "@mipmap/ic_launcher"
            if part.startswith("drawable"):
                return "@drawable/ic_launcher"
    return None


def _ensure_default_launcher_icon(res_dir: Path, icon_path: Path | None) -> str | None:
    icon_ref = _detect_launcher_icon_ref(res_dir)
    if icon_ref:
        return icon_ref
    if icon_path is None or not icon_path.exists():
        return None
    dest_dir = res_dir / "mipmap"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"ic_launcher{icon_path.suffix}"
    shutil.copyfile(icon_path, dest_path)
    return "@mipmap/ic_launcher"


def _parse_symbol_lines(text: str) -> dict[tuple[str, str], object]:
    symbols: dict[tuple[str, str], object] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("int[]"):
            parts = line.split(None, 3)
            if len(parts) < 4:
                continue
            _, rtype, name, rest = parts
            arr = []
            if "{" in rest and "}" in rest:
                inner = rest[rest.index("{") + 1 : rest.index("}")]
                for item in inner.split(","):
                    item = item.strip()
                    if not item:
                        continue
                    arr.append(int(item, 16) if item.startswith("0x") else int(item))
            symbols[(rtype, name)] = arr
            continue
        if line.startswith("int "):
            parts = line.split(None, 3)
            if len(parts) < 4:
                continue
            _, rtype, name, value = parts
            symbols[(rtype, name)] = int(value, 16) if value.startswith("0x") else int(value)
    return symbols


def _read_aar_package(aar_path: Path) -> str | None:
    try:
        with zipfile.ZipFile(aar_path, "r") as zf:
            data = zf.read("AndroidManifest.xml")
    except Exception:
        return None
    import re

    strings = re.findall(rb"[A-Za-z0-9_\\.]{3,}", data)
    candidates = []
    for s in strings:
        if b"." not in s:
            continue
        if s.startswith(b"http"):
            continue
        candidates.append(s.decode("utf-8", errors="ignore"))
    if not candidates:
        return None
    # Prefer likely application-style packages.
    candidates.sort(key=lambda v: (0 if v.startswith("com.") else 1, -v.count("."), -len(v)))
    return candidates[0]


def _read_aar_rtxt(aar_path: Path) -> dict[tuple[str, str], object]:
    try:
        with zipfile.ZipFile(aar_path, "r") as zf:
            text = zf.read("R.txt").decode("utf-8")
    except Exception:
        return {}
    return _parse_symbol_lines(text)


def _emit_r_smali_class(class_desc: str, int_fields: dict[str, int], array_fields: dict[str, list[int]]) -> str:
    lines = [
        f".class public final {class_desc}",
        ".super Ljava/lang/Object;",
        "",
    ]
    for name, value in sorted(int_fields.items()):
        lines.append(f".field public static {name}:I = 0x{int(value):08x}")
    for name in sorted(array_fields.keys()):
        lines.append(f".field public static {name}:[I")
    if array_fields:
        lines.append("")
        lines.append(".method static constructor <clinit>()V")
        lines.append("    .registers 2")
        idx = 0
        for name, values in array_fields.items():
            count = len(values)
            if count <= 0x7FFF:
                lines.append(f"    const/16 v0, {count}")
            else:
                lines.append(f"    const v0, {count}")
            lines.append("    new-array v0, v0, [I")
            lines.append(f"    fill-array-data v0, :array_{idx}")
            lines.append(f"    sput-object v0, {class_desc}->" + f"{name}:[I")
            idx += 1
        lines.append("    return-void")
        idx = 0
        for name, values in array_fields.items():
            lines.append(f"  :array_{idx}")
            lines.append("    .array-data 4")
            for v in values:
                lines.append(f"        0x{int(v):08x}")
            lines.append("    .end array-data")
            idx += 1
        lines.append(".end method")
    lines.append("")
    return "\n".join(lines)


def _generate_library_r_smali(extra_aars: list[str | Path], symbols: dict[tuple[str, str], object]) -> dict[str, str]:
    smali_map: dict[str, str] = {}
    for aar_path in extra_aars:
        aar_path = Path(aar_path)
        if aar_path.suffix != ".aar":
            continue
        package = _read_aar_package(aar_path)
        if not package:
            continue
        rtxt = _read_aar_rtxt(aar_path)
        if not rtxt:
            continue
        # Group by type
        type_entries: dict[str, dict[str, object]] = {}
        for (rtype, name), value in rtxt.items():
            type_entries.setdefault(rtype, {})[name] = value

        # Outer R class
        outer_desc = "L" + package.replace(".", "/") + "/R;"
        if outer_desc not in smali_map:
            smali_map[outer_desc] = "\n".join(
                [
                    f".class public final {outer_desc}",
                    ".super Ljava/lang/Object;",
                    "",
                ]
            )

        for rtype, entries in type_entries.items():
            int_fields: dict[str, int] = {}
            array_fields: dict[str, list[int]] = {}
            for name, value in entries.items():
                sym = symbols.get((rtype, name), value)
                if isinstance(sym, list):
                    array_fields[name] = sym
                else:
                    int_fields[name] = int(sym) if sym is not None else 0
            class_desc = "L" + package.replace(".", "/") + f"/R${rtype};"
            smali_map[class_desc] = _emit_r_smali_class(class_desc, int_fields, array_fields)
    return smali_map


def _write_smali_map(build_dir: Path, smali_map: dict[str, str]):
    smali_dir = build_dir / "smali"
    for class_desc, smali_text in smali_map.items():
        out_path = smali_dir / _class_desc_to_path(class_desc)
        out_path = out_path.with_suffix(".smali")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(smali_text, encoding="utf-8")


def _generate_resource_symbols(
    out_dir: Path,
    *,
    application_id: str,
    min_sdk: int,
    target_sdk: int,
    api: int | None,
    resources: AndroidResources | dict[str, str] | None,
    extra_aars: list[str | Path] | None,
) -> Path | None:
    aapt2 = _tool_path("aapt2")
    android_jar = _find_android_jar(_find_android_sdk(), api=api)
    out_dir = Path(out_dir)
    with tempfile.TemporaryDirectory(dir=out_dir) as tmp:
        tmp = Path(tmp)
        existing_res = out_dir / "res"
        if existing_res.exists():
            shutil.copytree(existing_res, tmp / "res")
        else:
            if isinstance(resources, dict):
                resources = resources_from_mapping(resources)
            if resources is None:
                resources = AndroidResources(strings={"app_name": "AnaliPreview"})
            resources.write_to_dir(tmp)

        icon_ref = _ensure_default_launcher_icon(tmp / "res", _find_default_launcher_icon())

        extra_res_dirs = []
        if extra_aars:
            extra_res_root = tmp / "res_extra"
            for idx, aar_path in enumerate(extra_aars):
                aar_path = Path(aar_path)
                if not aar_path.exists() or aar_path.suffix != ".aar":
                    continue
                dest_root = extra_res_root / f"aar_{idx}"
                with zipfile.ZipFile(aar_path, "r") as zf:
                    for name in zf.namelist():
                        if name.startswith("res/"):
                            zf.extract(name, dest_root)
                res_dir = dest_root / "res"
                if res_dir.exists():
                    extra_res_dirs.append(res_dir)

        compiled_dirs = []
        base_compiled = tmp / "compiled" / "base"
        base_compiled.mkdir(parents=True, exist_ok=True)
        subprocess.run([aapt2, "compile", "--dir", str(tmp / "res"), "-o", str(base_compiled)], check=True)
        compiled_dirs.append(base_compiled)
        if extra_res_dirs:
            extra_compiled_root = tmp / "compiled" / "extra"
            for idx, res_dir in enumerate(extra_res_dirs):
                out_dir = extra_compiled_root / f"aar_{idx}"
                out_dir.mkdir(parents=True, exist_ok=True)
                subprocess.run([aapt2, "compile", "--dir", str(res_dir), "-o", str(out_dir)], check=True)
                compiled_dirs.append(out_dir)

        flat_files = []
        for compiled_dir in compiled_dirs:
            flat_files.extend(compiled_dir.rglob("*.flat"))
        if not flat_files:
            return None

        symbols_path = tmp / "symbols.txt"
        link_cmd = [
            aapt2,
            "link",
            "-o",
            str(tmp / "symbols.apk"),
            "--manifest",
            str(tmp / "AndroidManifest.xml"),
            "-I",
            str(android_jar),
            "--min-sdk-version",
            str(min_sdk),
            "--target-sdk-version",
            str(target_sdk),
            "--auto-add-overlay",
            "--output-text-symbols",
            str(symbols_path),
        ]

        if isinstance(resources, AndroidResources) and (
            resources.string_ids
            or resources.color_ids
            or resources.dimen_ids
            or resources.style_ids
        ):
            stable_ids = tmp / "stable_ids.txt"
            resources.write_stable_ids(stable_ids, application_id)
            link_cmd.extend(["--stable-ids", str(stable_ids)])

        for f in flat_files:
            link_cmd.extend(["-R", str(f)])

        # Need a manifest to link; use a minimal one.
        (tmp / "AndroidManifest.xml").write_text(
            render_manifest(
                application_id=application_id,
                min_sdk=min_sdk,
                target_sdk=target_sdk,
                version_code=1,
                version_name="1.0",
                debuggable=False,
                show_action_bar=True,
                activity_name=".MainActivity",
                label="AnaliPreview",
                icon=icon_ref,
            ),
            encoding="utf-8",
        )
        subprocess.run(link_cmd, check=True)

        if not symbols_path.exists():
            return None
        # Copy to build dir for debugging
        out_symbols = out_dir / "symbols.R.txt"
        out_symbols.write_text(symbols_path.read_text(), encoding="utf-8")
        return out_symbols


def emit_build_dir(
    smali_text: str,
    out_dir: str | Path = "build",
    class_name: str | None = None,
    *,
    emit_wrapper: bool = False,
    wrapper_class_desc: str = "Lcom/anali/preview/MainActivity;",
    wrapper_target_desc: str | None = None,
    wrapper_target_sig: str = "()V",
    emit_support_classes: bool = False,
    click_listener_class_desc: str = "Lcom/anali/preview/AnaliClickListener;",
    click_listener_target_method: str = "onClick",
) -> Path:
    out_dir = Path(out_dir)
    smali_dir = out_dir / "smali"
    smali_dir.mkdir(parents=True, exist_ok=True)

    if class_name is None:
        class_name = _class_desc_from_smali(smali_text)
    if wrapper_target_desc is None:
        wrapper_target_desc = class_name

    class_path = _class_desc_to_path(class_name)
    smali_path = smali_dir / class_path
    smali_path = smali_path.with_suffix(".smali")
    smali_path.parent.mkdir(parents=True, exist_ok=True)
    smali_path.write_text(smali_text, encoding="utf-8")

    if emit_wrapper:
        wrapper_path = _class_desc_to_path(wrapper_class_desc).with_suffix(".smali")
        wrapper_out = smali_dir / wrapper_path
        wrapper_out.parent.mkdir(parents=True, exist_ok=True)
        wrapper_out.write_text(
            emit_activity_wrapper_smali(
                activity_desc=wrapper_class_desc,
                target_desc=wrapper_target_desc,
                target_sig=wrapper_target_sig,
            ),
            encoding="utf-8",
        )

    if emit_support_classes:
        listener_path = _class_desc_to_path(click_listener_class_desc).with_suffix(".smali")
        listener_out = smali_dir / listener_path
        listener_out.parent.mkdir(parents=True, exist_ok=True)
        listener_out.write_text(
            emit_click_listener_smali(
                class_desc=click_listener_class_desc,
                target_desc=wrapper_target_desc or class_name,
                target_method=click_listener_target_method,
            ),
            encoding="utf-8",
        )

    return out_dir


def emit_build_dir_from_program(
    frontend_ir,
    out_dir: str | Path = "build",
    class_name: str = "LTest;",
    *,
    emit_wrapper: bool = False,
    wrapper_class_desc: str = "Lcom/anali/preview/MainActivity;",
    wrapper_target_desc: str | None = None,
    wrapper_target_sig: str = "()V",
    emit_support_classes: bool = False,
    click_listener_class_desc: str = "Lcom/anali/preview/AnaliClickListener;",
    click_listener_target_method: str = "onClick",
) -> Path:
    result = alpha_pipeline(frontend_ir)
    smali_text = result["smali_class"]
    build_dir = emit_build_dir(
        smali_text,
        out_dir=out_dir,
        class_name=class_name,
        emit_wrapper=emit_wrapper,
        wrapper_class_desc=wrapper_class_desc,
        wrapper_target_desc=wrapper_target_desc,
        wrapper_target_sig=wrapper_target_sig,
        emit_support_classes=emit_support_classes or bool(getattr(frontend_ir, "support_classes", [])),
        click_listener_class_desc=click_listener_class_desc,
        click_listener_target_method=click_listener_target_method,
    )
    # Emit per-handler support classes if present
    support_classes = getattr(frontend_ir, "support_classes", [])
    if not support_classes:
        support_classes = result.get("support_classes", [])
    extra_smali_classes = result.get("extra_smali_classes", {})
    if extra_smali_classes:
        for class_desc in sorted(extra_smali_classes.keys()):
            extra_smali = extra_smali_classes[class_desc]
            extra_path = _class_desc_to_path(class_desc).with_suffix(".smali")
            extra_out = build_dir / "smali" / extra_path
            extra_out.parent.mkdir(parents=True, exist_ok=True)
            extra_out.write_text(extra_smali, encoding="utf-8")
    if support_classes:
        for entry in sorted(support_classes, key=lambda e: e[0]):
            if len(entry) == 2:
                class_desc, target_method = entry
                target_desc = wrapper_target_desc or class_name
            else:
                class_desc, target_method, target_desc = entry
            listener_path = _class_desc_to_path(class_desc).with_suffix(".smali")
            listener_out = build_dir / "smali" / listener_path
            listener_out.parent.mkdir(parents=True, exist_ok=True)
            listener_out.write_text(
                emit_click_listener_smali(
                    class_desc=class_desc,
                    target_desc=target_desc,
                    target_method=target_method,
                ),
                encoding="utf-8",
            )

    # Emit resources from ProgramIR if present.
    res_mapping = getattr(frontend_ir, "resources", None)
    if res_mapping:
        res = resources_from_program(frontend_ir)
        res.write_to_dir(build_dir)

    return build_dir


def _which_tool(name: str) -> str | None:
    path = shutil.which(name)
    if path:
        return path
    home = Path.home()
    local_bin = home / ".local" / "bin" / name
    if local_bin.exists():
        return str(local_bin)
    return None


def run_smali(
    smali_dir: str | Path,
    out_dir: str | Path | None = None,
    smali_jar: str | None = None,
    *,
    api: int | None = None,
) -> Path:
    smali_dir = Path(smali_dir)
    if out_dir is None:
        out_dir = smali_dir.parent / "classes.dex"
    out_dir = Path(out_dir)

    api_args = ["--api", str(api)] if api is not None else []
    if smali_jar:
        jar_path = Path(smali_jar)
        if jar_path.suffix == ".jar":
            cmd = ["java", "-jar", str(jar_path), "assemble", *api_args, str(smali_dir), "-o", str(out_dir)]
        else:
            cmd = [str(jar_path), "assemble", *api_args, str(smali_dir), "-o", str(out_dir)]
    else:
        smali = _which_tool("smali")
        if smali is None:
            raise RuntimeError("smali not found on PATH and smali_jar not provided")
        cmd = [smali, "assemble", *api_args, str(smali_dir), "-o", str(out_dir)]

    subprocess.run(cmd, check=True)
    return out_dir


def run_baksmali(dex_path: str | Path, out_dir: str | Path, baksmali_jar: str | None = None) -> Path:
    dex_path = Path(dex_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if baksmali_jar:
        jar_path = Path(baksmali_jar)
        if jar_path.suffix == ".jar":
            cmd = ["java", "-jar", str(jar_path), "disassemble", str(dex_path), "-o", str(out_dir)]
        else:
            cmd = [str(jar_path), "disassemble", str(dex_path), "-o", str(out_dir)]
    else:
        baksmali = _which_tool("baksmali")
        if baksmali is None:
            raise RuntimeError("baksmali not found on PATH and baksmali_jar not provided")
        cmd = [baksmali, "disassemble", str(dex_path), "-o", str(out_dir)]

    subprocess.run(cmd, check=True)
    return out_dir


def _find_android_sdk() -> Path:
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not sdk:
        raise RuntimeError("ANDROID_HOME or ANDROID_SDK_ROOT must be set for aapt2/apksigner")
    return Path(sdk)


def _find_build_tools(sdk: Path) -> Path:
    bt_dir = sdk / "build-tools"
    if not bt_dir.exists():
        raise RuntimeError("Android build-tools not found under SDK")
    versions = sorted([p for p in bt_dir.iterdir() if p.is_dir()])
    if not versions:
        raise RuntimeError("No build-tools versions found under SDK")
    return versions[-1]


def _find_android_jar(sdk: Path, api: int | None = None) -> Path:
    platforms = sdk / "platforms"
    if not platforms.exists():
        raise RuntimeError("Android platforms not found under SDK")
    if api is not None:
        jar = platforms / f"android-{api}" / "android.jar"
        if not jar.exists():
            raise RuntimeError(f"android.jar not found for API {api}")
        return jar
    candidates = sorted([p for p in platforms.iterdir() if p.is_dir() and p.name.startswith("android-")])
    if not candidates:
        raise RuntimeError("No android-* platform directories found under SDK")
    jar = candidates[-1] / "android.jar"
    if not jar.exists():
        raise RuntimeError("android.jar not found in latest platform directory")
    return jar


def _tool_path(name: str) -> str:
    path = shutil.which(name)
    if path:
        return path
    sdk = _find_android_sdk()
    bt = _find_build_tools(sdk)
    exe = f"{name}.bat" if os.name == "nt" else name
    candidate = bt / exe
    if candidate.exists():
        return str(candidate)
    raise RuntimeError(f"{name} not found on PATH or in Android build-tools")


def _collect_toolchain_diagnostics(*, require_adb: bool = False, require_baksmali: bool = False) -> list[str]:
    """
    Return a list of human-readable toolchain diagnostics. Empty list means OK.
    This is non-fatal and intended to be used by tests or higher-level commands.
    """
    issues = []
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not sdk:
        issues.append("ANDROID_HOME/ANDROID_SDK_ROOT not set")

    for tool in ("aapt2", "apksigner"):
        try:
            _tool_path(tool)
        except Exception:
            issues.append(f"{tool} not found on PATH or in Android build-tools")

    if shutil.which("smali") is None and not os.environ.get("SMALI_JAR"):
        issues.append("smali not found on PATH and SMALI_JAR not set")

    if require_baksmali:
        if shutil.which("baksmali") is None and not os.environ.get("BAKSMALI_JAR"):
            issues.append("baksmali not found on PATH and BAKSMALI_JAR not set")

    if require_adb:
        try:
            _adb_path()
        except Exception:
            issues.append("adb not found on PATH or in Android SDK platform-tools")

    return issues


def _adb_path() -> str:
    path = shutil.which("adb")
    if path:
        return path
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if sdk:
        candidate = Path(sdk) / "platform-tools" / "adb"
        if candidate.exists():
            return str(candidate)
    raise RuntimeError("adb not found on PATH or in Android SDK platform-tools")


def _ensure_debug_keystore(keystore_path: Path, alias: str = "androiddebugkey") -> None:
    if keystore_path.exists():
        return
    keystore_path.parent.mkdir(parents=True, exist_ok=True)
    keytool = shutil.which("keytool")
    if not keytool:
        raise RuntimeError("keytool not found on PATH (Java JDK required)")
    cmd = [
        keytool,
        "-genkeypair",
        "-keystore",
        str(keystore_path),
        "-storepass",
        "android",
        "-keypass",
        "android",
        "-alias",
        alias,
        "-keyalg",
        "RSA",
        "-keysize",
        "2048",
        "-validity",
        "10000",
        "-dname",
        "CN=Android Debug,O=Android,C=US",
    ]
    subprocess.run(cmd, check=True)


def _extract_aar_jars(extra_aars: list[str | Path], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    jar_paths = []
    for aar_path in extra_aars:
        aar_path = Path(aar_path)
        if not aar_path.exists():
            raise RuntimeError(f"AAR not found: {aar_path}")
        if aar_path.suffix == ".jar":
            jar_paths.append(aar_path)
            continue
        prefix = out_dir / aar_path.stem
        prefix.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(aar_path, "r") as zf:
            for name in zf.namelist():
                if name == "classes.jar":
                    zf.extract(name, prefix)
                    jar_paths.append(prefix / name)
                elif name.startswith("libs/") and name.endswith(".jar"):
                    zf.extract(name, prefix)
                    jar_paths.append(prefix / name)
    return jar_paths


def _find_latest_artifact_file(libs_dir: Path, artifact: str, suffix: str) -> Path | None:
    matches = sorted(libs_dir.glob(f"{artifact}-*{suffix}"))
    if matches:
        return matches[-1]
    candidate = libs_dir / f"{artifact}{suffix}"
    return candidate if candidate.exists() else None


def _resolve_extra_aars_from_manifest(
    libs_dir: Path,
    required_artifacts: set[str],
    jar_allowlist: set[str],
) -> list[Path] | None:
    manifest_path = libs_dir / "aar_resolved.json"
    if not manifest_path.exists():
        return None
    data = json.loads(manifest_path.read_text())
    resolved = []
    for raw in data.get("resolved", []):
        path = Path(raw)
        if not path.is_absolute() and not path.exists():
            path = libs_dir / path
        if path.exists():
            resolved.append(path)
    aars = [
        p
        for p in resolved
        if p.suffix == ".aar"
        and any(p.name.startswith(f"{artifact}-") for artifact in required_artifacts)
    ]
    jars = []
    if jar_allowlist:
        for p in resolved:
            if p.suffix != ".jar":
                continue
            stem = p.stem
            base = stem.rsplit("-", 1)[0] if "-" in stem else stem
            if base in jar_allowlist:
                jars.append(p)
    return aars + jars


def _resolve_extra_aars(frontend_ir, extra_aars: list[str | Path] | None) -> list[str | Path] | None:
    if extra_aars is not None:
        return extra_aars
    required_artifacts = set(getattr(frontend_ir, "required_artifacts", []) or [])
    jar_allowlist = set(getattr(frontend_ir, "jar_allowlist", []) or [])
    if not required_artifacts and not jar_allowlist:
        return None
    libs_dir = Path("libs")
    if not libs_dir.exists():
        raise RuntimeError("Missing ./libs directory. Run tools/download_aars.py --out libs.")

    resolved = _resolve_extra_aars_from_manifest(libs_dir, required_artifacts, jar_allowlist)
    if resolved is None:
        resolved = []
        for artifact in sorted(required_artifacts):
            match = _find_latest_artifact_file(libs_dir, artifact, ".aar")
            if match is not None:
                resolved.append(match)
        for jar in sorted(jar_allowlist):
            match = _find_latest_artifact_file(libs_dir, jar, ".jar")
            if match is not None:
                resolved.append(match)

    missing = []
    for artifact in sorted(required_artifacts):
        if not any(Path(p).name.startswith(f"{artifact}-") for p in resolved if Path(p).suffix == ".aar"):
            missing.append(f"{artifact}-*.aar")
    if missing:
        missing_list = ", ".join(missing)
        raise RuntimeError(
            f"Missing required AARs in ./libs: {missing_list}. "
            "Run tools/download_aars.py --out libs."
        )
    return resolved if resolved else None


def _merge_dex_with_aars(
    dex_path: Path,
    *,
    extra_aars: list[str | Path],
    out_dir: Path,
    api: int | None,
) -> Path:
    d8 = _tool_path("d8")
    android_jar = _find_android_jar(_find_android_sdk(), api=api)
    temp_dir = out_dir / "aar_tmp"
    jar_paths = _extract_aar_jars(extra_aars, temp_dir)
    if not jar_paths:
        return dex_path
    merged_dir = out_dir / "merged_dex"
    merged_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        d8,
        "--lib",
        str(android_jar),
        "--min-api",
        str(api or 21),
        "--output",
        str(merged_dir),
        str(dex_path),
    ]
    cmd.extend(str(p) for p in jar_paths)
    subprocess.run(cmd, check=True)
    merged_dex = merged_dir / "classes.dex"
    if not merged_dex.exists():
        raise RuntimeError("d8 did not produce classes.dex")
    return merged_dex


def package_apk_from_dex(
    dex_path: str | Path,
    out_dir: str | Path = "build",
    *,
    application_id: str = "com.anali.preview",
    min_sdk: int = 21,
    target_sdk: int = 33,
    version_code: int = 1,
    version_name: str = "1.0",
    debuggable: bool = False,
    show_action_bar: bool = True,
    api: int | None = None,
    keystore_path: str | Path | None = None,
    keystore_alias: str = "androiddebugkey",
    output_apk: str | Path | None = None,
    activity_name: str | None = None,
    activity_class_desc: str | None = None,
    resources: AndroidResources | dict[str, str] | None = None,
    stable_ids_path: str | Path | None = None,
    extra_aars: list[str | Path] | None = None,
) -> Path:
    """
    Build and sign a minimal APK from an existing classes.dex using aapt2 + apksigner.
    Requires ANDROID_HOME or ANDROID_SDK_ROOT pointing to an SDK with build-tools.
    """
    dex_path = Path(dex_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    aapt2 = _tool_path("aapt2")
    apksigner = _tool_path("apksigner")
    android_jar = _find_android_jar(_find_android_sdk(), api=api)

    unsigned_apk = out_dir / "unsigned.apk"
    signed_apk = Path(output_apk) if output_apk else (out_dir / "signed.apk")

    manifest_path = out_dir / "AndroidManifest.xml"
    if activity_name is None and activity_class_desc is not None:
        activity_name = _activity_name_from_desc(
            activity_class_desc,
            application_id,
        )
    if activity_name is None:
        activity_name = ".MainActivity"
    if resources is None and not (out_dir / "res").exists():
        resources = {"app_name": "AnaliPreview"}
    label = "@string/app_name" if (resources is not None or (out_dir / "res").exists()) else "AnaliPreview"

    with tempfile.TemporaryDirectory(dir=out_dir) as tmp:
        tmp = Path(tmp)
        existing_res = out_dir / "res"
        if existing_res.exists():
            shutil.copytree(existing_res, tmp / "res")
        else:
            if isinstance(resources, dict):
                resources = resources_from_mapping(resources)
            if resources is None:
                resources = AndroidResources(strings={"app_name": "AnaliPreview"})
            resources.write_to_dir(tmp)

        icon_ref = _ensure_default_launcher_icon(tmp / "res", _find_default_launcher_icon())
        manifest_path.write_text(
            render_manifest(
                application_id=application_id,
                min_sdk=min_sdk,
                target_sdk=target_sdk,
                version_code=version_code,
                version_name=version_name,
                debuggable=debuggable,
                show_action_bar=show_action_bar,
                activity_name=activity_name,
                label=label,
                icon=icon_ref,
            ),
            encoding="utf-8",
        )

        extra_res_dirs = []
        if extra_aars:
            extra_res_root = tmp / "res_extra"
            for idx, aar_path in enumerate(extra_aars):
                aar_path = Path(aar_path)
                if not aar_path.exists():
                    raise RuntimeError(f"AAR not found: {aar_path}")
                if aar_path.suffix != ".aar":
                    continue
                dest_root = extra_res_root / f"aar_{idx}"
                with zipfile.ZipFile(aar_path, "r") as zf:
                    for name in zf.namelist():
                        if name.startswith("res/"):
                            zf.extract(name, dest_root)
                res_dir = dest_root / "res"
                if res_dir.exists():
                    extra_res_dirs.append(res_dir)

        compiled_dirs = []
        base_compiled = tmp / "compiled" / "base"
        base_compiled.mkdir(parents=True, exist_ok=True)
        subprocess.run([aapt2, "compile", "--dir", str(tmp / "res"), "-o", str(base_compiled)], check=True)
        compiled_dirs.append(base_compiled)
        if extra_res_dirs:
            extra_compiled_root = tmp / "compiled" / "extra"
            for idx, res_dir in enumerate(extra_res_dirs):
                out_dir = extra_compiled_root / f"aar_{idx}"
                out_dir.mkdir(parents=True, exist_ok=True)
                subprocess.run([aapt2, "compile", "--dir", str(res_dir), "-o", str(out_dir)], check=True)
                compiled_dirs.append(out_dir)

        flat_files = []
        for compiled_dir in compiled_dirs:
            flat_files.extend(compiled_dir.rglob("*.flat"))
        if not flat_files:
            raise RuntimeError("aapt2 compile produced no resources")

        link_cmd = [
            aapt2,
            "link",
            "-o",
            str(unsigned_apk),
            "--manifest",
            str(manifest_path),
            "-I",
            str(android_jar),
            "--min-sdk-version",
            str(min_sdk),
            "--target-sdk-version",
            str(target_sdk),
            "--auto-add-overlay",
        ]
        auto_stable_ids = None
        if isinstance(resources, AndroidResources) and (
            resources.string_ids
            or resources.color_ids
            or resources.dimen_ids
            or resources.style_ids
        ):
            auto_stable_ids = tmp / "stable_ids.txt"
            resources.write_stable_ids(auto_stable_ids, application_id)

        if stable_ids_path is None:
            candidate_ids = out_dir / "stable_ids.txt"
            if candidate_ids.exists():
                stable_ids_path = candidate_ids
            elif auto_stable_ids is not None:
                stable_ids_path = auto_stable_ids
        if stable_ids_path is not None:
            link_cmd.extend(["--stable-ids", str(stable_ids_path)])
        for f in flat_files:
            link_cmd.extend(["-R", str(f)])
        subprocess.run(link_cmd, check=True)

    with zipfile.ZipFile(unsigned_apk, "a") as zf:
        zf.write(dex_path, "classes.dex")

    if keystore_path is None:
        keystore_path = out_dir / "debug.keystore"
    keystore_path = Path(keystore_path)
    _ensure_debug_keystore(keystore_path, alias=keystore_alias)

    subprocess.run(
        [
            apksigner,
            "sign",
            "--ks",
            str(keystore_path),
            "--ks-pass",
            "pass:android",
            "--key-pass",
            "pass:android",
            "--out",
            str(signed_apk),
            str(unsigned_apk),
        ],
        check=True,
    )

    return signed_apk


def build_install_run(
    frontend_ir,
    *,
    out_dir: str | Path = "build",
    class_name: str = "LTest;",
    emit_wrapper: bool = True,
    wrapper_class_desc: str = "Lcom/anali/preview/MainActivity;",
    wrapper_target_desc: str | None = None,
    wrapper_target_sig: str = "(Landroid/app/Activity;)V",
    emit_support_classes: bool = True,
    click_listener_class_desc: str = "Lcom/anali/preview/AnaliClickListener;",
    click_listener_target_method: str = "onClick",
    application_id: str = "com.anali.preview",
    min_sdk: int = 21,
    target_sdk: int = 33,
    version_code: int = 1,
    version_name: str = "1.0",
    debuggable: bool = False,
    show_action_bar: bool = True,
    api: int | None = None,
    smali_jar: str | None = None,
    keystore_path: str | Path | None = None,
    keystore_alias: str = "androiddebugkey",
    output_apk: str | Path | None = None,
    uninstall_first: bool = True,
    extra_aars: list[str | Path] | None = None,
) -> Path:
    """
    One-command flow: compile -> smali -> dex -> apk -> install -> run.
    Returns the signed APK path.
    """
    out_dir = Path(out_dir)
    extra_aars = _resolve_extra_aars(frontend_ir, extra_aars)
    build_dir = emit_build_dir_from_program(
        frontend_ir,
        out_dir=out_dir,
        class_name=class_name,
        emit_wrapper=emit_wrapper,
        wrapper_class_desc=wrapper_class_desc,
        wrapper_target_desc=wrapper_target_desc,
        wrapper_target_sig=wrapper_target_sig,
        emit_support_classes=emit_support_classes,
        click_listener_class_desc=click_listener_class_desc,
        click_listener_target_method=click_listener_target_method,
    )
    # Generate library R classes from merged resource symbols (if any).
    res_obj = resources_from_program(frontend_ir)
    symbols_path = _generate_resource_symbols(
        build_dir,
        application_id=application_id,
        min_sdk=min_sdk,
        target_sdk=target_sdk,
        api=api,
        resources=res_obj,
        extra_aars=extra_aars,
    )
    if symbols_path and extra_aars:
        symbols_file = Path(symbols_path)
        if not symbols_file.exists():
            fallback = build_dir / "symbols.R.txt"
            if fallback.exists():
                symbols_file = fallback
            else:
                symbols_file = None
        if symbols_file:
            symbols = _parse_symbol_lines(symbols_file.read_text())
            r_smali = _generate_library_r_smali(extra_aars, symbols)
            if r_smali:
                _write_smali_map(build_dir, r_smali)

    dex_path = run_smali(
        build_dir / "smali",
        out_dir=build_dir / "classes.dex",
        smali_jar=smali_jar,
        api=api,
    )
    if extra_aars:
        dex_path = _merge_dex_with_aars(
            dex_path,
            extra_aars=extra_aars,
            out_dir=build_dir,
            api=api,
        )

    signed_apk = package_apk_from_dex(
        dex_path,
        out_dir=build_dir,
        application_id=application_id,
        min_sdk=min_sdk,
        target_sdk=target_sdk,
        version_code=version_code,
        version_name=version_name,
        debuggable=debuggable,
        show_action_bar=show_action_bar,
        api=api,
        keystore_path=keystore_path,
        keystore_alias=keystore_alias,
        output_apk=output_apk,
        activity_class_desc=wrapper_class_desc,
        resources=res_obj,
        extra_aars=extra_aars,
    )

    adb = _adb_path()
    activity_name = _activity_name_from_desc(wrapper_class_desc, application_id)
    if uninstall_first:
        subprocess.run([adb, "uninstall", application_id], check=False)
    try :
        subprocess.run([adb, "install", "-r", str(signed_apk)], check=True)  
        subprocess.run(
            [adb, "shell", "am", "start", "-n", f"{application_id}/{activity_name}"],
            check=True,
        )
        return signed_apk

    except subprocess.CalledProcessError as e:
        print(e.output)
