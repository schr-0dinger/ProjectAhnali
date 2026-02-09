# ir/expr.py

class Expr:
    """
    Base class for all expressions.
    Expressions are structural, not SSA values.
    """
    pass

class Call:
    def __init__(
        self,
        func_name,
        args,
        *,
        return_type=None,
        arg_types=None,
        invoke_kind="static",
        owner="LTest;"
    ):
        self.func_name = func_name
        self.args = args
        self.return_type = return_type
        self.arg_types = arg_types
        self.invoke_kind = invoke_kind
        self.owner = owner

    def __repr__(self):
        return f"Call({self.func_name}, {self.args})"
    

class Var(Expr):
    """
    Variable reference.
    NOTE: name is still a string to stay compatible
    with existing Assign / SSA logic.
    """
    def __init__(self, name: str):
        self.name = name

    def replace_with(self, value):
        """
        SSA renaming hook.
        Mutates this Var into an SSAValue.
        """
        self.__class__ = value.__class__
        self.__dict__ = value.__dict__

    def __repr__(self):
        return self.name


class Const(Expr):
    """
    Literal constant (int/float/bool/string).
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class Compare(Expr):
    """
    Relational comparison.

    IMPORTANT:
    - Does NOT evaluate to a value
    - May ONLY appear as If / While condition
    """

    OPS = {"<", "<=", ">", ">=", "==", "!="}

    def __init__(self, op: str, left: Expr, right: Expr):
        if op not in self.OPS:
            raise ValueError(f"Invalid comparison operator: {op}")

        if not isinstance(left, Expr):
            raise TypeError("Compare.left must be Expr")
        if not isinstance(right, Expr):
            raise TypeError("Compare.right must be Expr")

        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

class BinaryOp(Expr):
    """
    Arithmetic operation that produces a value.
    Used inside Assign statements.
    """
    OPS = {"+", "-", "*", "/", "%"}

    def __init__(self, op: str, left: Expr, right: Expr):
        if op not in self.OPS:
            raise ValueError(f"Invalid arithmetic operator: {op}")

        # Strict type checking (Consistent with Compare class)
        if not isinstance(left, Expr):
            raise TypeError(f"BinaryOp.left must be Expr, got {type(left)}")
        if not isinstance(right, Expr):
            raise TypeError(f"BinaryOp.right must be Expr, got {type(right)}")

        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


class New(Expr):
    """
    Object construction (new-instance + invoke-direct <init>).
    class_desc: e.g. "Landroid/widget/TextView;"
    """
    def __init__(self, class_desc: str, args=None, arg_types=None):
        if not isinstance(class_desc, str):
            raise TypeError("New.class_desc must be str")
        self.class_desc = class_desc
        self.args = args or []
        self.arg_types = arg_types or []

    def __repr__(self):
        return f"new {self.class_desc}({len(self.args)} args)"


class StaticFieldGet(Expr):
    """
    Static field read.
    """
    def __init__(self, owner: str, name: str, desc: str):
        self.owner = owner
        self.name = name
        self.desc = desc

    def __repr__(self):
        return f"sget {self.owner}->{self.name}:{self.desc}"


class FieldGet(Expr):
    """
    Instance field read.
    """
    def __init__(self, obj, name: str, desc: str, owner: str):
        self.obj = obj
        self.name = name
        self.desc = desc
        self.owner = owner

    def __repr__(self):
        return f"iget {self.owner}->{self.name}:{self.desc}"


class ArrayGet(Expr):
    """
    Array element read.
    """
    def __init__(self, array, index, elem_desc: str):
        self.array = array
        self.index = index
        self.elem_desc = elem_desc

    def __repr__(self):
        return f"aget {self.elem_desc}"


class ArrayLength(Expr):
    """
    array-length instruction.
    """
    def __init__(self, array):
        self.array = array

    def __repr__(self):
        return "array-length"


class CheckCast(Expr):
    """
    Check-cast.
    """
    def __init__(self, value, desc: str):
        self.value = value
        self.desc = desc

    def __repr__(self):
        return f"check-cast {self.desc}"


class InstanceOf(Expr):
    """
    instance-of check.
    """
    def __init__(self, value, desc: str):
        self.value = value
        self.desc = desc

    def __repr__(self):
        return f"instance-of {self.desc}"


class NewArray(Expr):
    """
    new-array instruction.
    elem_desc: element descriptor (e.g. I, Z, Ljava/lang/String;)
    array_desc: optional full array descriptor; defaults to [elem_desc
    """

    def __init__(self, length, elem_desc: str, array_desc: str = None):
        self.length = length
        self.elem_desc = elem_desc
        self.array_desc = array_desc or f"[{elem_desc}"

    def __repr__(self):
        return f"new-array {self.array_desc}"


class FilledNewArray(Expr):
    """
    filled-new-array instruction.
    """

    def __init__(self, args, elem_desc: str, array_desc: str = None):
        self.args = args or []
        self.elem_desc = elem_desc
        self.array_desc = array_desc or f"[{elem_desc}"

    def __repr__(self):
        return f"filled-new-array {self.array_desc}"


class PrimitiveCast(Expr):
    """
    Primitive conversion (e.g. int-to-float, float-to-int).
    from_desc/to_desc use Dalvik primitive descriptors (I, F, J, D, B, C, S).
    """

    def __init__(self, value, from_desc: str, to_desc: str):
        self.value = value
        self.from_desc = from_desc
        self.to_desc = to_desc

    def __repr__(self):
        return f"cast {self.from_desc}->{self.to_desc}"
