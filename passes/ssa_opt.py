from ir.expr import Const, BinaryOp, Compare, Call
from ssa.value import SSAValue


def optimize_ssa(
    ssa_blocks,
    *,
    enable_folding=False,
    enable_copy_removal=False,
    enable_coalesce=False,
):
    """
    Epsilon-2 SSA optimizations (simple, safe):
    - Constant propagation
    - Copy propagation
    - Optional constant folding for BinaryOp with Const operands
    - Copy-prop removal (delete redundant moves)
    - Coalesce phi incoming copies (start)
    """
    const_map = {}
    copy_map = {}

    use_copy_map = enable_coalesce or enable_copy_removal

    def _resolve(val):
        if isinstance(val, SSAValue):
            v = copy_map.get(val, val) if use_copy_map else val
            return const_map.get(v, v)
        return val

    def _iter_uses(value):
        if isinstance(value, SSAValue):
            yield value
        elif isinstance(value, BinaryOp):
            yield from _iter_uses(value.left)
            yield from _iter_uses(value.right)
        elif isinstance(value, Compare):
            yield from _iter_uses(value.left)
            yield from _iter_uses(value.right)
        elif isinstance(value, Call):
            for arg in value.args:
                yield from _iter_uses(arg)

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
                elif use_copy_map and isinstance(expr, SSAValue) and isinstance(dst, SSAValue):
                    copy_map[dst] = expr
                continue

            if isinstance(expr, Const) and isinstance(dst, SSAValue):
                const_map[dst] = expr
                continue

            if isinstance(expr, BinaryOp):
                expr.left = _resolve(expr.left)
                expr.right = _resolve(expr.right)
                if enable_folding:
                    if isinstance(expr.left, Const) and isinstance(expr.right, Const):
                        if isinstance(expr.left.value, int) and isinstance(expr.right.value, int):
                            op = expr.op
                            if op == "+":
                                folded = Const(expr.left.value + expr.right.value)
                            elif op == "-":
                                folded = Const(expr.left.value - expr.right.value)
                            elif op == "*":
                                folded = Const(expr.left.value * expr.right.value)
                            elif op == "/":
                                if expr.right.value == 0:
                                    folded = None
                                else:
                                    folded = Const(expr.left.value // expr.right.value)
                            elif op == "%":
                                if expr.right.value == 0:
                                    folded = None
                                else:
                                    folded = Const(expr.left.value % expr.right.value)
                            else:
                                folded = None
                            if folded is not None:
                                stmt.expr = folded
                                if isinstance(dst, SSAValue):
                                    const_map[dst] = folded
                continue

            if isinstance(expr, Compare):
                expr.left = _resolve(expr.left)
                expr.right = _resolve(expr.right)
                continue

            if isinstance(expr, Call):
                expr.args = [_resolve(a) for a in expr.args]
                continue

    if enable_coalesce:
        def _rewrite_expr(expr):
            if isinstance(expr, SSAValue):
                return _resolve(expr)
            if isinstance(expr, BinaryOp):
                expr.left = _resolve(expr.left)
                expr.right = _resolve(expr.right)
            elif isinstance(expr, Compare):
                expr.left = _resolve(expr.left)
                expr.right = _resolve(expr.right)
            elif isinstance(expr, Call):
                expr.args = [_resolve(a) for a in expr.args]
            return expr

        for block in ssa_blocks.values():
            for phi in block.phis:
                for pred, val in list(phi.incoming.items()):
                    if isinstance(val, SSAValue):
                        phi.incoming[pred] = _resolve(val)

            for stmt in block.statements:
                expr = getattr(stmt, "expr", None)
                if expr is not None:
                    stmt.expr = _rewrite_expr(expr)

            term = block.cfg_block.terminator
            if term and term.kind == "branch":
                term.cond = _rewrite_expr(term.cond)

    if enable_copy_removal:
        # Aggressive copy-prop rewrite + delete
        changed = True
        while changed:
            changed = False

            # Build use counts
            uses = {}

            def _mark_use(val):
                if isinstance(val, SSAValue):
                    uses[val] = uses.get(val, 0) + 1

            for block in ssa_blocks.values():
                for phi in block.phis:
                    for v in phi.incoming.values():
                        _mark_use(v)

                for stmt in block.statements:
                    for u in stmt.uses():
                        for v in _iter_uses(u):
                            _mark_use(v)

                    expr = getattr(stmt, "expr", None)
                    for v in _iter_uses(expr):
                        _mark_use(v)

                term = block.cfg_block.terminator
                if term and term.kind == "branch":
                    for v in _iter_uses(term.cond):
                        _mark_use(v)

            for block in ssa_blocks.values():
                new_stmts = []
                for stmt in block.statements:
                    expr = getattr(stmt, "expr", None)
                    dst = stmt.defines() if hasattr(stmt, "defines") else None

                    if isinstance(expr, SSAValue) and isinstance(dst, SSAValue):
                        # Only drop dead copies; keep live copies to preserve dataflow.
                        if uses.get(dst, 0) == 0:
                            changed = True
                            continue

                    new_stmts.append(stmt)
                block.statements = new_stmts

    return ssa_blocks
