from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from ir.expr import BinaryOp, Var, Const, Call, Compare
from ir.types import AhnaliType


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


def test_constfold_skips_mod_by_zero():
    ir = [
        Assign("x", 1),
        Assign("y", 0),
        Assign("z", BinaryOp("%", Var("x"), Var("y"))),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    for b in ssa_blocks.values():
        for stmt in b.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, BinaryOp):
                assert expr.op == "%"


def test_constfold_skips_bool_operands():
    ir = [
        Assign("x", True),
        Assign("y", False),
        Assign("z", BinaryOp("+", Var("x"), Var("y"))),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    for b in ssa_blocks.values():
        for stmt in b.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, BinaryOp):
                assert isinstance(expr.left, Const)
                assert isinstance(expr.right, Const)
                assert isinstance(expr.left.value, bool)
                assert isinstance(expr.right.value, bool)


def test_constfold_skips_non_const_operand():
    ir = [
        Assign(
            "x",
            Call(
                "foo",
                args=[],
                return_type=AhnaliType.INT,
                arg_types=[],
            ),
        ),
        Assign("y", BinaryOp("+", Var("x"), Const(2))),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    for b in ssa_blocks.values():
        for stmt in b.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, BinaryOp):
                assert not isinstance(expr.left, Const)
                assert isinstance(expr.right, Const)


def test_constfold_branch_heavy_keeps_binaryop_when_needed():
    ir = [
        Assign("x", 1),
        Assign("y", 2),
        If("x", [Assign("z", BinaryOp("+", Var("x"), Var("y")))], []),
        Assign("w", "z"),
        If(Compare("!=", Var("w"), Const(0)), [], []),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    has_binaryop_or_const = False
    for b in ssa_blocks.values():
        for stmt in b.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, (BinaryOp, Const)):
                has_binaryop_or_const = True

    assert has_binaryop_or_const


def test_constfold_extended_int_binary_ops():
    ir = [
        Assign("x", 12),
        Assign("y", 5),
        Assign("a", BinaryOp("&", Var("x"), Var("y"))),
        Assign("b", BinaryOp("|", Var("x"), Var("y"))),
        Assign("c", BinaryOp("^", Var("x"), Var("y"))),
        Assign("d", BinaryOp("<<", Var("x"), Const(1))),
        Assign("e", BinaryOp(">>", Var("x"), Const(1))),
        Assign("f", BinaryOp(">>>", Var("x"), Const(1))),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    folded_values = {expr.value for b in ssa_blocks.values() for stmt in b.statements for expr in [getattr(stmt, "expr", None)] if isinstance(expr, Const)}

    assert (12 & 5) in folded_values
    assert (12 | 5) in folded_values
    assert (12 ^ 5) in folded_values
    assert (12 << 1) in folded_values
    assert (12 >> 1) in folded_values
    assert 6 in folded_values  # 12 >>> 1


def test_constfold_unsigned_right_shift_negative():
    ir = [
        Assign("x", -2),
        Assign("y", BinaryOp(">>>", Var("x"), Const(1))),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_folding": True})
    ssa_blocks = result["ssa"]

    folded_values = {expr.value for b in ssa_blocks.values() for stmt in b.statements for expr in [getattr(stmt, "expr", None)] if isinstance(expr, Const)}
    assert 0x7FFFFFFF in folded_values
