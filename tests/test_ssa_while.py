from cfg.builder import CFGBuilder
from cfg.dominance import (
    compute_dominators,
    compute_immediate_dominators,
    build_dominator_tree,
)
from cfg.frontier import compute_dominance_frontier
from ssa.insert_phi import insert_phi_nodes
from ssa.rename import SSARenamer
from tests.ir_stub import Assign, While


def test_while_loop_phi_and_versions():
    """
    x = 0
    while c:
        x = x + 1
    y = x
    """

    ir = [
        Assign("x", 0),
        While(
            cond="c",
            body=[Assign("x", "x")],  # symbolic increment
        ),
        Assign("y", "x"),
    ]

    cfg = CFGBuilder().build(ir)

    # ---- dominance ----
    dom = compute_dominators(cfg)
    idom = compute_immediate_dominators(cfg, dom)
    dom_tree = build_dominator_tree(idom)

    # ---- dominance frontier ----
    df = compute_dominance_frontier(cfg, idom)

    # ---- def blocks ----
    def_blocks = {}
    for b in cfg.blocks.values():
        for stmt in b.statements:
            if isinstance(stmt, Assign):
                def_blocks.setdefault(stmt.name, set()).add(b)

    # ---- phi insertion ----
    phi_nodes = insert_phi_nodes(cfg, df, def_blocks)

    # Find loop header (block with 2 predecessors, one is back-edge)
    loop_headers = [
        b for b in cfg.blocks.values()
        if len(b.predecessors) == 2
    ]
    assert len(loop_headers) == 1, "Expected exactly one loop header"

    header = loop_headers[0]
    assert header in phi_nodes and phi_nodes[header], "Loop header must contain Phi nodes"

