import json
from pathlib import Path

from tools.v1_scope_matrix import build_v1_scope_matrix, check_v1_scope_matrix


def test_v1_scope_matrix_matches_masterplan_contract():
    ok, message = check_v1_scope_matrix(
        masterplan=Path("Masterplan_All_In_One.md"),
        matrix_path=Path("cfg/v1_scope_matrix.yaml"),
    )
    assert ok, message


def test_v1_scope_matrix_done_status_requires_docs_and_tests(tmp_path):
    matrix = build_v1_scope_matrix(masterplan=Path("Masterplan_All_In_One.md"))
    assert matrix["entries"]
    matrix["entries"][0]["status"] = "done"
    matrix["entries"][0]["tests_required"] = []
    matrix["entries"][0]["docs_required"] = []

    p = tmp_path / "v1_scope_matrix.yaml"
    p.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ok, message = check_v1_scope_matrix(
        masterplan=Path("Masterplan_All_In_One.md"),
        matrix_path=p,
    )
    assert not ok
    assert "status=done requires non-empty tests_required" in message
