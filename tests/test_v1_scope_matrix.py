import json
from pathlib import Path

from tools.v1_scope_matrix import build_v1_scope_matrix, check_v1_scope_matrix


def test_v1_scope_matrix_matches_masterplan_contract():
    ok, message = check_v1_scope_matrix(
        masterplan=Path("docs/Masterplan_All_In_One.md"),
        matrix_path=Path("cfg/v1_scope_matrix.yaml"),
    )
    assert ok, message


def test_v1_scope_matrix_done_status_requires_docs_and_tests(tmp_path):
    matrix = build_v1_scope_matrix(masterplan=Path("docs/Masterplan_All_In_One.md"))
    assert matrix["entries"]
    matrix["entries"][0]["status"] = "done"
    matrix["entries"][0]["tests_required"] = []
    matrix["entries"][0]["docs_required"] = []

    p = tmp_path / "v1_scope_matrix.yaml"
    p.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ok, message = check_v1_scope_matrix(
        masterplan=Path("docs/Masterplan_All_In_One.md"),
        matrix_path=p,
    )
    assert not ok
    assert "status=done requires non-empty tests_required" in message


def test_v1_scope_matrix_rebaseline_rejects_planned_status_for_frozen_scope(tmp_path):
    matrix = build_v1_scope_matrix(masterplan=Path("docs/Masterplan_All_In_One.md"))
    assert matrix["entries"]
    matrix["entries"][0]["status"] = "planned"

    p = tmp_path / "v1_scope_matrix.yaml"
    p.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ok, message = check_v1_scope_matrix(
        masterplan=Path("docs/Masterplan_All_In_One.md"),
        matrix_path=p,
    )
    assert not ok
    assert "static-v1 rebaseline" in message


def test_v1_scope_matrix_enforces_guardrail_scope_flags(tmp_path):
    matrix = build_v1_scope_matrix(masterplan=Path("docs/Masterplan_All_In_One.md"))
    matrix["scope_flags"]["reactive_opt_in"] = False

    p = tmp_path / "v1_scope_matrix.yaml"
    p.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ok, message = check_v1_scope_matrix(
        masterplan=Path("docs/Masterplan_All_In_One.md"),
        matrix_path=p,
    )
    assert not ok
    assert "scope_flags['reactive_opt_in'] must be True" in message


def test_v1_scope_matrix_done_status_requires_pytest_discoverable_test_paths(tmp_path):
    matrix = build_v1_scope_matrix(masterplan=Path("docs/Masterplan_All_In_One.md"))
    assert matrix["entries"]
    matrix["entries"][0]["status"] = "done"
    matrix["entries"][0]["tests_required"] = ["docs/not_a_test.md"]
    matrix["entries"][0]["docs_required"] = ["README.md"]

    p = tmp_path / "v1_scope_matrix.yaml"
    p.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ok, message = check_v1_scope_matrix(
        masterplan=Path("docs/Masterplan_All_In_One.md"),
        matrix_path=p,
    )
    assert not ok
    assert "tests_required entry must be under tests/" in message
