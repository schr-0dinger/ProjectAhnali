from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from ir.expr import BinaryOp, Compare, Var, Const
from dalvik.ir import DAdd


def test_binaryop_with_phi_lowering():
    ir = [
        Assign("x", 0),
        Assign("c", 1),
        If(
            "c",
            then=[Assign("x", BinaryOp("+", Var("x"), Const(1)))],
            else_=[Assign("x", BinaryOp("+", Var("x"), Const(2)))],
        ),
        Assign("y", "x"),
        If(Compare("!=", Var("y"), Const(0)), [], [])
    ]

    result = alpha_pipeline(ir)
    dalvik_blocks = result["dalvik"]

    adds = []
    for block in dalvik_blocks.values():
        for instr in block.instructions:
            if isinstance(instr, DAdd):
                adds.append(instr)

    # One add in each branch
    assert len(adds) == 2
