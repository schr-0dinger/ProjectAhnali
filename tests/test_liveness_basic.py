from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from ir.expr import BinaryOp, Var, Const


def test_liveness_marks_used_values_live():
    ir = [
        Assign("x", 1),
        Assign("y", BinaryOp("+", Var("x"), Const(2))),
        Assign("z", "y"),
        If("z", [], []),
    ]

    result = alpha_pipeline(ir)
    liveness = result["liveness"]

    # At least one block must have live-in values
    assert any(liveness.live_in[b] for b in liveness.live_in)
