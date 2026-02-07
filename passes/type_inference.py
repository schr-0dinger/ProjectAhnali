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
    CheckCast,
)
from ssa.value import SSAValue


class TypeInferenceError(Exception):
    pass


class TypeInferencePass:
    def __init__(self, cfg, ssa_blocks):
        self.cfg = cfg
        self.ssa_blocks = ssa_blocks

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

                raise TypeInferenceError(
                    f"Invalid arithmetic: {left_t} {expr.op} {right_t}"
                )

        if isinstance(expr, Compare):
            return AnaliType.BOOL
        
        if isinstance(expr, Call):
            if expr.return_type is not None:
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
        if isinstance(expr, CheckCast):
            return self._type_from_desc(expr.desc)

        return AnaliType.UNKNOWN

    def _type_from_desc(self, desc):
        if desc in ("I", "J", "B", "C", "S"):
            return AnaliType.INT
        if desc == "Z":
            return AnaliType.BOOL
        if desc in ("F", "D"):
            return AnaliType.FLOAT
        if desc == "Ljava/lang/String;":
            return AnaliType.STRING
        if isinstance(desc, str) and (desc.startswith("L") or desc.startswith("[")):
            return AnaliType.OBJECT
        return AnaliType.UNKNOWN
