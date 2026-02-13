# ssa/value.py

from ir.types import AhnaliType
from ir.expr import Expr


class SSAValue(Expr):
    """
    A single-assignment value.
    """

    def __init__(self, name: str, version: int):
        self.name = name      # original variable name
        self.version = version
        self.type = AhnaliType.UNKNOWN
        self.def_block = None
        self.is_undef = False

    @staticmethod
    def undef(name):
        v = SSAValue(name, -1)
        v.is_undef = True
        return v

    def __repr__(self):
        return f"{self.name}_{self.version}"

    def __eq__(self, other):
        return (
            isinstance(other, SSAValue)
            and self.name == other.name
            and self.version == other.version
        )

    def __hash__(self):
        return hash((self.name, self.version))
