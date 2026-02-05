from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from dalvik.ir import DIf


def test_ssa_coalesce_preserves_branch_semantics():
    ir = [
        Assign("x", 1),
        Assign("y", "x"),
        Assign("z", "y"),
        If("z", [], []),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_coalesce": True})
    dalvik = result["dalvik"]

    # Ensure branch still exists after aggressive coalescing + DCE
    assert any(isinstance(i, DIf) for b in dalvik.values() for i in b.instructions)
