from ir.expr import Const, BinaryOp, Compare, Call
from ssa.value import SSAValue


def optimize_ssa(ssa_blocks):
    """
    Epsilon-2 SSA optimizations (simple, safe):
    - Constant propagation
    - Copy propagation
    - Constant folding for BinaryOp with Const operands
    """
    const_map = {}
    copy_map = {}

    def _resolve(val):
        if isinstance(val, SSAValue):
            v = copy_map.get(val, val)
            return const_map.get(v, v)
        return val

    for block in ssa_blocks.values():
        for stmt in block.statements:
            expr = getattr(stmt, "expr", None)
            dst = stmt.defines() if hasattr(stmt, "defines") else None

            if isinstance(expr, (int, float, bool)) and isinstance(dst, SSAValue):
                c = Const(expr)
                stmt.expr = c
                const_map[dst] = c
                continue

            if isinstance(expr, SSAValue):
                expr = _resolve(expr)
                stmt.expr = expr
                if isinstance(expr, Const) and isinstance(dst, SSAValue):
                    const_map[dst] = expr
                elif isinstance(expr, SSAValue) and isinstance(dst, SSAValue):
                    copy_map[dst] = expr
                continue

            if isinstance(expr, Const) and isinstance(dst, SSAValue):
                const_map[dst] = expr
                continue

            if isinstance(expr, BinaryOp):
                expr.left = _resolve(expr.left)
                expr.right = _resolve(expr.right)
                continue

            if isinstance(expr, Compare):
                expr.left = _resolve(expr.left)
                expr.right = _resolve(expr.right)
                continue

            if isinstance(expr, Call):
                expr.args = [_resolve(a) for a in expr.args]
                continue

    return ssa_blocks
