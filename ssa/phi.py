# ssa/phi.py

from typing import Dict
from ssa.value import SSAValue
from cfg.block import BasicBlock

class Phi:
    """
    SSA Phi node.

    target = phi(pred1: value1, pred2: value2, ...)
    """

    def __init__(self, target: SSAValue):
        self.target = target
        self.incoming: Dict[BasicBlock, SSAValue] = {}

    def add_incoming(self, block: BasicBlock, value: SSAValue):
        self.incoming[block] = value

    def __repr__(self):
        args = ", ".join(
            f"B{blk.id}:{val}" for blk, val in self.incoming.items()
        )
        return f"{self.target} = phi({args})"
