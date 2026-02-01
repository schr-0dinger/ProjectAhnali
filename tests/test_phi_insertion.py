from cfg.builder import CFGBuilder
from cfg.dominance import compute_dominators, compute_immediate_dominators
from cfg.frontier import compute_dominance_frontier
from ssa.insert_phi import insert_phi_nodes
from tests.ir_stub import Assign, If


def test_phi_inserted_at_merge():
    ir = [
        Assign("x", 0),
        If("c", [Assign("x", 1)], [Assign("x", 2)]),
        Assign("y", "x"),
    ]

    cfg = CFGBuilder().build(ir)
    dom = compute_dominators(cfg)
    idom = compute_immediate_dominators(cfg, dom)
    df = compute_dominance_frontier(cfg, idom)

    def_blocks = {}
    for b in cfg.blocks.values():
        for stmt in b.statements:
            if isinstance(stmt, Assign):
                def_blocks.setdefault(stmt.name, set()).add(b)

    phi_nodes = insert_phi_nodes(cfg, df, def_blocks)

    merge = [b for b in cfg.blocks.values() if len(b.predecessors) == 2][0]

    assert merge in phi_nodes
    assert len(phi_nodes[merge]) == 1
    assert phi_nodes[merge][0].target.name == "x"
