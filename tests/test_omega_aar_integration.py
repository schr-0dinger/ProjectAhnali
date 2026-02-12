import json
import os
from pathlib import Path

import pytest

from apk.toolchain import _resolve_extra_aars


class _DummyProgram:
    def __init__(self, required_artifacts=None, jar_allowlist=None):
        self.required_artifacts = required_artifacts or []
        self.jar_allowlist = jar_allowlist or []


def test_aar_resolution_requires_libs_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    prog = _DummyProgram(required_artifacts=["material"])
    with pytest.raises(RuntimeError, match="Missing ./libs directory"):
        _resolve_extra_aars(prog, extra_aars=None)


def test_aar_resolution_from_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    libs = tmp_path / "libs"
    libs.mkdir(parents=True, exist_ok=True)
    # Create a dummy AAR file.
    dummy_aar = libs / "material-1.0.0.aar"
    dummy_aar.write_bytes(b"")
    # Write manifest with resolved artifacts.
    manifest = {"resolved": [str(dummy_aar)]}
    (libs / "aar_resolved.json").write_text(json.dumps(manifest), encoding="utf-8")

    prog = _DummyProgram(required_artifacts=["material"])
    resolved = _resolve_extra_aars(prog, extra_aars=None)
    assert resolved is not None
    assert any(Path(p).name == "material-1.0.0.aar" for p in resolved)


def test_aar_resolution_manifest_includes_transitive_aars(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    libs = tmp_path / "libs"
    libs.mkdir(parents=True, exist_ok=True)

    material = libs / "material-1.0.0.aar"
    appcompat = libs / "appcompat-1.0.0.aar"
    jar_ok = libs / "annotation-1.0.0.jar"
    jar_skip = libs / "not-allowed-1.0.0.jar"
    for path in (material, appcompat, jar_ok, jar_skip):
        path.write_bytes(b"")

    manifest = {
        "resolved": [
            str(material),
            str(appcompat),
            str(jar_ok),
            str(jar_skip),
        ]
    }
    (libs / "aar_resolved.json").write_text(json.dumps(manifest), encoding="utf-8")

    prog = _DummyProgram(required_artifacts=["material"], jar_allowlist=["annotation"])
    resolved = _resolve_extra_aars(prog, extra_aars=None)
    assert resolved is not None
    names = {Path(p).name for p in resolved}
    assert "material-1.0.0.aar" in names
    assert "appcompat-1.0.0.aar" in names
    assert "annotation-1.0.0.jar" in names
    assert "not-allowed-1.0.0.jar" not in names
