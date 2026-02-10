import os
import shutil
import subprocess
import time
import pytest

from apk.toolchain import (
    emit_build_dir_from_program,
    run_smali,
    run_baksmali,
    package_apk_from_dex,
    _tool_path,
    _collect_toolchain_diagnostics,
)
from dsl.app import assign, const
from dsl.app import app, activity, ui, text, button, row


def _has_android_sdk():
    return bool(os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT"))


def _has_tool(name: str):
    if shutil.which(name) is not None:
        return True
    local_bin = os.path.expanduser(f"~/.local/bin/{name}")
    return os.path.exists(local_bin)


def _has_baksmali():
    if _has_tool("baksmali"):
        return True
    return bool(os.environ.get("BAKSMALI_JAR"))


def _skip_if_missing(require_adb=False, require_baksmali=False):
    issues = _collect_toolchain_diagnostics(
        require_adb=require_adb,
        require_baksmali=require_baksmali,
    )
    if issues:
        pytest.skip("; ".join(issues))


def _smali_jar():
    return os.environ.get("SMALI_JAR")


def test_omega_apk_packaging_integration(tmp_path):
    _skip_if_missing()
    smali_jar = _smali_jar()

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
    _skip_if_missing()
    smali_jar = _smali_jar()

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
    _skip_if_missing(require_adb=True)
    if not _has_device():
        pytest.skip("no adb devices in 'device' state")
    smali_jar = _smali_jar()

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


def test_omega_smali_register_nibble_safety_integration(tmp_path):
    _skip_if_missing()
    smali_jar = _smali_jar()

    rows = []
    for i in range(20):
        rows.append(
            row(
                button(f"B{i}a", id=f"b_{i}_a", padding=12, margin=8, layout=("wrap", "wrap")),
                button(f"B{i}b", id=f"b_{i}_b", padding=12, margin=8, layout=("wrap", "wrap")),
                id=f"row_{i}",
                margin=8,
                layout=("match", "wrap"),
            )
        )
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Register safety", id="title", margin=8, padding=8),
                *rows,
            ),
        )
    )

    out_dir = emit_build_dir_from_program(
        prog.build(),
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/anali/preview/MainActivity;",
    )
    dex_path = run_smali(
        out_dir / "smali",
        out_dir=out_dir / "classes.dex",
        smali_jar=smali_jar,
        api=21,
    )
    assert dex_path.exists()


def test_omega_smali_baksmali_roundtrip(tmp_path):
    _skip_if_missing(require_baksmali=True)
    smali_jar = _smali_jar()

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
    baksmali_jar = os.environ.get("BAKSMALI_JAR")
    disasm_dir = tmp_path / "disasm"
    run_baksmali(dex_path, disasm_dir, baksmali_jar=baksmali_jar)
    # Expect at least one disassembled class
    assert any(p.suffix == ".smali" for p in disasm_dir.rglob("*.smali"))


def test_omega_smali_baksmali_smali_roundtrip(tmp_path):
    _skip_if_missing(require_baksmali=True)
    smali_jar = _smali_jar()

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

    baksmali_jar = os.environ.get("BAKSMALI_JAR")
    disasm_dir = tmp_path / "disasm_roundtrip"
    run_baksmali(dex_path, disasm_dir, baksmali_jar=baksmali_jar)

    # Re-assemble disassembled smali to ensure verifier-safe output.
    roundtrip_dex = run_smali(
        disasm_dir,
        out_dir=tmp_path / "classes_roundtrip.dex",
        smali_jar=smali_jar,
        api=21,
    )
    assert roundtrip_dex.exists()
