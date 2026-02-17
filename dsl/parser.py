import ast
import inspect
import textwrap

from .ast import (
    _ExprBinary,
    _ExprBoolOp,
    _ExprCompare,
    _ExprConst,
    _ExprFormat,
    _ExprHttpGet,
    _ExprStorageGet,
    _ExprSymbol,
    _ExprUnary,
    _StmtAssign,
    _StmtIf,
    _StmtSetText,
    _StmtExitApp,
    _StmtSimpleDialog,
    _StmtSnackbar,
    _StmtToast,
    _StmtOpenUrl,
    _StmtCheckConnectivity,
    _StmtHttpGet,
    _StmtStorageGet,
    _StmtStorageRemove,
    _StmtStoragePut,
    _StmtAnimate,
    _StmtAnimationGroup,
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
            if fn in (
                "animate",
                "Animate",
                "fade_in",
                "FadeIn",
                "fade_out",
                "FadeOut",
                "rotate",
                "Rotate",
                "scale",
                "Scale",
                "translate",
                "Translate",
                "animate_elevation",
                "AnimateElevation",
                "sequence",
                "Sequence",
                "parallel",
                "Parallel",
            ):
                return _parse_animation_call(call)
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
            if fn in ("open_url", "OpenUrl", "launch_url", "LaunchUrl", "url_launcher", "URLLauncher"):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError('open_url expects exactly 1 string argument. Usage: open_url("https://...")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("open_url argument 'url' must be a constant string")
                return _StmtOpenUrl(args[0].value)
            if fn in (
                "check_connectivity",
                "CheckConnectivity",
                "connectivity_check",
                "ConnectivityCheck",
                "is_connected",
                "IsConnected",
            ):
                if call.args:
                    raise RuntimeError("check_connectivity expects no arguments. Usage: check_connectivity()")
                return _StmtCheckConnectivity()
            if fn in (
                "http_get",
                "HttpGet",
                "fetch_url",
                "FetchUrl",
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (1 <= len(args) <= 2):
                    raise RuntimeError('http_get expects 1 or 2 string arguments. Usage: http_get("https://...", "fallback")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("http_get argument 'url' must be a constant string")
                default_expr = args[1] if len(args) > 1 else _ExprConst("")
                if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                    raise RuntimeError("http_get argument 'default_value' must be a constant string")
                return _StmtHttpGet(args[0].value, default_expr.value)
            if fn in (
                "storage_put",
                "StoragePut",
                "set_storage",
                "SetStorage",
                "save_storage",
                "SaveStorage",
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError('storage_put expects exactly 2 string arguments. Usage: storage_put("key", "value")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("storage_put argument 'key' must be a constant string")
                if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                    raise RuntimeError("storage_put argument 'value' must be a constant string")
                return _StmtStoragePut(args[0].value, args[1].value)
            if fn in (
                "storage_get",
                "StorageGet",
                "get_storage",
                "GetStorage",
                "load_storage",
                "LoadStorage",
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (1 <= len(args) <= 2):
                    raise RuntimeError('storage_get expects 1 or 2 string arguments. Usage: storage_get("key", "default")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("storage_get argument 'key' must be a constant string")
                default_expr = args[1] if len(args) > 1 else _ExprConst("")
                if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                    raise RuntimeError("storage_get argument 'default_value' must be a constant string")
                return _StmtStorageGet(args[0].value, default_expr.value)
            if fn in (
                "storage_remove",
                "StorageRemove",
                "remove_storage",
                "RemoveStorage",
                "delete_storage",
                "DeleteStorage",
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError('storage_remove expects exactly 1 string argument. Usage: storage_remove("key")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("storage_remove argument 'key' must be a constant string")
                return _StmtStorageRemove(args[0].value)
            if fn in ("request_permissions", "request_permission", "RequestPermissions", "RequestPermission"):
                perms, request_code = _parse_permissions_call(call)
                from .ast import _StmtRequestPermissions
                return _StmtRequestPermissions(perms, request_code=request_code)
            if fn in ("back", "Back"):
                if call.args:
                    raise RuntimeError("Back takes no arguments")
                from .ast import _StmtBack
                return _StmtBack()
            if fn in ("replace", "Replace"):
                args = [_parse_expr(a) for a in call.args]
                if not args:
                    raise RuntimeError("Replace requires a target screen name")
                target = args[0].value if isinstance(args[0], _ExprConst) else None
                if target is None:
                    raise RuntimeError("Replace target must be a constant string")
                from .ast import _StmtReplace
                return _StmtReplace(target)
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
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in (
            "http_get",
            "HttpGet",
            "fetch_url",
            "FetchUrl",
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 2):
                raise RuntimeError('http_get expects 1 or 2 string arguments. Usage: http_get("https://...", "fallback")')
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("http_get argument 'url' must be a constant string")
            default_expr = args[1] if len(args) > 1 else _ExprConst("")
            if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                raise RuntimeError("http_get argument 'default_value' must be a constant string")
            return _ExprHttpGet(args[0].value, default_expr.value)
        if node.func.id in (
            "storage_get",
            "StorageGet",
            "get_storage",
            "GetStorage",
            "load_storage",
            "LoadStorage",
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 2):
                raise RuntimeError('storage_get expects 1 or 2 string arguments. Usage: storage_get("key", "default")')
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("storage_get argument 'key' must be a constant string")
            default_expr = args[1] if len(args) > 1 else _ExprConst("")
            if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                raise RuntimeError("storage_get argument 'default_value' must be a constant string")
            return _ExprStorageGet(args[0].value, default_expr.value)
        if node.func.id in ("ushr", "unsigned_rshift"):
            if len(node.args) != 2:
                raise RuntimeError("ushr expects exactly two arguments")
            lhs = _parse_expr(node.args[0])
            rhs = _parse_expr(node.args[1])
            return _ExprBinary(lhs, ">>>", rhs)
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


def _parse_permissions_call(call):
    perms = []
    request_code = None
    for kw in call.keywords or []:
        if kw.arg == "request_code":
            if not isinstance(kw.value, ast.Constant) or not isinstance(kw.value.value, int):
                raise RuntimeError("request_code must be an integer constant")
            request_code = int(kw.value.value)
        elif kw.arg in ("permissions", "perms"):
            perms.extend(_parse_permission_arg(kw.value))
        else:
            raise RuntimeError(f"Unsupported keyword '{kw.arg}' for request_permissions")

    args = list(call.args or [])
    if args:
        # Allow trailing request_code int.
        last = args[-1]
        if isinstance(last, ast.Constant) and isinstance(last.value, int):
            if request_code is None:
                request_code = int(last.value)
            args = args[:-1]
    for arg in args:
        perms.extend(_parse_permission_arg(arg))

    if not perms:
        raise RuntimeError("request_permissions requires at least one permission string")
    if request_code is None:
        request_code = 0
    return perms, request_code


def _parse_animation_call(call):
    if not isinstance(call.func, ast.Name):
        raise RuntimeError("Animation calls must use direct function names")

    fn = call.func.id
    fn_l = _normalize_anim_fn_name(fn)
    if fn_l in ("sequence", "parallel"):
        if call.keywords:
            raise RuntimeError(f"{fn} does not accept keyword arguments")
        items = []
        for arg in call.args:
            if not isinstance(arg, ast.Call):
                raise RuntimeError(f"{fn} arguments must be animation calls")
            items.append(_parse_animation_call(arg))
        if not items:
            raise RuntimeError(f"{fn} requires at least one animation")
        mode = "sequence" if fn_l == "sequence" else "parallel"
        return _StmtAnimationGroup(mode, items)

    return _parse_animate_like_call(call, fn_l)


def _parse_animate_like_call(call, fn_l):
    target, remaining_args = _parse_anim_target(call.args)
    kwargs = {kw.arg: kw.value for kw in (call.keywords or [])}
    if any(k is None for k in kwargs):
        raise RuntimeError("Animation keyword unpacking is not supported")

    duration = _pop_const_int(kwargs, "duration")
    delay = _pop_const_int(kwargs, "delay")
    interpolator = _pop_const_str(kwargs, "interpolator")
    properties = {}

    if fn_l in ("animate",):
        properties, kwargs = _parse_animate_properties(remaining_args, kwargs)
    elif fn_l in ("fade_in",):
        _require_no_args(remaining_args, "fade_in")
        properties["alpha"] = 1.0
    elif fn_l in ("fade_out",):
        _require_no_args(remaining_args, "fade_out")
        properties["alpha"] = 0.0
    elif fn_l in ("rotate",):
        value = _parse_single_numeric_arg_or_kw(
            remaining_args,
            kwargs,
            fn_name="rotate",
            kw_names=("to", "value", "degrees"),
        )
        properties["rotate"] = value
    elif fn_l in ("scale",):
        properties.update(_parse_scale_args(remaining_args, kwargs))
    elif fn_l in ("translate",):
        properties.update(_parse_translate_args(remaining_args, kwargs))
    elif fn_l in ("animate_elevation",):
        value = _parse_single_numeric_arg_or_kw(
            remaining_args,
            kwargs,
            fn_name="animate_elevation",
            kw_names=("to", "value"),
        )
        properties["elevation"] = value
    else:
        raise RuntimeError(f"Unsupported animation helper: {fn_l}")

    if kwargs:
        bad = ", ".join(sorted(kwargs.keys()))
        raise RuntimeError(f"Unsupported animation keyword(s): {bad}")
    if not properties:
        raise RuntimeError("Animation requires at least one property")
    return _StmtAnimate(
        target=target,
        properties=properties,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
    )


def _parse_anim_target(args):
    if not args:
        raise RuntimeError("Animation requires a target view id")
    first = args[0]
    if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
        raise RuntimeError("Animation target must be a constant string id")
    return first.value, list(args[1:])


def _parse_single_numeric_arg_or_kw(args, kwargs, *, fn_name, kw_names):
    value = None
    if args:
        if len(args) > 1:
            raise RuntimeError(f"{fn_name} accepts at most one positional value")
        value = _require_numeric_const(args[0], f"{fn_name} value")
    for key in kw_names:
        if key in kwargs:
            if value is not None:
                raise RuntimeError(f"{fn_name} value specified more than once")
            value = _require_numeric_const(kwargs.pop(key), f"{fn_name} {key}")
    if value is None:
        raise RuntimeError(f"{fn_name} requires a numeric value")
    return value


def _parse_scale_args(args, kwargs):
    props = {}
    if args:
        if len(args) > 1:
            raise RuntimeError("scale accepts at most one positional scale value")
        value = _require_numeric_const(args[0], "scale value")
        props["scale"] = value

    if "to" in kwargs:
        value = _require_numeric_const(kwargs.pop("to"), "scale to")
        if props:
            raise RuntimeError("scale value specified more than once")
        props["scale"] = value
    if "value" in kwargs:
        value = _require_numeric_const(kwargs.pop("value"), "scale value")
        if props:
            raise RuntimeError("scale value specified more than once")
        props["scale"] = value

    if "x" in kwargs:
        props["scale_x"] = _require_numeric_const(kwargs.pop("x"), "scale x")
    if "y" in kwargs:
        props["scale_y"] = _require_numeric_const(kwargs.pop("y"), "scale y")
    if "scale_x" in kwargs:
        props["scale_x"] = _require_numeric_const(kwargs.pop("scale_x"), "scale_x")
    if "scale_y" in kwargs:
        props["scale_y"] = _require_numeric_const(kwargs.pop("scale_y"), "scale_y")
    if not props:
        raise RuntimeError("scale requires value, x/y, or scale_x/scale_y")
    return props


def _parse_translate_args(args, kwargs):
    props = {}
    if args:
        if len(args) > 2:
            raise RuntimeError("translate accepts at most two positional values")
        props["translate_x"] = _require_numeric_const(args[0], "translate x")
        if len(args) == 2:
            props["translate_y"] = _require_numeric_const(args[1], "translate y")

    if "x" in kwargs:
        props["translate_x"] = _require_numeric_const(kwargs.pop("x"), "translate x")
    if "y" in kwargs:
        props["translate_y"] = _require_numeric_const(kwargs.pop("y"), "translate y")
    if "translate_x" in kwargs:
        props["translate_x"] = _require_numeric_const(kwargs.pop("translate_x"), "translate_x")
    if "translate_y" in kwargs:
        props["translate_y"] = _require_numeric_const(kwargs.pop("translate_y"), "translate_y")
    if not props:
        raise RuntimeError("translate requires x/y or translate_x/translate_y")
    return props


def _parse_animate_properties(args, kwargs):
    properties = {}
    if args:
        if len(args) != 2:
            raise RuntimeError("animate positional form is animate(id, property, value)")
        prop_node, value_node = args
        if not isinstance(prop_node, ast.Constant) or not isinstance(prop_node.value, str):
            raise RuntimeError("animate property must be a constant string")
        prop_name = _normalize_anim_property(prop_node.value)
        properties[prop_name] = _require_numeric_const(value_node, f"animate {prop_name}")

    allowed = {
        "rotate",
        "scale",
        "scale_x",
        "scale_y",
        "translate_x",
        "translate_y",
        "alpha",
        "elevation",
    }
    for key in list(kwargs.keys()):
        if key in ("duration", "delay", "interpolator"):
            continue
        normalized = _normalize_anim_property(key)
        if normalized not in allowed:
            raise RuntimeError(f"Unsupported animate property '{key}'")
        properties[normalized] = _require_numeric_const(kwargs.pop(key), f"animate {normalized}")

    if not properties:
        raise RuntimeError("animate requires at least one animatable property")
    return properties, kwargs


def _normalize_anim_property(name):
    mapping = {
        "rotation": "rotate",
        "rotate": "rotate",
        "scale": "scale",
        "scale_x": "scale_x",
        "scalex": "scale_x",
        "scale_y": "scale_y",
        "scaley": "scale_y",
        "translate_x": "translate_x",
        "translation_x": "translate_x",
        "translatey": "translate_y",
        "translate_y": "translate_y",
        "translation_y": "translate_y",
        "alpha": "alpha",
        "elevation": "elevation",
    }
    key = str(name).strip().lower().replace("-", "_")
    return mapping.get(key, key)


def _normalize_anim_fn_name(name):
    key = str(name).strip().lower().replace("-", "_")
    mapping = {
        "fadein": "fade_in",
        "fadeout": "fade_out",
        "animateelevation": "animate_elevation",
    }
    return mapping.get(key, key)


def _pop_const_int(kwargs, key):
    if key not in kwargs:
        return None
    node = kwargs.pop(key)
    if not isinstance(node, ast.Constant) or not isinstance(node.value, int) or isinstance(node.value, bool):
        raise RuntimeError(f"{key} must be an integer constant")
    return int(node.value)


def _pop_const_str(kwargs, key):
    if key not in kwargs:
        return None
    node = kwargs.pop(key)
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        raise RuntimeError(f"{key} must be a string constant")
    return str(node.value)


def _require_numeric_const(node, label):
    if not isinstance(node, ast.Constant):
        raise RuntimeError(f"{label} must be a numeric constant")
    value = node.value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(f"{label} must be a numeric constant")
    return float(value)


def _require_no_args(args, fn_name):
    if args:
        raise RuntimeError(f"{fn_name} does not accept positional value arguments")


def _parse_permission_arg(node):
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, str):
            raise RuntimeError("Permission must be a string constant")
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple)):
        out = []
        for elt in node.elts:
            if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
                raise RuntimeError("Permission list must contain string constants")
            out.append(elt.value)
        return out
    raise RuntimeError("Permissions must be string constants or lists of string constants")


def _binop_symbol(op):
    if isinstance(op, ast.Add):
        return "+"
    if isinstance(op, ast.Sub):
        return "-"
    if isinstance(op, ast.Mult):
        return "*"
    if isinstance(op, ast.Div):
        return "/"
    if isinstance(op, ast.FloorDiv):
        return "/"
    if isinstance(op, ast.Mod):
        return "%"
    if isinstance(op, ast.BitAnd):
        return "&"
    if isinstance(op, ast.BitOr):
        return "|"
    if isinstance(op, ast.BitXor):
        return "^"
    if isinstance(op, ast.LShift):
        return "<<"
    if isinstance(op, ast.RShift):
        return ">>"
    raise RuntimeError("Only +, -, *, /, %, &, |, ^, <<, >> are supported")


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
