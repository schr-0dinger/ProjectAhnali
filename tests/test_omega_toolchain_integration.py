import os
import shutil
import subprocess
import time
import pytest

from apk.toolchain import (
    emit_build_dir_from_program,
    run_smali,
    package_apk_from_dex,
    _tool_path,
)
from dsl.app import assign, const


def _has_android_sdk():
    return bool(os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT"))


def _has_tool(name: str):
    if shutil.which(name) is not None:
        return True
    local_bin = os.path.expanduser(f"~/.local/bin/{name}")
    return os.path.exists(local_bin)


def test_omega_apk_packaging_integration(tmp_path):
    if not _has_android_sdk():
        pytest.skip("ANDROID_HOME/ANDROID_SDK_ROOT not set")
    try:
        _tool_path("aapt2")
        _tool_path("apksigner")
    except RuntimeError:
        pytest.skip("aapt2/apksigner not found on PATH or in Android build-tools")
    smali_jar = os.environ.get("SMALI_JAR")
    if not _has_tool("smali") and not smali_jar:
        pytest.skip("smali not found on PATH and SMALI_JAR not set")

    out_dir = emit_build_dir_from_program(
        [assign("x", const(1))],
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    dex_path = run_smali(
        out_dir / "smali",
        out_dir=out_dir / "classes.dex",
        smali_jar=smali_jar,
        api=21,
    )
    signed_apk = package_apk_from_dex(dex_path, out_dir=out_dir)

    assert signed_apk.exists()


def test_omega_apk_packaging_manifest_activity(tmp_path):
    if not _has_android_sdk():
        pytest.skip("ANDROID_HOME/ANDROID_SDK_ROOT not set")
    try:
        _tool_path("aapt2")
        _tool_path("apksigner")
    except RuntimeError:
        pytest.skip("aapt2/apksigner not found on PATH or in Android build-tools")
    smali_jar = os.environ.get("SMALI_JAR")
    if not _has_tool("smali") and not smali_jar:
        pytest.skip("smali not found on PATH and SMALI_JAR not set")

    out_dir = emit_build_dir_from_program(
        [assign("x", const(1))],
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    dex_path = run_smali(
        out_dir / "smali",
        out_dir=out_dir / "classes.dex",
        smali_jar=smali_jar,
        api=21,
    )
    activity_desc = "Lcom/example/app/EntryActivity;"
    signed_apk = package_apk_from_dex(
        dex_path,
        out_dir=out_dir,
        application_id="com.example.app",
        activity_class_desc=activity_desc,
    )

    assert signed_apk.exists()

    manifest_path = out_dir / "AndroidManifest.xml"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    assert 'android:name=".EntryActivity"' in manifest_text


def _adb_path():
    path = shutil.which("adb")
    if path:
        return path
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if sdk:
        candidate = os.path.join(sdk, "platform-tools", "adb")
        if os.path.exists(candidate):
            return candidate
    return None


def _has_adb():
    return _adb_path() is not None


def _has_device():
    try:
        adb = _adb_path()
        if not adb:
            return False
        result = subprocess.run(
            [adb, "devices"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return False
    lines = [line.strip() for line in result.stdout.splitlines()[1:]]
    for line in lines:
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return True
    return False


def test_omega_apk_adb_smoke(tmp_path):
    if not _has_android_sdk():
        pytest.skip("ANDROID_HOME/ANDROID_SDK_ROOT not set")
    try:
        _tool_path("aapt2")
        _tool_path("apksigner")
    except RuntimeError:
        pytest.skip("aapt2/apksigner not found on PATH or in Android build-tools")
    smali_jar = os.environ.get("SMALI_JAR")
    if not _has_tool("smali") and not smali_jar:
        pytest.skip("smali not found on PATH and SMALI_JAR not set")
    if not _has_adb():
        pytest.skip("adb not found on PATH")
    if not _has_device():
        pytest.skip("no adb devices in 'device' state")

    activity_desc = "Lcom/anali/preview/MainActivity;"
    out_dir = emit_build_dir_from_program(
        [assign("x", const(1))],
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc=activity_desc,
    )

    dex_path = run_smali(
        out_dir / "smali",
        out_dir=out_dir / "classes.dex",
        smali_jar=smali_jar,
        api=21,
    )
    signed_apk = package_apk_from_dex(
        dex_path,
        out_dir=out_dir,
        application_id="com.anali.preview",
        activity_class_desc=activity_desc,
    )

    adb = _adb_path()
    subprocess.run([adb, "uninstall", "com.anali.preview"], check=False)
    subprocess.run([adb, "install", "-r", str(signed_apk)], check=True)
    subprocess.run([adb, "logcat", "-c"], check=True)
    subprocess.run(
        [adb, "shell", "am", "start", "-n", "com.anali.preview/.MainActivity"],
        check=True,
    )
    time.sleep(1.0)
    logcat = subprocess.run(
        [adb, "logcat", "-d", "-s", "AndroidRuntime", "ActivityManager"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if "FATAL EXCEPTION" in logcat or "Process: com.anali.preview" in logcat:
        raise AssertionError(f"App crash detected in logcat:\n{logcat}")
