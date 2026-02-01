# dalvik/block.py

class DalvikBlock:
    def __init__(self, cfg_block):
        self.cfg_block = cfg_block
        self.id = cfg_block.id
        self.instructions = []

    def emit(self, instr):
        self.instructions.append(instr)

    def __repr__(self):
        body = "\n    ".join(map(str, self.instructions))
        return f"B{self.id}:\n    {body}"
