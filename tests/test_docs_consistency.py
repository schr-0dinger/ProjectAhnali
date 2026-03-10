from pathlib import Path

from tools.docs_consistency import check_docs_consistency


def test_docs_consistency_passes_on_repo_docs():
    ok, message = check_docs_consistency(
        masterplan_path=Path("Masterplan_All_In_One.md"),
        readme_path=Path("README.md"),
        runtime_abi_path=Path("runtime_abi_v1.md"),
        capability_mapping_path=Path("docs/capability_runtime_mapping_v1.md"),
        program6b_path=Path("docs/Program6B_Task_Breakdown.md"),
    )
    assert ok, message


def test_docs_consistency_detects_readme_plan_order_drift(tmp_path):
    readme_path = tmp_path / "README.md"
    readme_text = Path("README.md").read_text(encoding="utf-8")
    readme_text = readme_text.replace("Program 11-A", "Program 6-A", 1)
    readme_path.write_text(readme_text, encoding="utf-8")

    ok, message = check_docs_consistency(
        masterplan_path=Path("Masterplan_All_In_One.md"),
        readme_path=readme_path,
        runtime_abi_path=Path("runtime_abi_v1.md"),
        capability_mapping_path=Path("docs/capability_runtime_mapping_v1.md"),
        program6b_path=Path("docs/Program6B_Task_Breakdown.md"),
    )
    assert not ok
    assert "README active v1 plan order mismatch" in message


def test_docs_consistency_detects_program6b_source_of_truth_drift(tmp_path):
    program6b_path = tmp_path / "Program6B_Task_Breakdown.md"
    text = Path("docs/Program6B_Task_Breakdown.md").read_text(encoding="utf-8")
    text = text.replace("source of truth", "progress note", 1)
    program6b_path.write_text(text, encoding="utf-8")

    ok, message = check_docs_consistency(
        masterplan_path=Path("Masterplan_All_In_One.md"),
        readme_path=Path("README.md"),
        runtime_abi_path=Path("runtime_abi_v1.md"),
        capability_mapping_path=Path("docs/capability_runtime_mapping_v1.md"),
        program6b_path=program6b_path,
    )
    assert not ok
    assert "source of truth" in message
