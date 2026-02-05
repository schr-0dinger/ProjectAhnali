# cfg/graph.py

from typing import Dict
from cfg.block import BasicBlock

class ControlFlowGraph:
    """
    A complete CFG for a single function/method.
    """

    def __init__(self):
        self.blocks: Dict[int, BasicBlock] = {}
        self.entry: BasicBlock | None = None
        self.exit: BasicBlock | None = None
        self.try_regions = []

        self._next_id = 0

    def new_block(self) -> BasicBlock:
        block = BasicBlock(self._next_id)
        self.blocks[self._next_id] = block
        self._next_id += 1
        return block

    def set_entry(self, block: BasicBlock):
        self.entry = block

    def set_exit(self, block: BasicBlock):
        self.exit = block
