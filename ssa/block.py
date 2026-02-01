# ssa/block.py

from typing import List
from cfg.block import BasicBlock
from ssa.phi import Phi

class SSABlock:
    """
    A CFG block enriched with SSA information.
    """

    def __init__(self, cfg_block: BasicBlock):
        self.cfg_block = cfg_block

        # Phi nodes must come first
        self.phis: List[Phi] = []

        # SSA-form statements
        self.statements: List[object] = []

    def __repr__(self):
        return f"<SSABlock {self.cfg_block.id}>"
