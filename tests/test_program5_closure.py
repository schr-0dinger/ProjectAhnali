from pathlib import Path


def test_program5_closure_doc_exists_and_references_required_artifacts():
    doc = Path("docs/Program5_Closure.md")
    assert doc.exists(), "Program 5 closure doc is required"
    text = doc.read_text(encoding="utf-8")

    required_refs = [
        "tests/test_program5_state_backends.py",
        "tests/test_program5_lifecycle.py",
        "tests/test_runtime_abi_v1.py",
        "tests/test_runtime_abi_snapshot.py",
        "README.md",
        "runtime_abi_v1.md",
        "docs/capability_runtime_mapping_v1.md",
    ]
    for ref in required_refs:
        assert ref in text, f"Missing Program 5 closure reference: {ref}"
