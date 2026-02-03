import pytest
from cfg.builder import CFGBuilder
from tests.ir_stub import Assign, If
from ir.expr import Var


def test_non_compare_expr_rejected_in_condition():
    ir = [
        Assign("x", 0),
        If(Var("x"), [], []),  # Var is Expr but not Compare
    ]

    with pytest.raises(TypeError):
        CFGBuilder().build(ir)
