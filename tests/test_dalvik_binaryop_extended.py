from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from ir.expr import BinaryOp, Compare, Var, Const
from dalvik.ir import DAnd, DOr, DXor, DShl, DShr, DUshr


def test_extended_binaryops_lower_correctly():
    ir = [
        Assign("x", 42),
        Assign("y", 5),
        Assign("a", BinaryOp("&", Var("x"), Var("y"))),
        Assign("b", BinaryOp("|", Var("a"), Var("y"))),
        Assign("c", BinaryOp("^", Var("b"), Var("x"))),
        Assign("d", BinaryOp("<<", Var("c"), Const(1))),
        Assign("e", BinaryOp(">>", Var("d"), Const(1))),
        Assign("f", BinaryOp(">>>", Var("e"), Const(1))),
        If(Compare("!=", Var("f"), Const(0)), [], []),
    ]

    result = alpha_pipeline(ir)
    dalvik_blocks = result["dalvik"]

    counts = {
        DAnd: 0,
        DOr: 0,
        DXor: 0,
        DShl: 0,
        DShr: 0,
        DUshr: 0,
    }

    for block in dalvik_blocks.values():
        for instr in block.instructions:
            for cls in counts:
                if isinstance(instr, cls):
                    counts[cls] += 1

    assert counts[DAnd] == 1
    assert counts[DOr] == 1
    assert counts[DXor] == 1
    assert counts[DShl] == 1
    assert counts[DShr] == 1
    assert counts[DUshr] == 1
