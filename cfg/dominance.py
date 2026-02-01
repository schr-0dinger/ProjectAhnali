# cfg/dominance.py

def compute_dominators(cfg):
    """
    Compute dominator sets for all blocks using
    the classic iterative algorithm.
    Returns: dict[BasicBlock, set[BasicBlock]]
    """

    blocks = list(cfg.blocks.values())
    entry = cfg.entry

    # Initialize
    dom = {}
    for b in blocks:
        if b is entry:
            dom[b] = {b}
        else:
            dom[b] = set(blocks)

    changed = True
    while changed:
        changed = False

        for b in blocks:
            if b is entry:
                continue

            if not b.predecessors:
                new_dom = {b}
            else:
                new_dom = {b}.union(
                    set.intersection(*(dom[p] for p in b.predecessors))
                )

            if new_dom != dom[b]:
                dom[b] = new_dom
                changed = True

    return dom


def compute_immediate_dominators(cfg, dom):
    """
    Compute immediate dominators from dominator sets.
    Returns: dict[BasicBlock, BasicBlock | None]
    """

    idom = {}
    entry = cfg.entry

    idom[entry] = None

    for b in cfg.blocks.values():
        if b is entry:
            continue

        strict_doms = dom[b] - {b}

        # Immediate dominator is the strict dominator
        # that dominates all other strict dominators
        candidate = None
        for d in strict_doms:
            if all(
                d == other or d not in dom[other]
                for other in strict_doms
            ):
                candidate = d
                break

        if candidate is None:
            raise RuntimeError(
                f"No immediate dominator found for block {b.id}"
            )

        idom[b] = candidate

    return idom


def build_dominator_tree(idom):
    """
    Build dominator tree from immediate dominators.
    Returns: dict[BasicBlock, list[BasicBlock]]
    """

    tree = {b: [] for b in idom}

    for b, parent in idom.items():
        if parent is not None:
            tree[parent].append(b)

    return tree
