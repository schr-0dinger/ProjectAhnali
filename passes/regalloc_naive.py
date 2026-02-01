# passes/regalloc_naive.py

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
