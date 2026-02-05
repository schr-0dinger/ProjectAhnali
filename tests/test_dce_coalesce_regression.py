from alpha_pipeline import alpha_pipeline
from passes.dce import eliminate_dead_code
from tests.ir_stub import Assign, If
from dalvik.ir import DIf, DConst


def test_dce_with_coalesce_preserves_live_condition():
    ir = [
        Assign("x", 1),
        Assign("y", "x"),
        Assign("z", "y"),
        If("z", [], []),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_coalesce": True})
    dalvik = result["dalvik"]

    eliminate_dead_code(dalvik)

    instrs = [i for b in dalvik.values() for i in b.instructions]
    assert any(isinstance(i, DIf) for i in instrs)
    assert any(isinstance(i, DConst) for i in instrs)
