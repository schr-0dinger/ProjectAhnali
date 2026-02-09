from ir.types import AnaliType
from ir.expr import (
    Const,
    BinaryOp,
    Var,
    Compare,
    Call,
    New,
    NewArray,
    PrimitiveCast,
    StaticFieldGet,
    FieldGet,
    ArrayGet,
    ArrayLength,
    CheckCast,
    InstanceOf,
    FilledNewArray,
)
from ir.stmt import Return, Throw, StaticFieldSet, FieldSet, ArraySet, CallStmt
from ssa.value import SSAValue


class TypeInferenceError(Exception):
    pass


class TypeInferencePass:
    def __init__(self, cfg, ssa_blocks, return_type=None):
        self.cfg = cfg
        self.ssa_blocks = ssa_blocks
        self.return_type = return_type

    def run(self):
        # Fixpoint: branch/loop locals can require multiple rounds
        # before phi and move types stabilize.
        for _ in range(8):
            changed = False

            # 1) Phi nodes
            for _, ssa_block in self.ssa_blocks.items():
                for phi in ssa_block.phis:
                    incoming_vals = list(phi.incoming.values())
                    if not incoming_vals:
                        continue

                    incoming_types = {
                        v.type
                        for v in incoming_vals
                        if isinstance(v, SSAValue) and v.type not in (None, AnaliType.UNKNOWN)
                    }
                    if not incoming_types:
                        continue
                    if len(incoming_types) != 1:
                        raise TypeInferenceError(
                            f"Cannot infer phi type for {phi.target}: {incoming_types}"
                        )

                    inferred = incoming_types.pop()
                    if phi.target.type != inferred:
                        phi.target.type = inferred
                        changed = True
                    for incoming in incoming_vals:
                        if isinstance(incoming, SSAValue):
                            if self._set_type(incoming, phi.target.type):
                                changed = True

            # 2) Statements
            for _, ssa_block in self.ssa_blocks.items():
                for stmt in ssa_block.statements:
                    target = stmt.defines()
                    if not isinstance(target, SSAValue):
                        continue

                    expr = stmt.expr
                    if expr is None:
                        continue
                    if isinstance(expr, SSAValue) and expr.type == AnaliType.UNKNOWN:
                        continue

                    inferred = self._infer_expr_type(expr)
                    if inferred in (None, AnaliType.UNKNOWN):
                        continue
                    if target.type != inferred:
                        target.type = inferred
                        changed = True

            # 3) Usage-driven propagation (reference vs primitive)
            for _, ssa_block in self.ssa_blocks.items():
                for stmt in ssa_block.statements:
                    if isinstance(stmt, Return):
                        if isinstance(stmt.value, SSAValue):
                            if self._set_type(stmt.value, self.return_type):
                                changed = True
                        continue
                    if isinstance(stmt, Throw):
                        if isinstance(stmt.value, SSAValue):
                            if stmt.value.type not in (None, AnaliType.UNKNOWN):
                                if not self._is_ref_type(stmt.value.type):
                                    raise RuntimeError(
                                        f"Throw requires object type, got {stmt.value.type}"
                                    )
                            if self._set_type(stmt.value, AnaliType.OBJECT):
                                changed = True
                        continue
                    if isinstance(stmt, StaticFieldSet):
                        if isinstance(stmt.value, SSAValue):
                            if self._set_type(stmt.value, stmt.desc):
                                changed = True
                        continue
                    if isinstance(stmt, FieldSet):
                        if isinstance(stmt.obj, SSAValue):
                            if self._set_type(stmt.obj, stmt.owner):
                                changed = True
                        if isinstance(stmt.value, SSAValue):
                            if self._set_type(stmt.value, stmt.desc):
                                changed = True
                        continue
                    if isinstance(stmt, ArraySet):
                        if isinstance(stmt.array, SSAValue):
                            array_desc = f"[{stmt.elem_desc}"
                            if self._set_type(stmt.array, array_desc):
                                changed = True
                        if isinstance(stmt.index, SSAValue):
                            if self._set_type(stmt.index, AnaliType.INT):
                                changed = True
                        if isinstance(stmt.value, SSAValue):
                            if self._set_type(stmt.value, stmt.elem_desc):
                                changed = True
                        continue

                    expr = getattr(stmt, "expr", None)
                    if isinstance(expr, Call):
                        if expr.invoke_kind in ("virtual", "direct", "interface", "super") and expr.args:
                            recv = expr.args[0]
                            if isinstance(recv, SSAValue):
                                if self._set_type(recv, expr.owner or AnaliType.OBJECT):
                                    changed = True
                        if expr.arg_types is not None:
                            arg_types = list(expr.arg_types)
                            if expr.invoke_kind in ("virtual", "direct", "interface", "super"):
                                if len(arg_types) == len(expr.args):
                                    pairs = zip(expr.args, arg_types)
                                elif len(arg_types) == len(expr.args) - 1:
                                    pairs = zip(expr.args[1:], arg_types)
                                else:
                                    pairs = zip(expr.args, arg_types)
                            else:
                                pairs = zip(expr.args, arg_types)
                            for arg, typ in pairs:
                                if isinstance(arg, SSAValue):
                                    if self._set_type(arg, typ):
                                        changed = True
                        continue
                    if isinstance(expr, New):
                        for arg, typ in zip(expr.args, expr.arg_types or []):
                            if isinstance(arg, SSAValue):
                                if self._set_type(arg, typ):
                                    changed = True
                        continue
                    if isinstance(expr, NewArray):
                        if isinstance(expr.length, SSAValue):
                            if self._set_type(expr.length, AnaliType.INT):
                                changed = True
                        continue
                    if isinstance(expr, FilledNewArray):
                        for arg in expr.args:
                            if isinstance(arg, SSAValue):
                                if self._set_type(arg, expr.elem_desc):
                                    changed = True
                        continue
                    if isinstance(expr, ArrayGet):
                        if isinstance(expr.array, SSAValue):
                            if self._set_type(expr.array, f"[{expr.elem_desc}"):
                                changed = True
                        if isinstance(expr.index, SSAValue):
                            if self._set_type(expr.index, AnaliType.INT):
                                changed = True
                        continue
                    if isinstance(expr, FieldGet):
                        if isinstance(expr.obj, SSAValue):
                            if self._set_type(expr.obj, expr.owner):
                                changed = True
                        continue
                    if isinstance(expr, CheckCast):
                        if isinstance(expr.value, SSAValue):
                            if self._set_type(expr.value, AnaliType.OBJECT):
                                changed = True
                        continue
                    if isinstance(expr, InstanceOf):
                        if isinstance(expr.value, SSAValue):
                            if self._set_type(expr.value, AnaliType.OBJECT):
                                changed = True
                        continue
                    if isinstance(expr, PrimitiveCast):
                        if isinstance(expr.value, SSAValue):
                            if self._set_type(expr.value, expr.from_desc):
                                changed = True
                        continue

            # 4) Terminators (conditions)
            for block in self.cfg.blocks.values():
                term = block.terminator
                if term and term.kind == "branch":
                    cond = term.cond
                    if isinstance(cond, Compare):
                        left = cond.left
                        right = cond.right
                        if cond.op in ("<", "<=", ">", ">="):
                            left_t = getattr(left, "type", None)
                            right_t = getattr(right, "type", None)
                            if not (self._is_ref_type(left_t) or self._is_ref_type(right_t)):
                                preferred = None
                                if not self._is_unknown_type(left_t):
                                    preferred = left_t
                                elif not self._is_unknown_type(right_t):
                                    preferred = right_t
                                if preferred is None:
                                    preferred = AnaliType.INT
                                if isinstance(left, SSAValue):
                                    if self._set_type(left, preferred):
                                        changed = True
                                if isinstance(right, SSAValue):
                                    if self._set_type(right, preferred):
                                        changed = True
                        elif cond.op in ("==", "!="):
                            left_ref = self._is_ref_type(getattr(left, "type", None))
                            right_ref = self._is_ref_type(getattr(right, "type", None))
                            if left_ref and isinstance(right, SSAValue):
                                if self._set_type(right, AnaliType.OBJECT):
                                    changed = True
                            if right_ref and isinstance(left, SSAValue):
                                if self._set_type(left, AnaliType.OBJECT):
                                    changed = True
                            if not (left_ref or right_ref):
                                left_t = getattr(left, "type", None)
                                right_t = getattr(right, "type", None)
                                preferred = None
                                if not self._is_unknown_type(left_t):
                                    preferred = left_t
                                elif not self._is_unknown_type(right_t):
                                    preferred = right_t
                                if preferred is None:
                                    preferred = AnaliType.INT
                                if isinstance(left, SSAValue):
                                    if self._set_type(left, preferred):
                                        changed = True
                                if isinstance(right, SSAValue):
                                    if self._set_type(right, preferred):
                                        changed = True
                    elif isinstance(cond, SSAValue):
                        if self._set_type(cond, AnaliType.BOOL):
                            changed = True

            if not changed:
                break

        return self.ssa_blocks

    # -----------------------------
    # Expression typing
    # -----------------------------
    def _infer_expr_type(self, expr):
        if isinstance(expr, int):
            return AnaliType.INT
        if isinstance(expr, float):
            return AnaliType.FLOAT
        if isinstance(expr, bool):
            return AnaliType.BOOL
        if isinstance(expr, str):
            return AnaliType.STRING

        if isinstance(expr, Const):
            return self._infer_expr_type(expr.value)

        if isinstance(expr, SSAValue):
            return expr.type

        if isinstance(expr, Var):
            raise TypeInferenceError(
                f"Raw Var found in SSA: {expr.name}"
            )

        if isinstance(expr, BinaryOp):
            left_t = self._infer_expr_type(expr.left)
            right_t = self._infer_expr_type(expr.right)

            if expr.op in {"+", "-", "*", "/", "%"}:
                if AnaliType.UNKNOWN in (left_t, right_t):
                    return AnaliType.UNKNOWN
                if left_t == right_t == AnaliType.INT:
                    return AnaliType.INT
                if left_t == right_t == AnaliType.FLOAT:
                    return AnaliType.FLOAT
                if left_t == right_t and left_t in ("J", "D"):
                    return left_t

                raise TypeInferenceError(
                    f"Invalid arithmetic: {left_t} {expr.op} {right_t}"
                )

        if isinstance(expr, Compare):
            return AnaliType.BOOL
        
        if isinstance(expr, Call):
            if expr.return_type is not None:
                if isinstance(expr.return_type, str):
                    return self._type_from_desc(expr.return_type)
                return expr.return_type
            return AnaliType.UNKNOWN
        if isinstance(expr, New):
            return expr.class_desc
        if isinstance(expr, NewArray):
            return expr.array_desc
        if isinstance(expr, PrimitiveCast):
            return self._type_from_desc(expr.to_desc)
        if isinstance(expr, StaticFieldGet):
            return self._type_from_desc(expr.desc)
        if isinstance(expr, FieldGet):
            return self._type_from_desc(expr.desc)
        if isinstance(expr, ArrayGet):
            return self._type_from_desc(expr.elem_desc)
        if isinstance(expr, ArrayLength):
            return AnaliType.INT
        if isinstance(expr, CheckCast):
            return self._type_from_desc(expr.desc)
        if isinstance(expr, InstanceOf):
            return AnaliType.BOOL
        if isinstance(expr, FilledNewArray):
            return self._type_from_desc(expr.array_desc)

        return AnaliType.UNKNOWN

    def _type_from_desc(self, desc):
        if desc in ("I", "B", "C", "S"):
            return AnaliType.INT
        if desc == "J":
            return "J"
        if desc == "Z":
            return AnaliType.BOOL
        if desc == "F":
            return AnaliType.FLOAT
        if desc == "D":
            return "D"
        if desc == "Ljava/lang/String;":
            return AnaliType.STRING
        if isinstance(desc, str) and (desc.startswith("L") or desc.startswith("[")):
            return AnaliType.OBJECT
        return AnaliType.UNKNOWN

    def _normalize_hint(self, hint):
        if hint is None:
            return None
        if isinstance(hint, AnaliType):
            if hint is AnaliType.UNKNOWN:
                return None
            return hint
        if isinstance(hint, str):
            if hint in ("I", "B", "C", "S", "Z", "F", "D", "J"):
                return self._type_from_desc(hint)
            if hint == "Ljava/lang/String;":
                return hint
            return hint
        return hint

    def _is_ref_type(self, t):
        if t in (AnaliType.OBJECT, AnaliType.STRING):
            return True
        if isinstance(t, str) and (t.startswith("L") or t.startswith("[")):
            return True
        return False

    def _is_generic_object(self, t):
        return t in (AnaliType.OBJECT, "Ljava/lang/Object;")

    def _is_unknown_type(self, t):
        return t in (None, AnaliType.UNKNOWN)

    def _set_type(self, val, hint):
        if not isinstance(val, SSAValue):
            return False
        hint = self._normalize_hint(hint)
        if hint is None:
            return False
        cur = val.type
        if cur in (None, AnaliType.UNKNOWN):
            val.type = hint
            return True
        cur_norm = self._normalize_hint(cur)
        if cur_norm is None:
            val.type = hint
            return True
        if cur_norm is not cur and isinstance(cur_norm, AnaliType):
            val.type = cur_norm
        cur = cur_norm
        if cur == hint:
            return False
        if (
            (cur == AnaliType.STRING and hint == "Ljava/lang/String;")
            or (hint == AnaliType.STRING and cur == "Ljava/lang/String;")
        ):
            return False
        cur_ref = self._is_ref_type(cur)
        hint_ref = self._is_ref_type(hint)
        if cur_ref and hint_ref:
            if self._is_generic_object(cur) and not self._is_generic_object(hint):
                val.type = hint
                return True
            return False
        if not cur_ref and not hint_ref:
            if cur == hint:
                return False
            raise TypeInferenceError(f"Type conflict for {val}: {cur} vs {hint}")
        raise TypeInferenceError(f"Type conflict for {val}: {cur} vs {hint}")
