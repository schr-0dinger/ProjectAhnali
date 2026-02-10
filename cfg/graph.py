# cfg/graph.py

from typing import Dict, List, Set
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
        # TODO(foundation): Make block ID assignment deterministic across runs,
        # independent of dict insertion order.
        block = BasicBlock(self._next_id)
        self.blocks[self._next_id] = block
        self._next_id += 1
        return block

    def set_entry(self, block: BasicBlock):
        self.entry = block

    def set_exit(self, block: BasicBlock):
        self.exit = block


def stable_block_order(cfg: "ControlFlowGraph") -> List[BasicBlock]:
    """
    Return a deterministic reverse-postorder traversal of the CFG.
    Includes exceptional successors and appends unreachable blocks
    in ascending block id order for stability.
    """
    visited: Set[BasicBlock] = set()
    postorder: List[BasicBlock] = []

    def dfs(block: BasicBlock):
        if block in visited:
            return
        visited.add(block)
        successors = block.successors | block.exceptional_successors
        for succ in sorted(successors, key=lambda b: b.id):
            dfs(succ)
        postorder.append(block)

    if cfg.entry is not None:
        dfs(cfg.entry)

    for block in sorted(cfg.blocks.values(), key=lambda b: b.id):
        if block not in visited:
            dfs(block)

    return list(reversed(postorder))
