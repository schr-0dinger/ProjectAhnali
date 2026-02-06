import os
import shutil
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
    return shutil.which(name) is not None


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
    )
    signed_apk = package_apk_from_dex(dex_path, out_dir=out_dir)

    assert signed_apk.exists()
