# passes/edge_split.py

from cfg.graph import ControlFlowGraph
def split_critical_edges(cfg: ControlFlowGraph, ssa_blocks: dict | None = None):
    """
    Split critical edges (pred with multiple successors -> succ with multiple predecessors)
    by inserting a new synthetic block between them.

    Updates CFG structure and Phi incoming maps to reference the new block.
    """
    if cfg is None:
        return

    # Collect edges first to avoid mutating during iteration.
    critical_edges = []
    for pred in list(cfg.blocks.values()):
        succs = list(pred.successors)
        if len(succs) <= 1:
            continue
        for succ in succs:
            if len(succ.predecessors) > 1:
                critical_edges.append((pred, succ))

    for pred, succ in critical_edges:
        # Create new block
        new_block = cfg.new_block()

        # Wire pred -> new_block
        if succ in pred.successors:
            pred.successors.remove(succ)
        pred.add_successor(new_block)

        # Wire new_block -> succ
        new_block.add_successor(succ)
        if pred in succ.predecessors:
            succ.predecessors.remove(pred)

        # Update pred terminator target(s)
        term = getattr(pred, "terminator", None)
        if term is not None:
            if getattr(term, "kind", None) == "branch":
                if term.true is succ:
                    term.true = new_block
                if term.false is succ:
                    term.false = new_block
            elif getattr(term, "kind", None) == "jump":
                if term.target is succ:
                    term.target = new_block

        # Set new block terminator as jump to succ
        new_block.terminator = type("Terminator", (), {"kind": "jump", "target": succ})()

        # Create SSA block for new block (empty statements/phis)
        if ssa_blocks is not None and new_block not in ssa_blocks:
            from ssa.block import SSABlock

            ssa_blocks[new_block] = SSABlock(new_block)

        # Redirect Phi incoming edges to the new block
        succ_ssa = ssa_blocks.get(succ) if ssa_blocks is not None else None
        if succ_ssa:
            for phi in succ_ssa.phis:
                if pred in phi.incoming:
                    phi.incoming[new_block] = phi.incoming.pop(pred)
