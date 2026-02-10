# ssa/verify.py

from ssa.value import SSAValue
from ir.expr import (
    Compare,
    Const,
    BinaryOp,
    BoolOp,
    Call,
    UnaryOp,
    Var,
    New,
    NewArray,
    PrimitiveCast,
    StaticFieldGet,
    FieldGet,
    ArrayGet,
    CheckCast,
)
from ir.stmt import StaticFieldSet, FieldSet, ArraySet


class SSAVerificationError(RuntimeError):
    pass


def verify_ssa(cfg, ssa_blocks, dominators):
    """
    Verify SSA invariants.
    Called after SSA renaming.
    """

    _verify_single_definition(ssa_blocks)
    _verify_uses_dominated(ssa_blocks, dominators)
    _verify_phi_legality(ssa_blocks)
    _verify_compare_is_ssa_clean(cfg, ssa_blocks)
    _verify_binaryop_is_ssa_clean(ssa_blocks)
    _verify_call_is_ssa_clean(ssa_blocks)


# --------------------------------------------------------------------
# Core helpers
# --------------------------------------------------------------------

def _iter_ssa_uses(value):
    """
    Yield all SSAValue uses contained inside a value/expression.
    This is the single source of truth for dominance verification.
    """

    if isinstance(value, SSAValue):
        yield value

    elif isinstance(value, BinaryOp):
        yield from _iter_ssa_uses(value.left)
        yield from _iter_ssa_uses(value.right)

    elif isinstance(value, Compare):
        yield from _iter_ssa_uses(value.left)
        yield from _iter_ssa_uses(value.right)

    elif isinstance(value, BoolOp):
        yield from _iter_ssa_uses(value.left)
        yield from _iter_ssa_uses(value.right)

    elif isinstance(value, UnaryOp):
        yield from _iter_ssa_uses(value.value)

    elif isinstance(value, Call):
        for arg in value.args:
            yield from _iter_ssa_uses(arg)
    elif isinstance(value, New):
        for arg in value.args:
            yield from _iter_ssa_uses(arg)
    elif isinstance(value, NewArray):
        yield from _iter_ssa_uses(value.length)
    elif isinstance(value, PrimitiveCast):
        yield from _iter_ssa_uses(value.value)
    elif isinstance(value, StaticFieldGet):
        return
    elif isinstance(value, FieldGet):
        yield from _iter_ssa_uses(value.obj)
    elif isinstance(value, ArrayGet):
        yield from _iter_ssa_uses(value.array)
        yield from _iter_ssa_uses(value.index)
    elif isinstance(value, CheckCast):
        yield from _iter_ssa_uses(value.value)

    # Const and unknown leaf nodes produce no SSA uses


# --------------------------------------------------------------------
# Verification passes
# --------------------------------------------------------------------

def _verify_single_definition(ssa_blocks):
    seen = set()

    for block in ssa_blocks.values():
        for phi in block.phis:
            if phi.target in seen:
                raise SSAVerificationError(
                    f"Multiple definitions of {phi.target}"
                )
            seen.add(phi.target)

        for stmt in block.statements:
            if hasattr(stmt, "defines"):
                val = stmt.defines()
                if val is None:
                    continue
                if val in seen:
                    raise SSAVerificationError(
                        f"Multiple definitions of {val}"
                    )
                seen.add(val)


