# dalvik/method.py

class DalvikMethod:
    def __init__(self, name, blocks, allocator, try_regions=None):
        self.name = name
        self.blocks = blocks
        self.allocator = allocator
        self.try_regions = try_regions or []

    @property
    def locals_count(self):
        max_reg = max(
            (i.reg for i in self.allocator.intervals if i.reg is not None),
            default=-1
        )
        spill_slots = sum(1 for i in self.allocator.intervals if i.spilled)
        return max_reg + 1 + spill_slots
