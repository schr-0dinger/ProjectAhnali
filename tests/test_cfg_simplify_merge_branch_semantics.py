from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If


def test_block_merge_preserves_branch_semantics():
    ir = [
        Assign("x", 1),
        If("x", [Assign("y", 1)], [Assign("y", 2)]),
        Assign("z", "y"),
        If("z", [], []),
    ]

    result = alpha_pipeline(ir)
    smali = result["smali"]

    # Ensure branch is still emitted after block merging
    assert "if-" in smali
