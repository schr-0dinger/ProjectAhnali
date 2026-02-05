from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign
from ir.expr import BinaryOp, Var, Const


def test_constprop_folds_binaryop():
    ir = [
        Assign("x", 1),
        Assign("y", 2),
        Assign("z", BinaryOp("+", Var("x"), Var("y"))),
    ]

    result = alpha_pipeline(ir)
    ssa_blocks = result["ssa"]

    left_right_consts = False
    for b in ssa_blocks.values():
        for stmt in b.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, BinaryOp):
                if isinstance(expr.left, Const) and isinstance(expr.right, Const):
                    left_right_consts = True

    assert left_right_consts