def _verify_uses_dominated(ssa_blocks, dominators):
    for block in ssa_blocks.values():
        cfg_block = block.cfg_block

        # ---- Statement uses ----
        for stmt in block.statements:
            if isinstance(stmt, StaticFieldSet):
                for val in _iter_ssa_uses(stmt.value):
                    if getattr(val, "is_undef", False):
                        continue
                    def_block = val.def_block
                    if def_block not in dominators[cfg_block]:
                        raise SSAVerificationError(
                            f"Use of {val} not dominated by its definition"
                        )
            if isinstance(stmt, FieldSet):
                for val in _iter_ssa_uses(stmt.obj):
                    if getattr(val, "is_undef", False):
                        continue
                    def_block = val.def_block
                    if def_block not in dominators[cfg_block]:
                        raise SSAVerificationError(
                            f"Use of {val} not dominated by its definition"
                        )
                for val in _iter_ssa_uses(stmt.value):
                    if getattr(val, "is_undef", False):
                        continue
                    def_block = val.def_block
                    if def_block not in dominators[cfg_block]:
                        raise SSAVerificationError(
                            f"Use of {val} not dominated by its definition"
                        )
            if isinstance(stmt, ArraySet):
                for val in _iter_ssa_uses(stmt.array):
                    if getattr(val, "is_undef", False):
                        continue
                    def_block = val.def_block
                    if def_block not in dominators[cfg_block]:
                        raise SSAVerificationError(
                            f"Use of {val} not dominated by its definition"
                        )
                for val in _iter_ssa_uses(stmt.index):
                    if getattr(val, "is_undef", False):
                        continue
                    def_block = val.def_block
                    if def_block not in dominators[cfg_block]:
                        raise SSAVerificationError(
                            f"Use of {val} not dominated by its definition"
                        )
                for val in _iter_ssa_uses(stmt.value):
                    if getattr(val, "is_undef", False):
                        continue
                    def_block = val.def_block
                    if def_block not in dominators[cfg_block]:
                        raise SSAVerificationError(
                            f"Use of {val} not dominated by its definition"
                        )
            for used in stmt.uses():
                for val in _iter_ssa_uses(used):
                    if getattr(val, "is_undef", False):
                        continue

                    def_block = val.def_block
                    if def_block not in dominators[cfg_block]:
                        raise SSAVerificationError(
                            f"Use of {val} not dominated by its definition"
                        )

            expr = getattr(stmt, "expr", None)
            if expr is not None:
                for val in _iter_ssa_uses(expr):
                    if getattr(val, "is_undef", False):
                        continue

                    def_block = val.def_block
                    if def_block not in dominators[cfg_block]:
                        raise SSAVerificationError(
                            f"Use of {val} in expression "
                            f"not dominated by its definition"
                        )

        # ---- Terminator uses ----
        term = cfg_block.terminator
        if term and term.kind == "branch":
            for val in _iter_ssa_uses(term.cond):
                if getattr(val, "is_undef", False):
                    continue

                def_block = val.def_block
                if def_block not in dominators[cfg_block]:
                    raise SSAVerificationError(
                        f"Branch use of {val} not dominated by its definition"
                    )


def _verify_phi_legality(ssa_blocks):
    for block in ssa_blocks.values():
        preds = set(block.cfg_block.predecessors)

        for phi in block.phis:
            incoming = set(phi.incoming.keys())

            if preds != incoming:
                raise SSAVerificationError(
                    f"Phi in block {block.cfg_block.id} "
                    f"has mismatched predecessors"
                )

            if len(preds) < 2:
                raise SSAVerificationError(
                    f"Illegal Phi in block {block.cfg_block.id} "
                    f"with <2 predecessors"
                )


def _verify_compare_is_ssa_clean(cfg, ssa_blocks):

    for block in ssa_blocks.values():
        term = block.cfg_block.terminator
        if term and term.kind == "branch":
            cond = term.cond
            if isinstance(cond, Compare):
                for side in (cond.left, cond.right):
                    if isinstance(side, (SSAValue, Const)):
                        continue
                    raise SSAVerificationError(
                        f"Non-SSA value {side} found in Compare condition "
                        f"in block {block.cfg_block.id}"
                    )

def _verify_binaryop_is_ssa_clean(ssa_blocks):
    for block in ssa_blocks.values():
        for stmt in block.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, BinaryOp):
                for side in (expr.left, expr.right):
                    if isinstance(side, (SSAValue, Const)):
                        continue

                    raise SSAVerificationError(
                        f"Non-SSA value {side} found in BinaryOp "
                        f"in block {block.cfg_block.id}"
                    )

def _verify_call_is_ssa_clean(ssa_blocks):

    for block in ssa_blocks.values():
        for stmt in block.statements:
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, Call):
                for arg in expr.args:
                    if isinstance(arg, (SSAValue, Const)):
                        continue
                    raise SSAVerificationError(
                        f"Non-SSA arg {arg} found in Call "
                        f"in block {block.cfg_block.id}"
                    )
