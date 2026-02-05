# cfg/dominance.py

def compute_dominators(cfg):
    """
    Compute dominator sets for all blocks using
    the classic iterative algorithm.
    Dominance is defined ONLY over normal control-flow edges.
    """

    blocks = list(cfg.blocks.values())
    entry = cfg.entry

    exceptional_preds = {b: set() for b in blocks}
    for b in blocks:
        for succ in b.exceptional_successors:
            exceptional_preds[succ].add(b)

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

            preds = b.predecessors or exceptional_preds[b]
            if not preds:
                new_dom = {b}
            else:
                new_dom = {b}.union(
                    set.intersection(*(dom[p] for p in preds))
                )

            if new_dom != dom[b]:
                dom[b] = new_dom
                changed = True

    return dom


def compute_immediate_dominators(cfg, dom):
    """
    Compute immediate dominators from dominator sets.
    """

    idom = {}
    entry = cfg.entry
    idom[entry] = None

    for b in cfg.blocks.values():
        if b is entry:
            continue

        strict_doms = dom[b] - {b}
        candidate = None

        for d in strict_doms:
            if all(
                d == other or d not in dom[other]
                for other in strict_doms
            ):
                candidate = d
                break

        if candidate is None:
            # Unreachable block (e.g., synthetic exit when returns exist)
            idom[b] = None
            continue

        idom[b] = candidate

    return idom


def build_dominator_tree(idom):
    """
    Build dominator tree from immediate dominators.
    """

    tree = {b: [] for b in idom}

    for b, parent in idom.items():
        if parent is not None:
            tree[parent].append(b)

    return tree
