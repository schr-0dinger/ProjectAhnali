from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from ir.expr import BinaryOp, Compare, Var, Const
from dalvik.ir import DAdd, DMul


def test_chained_binaryops_lower_correctly():
    ir = [
        Assign("x", 2),
        Assign("y", BinaryOp("+", Var("x"), Const(1))),
        Assign("z", BinaryOp("*", Var("y"), Const(4))),

        If(Compare(">", Var("z"), Const(0)), [], [])
    ]

    result = alpha_pipeline(ir)
    dalvik_blocks = result["dalvik"]

    adds = 0
    muls = 0

    for block in dalvik_blocks.values():
        for instr in block.instructions:
            if isinstance(instr, DAdd):
                adds += 1
            if isinstance(instr, DMul):
                muls += 1

    assert adds == 1
    assert muls == 1
