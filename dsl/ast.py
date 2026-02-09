# DSL AST and statement nodes.


class _ExprSymbol:
    def __init__(self, name):
        self.name = name

    def __add__(self, other):
        return _ExprBinary(self, "+", _coerce_expr(other))

    def __sub__(self, other):
        return _ExprBinary(self, "-", _coerce_expr(other))

    def __mul__(self, other):
        return _ExprBinary(self, "*", _coerce_expr(other))

    def __truediv__(self, other):
        return _ExprBinary(self, "/", _coerce_expr(other))

    def __mod__(self, other):
        return _ExprBinary(self, "%", _coerce_expr(other))

    def __lshift__(self, other):
        return _StmtAssign(self, _coerce_expr(other))

    def set_text(self, value):
        return _StmtSetText(self, value)


class _ExprConst:
    def __init__(self, value):
        self.value = value


class _ExprBinary:
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


class _ExprCompare:
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


class _ExprBoolOp:
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs


class _ExprUnary:
    def __init__(self, op, value):
        self.op = op
        self.value = value


class _ExprFormat:
    def __init__(self, parts):
        self.parts = parts


class _StmtAssign:
    def __init__(self, target, value):
        self.target = target
        self.value = value


class _StmtSetText:
    def __init__(self, view, value):
        self.view = view
        self.value = value


class _StmtToast:
    def __init__(self, message, duration=0):
        self.message = message
        self.duration = duration


class _StmtSnackbar:
    def __init__(self, message, duration=0):
        self.message = message
        self.duration = duration


class _StmtSimpleDialog:
    def __init__(self, title, message):
        self.title = title
        self.message = message


class _StmtExitApp:
    def __init__(self):
        pass


class _StmtIf:
    def __init__(self, cond, then, else_):
        self.cond = cond
        self.then = then
        self.else_ = else_


class _StmtWhile:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body


class _ExprRoot:
    def __getattr__(self, name):
        return _ExprSymbol(name)

    def f(self, template, *args):
        # template with {} placeholders
        parts = []
        segments = template.split("{}")
        for i, seg in enumerate(segments):
            if seg:
                parts.append(_ExprConst(seg))
            if i < len(args):
                parts.append(args[i])
        return _ExprFormat(parts)


expr = _ExprRoot()


def assign_stmt(target, value):
    return _StmtAssign(target, value)


def set_text(view, value):
    return _StmtSetText(view, value)


def _coerce_expr(value):
    if isinstance(
        value,
        (_ExprSymbol, _ExprBinary, _ExprCompare, _ExprBoolOp, _ExprUnary, _ExprFormat, _ExprConst),
    ):
        return value
    return _ExprConst(value)
