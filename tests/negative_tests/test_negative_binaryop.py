import pytest
from ir.expr import BinaryOp, Var, Const


def test_invalid_binaryop_operator_rejected():
    with pytest.raises(ValueError):
        BinaryOp("**", Var("x"), Const(2))
