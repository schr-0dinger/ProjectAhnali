from cfg.builder import CFGBuilder
from cfg.dominance import (
    compute_dominators,
    compute_immediate_dominators,
)
from tests.ir_stub import Assign, If


def test_dominators_if_else():
    ir = [
        Assign("x", 0),
        If("c", [Assign("x", 1)], [Assign("x", 2)]),
        Assign("y", "x"),
    ]

    cfg = CFGBuilder().build(ir)

    dom = compute_dominators(cfg)
    idom = compute_immediate_dominators(cfg, dom)

    entry = cfg.entry

    # Entry dominates all
    for b in cfg.blocks.values():
        assert entry in dom[b]

    # Merge is dominated by entry
    merge = [b for b in cfg.blocks.values() if len(b.predecessors) == 2][0]
    assert idom[merge] == entry
