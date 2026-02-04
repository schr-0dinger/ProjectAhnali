from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from ir.expr import BinaryOp, Compare, Var, Const
from dalvik.ir import DAdd, DConst


def test_binaryop_add_lowers_to_dadd():
    ir = [
        Assign("x", 1),
        Assign(
            "y",
            BinaryOp("+", Var("x"), Const(2))
        ),
        If(Compare("==", Var("y"), Const(3)), [], [])
    ]

    result = alpha_pipeline(ir)
    dalvik_blocks = result["dalvik"]

    adds = []
    consts = []

    for block in dalvik_blocks.values():
        for instr in block.instructions:
            if isinstance(instr, DAdd):
                adds.append(instr)
            if isinstance(instr, DConst):
                consts.append(instr)

    # One const for literal 2
    assert any(c.value == 2 for c in consts)
    assert len(adds) == 1

    # One arithmetic instruction
    assert len(adds) == 1

    add = adds[0]
    assert add.dst is not None
    assert add.lhs is not None
    assert add.rhs is not None
