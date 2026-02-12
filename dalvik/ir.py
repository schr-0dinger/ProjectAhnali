# dalvik/ir.py

class DValue:
    """
    Symbolic Dalvik value (backed by SSAValue).
    No registers yet.
    """
    def __init__(self, ssa_value):
        self.ssa = ssa_value
        self.reg = None

    def __repr__(self):
        if self.reg is not None:
            return f"v{self.reg}"
        return f"<DValue {self.ssa}>"


class DInstr:
    pass


class DConst(DInstr):
    def __init__(self, dst, value):
        self.dst = dst
        self.value = value

    def __repr__(self):
        return f"{self.dst} = const {self.value}"


class DConstWide(DInstr):
    def __init__(self, dst, value):
        self.dst = dst
        self.value = value

    def __repr__(self):
        return f"{self.dst} = const-wide {self.value}"


class DConstStringJumbo(DInstr):
    def __init__(self, dst, value):
        self.dst = dst
        self.value = value

    def __repr__(self):
        return f"{self.dst} = const-string/jumbo {self.value}"


class DStaticGet(DInstr):
    def __init__(self, dst, owner, name, desc):
        self.dst = dst
        self.owner = owner
        self.name = name
        self.desc = desc

    def __repr__(self):
        return f"{self.dst} = sget {self.owner}->{self.name}:{self.desc}"


class DStaticPut(DInstr):
    def __init__(self, value, owner, name, desc):
        self.value = value
        self.owner = owner
        self.name = name
        self.desc = desc

    def __repr__(self):
        return f"sput {self.owner}->{self.name}:{self.desc} {self.value}"


class DInstanceGet(DInstr):
    def __init__(self, dst, obj, owner, name, desc):
        self.dst = dst
        self.obj = obj
        self.owner = owner
        self.name = name
        self.desc = desc

    def __repr__(self):
        return f"{self.dst} = iget {self.owner}->{self.name}:{self.desc}"


class DInstancePut(DInstr):
    def __init__(self, obj, value, owner, name, desc):
        self.obj = obj
        self.value = value
        self.owner = owner
        self.name = name
        self.desc = desc

    def __repr__(self):
        return f"iput {self.owner}->{self.name}:{self.desc} {self.value}"


class DArrayGet(DInstr):
    def __init__(self, dst, array, index, elem_desc):
        self.dst = dst
        self.array = array
        self.index = index
        self.elem_desc = elem_desc

    def __repr__(self):
        return f"{self.dst} = aget {self.elem_desc}"


class DArrayPut(DInstr):
    def __init__(self, array, index, elem_desc, value):
        self.array = array
        self.index = index
        self.elem_desc = elem_desc
        self.value = value

    def __repr__(self):
        return f"aput {self.elem_desc} {self.value}"


class DArrayLength(DInstr):
    def __init__(self, dst, array):
        self.dst = dst
        self.array = array

    def __repr__(self):
        return f"{self.dst} = array-length {self.array}"


class DFilledNewArray(DInstr):
    def __init__(self, dst, args, array_desc):
        self.dst = dst
        self.args = args
        self.array_desc = array_desc

    def __repr__(self):
        return f"{self.dst} = filled-new-array {self.array_desc} ({len(self.args)} args)"


class DInstanceOf(DInstr):
    def __init__(self, dst, obj, desc):
        self.dst = dst
        self.obj = obj
        self.desc = desc

    def __repr__(self):
        return f"{self.dst} = instance-of {self.desc} {self.obj}"


class DCheckCast(DInstr):
    def __init__(self, obj, desc):
        self.obj = obj
        self.desc = desc

    def __repr__(self):
        return f"check-cast {self.desc} {self.obj}"


class DPrimitiveCast(DInstr):
    def __init__(self, dst, src, from_desc, to_desc):
        self.dst = dst
        self.src = src
        self.from_desc = from_desc
        self.to_desc = to_desc

    def __repr__(self):
        return f"{self.dst} = cast {self.from_desc}->{self.to_desc} {self.src}"


class DNew(DInstr):
    def __init__(self, dst, class_desc):
        self.dst = dst
        self.class_desc = class_desc

    def __repr__(self):
        return f"{self.dst} = new-instance {self.class_desc}"


class DNewArray(DInstr):
    def __init__(self, dst, src, array_desc):
        self.dst = dst
        self.src = src
        self.array_desc = array_desc

    def __repr__(self):
        return f"{self.dst} = new-array {self.array_desc} {self.src}"


class DMove(DInstr):
    """
    Used for Phi elimination.
    """
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src

    def __repr__(self):
        return f"{self.dst} = move {self.src}"


