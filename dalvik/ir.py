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


class DIf(DInstr):
    def __init__(self, cond, true_block, false_block):
        self.cond = cond
        self.true = true_block
        self.false = false_block

    def __repr__(self):
        return f"if {self.cond} goto B{self.true.id} else B{self.false.id}"


class DGoto(DInstr):
    def __init__(self, target):
        self.target = target

    def __repr__(self):
        return f"goto B{self.target.id}"


class DReturnVoid(DInstr):
    def __repr__(self):
        return "return-void"
