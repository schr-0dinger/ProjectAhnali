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


class _ExprStorageGet:
    def __init__(self, key, default_value):
        self.key = key
        self.default_value = default_value


class _ExprHttpGet:
    def __init__(self, url, default_value):
        self.url = url
        self.default_value = default_value


class _ExprHttpGetStatus:
    def __init__(self, url):
        self.url = url


class _ExprHttpGetError:
    def __init__(self, url):
        self.url = url


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


class _StmtLog:
    def __init__(self, tag, message):
        self.tag = tag
        self.message = message


class _StmtOpenUrl:
    def __init__(self, url):
        self.url = url


class _StmtCheckConnectivity:
    def __init__(self):
        pass


class _StmtStoragePut:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class _StmtStorageGet:
    def __init__(self, key, default_value):
        self.key = key
        self.default_value = default_value


class _StmtStorageRemove:
    def __init__(self, key):
        self.key = key


class _StmtHttpGet:
    def __init__(self, url, default_value):
        self.url = url
        self.default_value = default_value


class _StmtHttpGetStatus:
    def __init__(self, url):
        self.url = url


class _StmtHttpGetError:
    def __init__(self, url):
        self.url = url


class _StmtHttpGetRoute:
    def __init__(self, url, success_target_id, failure_target_id, default_value):
        self.url = url
        self.success_target_id = success_target_id
        self.failure_target_id = failure_target_id
        self.default_value = default_value


class _StmtNavigate:
    def __init__(self, target):
        self.target = target


class _StmtBack:
    def __init__(self):
        pass


class _StmtReplace:
    def __init__(self, target):
        self.target = target


class _StmtAnimate:
    def __init__(self, target, properties, duration=None, delay=None, interpolator=None):
        self.target = target
        self.properties = dict(properties or {})
        self.duration = duration
        self.delay = delay
        self.interpolator = interpolator


class _StmtAnimationGroup:
    def __init__(self, mode, animations):
        self.mode = mode
        self.animations = list(animations or [])


class _StmtRequestPermissions:
    def __init__(self, permissions, request_code=0):
        self.permissions = permissions
        self.request_code = request_code


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
        (
            _ExprSymbol,
            _ExprBinary,
            _ExprCompare,
            _ExprBoolOp,
            _ExprUnary,
            _ExprFormat,
            _ExprStorageGet,
            _ExprHttpGet,
            _ExprHttpGetStatus,
            _ExprHttpGetError,
            _ExprConst,
        ),
    ):
        return value
    return _ExprConst(value)
