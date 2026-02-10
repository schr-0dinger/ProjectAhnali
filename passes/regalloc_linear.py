# passes/regalloc_linear.py

from collections import defaultdict

from cfg.graph import stable_block_order


class LiveInterval:
    def __init__(self, value):
        self.value = value
        self.start = float("inf")
        self.end = -1
        self.reg = None
        self.width = 1

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
        # TODO(foundation): Enforce register limits and provide a fallback strategy
        # when allocated registers exceed encoding constraints.

    def _interval_width(self, value):
        t = getattr(value, "type", None)
        return 2 if t in ("J", "D") else 1

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
                    interval.width = self._interval_width(v)
                    interval.start = min(interval.start, index)
                    interval.end = max(interval.end, index)

                # uses
                for field in ("src", "lhs", "rhs", "cond", "value", "obj", "array", "index"):
                    if hasattr(instr, field):
                        d = getattr(instr, field)
                        if d and hasattr(d, "ssa") and d.ssa:
                            v = d.ssa
                            interval = interval_map.setdefault(v, LiveInterval(v))
                            interval.width = self._interval_width(v)
                            interval.start = min(interval.start, index)
                            interval.end = max(interval.end, index)
                if hasattr(instr, "args"):
                    for d in instr.args:
                        if d and hasattr(d, "ssa") and d.ssa:
                            v = d.ssa
                            interval = interval_map.setdefault(v, LiveInterval(v))
                            interval.width = self._interval_width(v)
                            interval.start = min(interval.start, index)
                            interval.end = max(interval.end, index)

                index += 1

        self.intervals = sorted(interval_map.values(), key=lambda i: i.start)

    def _alloc_reg(self, width):
        self.free_regs.sort()
        if width == 1:
            if not self.free_regs:
                return None
            return self.free_regs.pop(0)
        # width == 2: find consecutive pair
        free_set = set(self.free_regs)
        for r in self.free_regs:
            if r + 1 in free_set:
                self.free_regs.remove(r)
                self.free_regs.remove(r + 1)
                return r
        return None
        # TODO(foundation): Consider a smarter search strategy to reduce fragmentation.

    def allocate(self):
        for interval in self.intervals:
            self._expire_old(interval)

            reg = self._alloc_reg(interval.width)
            if reg is not None:
                interval.reg = reg
                self.active.append(interval)
                self.active.sort(key=lambda i: i.end)
                continue

            # ---- SPILL ----
            spill = self.active[-1]  # farthest end
            if spill.end > interval.end and spill.width >= interval.width:
                # Spill active interval
                interval.reg = spill.reg
                spill.spilled = True
                spill.reg = None
                self.active.remove(spill)
                if spill.width == 2 and interval.width == 1 and interval.reg is not None:
                    self.free_regs.append(interval.reg + 1)

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
                slot += interval.width

    def _expire_old(self, current):
        expired = [i for i in self.active if i.end < current.start]
        for i in expired:
            self.active.remove(i)
            if i.reg is None:
                continue
            self.free_regs.append(i.reg)
            if i.width == 2:
                self.free_regs.append(i.reg + 1)
