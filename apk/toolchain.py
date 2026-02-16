# apk/toolchain.py

from __future__ import annotations

from pathlib import Path
import io
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from alpha_pipeline import alpha_pipeline
from apk.project import render_manifest
from apk.resources import AndroidResources, resources_from_mapping, resources_from_program
from emit.smali_activity import (
    emit_activity_wrapper_smali,
    emit_click_listener_smali,
    emit_event_listener_smali,
)
from emit.smali_runtime_helpers import emit_capability_helper_smali


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
        Path.cwd() / "ahnali_launcher_icon.png",
        Path(__file__).resolve().parents[1] / "ahnali_launcher_icon.png",
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
    import re

    try:
        with zipfile.ZipFile(aar_path, "r") as zf:
            data = zf.read("AndroidManifest.xml")
            class_pkgs: set[str] = set()
            try:
                jar_bytes = zf.read("classes.jar")
                with zipfile.ZipFile(io.BytesIO(jar_bytes), "r") as jzf:
                    for name in jzf.namelist():
                        if not name.endswith(".class"):
                            continue
                        if "/" not in name:
                            continue
                        pkg = name.rsplit("/", 1)[0].replace("/", ".")
                        if pkg and not pkg.startswith("META-INF"):
                            class_pkgs.add(pkg)
            except Exception:
                class_pkgs = set()
    except Exception:
        return None

    strings = re.findall(rb"[A-Za-z0-9_\\.]{3,}", data)
    candidates: list[str] = []
    for raw in strings:
        s = raw.decode("utf-8", errors="ignore")
        if "." not in s:
            continue
        if s.startswith("http") or s.startswith("schemas."):
            continue
        if "android.com" in s or ".." in s:
            continue
        parts = s.split(".")
        if len(parts) < 2:
            continue
        if not all(part and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part) for part in parts):
            continue
        # Java package names are lowercase by convention; class-like tokens
        # (e.g. androidx.startup.InitializationProvider) should not be chosen.
        if any(any(ch.isupper() for ch in part) for part in parts):
            continue
        candidates.append(s)

    if not candidates:
        return None

    def _is_pkg_match(c: str) -> int:
        if c in class_pkgs:
            return 2
        if any(pkg.startswith(c + ".") for pkg in class_pkgs):
            return 1
        return 0

    # Prefer candidates that match the classes.jar package tree.
    candidates.sort(key=lambda v: (-_is_pkg_match(v), 0 if v.startswith("com.") else 1, -v.count("."), -len(v)))
    return candidates[0]


def _read_aar_rtxt(aar_path: Path) -> dict[tuple[str, str], object]:
    try:
        with zipfile.ZipFile(aar_path, "r") as zf:
            text = zf.read("R.txt").decode("utf-8")
    except Exception:
        return {}
    return _parse_symbol_lines(text)


_ANDROID_NS = "http://schemas.android.com/apk/res/android"
_TOOLS_NS = "http://schemas.android.com/tools"
ET.register_namespace("android", _ANDROID_NS)
_BLOCKED_AAR_APP_COMPONENTS = {
    # These auto-init paths pull Kotlin/lifecycle runtime chains that are not
    # currently bundled in Ahnali's runtime envelope.
    "androidx.startup.InitializationProvider",
    "androidx.profileinstaller.ProfileInstallReceiver",
}


def _strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _format_attrs(attrs: dict) -> str:
    parts = []
    for key, value in attrs.items():
        if key.startswith("{"):
            ns, local = key[1:].split("}", 1)
            if ns == _ANDROID_NS:
                key = "android:" + local
            elif ns == _TOOLS_NS:
                # tools: merge directives are not needed in merged output and
                # would require declaring xmlns:tools on the root manifest.
                continue
            else:
                # Drop unknown namespaced attributes from library manifests.
                continue
        safe_value = escape(str(value), {'"': "&quot;"})
        parts.append(f'{key}="{safe_value}"')
    return " ".join(parts)


def _element_to_xml(el: ET.Element, indent: str) -> str:
    tag = _strip_ns(el.tag)
    attrs = _format_attrs(el.attrib)
    children = list(el)
    if not children:
        if attrs:
            return f"{indent}<{tag} {attrs} />"
        return f"{indent}<{tag} />"
    start = f"{indent}<{tag}"
    if attrs:
        start += f" {attrs}"
    start += ">"
    inner = "\n".join(_element_to_xml(child, indent + "    ") for child in children)
    end = f"{indent}</{tag}>"
    return "\n".join([start, inner, end])


