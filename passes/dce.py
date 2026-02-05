# passes/dce.py

from dalvik.ir import (
    DConst,
    DMove,
    DIf,
    DGoto,
    DReturnVoid,
    DBinaryOp,
    DInvoke,
    DReturn,
    DThrow,
)
from ssa.value import SSAValue


def _ssa_of(dval):
    """
    Extract SSAValue from a DValue wrapper.
    """
    if dval is None:
        return None

    val = getattr(dval, "ssa", None)
    return val if isinstance(val, SSAValue) else None


def eliminate_dead_code(dalvik_blocks):
    """
    Epsilon-1 Dead Code Elimination (SSA-based, fixpoint).

    Invariants:
    - Only remove instructions that DEFINE SSA values.
    - A definition is dead iff its SSAValue is never read.
    - Control-flow instructions are NEVER removed.
    - Phi-elimination moves (DMove) are preserved conservatively.
    """

    def _collect_reads_and_defs(dalvik_blocks):
        """
        Collect:
        - read  : SSAValues that are used
        - defs  : SSAValue -> defining instruction
        """
        read = set()
        defines = {}

        # ---------------------------------
        # 1. Initial scan: direct reads & defs
        # ---------------------------------
        for block in dalvik_blocks.values():
            for instr in block.instructions:

                # ---- Definitions ----
                if hasattr(instr, "dst"):
                    dst = _ssa_of(instr.dst)
                    if dst:
                        defines[dst] = instr

                # ---- Reads ----
                if isinstance(instr, DMove):
                    v = _ssa_of(instr.src)
                    if v:
                        read.add(v)

                elif isinstance(instr, DBinaryOp):
                    for v in (_ssa_of(instr.lhs), _ssa_of(instr.rhs)):
                        if v:
                            read.add(v)

                elif isinstance(instr, DIf):
                    # Boolean condition
                    if instr.cond:
                        v = _ssa_of(instr.cond)
                        if v: read.add(v)

                    elif instr.cmp:
                        op, lhs, rhs = instr.cmp
                        for operand in (lhs, rhs):
                            v = _ssa_of(operand)
                            if v: read.add(v)

                    # Relational comparison
                    if instr.cmp:
                        _, a, b = instr.cmp
                        for v in (_ssa_of(a), _ssa_of(b)):
                            if v:
                                read.add(v)

                elif isinstance(instr, DInvoke):
                    for v in (_ssa_of(a) for a in instr.args):
                        if v:
                            read.add(v)

                elif isinstance(instr, DReturn):
                    v = _ssa_of(instr.value)
                    if v:
                        read.add(v)

                elif isinstance(instr, DThrow):
                    v = _ssa_of(instr.value)
                    if v:
                        read.add(v)

                elif isinstance(instr, DReturnVoid):
                    # Return is a control-flow sink.
                    # No SSA values directly read, but it anchors liveness.
                    pass

        # ---------------------------------
        # 1.5 Copy-propagation liveness rule
        # If a move target is live, its source is live
        # ---------------------------------
        changed = True
        while changed:
            changed = False
            for dst, instr in defines.items():
                if dst in read and isinstance(instr, DMove):
                    src = _ssa_of(instr.src)
                    if src and src not in read:
                        read.add(src)
                        changed = True

        # ---------------------------------
        # 2. Backward propagation through defs
        # ---------------------------------
        worklist = list(read)

        while worklist:
            v = worklist.pop()
            instr = defines.get(v)
            if not instr:
                continue

            if isinstance(instr, DMove):
                src = _ssa_of(instr.src)
                if src and src not in read:
                    read.add(src)
                    worklist.append(src)

            elif isinstance(instr, DBinaryOp):
                for src in (_ssa_of(instr.lhs), _ssa_of(instr.rhs)):
                    if src and src not in read:
                        read.add(src)
                        worklist.append(src)

            # DConst has no operands; nothing to propagate

        return read

    # ---------------------------------
    # Fixpoint iteration
    # ---------------------------------
    changed = True

    while changed:
        changed = False

        # 1. Compute live SSA values
        read = _collect_reads_and_defs(dalvik_blocks)

        # 2. Sweep dead definitions
        for block in dalvik_blocks.values():
            new_instrs = []

            for instr in block.instructions:
                is_dead = False

                # BinaryOp: removable if its result is unused
                if isinstance(instr, DBinaryOp):
                    dst = _ssa_of(instr.dst)
                    if dst and dst not in read:
                        is_dead = True
                        changed = True

                # Const: removable if its result is unused
                elif isinstance(instr, DConst):
                    dst = _ssa_of(instr.dst)
                    if dst and dst not in read:
                        is_dead = True
                        changed = True

                # Move: CONSERVATIVE — keep if dst OR src is live
                elif isinstance(instr, DMove):
                    dst = _ssa_of(instr.dst)
                    src = _ssa_of(instr.src)
                    if dst and dst not in read:        
                        is_dead = True
                        changed = True

                # Control-flow and others are always kept
                if not is_dead:
                    new_instrs.append(instr)

            block.instructions = new_instrs

        # 3. Safe goto removal (CFG-aware)
        for block in dalvik_blocks.values():
            if (
                len(block.instructions) == 1
                and isinstance(block.instructions[0], DGoto)
                and len(block.cfg_block.successors) == 1
            ):
                block.instructions = []
                changed = True

    return dalvik_blocks
