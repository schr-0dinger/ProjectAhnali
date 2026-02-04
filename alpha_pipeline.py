# alpha_pipeline.py

from cfg.builder import CFGBuilder
from cfg.validate import validate_cfg
from cfg.dominance import (
    compute_dominators,
    compute_immediate_dominators,
    build_dominator_tree,
)
from cfg.frontier import compute_dominance_frontier
from passes.type_verify import verify_types
from ssa.insert_phi import insert_phi_nodes
from ssa.rename import SSARenamer
from ssa.verify import verify_ssa
from passes.lower_ssa_to_dalvik import LowerSSAToDalvik
from passes.dce import eliminate_dead_code
from passes.type_inference import TypeInferencePass



def alpha_pipeline(frontend_ir):
    """
    Complete Alpha pipeline:
    Structured IR → CFG → Dominance → Phi → SSA → Verify
    """

    # 1. CFG
    cfg = CFGBuilder().build(frontend_ir)
    validate_cfg(cfg)

    # 2. Dominance
    dom = compute_dominators(cfg)
    idom = compute_immediate_dominators(cfg, dom)
    dom_tree = build_dominator_tree(idom)

    # 3. Dominance Frontier
    df = compute_dominance_frontier(cfg, idom)

    # 4. Collect def blocks
    def_blocks = {}
    for b in cfg.blocks.values():
        for stmt in b.statements:
            if hasattr(stmt, "defines") and stmt.defines():
                name = stmt.defines().name
                def_blocks.setdefault(name, set()).add(b)

    # 5. Phi insertion
    phi_nodes = insert_phi_nodes(cfg, df, def_blocks)

    # 6. SSA renaming
    renamer = SSARenamer(cfg, dom_tree, phi_nodes)
    ssa_blocks = renamer.run()

    # 7. SSA verification (hard gate)
    verify_ssa(cfg, ssa_blocks, dom)

    # 8. NEW: Type Inference (Phase Omega Gate)
    TypeInferencePass(cfg, ssa_blocks).run()

    verify_types(ssa_blocks)

    # 9. SSA → Dalvik lowering (no registers)
    dalvik_blocks = LowerSSAToDalvik(cfg, ssa_blocks).run()

    # 10. Optimizations
    dalvik_blocks = eliminate_dead_code(dalvik_blocks)

    return {
        "cfg": cfg,
        "dominators": dom,
        "idom": idom,
        "dom_tree": dom_tree,
        "df": df,
        "phi_nodes": phi_nodes,
        "ssa": ssa_blocks,
        "dalvik": dalvik_blocks,
    }
