# apk/toolchain.py

from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import zipfile

from alpha_pipeline import alpha_pipeline
from apk.project import render_manifest
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
    return emit_build_dir(
        smali_text,
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


def package_apk_from_dex(
    dex_path: str | Path,
    out_dir: str | Path = "build",
    *,
    application_id: str = "com.anali.preview",
    min_sdk: int = 21,
    target_sdk: int = 33,
    api: int | None = None,
    keystore_path: str | Path | None = None,
    keystore_alias: str = "androiddebugkey",
    output_apk: str | Path | None = None,
    activity_name: str | None = None,
    activity_class_desc: str | None = None,
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
    if not manifest_path.exists():
        if activity_name is None and activity_class_desc is not None:
            activity_name = _activity_name_from_desc(
                activity_class_desc,
                application_id,
            )
        if activity_name is None:
            activity_name = ".MainActivity"
        manifest_path.write_text(
            render_manifest(
                application_id=application_id,
                min_sdk=min_sdk,
                target_sdk=target_sdk,
                activity_name=activity_name,
            ),
            encoding="utf-8",
        )

    with tempfile.TemporaryDirectory(dir=out_dir) as tmp:
        tmp = Path(tmp)
        res_dir = tmp / "res" / "values"
        res_dir.mkdir(parents=True, exist_ok=True)
        (res_dir / "strings.xml").write_text(
            '<resources><string name="app_name">Anali</string></resources>',
            encoding="utf-8",
        )

        compiled_res = tmp / "compiled"
        compiled_res.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [aapt2, "compile", "--dir", str(tmp / "res"), "-o", str(compiled_res)],
            check=True,
        )

        flat_files = list(compiled_res.rglob("*.flat"))
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
    api: int | None = 21,
    smali_jar: str | None = None,
    keystore_path: str | Path | None = None,
    keystore_alias: str = "androiddebugkey",
    output_apk: str | Path | None = None,
    uninstall_first: bool = True,
) -> Path:
    """
    One-command flow: compile -> smali -> dex -> apk -> install -> run.
    Returns the signed APK path.
    """
    out_dir = Path(out_dir)
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

    dex_path = run_smali(
        build_dir / "smali",
        out_dir=build_dir / "classes.dex",
        smali_jar=smali_jar,
        api=api,
    )

    signed_apk = package_apk_from_dex(
        dex_path,
        out_dir=build_dir,
        application_id=application_id,
        min_sdk=min_sdk,
        target_sdk=target_sdk,
        api=api,
        keystore_path=keystore_path,
        keystore_alias=keystore_alias,
        output_apk=output_apk,
        activity_class_desc=wrapper_class_desc,
    )

    adb = _adb_path()
    activity_name = _activity_name_from_desc(wrapper_class_desc, application_id)
    if uninstall_first:
        subprocess.run([adb, "uninstall", application_id], check=False)
    subprocess.run([adb, "install", "-r", str(signed_apk)], check=True)
    subprocess.run(
        [adb, "shell", "am", "start", "-n", f"{application_id}/{activity_name}"],
        check=True,
    )
    return signed_apk
