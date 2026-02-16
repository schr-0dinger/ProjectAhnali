import subprocess
import os

import pytest

from apk.toolchain import run_baksmali, run_smali


def test_run_smali_jar_falls_back_to_classpath_main(tmp_path, monkeypatch):
    smali_dir = tmp_path / "smali"
    smali_dir.mkdir(parents=True, exist_ok=True)
    out_dex = tmp_path / "classes.dex"
    jar_path = tmp_path / "smali.jar"

    calls: list[list[str]] = []

    def _fake_run(cmd, capture_output=False, text=False, check=False):
        calls.append(list(cmd))
        if len(calls) == 1:
            return subprocess.CompletedProcess(cmd, 1, "", "no main manifest attribute")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("apk.toolchain.subprocess.run", _fake_run)

    run_smali(smali_dir, out_dir=out_dex, smali_jar=str(jar_path), api=21)

    assert calls[0][:3] == ["java", "-jar", str(jar_path)]
    assert calls[1][0:2] == ["java", "-cp"]
    cp = calls[1][2]
    assert cp.startswith(str(jar_path))
    assert cp.endswith(str(jar_path.parent / "*"))
    assert os.pathsep in cp
    assert calls[1][3] == "org.jf.smali.Main"


def test_run_baksmali_jar_falls_back_to_classpath_main(tmp_path, monkeypatch):
    dex_path = tmp_path / "classes.dex"
    dex_path.write_bytes(b"dex\n")
    out_dir = tmp_path / "disasm"
    out_dir.mkdir(parents=True, exist_ok=True)
    jar_path = tmp_path / "baksmali.jar"

    calls: list[list[str]] = []

    def _fake_run(cmd, capture_output=False, text=False, check=False):
        calls.append(list(cmd))
        if len(calls) == 1:
            return subprocess.CompletedProcess(cmd, 1, "", "no main manifest attribute")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("apk.toolchain.subprocess.run", _fake_run)

    run_baksmali(dex_path, out_dir, baksmali_jar=str(jar_path))

    assert calls[0][:3] == ["java", "-jar", str(jar_path)]
    assert calls[1][0:2] == ["java", "-cp"]
    cp = calls[1][2]
    assert cp.startswith(str(jar_path))
    assert cp.endswith(str(jar_path.parent / "*"))
    assert os.pathsep in cp
    assert calls[1][3] == "org.jf.baksmali.Main"


def test_run_smali_jar_raises_after_all_launchers_fail(tmp_path, monkeypatch):
    smali_dir = tmp_path / "smali"
    smali_dir.mkdir(parents=True, exist_ok=True)
    out_dex = tmp_path / "classes.dex"
    jar_path = tmp_path / "smali.jar"

    def _fake_run(cmd, capture_output=False, text=False, check=False):
        return subprocess.CompletedProcess(cmd, 1, "", "launch failed")

    monkeypatch.setattr("apk.toolchain.subprocess.run", _fake_run)

    with pytest.raises(RuntimeError, match="Unable to run smali from jar"):
        run_smali(smali_dir, out_dir=out_dex, smali_jar=str(jar_path), api=21)
