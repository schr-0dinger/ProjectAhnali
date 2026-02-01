from cfg.builder import CFGBuilder
from tests.ir_stub import Assign, If, While


def test_if_else_cfg_shape():
    ir = [
        Assign("x", 0),
        If(
            cond="c",
            then=[Assign("x", 1)],
            else_=[Assign("x", 2)],
        ),
        Assign("y", "x"),
    ]

    cfg = CFGBuilder().build(ir)

    blocks = list(cfg.blocks.values())

    # Expect: entry + then + else + merge + exit = 5
    assert len(blocks) == 5

    entry = cfg.entry
    merge = None

    for b in blocks:
        if len(b.predecessors) == 2:
            merge = b

    assert merge is not None, "Merge block not created"

    # Merge must have exactly 2 predecessors
    assert len(merge.predecessors) == 2
