# cfg/frontier.py

def compute_dominance_frontier(cfg, idom):
    """
    Compute dominance frontier for each block.

    Returns:
        dict[BasicBlock, set[BasicBlock]]
    """

    df = {b: set() for b in cfg.blocks.values()}

    for b in cfg.blocks.values():
        # Only blocks with multiple predecessors can be in a frontier
        if len(b.predecessors) >= 2:
            for p in b.predecessors:
                runner = p
                while runner is not None and runner != idom[b]:
                    df[runner].add(b)
                    runner = idom[runner]

    return df
