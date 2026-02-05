# passes/liveness.py

from dalvik.ir import DMove, DBinaryOp, DIf
from ssa.value import SSAValue


def _ssa_of(dval):
    if dval is None:
        return None
    return getattr(dval, "ssa", None)


class LivenessResult:
    def __init__(self):
        self.live_in = {}   # block -> set[SSAValue]
        self.live_out = {}  # block -> set[SSAValue]


def compute_liveness(cfg, dalvik_blocks):
    """
    Zeta-1: Backward liveness analysis over Dalvik IR.
    """

    result = LivenessResult()

    # Initialize
    for block in cfg.blocks.values():
        result.live_in[block] = set()
        result.live_out[block] = set()

    changed = True
    while changed:
        changed = False

        # Backward traversal order not required for correctness
        for block in cfg.blocks.values():
            old_in = result.live_in[block].copy()
            old_out = result.live_out[block].copy()

            # live_out = union of live_in of successors
            out = set()
            for succ in block.successors:
                out |= result.live_in[succ]
            result.live_out[block] = out

            # live_in = uses ∪ (live_out − defs)
            uses, defs = _block_uses_defs(dalvik_blocks[block])
            result.live_in[block] = uses | (out - defs)

            if old_in != result.live_in[block] or old_out != result.live_out[block]:
                changed = True

    return result


def _block_uses_defs(dblock):
    """
    Compute SSA uses and defs for a DalvikBlock.
    """
    uses = set()
    defs = set()

    for instr in dblock.instructions:

        # ---- defs ----
        if hasattr(instr, "dst"):
            v = _ssa_of(instr.dst)
            if isinstance(v, SSAValue):
                defs.add(v)

        # ---- uses ----
        if isinstance(instr, DMove):
            v = _ssa_of(instr.src)
            if isinstance(v, SSAValue):
                uses.add(v)

        elif isinstance(instr, DBinaryOp):
            for v in (_ssa_of(instr.lhs), _ssa_of(instr.rhs)):
                if isinstance(v, SSAValue):
                    uses.add(v)

        elif isinstance(instr, DIf):
            if instr.cond:
                v = _ssa_of(instr.cond)
                if isinstance(v, SSAValue):
                    uses.add(v)
            elif instr.cmp:
                _, a, b = instr.cmp
                for v in (_ssa_of(a), _ssa_of(b)):
                    if isinstance(v, SSAValue):
                        uses.add(v)

    return uses, defs
