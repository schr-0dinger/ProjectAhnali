from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If



def test_cfg_simplify_branch_heavy_preserves_validity():
    ir = [
        Assign("x", 1),
        If("x", [Assign("y", 1)], [Assign("y", 2)]),
        If("y", [Assign("z", 3)], [Assign("z", 4)]),
        If("z", [], []),
    ]

    result = alpha_pipeline(ir)
    dalvik = result["dalvik"]

    # Ensure CFG simplification did not break emission path
    assert any(b.instructions is not None for b in dalvik.values())
