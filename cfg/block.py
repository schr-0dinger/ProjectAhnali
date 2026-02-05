# cfg/block.py
from typing import Optional, Any

class BasicBlock:
    _id_counter = 0

    def __init__(self, name):
        # Stable numeric id (required by Dalvik lowering)
        self.id = BasicBlock._id_counter
        BasicBlock._id_counter += 1

        self.name = name

        # IR statements (CFG builder expects this)
        self.statements = []

        # Instructions (used later by lowering)
        self.instructions = []

        # Normal control-flow successors
        self.successors = set()

        # Exceptional control-flow successors (Omega-2)
        self.exceptional_successors = set()

        # Predecessors (normal flow only)
        self.predecessors = set()

        # Terminator (branch / jump / return)
        self.terminator: Optional[Any] = None

    def add_successor(self, block):
        self.successors.add(block)
        block.predecessors.add(self)

    def add_exceptional_successor(self, block):
        self.exceptional_successors.add(block)

    def __repr__(self):
        return f"<BasicBlock {self.name}#{self.id}>"
