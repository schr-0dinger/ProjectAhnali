# passes/regalloc_linear.py

from collections import defaultdict

from cfg.graph import stable_block_order


class LiveInterval:
    def __init__(self, value):
        self.value = value
        self.start = float("inf")
        self.end = -1
        self.reg = None

        # Zeta-3
        self.spilled = False
        self.stack_slot = None

    def __repr__(self):
        if self.spilled:
            return f"<Interval {self.value} [{self.start}, {self.end}] spill@{self.stack_slot}>"
        return f"<Interval {self.value} [{self.start}, {self.end}] r={self.reg}>"


RESERVED_LOW_TEMPS = 3
LOW_REG_LIMIT = 16


class LinearScanAllocator:
    def __init__(self, max_registers=LOW_REG_LIMIT - RESERVED_LOW_TEMPS):
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

        for block in stable_block_order(cfg):
            dblock = dalvik_blocks[block]

            for instr in dblock.instructions:
                # defs
                if hasattr(instr, "dst") and instr.dst and instr.dst.ssa:
                    v = instr.dst.ssa
                    interval = interval_map.setdefault(v, LiveInterval(v))
                    interval.start = min(interval.start, index)
                    interval.end = max(interval.end, index)

                # uses
                for field in ("src", "lhs", "rhs", "cond", "value"):
                    if hasattr(instr, field):
                        d = getattr(instr, field)
                        if d and hasattr(d, "ssa") and d.ssa:
                            v = d.ssa
                            interval = interval_map.setdefault(v, LiveInterval(v))
                            interval.start = min(interval.start, index)
                            interval.end = max(interval.end, index)
                if hasattr(instr, "args"):
                    for d in instr.args:
                        if d and hasattr(d, "ssa") and d.ssa:
                            v = d.ssa
                            interval = interval_map.setdefault(v, LiveInterval(v))
                            interval.start = min(interval.start, index)
                            interval.end = max(interval.end, index)

                index += 1

        self.intervals = sorted(interval_map.values(), key=lambda i: i.start)

    def allocate(self):
        for interval in self.intervals:
            self._expire_old(interval)

            if self.free_regs:
                reg = self.free_regs.pop(0)
                interval.reg = reg
                self.active.append(interval)
                self.active.sort(key=lambda i: i.end)
                continue

            # ---- SPILL ----
            spill = self.active[-1]  # farthest end
            if spill.end > interval.end:
                # Spill active interval
                interval.reg = spill.reg
                spill.spilled = True
                spill.reg = None
                self.active.remove(spill)

                self.active.append(interval)
                self.active.sort(key=lambda i: i.end)
            else:
                # Spill current interval
                interval.spilled = True

    def assign_stack_slots(self):
        slot = 0
        for interval in self.intervals:
            if interval.spilled:
                interval.stack_slot = slot
                slot += 1

    def _expire_old(self, current):
        expired = [i for i in self.active if i.end < current.start]
        for i in expired:
            self.active.remove(i)
            self.free_regs.append(i.reg)