def _read_aar_manifest_entries(aar_path: Path) -> tuple[list[str], list[str]]:
    try:
        with zipfile.ZipFile(aar_path, "r") as zf:
            raw = zf.read("AndroidManifest.xml").decode("utf-8")
    except Exception:
        return [], []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return [], []
    perm_entries: list[str] = []
    app_entries: list[str] = []
    for child in list(root):
        tag = _strip_ns(child.tag)
        if tag in ("uses-permission", "uses-permission-sdk-23"):
            perm_entries.append(_element_to_xml(child, ""))
    app = None
    for child in list(root):
        if _strip_ns(child.tag) == "application":
            app = child
            break
    if app is not None:
        for node in list(app):
            tag = _strip_ns(node.tag)
            if tag in ("provider", "service", "receiver"):
                comp_name = node.attrib.get(f"{{{_ANDROID_NS}}}name", "").strip()
                if comp_name in _BLOCKED_AAR_APP_COMPONENTS:
                    continue
                app_entries.append(_element_to_xml(node, ""))
    return perm_entries, app_entries


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
    permissions: list[str] | None = None,
) -> Path | None:
    aapt2 = _tool_path("aapt2")
    android_jar = _find_android_jar(_find_android_sdk(), api=api)
    build_out_dir = Path(out_dir)
    with tempfile.TemporaryDirectory(dir=build_out_dir) as tmp:
        tmp = Path(tmp)
        existing_res = build_out_dir / "res"
        if existing_res.exists():
            shutil.copytree(existing_res, tmp / "res")
        else:
            if isinstance(resources, dict):
                resources = resources_from_mapping(resources)
            if resources is None:
                resources = AndroidResources(strings={"app_name": "AhnaliPreview"})
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
                compiled_dir = extra_compiled_root / f"aar_{idx}"
                compiled_dir.mkdir(parents=True, exist_ok=True)
                subprocess.run([aapt2, "compile", "--dir", str(res_dir), "-o", str(compiled_dir)], check=True)
                compiled_dirs.append(compiled_dir)

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
                label="AhnaliPreview",
                icon=icon_ref,
                permissions=permissions,
            ),
            encoding="utf-8",
        )
        result = subprocess.run(link_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            hint = (
                "aapt2 link failed; this often means a missing transitive AAR. "
                "Ensure all dependencies are present in ./libs (see tools/download_aars.py)."
            )
            detail = f"\n\nstderr:\n{stderr}" if stderr else ""
            raise RuntimeError(f"{hint}{detail}")

        if not symbols_path.exists():
            return None
        # Copy to build dir for debugging
        out_symbols = build_out_dir / "symbols.R.txt"
        out_symbols.write_text(symbols_path.read_text(), encoding="utf-8")
        return out_symbols


def emit_build_dir(
    smali_text: str,
    out_dir: str | Path = "build",
    class_name: str | None = None,
    *,
    emit_wrapper: bool = False,
    wrapper_class_desc: str = "Lcom/ahnali/preview/MainActivity;",
    wrapper_target_desc: str | None = None,
    wrapper_target_sig: str = "()V",
    emit_system_back_bridge: bool = False,
    emit_support_classes: bool = False,
    click_listener_class_desc: str = "Lcom/ahnali/preview/AhnaliClickListener;",
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
                emit_system_back_bridge=emit_system_back_bridge,
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
    wrapper_class_desc: str = "Lcom/ahnali/preview/MainActivity;",
    wrapper_target_desc: str | None = None,
    wrapper_target_sig: str = "()V",
    emit_system_back_bridge: bool | None = None,
    emit_support_classes: bool = False,
    click_listener_class_desc: str = "Lcom/ahnali/preview/AhnaliClickListener;",
    click_listener_target_method: str = "onClick",
) -> Path:
    result = alpha_pipeline(frontend_ir)
    smali_text = result["smali_class"]
    if emit_system_back_bridge is None:
        methods = getattr(frontend_ir, "methods", []) or []
        emit_system_back_bridge = any(getattr(m, "name", "") == "onSystemBack" for m in methods)
    build_dir = emit_build_dir(
        smali_text,
        out_dir=out_dir,
        class_name=class_name,
        emit_wrapper=emit_wrapper,
        wrapper_class_desc=wrapper_class_desc,
        wrapper_target_desc=wrapper_target_desc,
        wrapper_target_sig=wrapper_target_sig,
        emit_system_back_bridge=bool(emit_system_back_bridge),
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
    capability_runtime_bindings = getattr(frontend_ir, "capability_runtime_bindings", []) or []
    for binding in sorted(
        capability_runtime_bindings,
        key=lambda b: (getattr(b, "helper_class_desc", "") or "", getattr(b, "capability", "")),
    ):
        if getattr(binding, "mode", "permission_only") != "helper_call":
            continue
        helper_class_desc = getattr(binding, "helper_class_desc", None)
        helper_method = getattr(binding, "helper_method", None)
        helper_sig = getattr(binding, "helper_sig", None)
        if not (helper_class_desc and helper_method and helper_sig):
            raise RuntimeError(
                f"helper_call binding for '{getattr(binding, 'capability', '?')}' "
                "is missing helper_class_desc/helper_method/helper_sig"
            )
        helper_path = _class_desc_to_path(helper_class_desc).with_suffix(".smali")
        helper_out = build_dir / "smali" / helper_path
        helper_out.parent.mkdir(parents=True, exist_ok=True)
        helper_out.write_text(
            emit_capability_helper_smali(
                class_desc=helper_class_desc,
                helper_method=helper_method,
                helper_sig=helper_sig,
            ),
            encoding="utf-8",
        )
    if support_classes:
        for entry in sorted(support_classes, key=lambda e: e[0]):
            listener_kind = "click"
            if len(entry) == 2:
                class_desc, target_method = entry
                target_desc = wrapper_target_desc or class_name
            elif len(entry) == 3:
                class_desc, target_method, target_desc = entry
            elif len(entry) == 4:
                class_desc, target_method, target_desc, listener_kind = entry
            else:
                raise RuntimeError(f"Unsupported support class entry: {entry!r}")
            listener_path = _class_desc_to_path(class_desc).with_suffix(".smali")
            listener_out = build_dir / "smali" / listener_path
            listener_out.parent.mkdir(parents=True, exist_ok=True)
            listener_out.write_text(
                emit_event_listener_smali(
                    class_desc=class_desc,
                    target_desc=target_desc,
                    target_method=target_method,
                    listener_kind=listener_kind,
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


def _run_java_tool_from_jar(
    *,
    jar_path: Path,
    args: list[str],
    main_classes: list[str],
    tool_name: str,
) -> None:
    cp = os.pathsep.join([str(jar_path), str(jar_path.parent / "*")])
    attempts: list[list[str]] = [["java", "-jar", str(jar_path), *args]]
    attempts.extend(
        [["java", "-cp", cp, main_class, *args] for main_class in main_classes]
    )

    failures: list[tuple[list[str], subprocess.CompletedProcess[str]]] = []
    for cmd in attempts:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return
        failures.append((cmd, result))

    lines = []
    for cmd, result in failures:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        detail = stderr or stdout or f"exit code {result.returncode}"
        lines.append(f"{' '.join(cmd)} -> {detail}")
    raise RuntimeError(
        f"Unable to run {tool_name} from jar '{jar_path}'. Tried launchers:\n- "
        + "\n- ".join(lines)
    )


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
        if jar_path.suffix.lower() == ".jar":
            _run_java_tool_from_jar(
                jar_path=jar_path,
                args=["assemble", *api_args, str(smali_dir), "-o", str(out_dir)],
                main_classes=["org.jf.smali.Main", "org.jf.smali.Smali"],
                tool_name="smali",
            )
        else:
            cmd = [str(jar_path), "assemble", *api_args, str(smali_dir), "-o", str(out_dir)]
            subprocess.run(cmd, check=True)
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
        if jar_path.suffix.lower() == ".jar":
            _run_java_tool_from_jar(
                jar_path=jar_path,
                args=["disassemble", str(dex_path), "-o", str(out_dir)],
                main_classes=["org.jf.baksmali.Main", "org.jf.baksmali.Baksmali"],
                tool_name="baksmali",
            )
        else:
            cmd = [str(jar_path), "disassemble", str(dex_path), "-o", str(out_dir)]
            subprocess.run(cmd, check=True)
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
        raise RuntimeError("ANDROID_HOME or ANDROID_SDK_ROOT must be set for aapt2/zipalign/apksigner")
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

    for tool in ("aapt2", "zipalign", "apksigner"):
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


def _resolve_signing_params(
    *,
    out_dir: Path,
    signing_mode: str = "debug",
    keystore_path: str | Path | None = None,
    keystore_alias: str = "androiddebugkey",
    keystore_pass: str | None = None,
    key_pass: str | None = None,
) -> tuple[Path, str, str, str, bool]:
    mode = str(signing_mode or "debug").strip().lower()
    if mode not in {"debug", "release"}:
        raise RuntimeError("signing_mode must be 'debug' or 'release'")

    alias = str(keystore_alias or "androiddebugkey")
    if mode == "debug":
        ks_path = Path(keystore_path) if keystore_path is not None else (out_dir / "debug.keystore")
        return ks_path, alias, "android", "android", True

    # release mode
    if keystore_path is None:
        raise RuntimeError("Release signing requires keystore_path")
    if not keystore_pass:
        raise RuntimeError("Release signing requires keystore_pass")
    if not key_pass:
        key_pass = keystore_pass
    return Path(keystore_path), alias, str(keystore_pass), str(key_pass), False


def _zip_content_digest(
    archive_path: str | Path,
    *,
    ignore_prefixes: tuple[str, ...] = (),
) -> str:
    digest = hashlib.sha256()
    with zipfile.ZipFile(archive_path, "r") as zf:
        names = sorted(
            name for name in zf.namelist() if not any(name.startswith(prefix) for prefix in ignore_prefixes)
        )
        for name in names:
            data = zf.read(name)
            digest.update(name.encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def _verify_reproducible_archive(
    archive_path: str | Path,
    digest_path: str | Path,
) -> str:
    current = _zip_content_digest(archive_path)
    digest_path = Path(digest_path)
    if digest_path.exists():
        previous = digest_path.read_text(encoding="utf-8").strip()
        if previous and previous != current:
            raise RuntimeError(
                "Reproducibility check failed: archive content hash changed "
                f"(previous={previous}, current={current})."
            )
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(current + "\n", encoding="utf-8")
    return current


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
    # Manifest "resolved" contains the closure produced during AAR fetch.
    # Keep all AARs whenever AAR artifacts are requested so transitives are available.
    aars = [p for p in resolved if p.suffix == ".aar"] if required_artifacts else []
    jars = []
    if jar_allowlist:
        for p in resolved:
            if p.suffix != ".jar":
                continue
            stem = p.stem
            base = stem.rsplit("-", 1)[0] if "-" in stem else stem
            if base in jar_allowlist:
                jars.append(p)
    out = []
    seen = set()
    for p in [*aars, *jars]:
        key = str(p.resolve()) if p.exists() else str(p)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


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


def _collect_aar_manifest_entries(extra_aars: list[str | Path] | None) -> tuple[list[str], list[str]]:
    perm_entries: list[str] = []
    app_entries: list[str] = []
    if not extra_aars:
        return perm_entries, app_entries
    for aar_path in extra_aars:
        aar_path = Path(aar_path)
        if aar_path.suffix != ".aar":
            continue
        perms, app_nodes = _read_aar_manifest_entries(aar_path)
        perm_entries.extend(perms or [])
        app_entries.extend(app_nodes or [])
    return perm_entries, app_entries


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


def _select_manifest_theme(
    *,
    extra_aars: list[str | Path] | None,
    show_action_bar: bool,
) -> str | None:
    has_material = False
    for aar_path in extra_aars or []:
        p = Path(aar_path)
        if p.suffix != ".aar":
            continue
        if p.name.startswith("material-"):
            has_material = True
            break

    if has_material:
        if show_action_bar:
            return "@style/Theme.MaterialComponents.Light"
        return "@style/Theme.MaterialComponents.Light.NoActionBar"

    if not show_action_bar:
        return "@android:style/Theme.Material.Light.NoActionBar"
    return None


def package_apk_from_dex(
    dex_path: str | Path,
    out_dir: str | Path = "build",
    *,
    application_id: str = "com.ahnali.preview",
    min_sdk: int = 21,
    target_sdk: int = 33,
    version_code: int = 1,
    version_name: str = "1.0",
    debuggable: bool = False,
    show_action_bar: bool = True,
    theme: str | None = None,
    api: int | None = None,
    signing_mode: str = "debug",
    keystore_path: str | Path | None = None,
    keystore_alias: str = "androiddebugkey",
    keystore_pass: str | None = None,
    key_pass: str | None = None,
    output_apk: str | Path | None = None,
    activity_name: str | None = None,
    activity_class_desc: str | None = None,
    resources: AndroidResources | dict[str, str] | None = None,
    stable_ids_path: str | Path | None = None,
    extra_aars: list[str | Path] | None = None,
    permissions: list[str] | None = None,
    permission_entries: list[str] | None = None,
    application_entries: list[str] | None = None,
    verify_reproducible: bool = False,
    reproducible_digest_path: str | Path | None = None,
) -> Path:
    """
    Build, align, and sign a minimal APK from an existing classes.dex using
    aapt2 + zipalign + apksigner.
    Requires ANDROID_HOME or ANDROID_SDK_ROOT pointing to an SDK with build-tools.
    """
    dex_path = Path(dex_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    aapt2 = _tool_path("aapt2")
    zipalign = _tool_path("zipalign")
    apksigner = _tool_path("apksigner")
    android_jar = _find_android_jar(_find_android_sdk(), api=api)

    unsigned_apk = out_dir / "unsigned.apk"
    aligned_apk = out_dir / "aligned.apk"
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
        resources = {"app_name": "AhnaliPreview"}
    label = "@string/app_name" if (resources is not None or (out_dir / "res").exists()) else "AhnaliPreview"

    with tempfile.TemporaryDirectory(dir=out_dir) as tmp:
        tmp = Path(tmp)
        existing_res = out_dir / "res"
        if existing_res.exists():
            shutil.copytree(existing_res, tmp / "res")
        else:
            if isinstance(resources, dict):
                resources = resources_from_mapping(resources)
            if resources is None:
                resources = AndroidResources(strings={"app_name": "AhnaliPreview"})
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
                theme=theme,
                activity_name=activity_name,
                label=label,
                icon=icon_ref,
                permissions=permissions,
                permission_entries=permission_entries,
                application_entries=application_entries,
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

    if verify_reproducible:
        digest_path = reproducible_digest_path or (out_dir / "unsigned.apk.sha256")
        _verify_reproducible_archive(unsigned_apk, digest_path)

    subprocess.run(
        [
            zipalign,
            "-f",
            "-p",
            "4",
            str(unsigned_apk),
            str(aligned_apk),
        ],
        check=True,
    )

    keystore_path, keystore_alias, store_pass, key_pass, ensure_debug = _resolve_signing_params(
        out_dir=out_dir,
        signing_mode=signing_mode,
        keystore_path=keystore_path,
        keystore_alias=keystore_alias,
        keystore_pass=keystore_pass,
        key_pass=key_pass,
    )
    if ensure_debug:
        _ensure_debug_keystore(keystore_path, alias=keystore_alias)
    elif not keystore_path.exists():
        raise RuntimeError(f"Release keystore not found: {keystore_path}")

    subprocess.run(
        [
            apksigner,
            "sign",
            "--ks",
            str(keystore_path),
            "--ks-key-alias",
            keystore_alias,
            "--ks-pass",
            f"pass:{store_pass}",
            "--key-pass",
            f"pass:{key_pass}",
            "--out",
            str(signed_apk),
            str(aligned_apk),
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
    wrapper_class_desc: str = "Lcom/ahnali/preview/MainActivity;",
    wrapper_target_desc: str | None = None,
    wrapper_target_sig: str = "(Landroid/app/Activity;)V",
    emit_support_classes: bool = True,
    click_listener_class_desc: str = "Lcom/ahnali/preview/AhnaliClickListener;",
    click_listener_target_method: str = "onClick",
    application_id: str = "com.ahnali.preview",
    min_sdk: int = 21,
    target_sdk: int = 33,
    version_code: int = 1,
    version_name: str = "1.0",
    debuggable: bool = False,
    show_action_bar: bool = True,
    api: int | None = None,
    smali_jar: str | None = None,
    signing_mode: str = "debug",
    keystore_path: str | Path | None = None,
    keystore_alias: str = "androiddebugkey",
    keystore_pass: str | None = None,
    key_pass: str | None = None,
    output_apk: str | Path | None = None,
    uninstall_first: bool = True,
    extra_aars: list[str | Path] | None = None,
    permissions: list[str] | None = None,
    verify_reproducible: bool = False,
    reproducible_digest_path: str | Path | None = None,
) -> Path:
    """
    One-command flow: compile -> smali -> dex -> apk -> install -> run.
    Returns the signed APK path.
    """
    issues = _collect_toolchain_diagnostics(require_adb=True)
    if issues:
        raise RuntimeError("Toolchain diagnostics failed: " + "; ".join(issues))
    out_dir = Path(out_dir)
    if permissions is None:
        permissions = list(getattr(frontend_ir, "permissions", []) or [])
    extra_aars = _resolve_extra_aars(frontend_ir, extra_aars)
    perm_entries, app_entries = _collect_aar_manifest_entries(extra_aars)
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
        permissions=permissions,
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
        theme=_select_manifest_theme(extra_aars=extra_aars, show_action_bar=show_action_bar),
        api=api,
        signing_mode=signing_mode,
        keystore_path=keystore_path,
        keystore_alias=keystore_alias,
        keystore_pass=keystore_pass,
        key_pass=key_pass,
        output_apk=output_apk,
        activity_class_desc=wrapper_class_desc,
        resources=res_obj,
        extra_aars=extra_aars,
        permissions=permissions,
        permission_entries=perm_entries,
        application_entries=app_entries,
        verify_reproducible=verify_reproducible,
        reproducible_digest_path=reproducible_digest_path,
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
