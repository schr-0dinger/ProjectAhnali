# dalvik/ir.py

class DValue:
    """
    Symbolic Dalvik value (backed by SSAValue).
    No registers yet.
    """
    def __init__(self, ssa_value):
        self.ssa = ssa_value

    def __repr__(self):
        return f"<{self.ssa}>"


class DInstr:
    pass


class DConst(DInstr):
    def __init__(self, dst, value):
        self.dst = dst
        self.value = value

    def __repr__(self):
        return f"{self.dst} = const {self.value}"


class DMove(DInstr):
    """
    Used for Phi elimination.
    """
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src

    def __repr__(self):
        return f"{self.dst} = move {self.src}"
    
class DBinaryOp(DInstr):
    """
    Base class for Dalvik binary arithmetic instructions.
    dst = lhs <op> rhs
    """
    def __init__(self, dst, lhs, rhs):
        self.dst = dst    # DValue
        self.lhs = lhs    # DValue
        self.rhs = rhs    # DValue

    def __repr__(self):
        return f"{self.dst} = {self.op} {self.lhs}, {self.rhs}"
    
class DAdd(DBinaryOp):
    op = "add"


class DSub(DBinaryOp):
    op = "sub"


class DMul(DBinaryOp):
    op = "mul"


class DDiv(DBinaryOp):
    op = "div"


class DRem(DBinaryOp):
    op = "rem"


class DIf(DInstr):
    def __init__(self, *, cond=None, cmp=None, true_block, false_block):
        # Exactly one must be set
        assert (cond is None) ^ (cmp is None)

        self.cond = cond          # DValue (boolean variable)
        self.cmp = cmp            # (op, DValue, DValue)
        self.true = true_block
        self.false = false_block


class DGoto(DInstr):
    def __init__(self, target):
        self.target = target

    def __repr__(self):
        return f"goto B{self.target.id}"


class DReturnVoid(DInstr):
    def __repr__(self):
        return "return-void"
