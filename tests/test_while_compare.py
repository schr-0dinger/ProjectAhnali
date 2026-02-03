from cfg.builder import CFGBuilder
from tests.ir_stub import Assign, While
from ir.expr import Compare, Var, Const


def test_while_with_compare_condition():
    ir = [
        Assign("i", 0),
        While(
            Compare("<", Var("i"), Const(10)),
            body=[Assign("i", "i")],
        ),
        Assign("x", "i"),
    ]

    cfg = CFGBuilder().build(ir)

    # Loop header has two predecessors (entry + backedge)
    headers = [
        b for b in cfg.blocks.values()
        if len(b.predecessors) == 2
    ]

    assert len(headers) == 1
