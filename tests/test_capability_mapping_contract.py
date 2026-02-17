import json
from pathlib import Path

from tools.capability_mapping_contract import (
    build_capability_mapping_snapshot,
    check_capability_mapping_contract,
)


def test_capability_mapping_contract_matches_committed_snapshot_and_docs():
    ok, message = check_capability_mapping_contract(
        snapshot_path=Path("cfg/capability_mapping_snapshot_v1.json"),
        docs_path=Path("docs/capability_runtime_mapping_v1.md"),
    )
    assert ok, message


def test_capability_mapping_contract_detects_snapshot_drift(tmp_path):
    baseline = build_capability_mapping_snapshot()
    snapshot_path = tmp_path / "capability_mapping_snapshot_v1.json"
    snapshot_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    drifted = json.loads(snapshot_path.read_text(encoding="utf-8"))
    drifted["entries"][0]["mode"] = "drifted"
    snapshot_path.write_text(json.dumps(drifted, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ok, message = check_capability_mapping_contract(
        snapshot_path=snapshot_path,
        docs_path=Path("docs/capability_runtime_mapping_v1.md"),
    )
    assert not ok
    assert "Capability mapping snapshot drift detected." in message


def test_capability_mapping_contract_detects_docs_drift(tmp_path):
    snapshot = build_capability_mapping_snapshot()
    snapshot_path = tmp_path / "capability_mapping_snapshot_v1.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    docs_path = tmp_path / "capability_runtime_mapping_v1.md"
    text = Path("docs/capability_runtime_mapping_v1.md").read_text(encoding="utf-8")
    text = text.replace("Lcom/ahnali/runtime/UrlLauncherHelper;", "Lcom/ahnali/runtime/BrokenHelper;", 1)
    docs_path.write_text(text, encoding="utf-8")

    ok, message = check_capability_mapping_contract(
        snapshot_path=snapshot_path,
        docs_path=docs_path,
    )
    assert not ok
    assert "missing helper class descriptor" in message
