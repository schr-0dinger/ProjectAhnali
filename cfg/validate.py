# cfg/validate.py

from collections import deque


class CFGValidationError(RuntimeError):
    pass


def validate_cfg(cfg):
    """
    Structural CFG validation.
    Exceptional edges are allowed but ignored for semantics.
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

    # CFG-2: Reachability from entry (normal + exceptional)
    reachable = set()
    work = deque([entry])

    while work:
        b = work.popleft()
        if b in reachable:
            continue
        reachable.add(b)
        work.extend(b.successors)
        work.extend(b.exceptional_successors)

    unreachable = set(blocks.values()) - reachable
    return_blocks = {
        b for b in blocks.values()
        if b.terminator is not None and b.terminator.kind == "return"
    }
    throw_blocks = {
        b for b in blocks.values()
        if b.terminator is not None and b.terminator.kind == "throw"
    }
    has_return = bool(return_blocks)
    if unreachable:
        if not (has_return and unreachable == {exit}):
            raise CFGValidationError(
                f"Unreachable blocks detected: {[b for b in unreachable]}"
            )

    # CFG-3: Terminator completeness
    for b in blocks.values():
        if b.terminator is None:
            raise CFGValidationError(
                f"Block {b} has no terminator"
            )

    # CFG-4: Successor / predecessor symmetry (normal edges only)
    for b in blocks.values():
        for succ in b.successors:
            if b not in succ.predecessors:
                raise CFGValidationError(
                    f"CFG edge mismatch: {b} -> {succ}"
                )

        for pred in b.predecessors:
            if b not in pred.successors:
                raise CFGValidationError(
                    f"CFG edge mismatch: {pred} -> {b}"
                )

    # CFG-5: Terminator legality (normal successors only)
    for b in blocks.values():
        term = b.terminator
        succ_count = len(b.successors)
        kind = term.kind  # branch / jump / return

        if kind == "branch" and succ_count != 2:
            raise CFGValidationError(
                f"Branch block {b} must have exactly 2 successors"
            )

        if kind == "jump" and succ_count != 1:
            raise CFGValidationError(
                f"Jump block {b} must have exactly 1 successor"
            )

        if kind == "return" and succ_count != 0:
            raise CFGValidationError(
                f"Return block {b} must have no successors"
            )
        if kind == "throw" and succ_count != 0:
            raise CFGValidationError(
                f"Throw block {b} must have no successors"
            )

    # CFG-6: Exit reachability (normal + exceptional)
    exceptional_preds = {b: set() for b in blocks.values()}
    for b in blocks.values():
        for succ in b.exceptional_successors:
            exceptional_preds[succ].add(b)

    can_reach_exit = set()
    work = deque([exit])

    while work:
        b = work.popleft()
        if b in can_reach_exit:
            continue
        can_reach_exit.add(b)
        work.extend(b.predecessors)
        work.extend(exceptional_preds[b])

    dead_ends = set(blocks.values()) - can_reach_exit
    dead_ends -= return_blocks
    dead_ends -= throw_blocks
    if has_return:
        dead_ends -= {exit}
    if dead_ends:
        raise CFGValidationError(
            f"Blocks cannot reach exit: {[b for b in dead_ends]}"
        )

    return True
