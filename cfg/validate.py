# cfg/validate.py

from collections import deque

class CFGValidationError(RuntimeError):
    pass


def validate_cfg(cfg):
    """
    Validate structural correctness of a ControlFlowGraph.
    Must be called before SSA or dominance.
    """

    blocks = cfg.blocks
    entry = cfg.entry
    exit = cfg.exit

    if entry is None or exit is None:
        raise CFGValidationError("CFG must have entry and exit blocks")

    # CFG-1: Entry / Exit integrity
    if entry.predecessors:
        raise CFGValidationError("Entry block must have no predecessors")

    if exit.successors:
        raise CFGValidationError("Exit block must have no successors")

    # CFG-2: Reachability from entry
    reachable = set()
    work = deque([entry])

    while work:
        b = work.popleft()
        if b in reachable:
            continue
        reachable.add(b)
        work.extend(b.successors)

    unreachable = set(blocks.values()) - reachable
    if unreachable:
        raise CFGValidationError(
            f"Unreachable blocks detected: {[b.id for b in unreachable]}"
        )

    # CFG-3: Terminator completeness
    for b in blocks.values():
        if b.terminator is None:
            raise CFGValidationError(
                f"Block {b.id} has no terminator"
            )

    # CFG-4: Successor / predecessor symmetry
    for b in blocks.values():
        for succ in b.successors:
            if b not in succ.predecessors:
                raise CFGValidationError(
                    f"CFG edge mismatch: {b.id} -> {succ.id}"
                )

        for pred in b.predecessors:
            if b not in pred.successors:
                raise CFGValidationError(
                    f"CFG edge mismatch: {pred.id} -> {b.id}"
                )

    # CFG-5: Terminator legality
    for b in blocks.values():
        term = b.terminator
        succ_count = len(b.successors)

        kind = term.kind  # Branch / Jump / Return

        if kind == "branch" and succ_count != 2:
            raise CFGValidationError(
                f"Branch block {b.id} must have exactly 2 successors"
            )

        if kind == "jump" and succ_count != 1:
            raise CFGValidationError(
                f"Jump block {b.id} must have exactly 1 successor"
            )

        if kind == "return" and succ_count != 0:
            raise CFGValidationError(
                f"Return block {b.id} must have no successors"
            )

    # CFG-6: Exit reachability (all blocks must reach exit)
    can_reach_exit = set()
    work = deque([exit])

    while work:
        b = work.popleft()
        if b in can_reach_exit:
            continue
        can_reach_exit.add(b)
        work.extend(b.predecessors)

    dead_ends = set(blocks.values()) - can_reach_exit
    if dead_ends:
        raise CFGValidationError(
            f"Blocks cannot reach exit: {[b.id for b in dead_ends]}"
        )
