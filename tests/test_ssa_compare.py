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
from ir.expr import Compare, Var
from ssa.value import SSAValue


def test_ssa_renames_compare_operands():
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

    # Find branch block
    branch_blocks = [
        b for b in cfg.blocks.values()
        if b.terminator and b.terminator.kind == "branch"
    ]
    assert len(branch_blocks) == 1

    term = branch_blocks[0].terminator
    cond = term.cond

    assert isinstance(cond, Compare)
    assert isinstance(cond.left, SSAValue)
    assert isinstance(cond.right, SSAValue)
