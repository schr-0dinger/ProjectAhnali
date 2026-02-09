# passes/regalloc_naive.py

RESERVED_LOW_TEMPS = 3
LOW_REG_LIMIT = 16
TEMP_REG_START = LOW_REG_LIMIT - RESERVED_LOW_TEMPS


class RegisterAllocatorNaive:
    def __init__(self, dalvik_blocks):
        self.blocks = dalvik_blocks
        self.reg_map = {}
        self.next_reg = 0

    def allocate(self):
        # Assign registers to all DValues we see
        for block in self.blocks.values():
            for instr in block.instructions:
                for val in self._values_in(instr):
                    if val not in self.reg_map:
                        if self.next_reg == TEMP_REG_START:
                            self.next_reg = LOW_REG_LIMIT
                        self.reg_map[val] = f"v{self.next_reg}"
                        self.next_reg += 1

        return self.reg_map, self.next_reg

    def _values_in(self, instr):
        vals = []
        for attr in ("dst", "src", "cond"):
            if hasattr(instr, attr):
                v = getattr(instr, attr)
                if hasattr(v, "ssa"):
                    vals.append(v)
        return vals
