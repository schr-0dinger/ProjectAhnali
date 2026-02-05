from ir.types import AnaliType
from ir.expr import Const, BinaryOp, Var, Compare, Call
from ssa.value import SSAValue


class TypeInferenceError(Exception):
    pass


class TypeInferencePass:
    def __init__(self, cfg, ssa_blocks):
        self.cfg = cfg
        self.ssa_blocks = ssa_blocks

    def run(self):
        # -----------------------------
        # 1. Phi nodes FIRST
        # -----------------------------
        for _, ssa_block in self.ssa_blocks.items():
            for phi in ssa_block.phis:
                incoming_vals = list(phi.incoming.values())

                # Structural phi (no incoming edges)
                if not incoming_vals:
                    continue

                incoming_types = {
                    v.type
                    for v in incoming_vals
                    if isinstance(v, SSAValue)
                    and v.type not in (None, AnaliType.UNKNOWN)
                }


                # Undetermined phi (all inputs UNKNOWN) → skip for now
                if not incoming_types:
                    continue

                # Conflicting concrete types → error
                if len(incoming_types) != 1:
                    raise TypeInferenceError(
                        f"Cannot infer phi type for {phi.target}: {incoming_types}"
                    )

                # Exactly one concrete type
                phi.target.type = incoming_types.pop()

        # -----------------------------
        # 2. Statements
        # -----------------------------
        for _, ssa_block in self.ssa_blocks.items():
            for stmt in ssa_block.statements:
                target = stmt.defines()
                if not isinstance(target, SSAValue):
                    continue

                expr = stmt.expr

                # Structural / placeholder assignment
                if expr is None:
                    continue

                # Pure move: y = x → propagate later
                if isinstance(expr, SSAValue) and expr.type == AnaliType.UNKNOWN:
                    continue

                inferred = self._infer_expr_type(expr)

                if inferred in (None, AnaliType.UNKNOWN):
                    raise TypeInferenceError(
                        f"Could not infer type for {target}"
                    )

                target.type = inferred



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

        return AnaliType.UNKNOWN
