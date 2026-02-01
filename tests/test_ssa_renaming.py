from cfg.builder import CFGBuilder
from cfg.dominance import (
    compute_dominators,
    compute_immediate_dominators,
    build_dominator_tree,
)
from cfg.frontier import compute_dominance_frontier
from ssa.insert_phi import insert_phi_nodes
from ssa.rename import SSARenamer
from tests.ir_stub import Assign, If


def test_ssa_versions_and_phi_incoming():
    ir = [
        Assign("x", 0),
        If("c", [Assign("x", 1)], [Assign("x", 2)]),
        Assign("y", "x"),
    ]

    cfg = CFGBuilder().build(ir)

    dom = compute_dominators(cfg)
    idom = compute_immediate_dominators(cfg, dom)
    dom_tree = build_dominator_tree(idom)
    df = compute_dominance_frontier(cfg, idom)

    def_blocks = {}
    for b in cfg.blocks.values():
        for stmt in b.statements:
            if isinstance(stmt, Assign):
                def_blocks.setdefault(stmt.name, set()).add(b)

    phi_nodes = insert_phi_nodes(cfg, df, def_blocks)

    renamer = SSARenamer(cfg, dom_tree, phi_nodes)
    ssa_blocks = renamer.run()

    merge = [b for b in ssa_blocks if len(b.predecessors) == 2][0]
    ssa_merge = ssa_blocks[merge]

    assert len(ssa_merge.phis) == 1
    phi = ssa_merge.phis[0]

    incoming_versions = {v.version for v in phi.incoming.values()}
    assert len(incoming_versions) == 2
