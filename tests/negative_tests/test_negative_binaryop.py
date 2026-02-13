import pytest
from ir.expr import BinaryOp, Var, Const


def test_invalid_binaryop_operator_rejected():
    with pytest.raises(ValueError):
        BinaryOp("**", Var("x"), Const(2))


def test_extended_binaryop_operators_accepted():
    BinaryOp("&", Var("x"), Const(2))
    BinaryOp("|", Var("x"), Const(2))
    BinaryOp("^", Var("x"), Const(2))
    BinaryOp("<<", Var("x"), Const(2))
    BinaryOp(">>", Var("x"), Const(2))
    BinaryOp(">>>", Var("x"), Const(2))
