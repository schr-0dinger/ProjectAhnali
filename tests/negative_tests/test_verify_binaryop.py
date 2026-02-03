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

class MockSsaBlock:
    def __init__(self, cfg_block):
        self.cfg_block = cfg_block
        self.statements = []
        self.phis = []

def test_verify_binaryop_clean_rejected():
    b0 = MockCfgBlock(0)
    ssa_b0 = MockSsaBlock(b0)
    
    # y = x + 1, where 'x' is a raw Var, not renamed to SSAValue
    expr = BinaryOp("+", Var("x"), Const(1))
    stmt = Assign("y", expr)
    ssa_b0.statements.append(stmt)
    
    ssa_blocks = {b0: ssa_b0}
    dominators = {b0: {b0}} 

    # Should fail because 'x' is not SSAValue or Const
    with pytest.raises(SSAVerificationError, match="Non-SSA value x found in BinaryOp"):
        verify_ssa(None, ssa_blocks, dominators)

def test_verify_binaryop_clean_accepted():
    b0 = MockCfgBlock(0)
    ssa_b0 = MockSsaBlock(b0)
    
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
    verify_ssa(None, ssa_blocks, dominators)

def test_verify_binaryop_dominance_rejected():
    b0 = MockCfgBlock(0)
    b1 = MockCfgBlock(1)
    
    ssa_b0 = MockSsaBlock(b0)
    ssa_b1 = MockSsaBlock(b1)
    
    # Define x in b1
    val_x = SSAValue("x", 0)
    val_x.def_block = ssa_b1 
    
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
    # This also confirms that verify_uses_dominated correctly inspects BinaryOp operands (via Assign.uses)
    try:
        verify_ssa(None, ssa_blocks, dominators)
    except Exception as e:
        print(f"\nCaught exception: {type(e)} {e}")
        # Assuming we want to reproduce the failure or just inspect it.
        # If I want the test to key off this, I should assert type here.
        assert "SSAVerificationError" in str(type(e))
    else:
        pytest.fail("Did not raise exception")
