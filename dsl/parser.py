import ast
import inspect
import textwrap

from .ast import (
    _ExprBinary,
    _ExprBoolOp,
    _ExprCompare,
    _ExprConst,
    _ExprFormat,
    _ExprSymbol,
    _ExprUnary,
    _StmtAssign,
    _StmtIf,
    _StmtSetText,
    _StmtExitApp,
    _StmtSimpleDialog,
    _StmtSnackbar,
    _StmtToast,
    _StmtLog,
    _StmtNavigate,
    _StmtWhile,
)


def _parse_handler_ast(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    tree = ast.parse(src)
    fn_def = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            fn_def = node
            break
    if fn_def is None:
        raise RuntimeError("Handler must be a function")

    out = []
    for stmt in fn_def.body:
        parsed = _parse_stmt(stmt)
        if parsed is None:
            continue
        out.append(parsed)
    return out


def _parse_stmt(stmt):
    if isinstance(stmt, ast.AugAssign):
        if not isinstance(stmt.target, ast.Name):
            raise RuntimeError("Only name targets are supported in +=/-=")
        target = _ExprSymbol(stmt.target.id)
        op = _binop_symbol(stmt.op)
        value = _parse_expr(stmt.value)
        return _StmtAssign(target, _ExprBinary(target, op, value))
    if isinstance(stmt, ast.Assign):
        if len(stmt.targets) != 1:
            raise RuntimeError("Only single-target assignments are supported")
        target = stmt.targets[0]
        value = _parse_expr(stmt.value)
        if isinstance(target, ast.Name):
            return _StmtAssign(_ExprSymbol(target.id), value)
        if isinstance(target, ast.Attribute) and target.attr == "text" and isinstance(target.value, ast.Name):
            return _StmtSetText(_ExprSymbol(target.value.id), value)
        raise RuntimeError("Unsupported assignment target")
    if isinstance(stmt, ast.Expr):
        call = stmt.value
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
            fn = call.func.id
            if fn in ("toast", "Toast"):
                args = [_parse_expr(a) for a in call.args]
                if not args:
                    raise RuntimeError("toast requires message")
                msg = args[0].value if isinstance(args[0], _ExprConst) else None
                if msg is None:
                    raise RuntimeError("toast message must be a constant string")
                duration = 0
                if len(args) > 1:
                    if not isinstance(args[1], _ExprConst):
                        raise RuntimeError("toast duration must be constant")
                    duration = int(args[1].value)
                return _StmtToast(msg, duration)
            if fn in ("snackbar", "Snackbar"):
                args = [_parse_expr(a) for a in call.args]
                if not args:
                    raise RuntimeError("snackbar requires message")
                msg = args[0].value if isinstance(args[0], _ExprConst) else None
                if msg is None:
                    raise RuntimeError("snackbar message must be a constant string")
                duration = 0
                if len(args) > 1:
                    if not isinstance(args[1], _ExprConst):
                        raise RuntimeError("snackbar duration must be constant")
                    duration = int(args[1].value)
                return _StmtSnackbar(msg, duration)
            if fn in ("simple_dialog", "SimpleDialog"):
                args = [_parse_expr(a) for a in call.args]
                if len(args) < 2:
                    raise RuntimeError("simple_dialog requires title and message")
                if not isinstance(args[0], _ExprConst) or not isinstance(args[1], _ExprConst):
                    raise RuntimeError("simple_dialog args must be constants")
                return _StmtSimpleDialog(args[0].value, args[1].value)
            if fn == "log":
                args = [_parse_expr(a) for a in call.args]
                if len(args) < 2:
                    raise RuntimeError("log requires tag and message")
                if not isinstance(args[0], _ExprConst) or not isinstance(args[1], _ExprConst):
                    raise RuntimeError("log args must be constant strings")
                return _StmtLog(args[0].value, args[1].value)
            if fn in ("navigate", "Navigate"):
                args = [_parse_expr(a) for a in call.args]
                if not args:
                    raise RuntimeError("Navigate requires a target screen name")
                target = args[0].value if isinstance(args[0], _ExprConst) else None
                if target is None:
                    raise RuntimeError("Navigate target must be a constant string")
                return _StmtNavigate(target)
            if fn == "exit_app":
                if call.args:
                    raise RuntimeError("exit_app takes no arguments")
                return _StmtExitApp()
        return None
    if isinstance(stmt, ast.Pass):
        return None
    if isinstance(stmt, ast.If):
        return _StmtIf(
            _parse_expr(stmt.test),
            _parse_stmt_block(stmt.body),
            _parse_stmt_block(stmt.orelse),
        )
    if isinstance(stmt, ast.While):
        return _StmtWhile(
            _parse_expr(stmt.test),
            _parse_stmt_block(stmt.body),
        )
    raise RuntimeError(f"Unsupported statement: {ast.dump(stmt)}")


def _parse_stmt_block(stmts):
    out = []
    for stmt in stmts:
        parsed = _parse_stmt(stmt)
        if parsed is None:
            continue
        out.append(parsed)
    return out


def _parse_expr(node):
    if isinstance(node, ast.Constant):
        return _ExprConst(node.value)
    if isinstance(node, ast.Name):
        return _ExprSymbol(node.id)
    if isinstance(node, ast.BinOp):
        lhs = _parse_expr(node.left)
        rhs = _parse_expr(node.right)
        return _ExprBinary(lhs, _binop_symbol(node.op), rhs)
    if isinstance(node, ast.Compare):
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise RuntimeError("Only single comparisons are supported")
        lhs = _parse_expr(node.left)
        rhs = _parse_expr(node.comparators[0])
        if not isinstance(lhs, (_ExprSymbol, _ExprConst)) or not isinstance(rhs, (_ExprSymbol, _ExprConst)):
            raise RuntimeError("Only simple name/const comparisons are supported")
        return _ExprCompare(lhs, _cmpop_symbol(node.ops[0]), rhs)
    if isinstance(node, ast.BoolOp):
        op = _boolop_symbol(node.op)
        values = [_parse_expr(v) for v in node.values]
        if len(values) < 2:
            raise RuntimeError("BoolOp requires at least two operands")
        out = values[0]
        for rhs in values[1:]:
            out = _ExprBoolOp(op, out, rhs)
        return out
    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.Not):
            return _ExprUnary("not", _parse_expr(node.operand))
        if isinstance(node.op, ast.USub):
            v = _parse_expr(node.operand)
            if isinstance(v, _ExprConst):
                if not isinstance(v.value, int) or isinstance(v.value, bool):
                    raise RuntimeError("Unary '-' supports integer constants only")
                return _ExprConst(-v.value)
            return _ExprBinary(_ExprConst(0), "-", v)
        raise RuntimeError("Unsupported unary operator")
    if isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(_ExprConst(value.value))
            elif isinstance(value, ast.FormattedValue):
                parts.append(_parse_expr(value.value))
            else:
                raise RuntimeError("Unsupported f-string part")
        return _ExprFormat(parts)
    raise RuntimeError(f"Unsupported expression: {ast.dump(node)}")


def _binop_symbol(op):
    if isinstance(op, ast.Add):
        return "+"
    if isinstance(op, ast.Sub):
        return "-"
    if isinstance(op, ast.Mult):
        return "*"
    if isinstance(op, ast.Div):
        return "/"
    if isinstance(op, ast.Mod):
        return "%"
    raise RuntimeError("Only +, -, *, /, % are supported")


def _cmpop_symbol(op):
    if isinstance(op, ast.Eq):
        return "=="
    if isinstance(op, ast.NotEq):
        return "!="
    if isinstance(op, ast.Lt):
        return "<"
    if isinstance(op, ast.LtE):
        return "<="
    if isinstance(op, ast.Gt):
        return ">"
    if isinstance(op, ast.GtE):
        return ">="
    raise RuntimeError("Unsupported comparison operator")


def _boolop_symbol(op):
    if isinstance(op, ast.And):
        return "and"
    if isinstance(op, ast.Or):
        return "or"
    raise RuntimeError("Unsupported boolean operator")
