import json
from pathlib import Path

from tools.reactive_surface_snapshot import (
    build_reactive_surface_snapshot,
    check_reactive_surface_snapshot,
)


def test_reactive_surface_snapshot_matches_committed_contract():
    ok, message = check_reactive_surface_snapshot(Path("cfg/reactive_surface_snapshot_v1.json"))
    assert ok, message


def test_reactive_surface_snapshot_includes_mode_guardrails_and_symbols():
    snapshot = build_reactive_surface_snapshot()
    mode = snapshot["mode_contract"]
    assert mode["default"] == "static"
    assert mode["reactive_opt_in"] is True
    assert mode["no_implicit_diff"] is True

    symbols = snapshot["dsl_symbols"]
    assert "observable" in symbols["statements"]
    assert "set_observable" in symbols["statements"]
    assert "bind_text" in symbols["statements"]
    assert "observable_get" in symbols["expressions"]


def test_reactive_surface_snapshot_check_detects_drift(tmp_path):
    baseline = build_reactive_surface_snapshot()
    snapshot_path = tmp_path / "reactive_surface_snapshot_v1.json"
    snapshot_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    drifted = json.loads(snapshot_path.read_text(encoding="utf-8"))
    drifted["dsl_symbols"]["statements"] = []
    snapshot_path.write_text(json.dumps(drifted, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ok, message = check_reactive_surface_snapshot(snapshot_path)
    assert not ok
    assert "Reactive surface snapshot drift detected." in message
