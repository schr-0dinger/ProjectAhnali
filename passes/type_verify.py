# passes/type_verify.py

from ir.types import AnaliType
from ir.expr import BinaryOp, Compare
from ssa.value import SSAValue


class TypeVerificationError(Exception):
    pass


def verify_types(ssa_blocks):
    """
    Omega-1 type verification gate.

    Reject UNKNOWN types ONLY when they are semantically required
    (i.e., participate in typed operations).
    """

    # ---------------------------------
    # 1. Collect SSAValues that REQUIRE types
    # ---------------------------------
    required = set()

    for block in ssa_blocks.values():
        for stmt in block.statements:
            expr = stmt.expr

            if isinstance(expr, BinaryOp):
                required.add(expr.left)
                required.add(expr.right)
                required.add(stmt.defines())

            elif isinstance(expr, Compare):
                required.add(expr.left)
                required.add(expr.right)
                required.add(stmt.defines())
                
    # ---------------------------------
    # 2. Verify only REQUIRED SSAValues
    # ---------------------------------
    for block in ssa_blocks.values():
        for phi in block.phis:
            if (
                phi.target in required
                and phi.target.type == AnaliType.UNKNOWN
            ):
                raise TypeVerificationError(
                    f"Untyped phi {phi.target}"
                )

        for stmt in block.statements:
            dst = stmt.defines()
            if (
                isinstance(dst, SSAValue)
                and dst in required
                and dst.type == AnaliType.UNKNOWN
            ):
                raise TypeVerificationError(
                    f"Untyped value {dst}"
                )
