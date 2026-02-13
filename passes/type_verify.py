# passes/type_verify.py

from ir.types import AhnaliType
from ir.expr import BinaryOp, Compare, Call
from ir.stmt import CallStmt
from passes.ignored_return import allow_ignored_return
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
            expr = getattr(stmt, "expr", None)

            if isinstance(expr, BinaryOp):
                required.add(expr.left)
                required.add(expr.right)
                required.add(stmt.defines())

            elif isinstance(expr, Compare):
                required.add(expr.left)
                required.add(expr.right)
                required.add(stmt.defines())

            elif isinstance(expr, Call):
                if expr.arg_types is not None:
                    expected = len(expr.args)
                    if expr.invoke_kind in ("virtual", "direct", "interface"):
                        if len(expr.arg_types) not in (expected, expected - 1):
                            raise TypeVerificationError(
                                "Call arg_types length does not match args for instance invoke"
                            )
                    elif len(expr.arg_types) != expected:
                        raise TypeVerificationError(
                            "Call arg_types length does not match args"
                        )
                if expr.return_type is None and isinstance(stmt.defines(), SSAValue):
                    raise TypeVerificationError(
                        "Void call cannot assign to a destination"
                    )
                if expr.return_type is not None and not isinstance(stmt.defines(), SSAValue):
                    if isinstance(stmt, CallStmt) and allow_ignored_return(expr):
                        continue
                    raise TypeVerificationError(
                        "Non-void call must assign to a destination"
                    )
                continue  # UNKNOWN allowed at this stage


                
    # ---------------------------------
    # 2. Verify only REQUIRED SSAValues
    # ---------------------------------
    for block in ssa_blocks.values():
        for phi in block.phis:
            if (
                phi.target in required
                and phi.target.type == AhnaliType.UNKNOWN
            ):
                raise TypeVerificationError(
                    f"Untyped phi {phi.target}"
                )

        for stmt in block.statements:
            dst = stmt.defines()
            if (
                isinstance(dst, SSAValue)
                and dst in required
                and dst.type == AhnaliType.UNKNOWN
            ):
                raise TypeVerificationError(
                    f"Untyped value {dst}"
                )
