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


def test_constfold_flag_folds_binaryop():
    ir = [
        Assign("x", 1),
        Assign("y", 2),
        Assign("z", BinaryOp("+", Var("x"), Var("y"))),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    folded = False
    for b in ssa_blocks.values():
        for stmt in b.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, Const) and expr.value == 3:
                folded = True

    assert folded


def test_constfold_multiple_ops_chain():
    ir = [
        Assign("a", 2),
        Assign("b", 3),
        Assign("c", BinaryOp("*", Var("a"), Var("b"))),
        Assign("d", BinaryOp("+", Var("c"), Const(4))),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    folded_values = []
    for b in ssa_blocks.values():
        for stmt in b.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, Const):
                folded_values.append(expr.value)

    assert 6 in folded_values
    assert 10 in folded_values


def test_constfold_skips_division_by_zero():
    ir = [
        Assign("x", 1),
        Assign("y", 0),
        Assign("z", BinaryOp("/", Var("x"), Var("y"))),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    # Should not fold; division by zero is unsafe
    for b in ssa_blocks.values():
        for stmt in b.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, BinaryOp):
                assert expr.op == "/"