class DMoveWide(DInstr):
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src

    def __repr__(self):
        return f"{self.dst} = move-wide {self.src}"


class DSpillLoad(DInstr):
    """
    Spill reload from a spill slot into a temp value.
    """
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src

    def __repr__(self):
        return f"{self.dst} = spill-load {self.src}"


class DSpillStore(DInstr):
    """
    Spill store from a temp value into a spill slot.
    """
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src

    def __repr__(self):
        return f"spill-store {self.dst} {self.src}"


class DMoveResult(DInstr):
    def __init__(self, dst):
        self.dst = dst

    def __repr__(self):
        return f"{self.dst} = move-result"


class DMoveResultObject(DInstr):
    def __init__(self, dst):
        self.dst = dst

    def __repr__(self):
        return f"{self.dst} = move-result-object"


class DMoveResultWide(DInstr):
    def __init__(self, dst):
        self.dst = dst

    def __repr__(self):
        return f"{self.dst} = move-result-wide"


class DMoveException(DInstr):
    def __init__(self, dst):
        self.dst = dst

    def __repr__(self):
        return f"{self.dst} = move-exception"
    
class DBinaryOp(DInstr):
    """
    Base class for Dalvik binary arithmetic instructions.
    dst = lhs <op> rhs
    """
    def __init__(self, dst, lhs, rhs, type_desc="I"):
        self.dst = dst    # DValue
        self.lhs = lhs    # DValue
        self.rhs = rhs    # DValue
        self.type_desc = type_desc  # I, J, F, D (or other primitive desc)

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


class DCompare(DInstr):
    """
    Primitive compare:
    - long: cmp-long
    - float/double: cmpl/cmpg
    Produces int result in dst.
    """
    def __init__(self, dst, lhs, rhs, *, cmp_kind, nan_mode=None):
        self.dst = dst
        self.lhs = lhs
        self.rhs = rhs
        self.cmp_kind = cmp_kind  # "long" | "float" | "double"
        self.nan_mode = nan_mode  # "cmpl" | "cmpg" (for float/double)


class DIf(DInstr):
    def __init__(self, *, cond=None, cmp=None, true_block, false_block):
        # Exactly one must be set
        assert (cond is None) ^ (cmp is None)

        self.cond = cond          # DValue (boolean variable)
        self.cmp = cmp            # (op, DValue, DValue)
        self.true = true_block
        self.false = false_block


class DIfZ(DInstr):
    OPS = {"eqz", "nez", "ltz", "lez", "gtz", "gez"}

    def __init__(self, *, cond, op, true_block, false_block):
        if op not in self.OPS:
            raise ValueError(f"Invalid ifz op: {op}")
        self.cond = cond
        self.op = op
        self.true = true_block
        self.false = false_block


class DPackedSwitch(DInstr):
    def __init__(self, *, cond, first_key, targets, default_block):
        self.cond = cond
        self.first_key = int(first_key)
        self.targets = list(targets)
        self.default = default_block

    def __repr__(self):
        return (
            f"packed-switch {self.cond} first={self.first_key} "
            f"cases={len(self.targets)} default=B{self.default.id}"
        )


class DSparseSwitch(DInstr):
    def __init__(self, *, cond, keys, targets, default_block):
        if len(keys) != len(targets):
            raise ValueError("sparse-switch keys and targets must have the same length")
        self.cond = cond
        self.keys = [int(k) for k in keys]
        self.targets = list(targets)
        self.default = default_block

    def __repr__(self):
        return (
            f"sparse-switch {self.cond} cases={len(self.keys)} "
            f"default=B{self.default.id}"
        )


class DMonitorEnter(DInstr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"monitor-enter {self.value}"


class DMonitorExit(DInstr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"monitor-exit {self.value}"


class DGoto(DInstr):
    def __init__(self, target):
        self.target = target

    def __repr__(self):
        return f"goto B{self.target.id}"


class DReturnVoid(DInstr):
    def __repr__(self):
        return "return-void"


class DReturn(DInstr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"return {self.value}"


class DThrow(DInstr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"throw {self.value}"


class DInvoke(DInstr):
    def __init__(
        self,
        *,
        method,
        args,
        dst=None,
        return_type=None,
        arg_types=None,
        invoke_kind="static",
        owner="LTest;"
    ):
        self.method = method
        self.args = args
        self.dst = dst
        self.return_type = return_type
        self.arg_types = arg_types
        self.invoke_kind = invoke_kind
        self.owner = owner

    def __repr__(self):
        return f"invoke-{self.invoke_kind} {self.owner}->{self.method}({len(self.args)} args)"
