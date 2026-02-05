import pytest
from ssa.verify import verify_ssa, SSAVerificationError
from ssa.value import SSAValue
from ir.expr import BinaryOp, Var, Const
from tests.ir_stub import Assign

class MockCfgBlock:
    def __init__(self, id):
        self.id = id
        self.statements = []
        self.terminator = None
        self.predecessors = []

    def __repr__(self):
        return f"Block({self.id})"

class MockSsaBlock:
    def __init__(self, cfg_block):
        self.cfg_block = cfg_block
        self.statements = []
        self.phis = []

class MockCFG:
    """Minimal Mock CFG to satisfy verify_ssa signature"""
    def __init__(self, blocks):
        self.blocks = {b.id: b for b in blocks}
        self.entry = blocks[0] if blocks else None

def test_verify_binaryop_clean_rejected():
    b0 = MockCfgBlock(0)
    ssa_b0 = MockSsaBlock(b0)
    cfg = MockCFG([b0])
    
    # y = x + 1, where 'x' is a raw Var, not renamed to SSAValue
    expr = BinaryOp("+", Var("x"), Const(1))
    stmt = Assign("y", expr)
    ssa_b0.statements.append(stmt)
    
    ssa_blocks = {b0: ssa_b0}
    dominators = {b0: {b0}} 

    # Should fail because 'x' is not SSAValue or Const
    with pytest.raises(SSAVerificationError, match="Non-SSA value x found in BinaryOp"):
        verify_ssa(cfg, ssa_blocks, dominators)

def test_verify_binaryop_clean_accepted():
    b0 = MockCfgBlock(0)
    ssa_b0 = MockSsaBlock(b0)
    cfg = MockCFG([b0])
    
    # y = x_0 + 1, where x_0 is an SSAValue
    val_x = SSAValue("x", 0)
    val_x.def_block = b0 # defined here to satisfy domination (must be CFG block)

    # We must construct with valid Exprs first because BinaryOp.__init__ enforces types
    expr = BinaryOp("+", Var("x"), Const(1))
    # Then we simulate SSA renaming by patching the operand
    expr.left = val_x
    stmt = Assign("y", expr)
    
    ssa_b0.statements.append(stmt)
    
    ssa_blocks = {b0: ssa_b0}
    dominators = {b0: {b0}}

    # Should pass
    verify_ssa(cfg, ssa_blocks, dominators)

def test_verify_binaryop_dominance_rejected():
    b0 = MockCfgBlock(0)
    b1 = MockCfgBlock(1)
    cfg = MockCFG([b0, b1])
    
    ssa_b0 = MockSsaBlock(b0)
    ssa_b1 = MockSsaBlock(b1)
    
    # Define x in b1
    val_x = SSAValue("x", 0)
    
    # FIX: Assign def_block to the CFG block (b1), not the SSA block (ssa_b1)
    # The verifier checks `if val.def_block not in dominators[current_block]`
    val_x.def_block = b1 
    
    # Use x in b0 (but b1 does not dominate b0)
    # y = x + 1
    expr = BinaryOp("+", Var("x"), Const(1))
    expr.left = val_x 
    stmt = Assign("y", expr)
    ssa_b0.statements.append(stmt)
    
    ssa_blocks = {b0: ssa_b0, b1: ssa_b1}
    # Dominators: b0 dominates {b0}, b1 dominates {b1}
    dominators = {b0: {b0}, b1: {b1}}
    
    # Expect error: Use of x not dominated
    with pytest.raises(SSAVerificationError, match="not dominated by its definition"):
        verify_ssa(cfg, ssa_blocks, dominators)