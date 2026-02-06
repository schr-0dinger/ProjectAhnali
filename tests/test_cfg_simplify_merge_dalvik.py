from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign


def test_cfg_block_merging_does_not_change_smali_shape():
    ir = [
        Assign("x", 1),
        Assign("y", "x"),
        Assign("z", "y"),
    ]

    result = alpha_pipeline(ir)
    smali = result["smali"]

    # Ensure Smali still contains at least one basic block label
    assert ":B" in smali
