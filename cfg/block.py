# cfg/block.py

from typing import List, Optional, Set

class BasicBlock:
    """
    A basic block is a straight-line sequence of statements
    with a single entry and explicit exits.
    """

    def __init__(self, id: int):
        self.id: int = id

        # Frontend or SSA statements (phase-dependent)
        self.statements: List[object] = []

        # Control flow
        self.successors: Set["BasicBlock"] = set()
        self.predecessors: Set["BasicBlock"] = set()

        # Optional terminator (If / Goto / Return)
        self.terminator: Optional[object] = None

    def add_successor(self, block: "BasicBlock"):
        self.successors.add(block)
        block.predecessors.add(self)

    def __repr__(self):
        return f"<Block {self.id}>"
