# passes/regalloc_linear.py

from collections import defaultdict


class LiveInterval:
    def __init__(self, value):
        self.value = value
        self.start = float("inf")
        self.end = -1
        self.reg = None

    def __repr__(self):
        return f"<Interval {self.value} [{self.start}, {self.end}] r={self.reg}>"



class LinearScanAllocator:
    def __init__(self, max_registers=16):
        self.max_registers = max_registers
        self.intervals = []
        self.active = []
        self.free_regs = list(range(max_registers))

    def build_intervals(self, cfg, dalvik_blocks, liveness):
        """
        Build live intervals from liveness info.
        Instruction index is block-local but monotonic across traversal.
        """
        index = 0
        interval_map = {}

        for block in cfg.blocks.values():
            dblock = dalvik_blocks[block]

            for instr in dblock.instructions:
                # defs
                if hasattr(instr, "dst") and instr.dst and instr.dst.ssa:
                    v = instr.dst.ssa
                    interval = interval_map.setdefault(v, LiveInterval(v))
                    interval.start = min(interval.start, index)
                    interval.end = max(interval.end, index)

                # uses
                for field in ("src", "lhs", "rhs", "cond"):
                    if hasattr(instr, field):
                        d = getattr(instr, field)
                        if d and hasattr(d, "ssa") and d.ssa:
                            v = d.ssa
                            interval = interval_map.setdefault(v, LiveInterval(v))
                            interval.start = min(interval.start, index)
                            interval.end = max(interval.end, index)

                index += 1

        self.intervals = sorted(interval_map.values(), key=lambda i: i.start)

    def allocate(self):
        """
        Linear scan allocation (no spilling yet).
        """
        for interval in self.intervals:
            self._expire_old(interval)

            if not self.free_regs:
                raise RuntimeError("Register spill required (Zeta-3)")

            reg = self.free_regs.pop(0)
            interval.reg = reg
            self.active.append(interval)
            self.active.sort(key=lambda i: i.end)

    def _expire_old(self, current):
        expired = [i for i in self.active if i.end < current.start]
        for i in expired:
            self.active.remove(i)
            self.free_regs.append(i.reg)
