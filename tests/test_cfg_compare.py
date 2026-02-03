from cfg.builder import CFGBuilder
from tests.ir_stub import Assign, If
from ir.expr import Compare, Var


def test_cfg_if_with_compare_condition():
    ir = [
        Assign("x", 0),
        Assign("y", 1),
        If(
            Compare("<", Var("x"), Var("y")),
            then=[Assign("x", 2)],
            else_=[Assign("x", 3)],
        ),
        Assign("z", "x"),
    ]

    cfg = CFGBuilder().build(ir)

    # Expect: entry + then + else + merge + exit
    assert len(cfg.blocks) == 5

    merge_blocks = [b for b in cfg.blocks.values() if len(b.predecessors) == 2]
    assert len(merge_blocks) == 1
