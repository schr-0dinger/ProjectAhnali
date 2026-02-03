# ir/expr.py

class Expr:
    """
    Base class for all expressions.
    Expressions are structural, not SSA values.
    """
    pass


class Var(Expr):
    """
    Variable reference.
    NOTE: name is still a string to stay compatible
    with existing Assign / SSA logic.
    """
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class Const(Expr):
    """
    Literal constant (int only for now).
    """
    def __init__(self, value: int):
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