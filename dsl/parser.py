import ast
import inspect
import textwrap

from .parser_dispatch import EXPR_FN_BY_DOMAIN, STATEMENT_FN_BY_DOMAIN
from .ast import (
    _ExprBinary,
    _ExprBoolOp,
    _ExprCompare,
    _ExprConst,
    _ExprFormat,
    _ExprCall,
    _ExprDictLiteral,
    _ExprListLiteral,
    _ExprSetLiteral,
    _ExprTupleLiteral,
    _ExprHttpGetError,
    _ExprHttpAsyncError,
    _ExprHttpAsyncBody,
    _ExprHttpAsyncJsonArrayLength,
    _ExprHttpAsyncJsonField,
    _ExprHttpAsyncJsonFieldError,
    _ExprHttpAsyncStatus,
    _ExprHttpAsyncProgress,
    _ExprHttpGetRouteAsync,
    _ExprHttpGetJsonField,
    _ExprHttpGetJsonFieldError,
    _ExprHttpGetRetry,
    _ExprHttpGetStatus,
    _ExprHttpGet,
    _ExprClipboardGet,
    _ExprDeepLinkError,
    _ExprDeepLinkGet,
    _ExprWorkError,
    _ExprWorkStatus,
    _ExprAlarmError,
    _ExprAlarmStatus,
    _ExprJobError,
    _ExprJobStatus,
    _ExprOpenExternalResult,
    _ExprOpenExternalError,
    _ExprWebAddJsBridgeError,
    _ExprWebAddJsBridgeResult,
    _ExprWebChooseFileError,
    _ExprWebChooseFileResult,
    _ExprWebCookieGet,
    _ExprWebCookieGetError,
    _ExprWebCookieSetError,
    _ExprWebCookieSetResult,
    _ExprWebLoadError,
    _ExprWebLoadResult,
    _ExprLocationEnabled,
    _ExprShareFileError,
    _ExprShareFileResult,
    _ExprShareTextError,
    _ExprShareTextResult,
    _ExprNotifyError,
    _ExprNotifyResult,
    _ExprPermissionGranted,
    _ExprReactiveGet,
    _ExprStateBackendGet,
    _ExprStateBackendExists,
    _ExprStorageGet,
    _ExprStorageExists,
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
    _StmtCheckLocation,
    _StmtCheckPermission,
    _StmtClipboardSet,
    _StmtCreateNotificationChannel,
    _StmtWorkCancel,
    _StmtWorkEnqueue,
    _StmtAlarmCancel,
    _StmtAlarmSchedule,
    _StmtJobCancel,
    _StmtJobSchedule,
    _StmtAndroidStartActivity,
    _StmtOpenExternal,
    _StmtShareFile,
    _StmtWebAddJsBridge,
    _StmtWebChooseFile,
    _StmtWebCookieSet,
    _StmtWebLoad,
    _StmtWebSetPolicy,
    _StmtHttpGetError,
    _StmtHttpAsyncCancel,
    _StmtHttpAsyncBody,
    _StmtHttpAsyncJsonArrayLength,
    _StmtHttpAsyncJsonField,
    _StmtHttpAsyncJsonFieldError,
    _StmtHttpAsyncError,
    _StmtHttpAsyncStatus,
    _StmtHttpAsyncProgress,
    _StmtHttpGetJsonField,
    _StmtHttpGetJsonFieldError,
    _StmtHttpGetRouteAsync,
    _StmtHttpGetRetry,
    _StmtHttpGetRoute,
    _StmtHttpGetStatus,
    _StmtHttpGet,
    _StmtStorageClear,
    _StmtStorageExists,
    _StmtStorageGet,
    _StmtStorageRemove,
    _StmtStoragePut,
    _StmtReactiveObservable,
    _StmtReactiveSet,
    _StmtReactiveDerived,
    _StmtReactiveListen,
    _StmtReactiveBindText,
    _StmtStateBackendClear,
    _StmtStateBackendExists,
    _StmtStateBackendGet,
    _StmtStateBackendPut,
    _StmtStateBackendRemove,
    _StmtAnimate,
    _StmtAnimationGroup,
    _StmtLog,
    _StmtNavigate,
    _StmtNotify,
    _StmtShareText,
    _StmtWhile,
    _StmtForLoop,
    _StmtTryExcept,
    _StmtFunctionDef,
    _StmtReturn,
    _StmtAsyncFunctionDef,
    _StmtAsyncFor,
    _StmtAsyncWith,
    _StmtWith,
    _StmtClassDef,
    _ExprAwait,
    _ExprYield,
    _ExprYieldFrom,
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


_STATE_BACKEND_STMT_ALIASES = {
    "datastore_put": ("datastore", "put", "datastore_put"),
    "DatastorePut": ("datastore", "put", "datastore_put"),
    "datastore_get": ("datastore", "get", "datastore_get"),
    "DatastoreGet": ("datastore", "get", "datastore_get"),
    "datastore_exists": ("datastore", "exists", "datastore_exists"),
    "DatastoreExists": ("datastore", "exists", "datastore_exists"),
    "datastore_remove": ("datastore", "remove", "datastore_remove"),
    "DatastoreRemove": ("datastore", "remove", "datastore_remove"),
    "datastore_clear": ("datastore", "clear", "datastore_clear"),
    "DatastoreClear": ("datastore", "clear", "datastore_clear"),
    "file_write": ("file", "put", "file_write"),
    "FileWrite": ("file", "put", "file_write"),
    "file_read": ("file", "get", "file_read"),
    "FileRead": ("file", "get", "file_read"),
    "file_exists": ("file", "exists", "file_exists"),
    "FileExists": ("file", "exists", "file_exists"),
    "file_remove": ("file", "remove", "file_remove"),
    "FileRemove": ("file", "remove", "file_remove"),
    "file_clear": ("file", "clear", "file_clear"),
    "FileClear": ("file", "clear", "file_clear"),
    "sqlite_put": ("sqlite", "put", "sqlite_put"),
    "SqlitePut": ("sqlite", "put", "sqlite_put"),
    "sqlite_get": ("sqlite", "get", "sqlite_get"),
    "SqliteGet": ("sqlite", "get", "sqlite_get"),
    "sqlite_exists": ("sqlite", "exists", "sqlite_exists"),
    "SqliteExists": ("sqlite", "exists", "sqlite_exists"),
    "sqlite_remove": ("sqlite", "remove", "sqlite_remove"),
    "SqliteRemove": ("sqlite", "remove", "sqlite_remove"),
    "sqlite_clear": ("sqlite", "clear", "sqlite_clear"),
    "SqliteClear": ("sqlite", "clear", "sqlite_clear"),
    "room_put": ("room", "put", "room_put"),
    "RoomPut": ("room", "put", "room_put"),
    "room_get": ("room", "get", "room_get"),
    "RoomGet": ("room", "get", "room_get"),
    "room_exists": ("room", "exists", "room_exists"),
    "RoomExists": ("room", "exists", "room_exists"),
    "room_remove": ("room", "remove", "room_remove"),
    "RoomRemove": ("room", "remove", "room_remove"),
    "room_clear": ("room", "clear", "room_clear"),
    "RoomClear": ("room", "clear", "room_clear"),
    "encrypted_storage_put": ("encrypted", "put", "encrypted_storage_put"),
    "EncryptedStoragePut": ("encrypted", "put", "encrypted_storage_put"),
    "encrypted_storage_get": ("encrypted", "get", "encrypted_storage_get"),
    "EncryptedStorageGet": ("encrypted", "get", "encrypted_storage_get"),
    "encrypted_storage_exists": ("encrypted", "exists", "encrypted_storage_exists"),
    "EncryptedStorageExists": ("encrypted", "exists", "encrypted_storage_exists"),
    "encrypted_storage_remove": ("encrypted", "remove", "encrypted_storage_remove"),
    "EncryptedStorageRemove": ("encrypted", "remove", "encrypted_storage_remove"),
    "encrypted_storage_clear": ("encrypted", "clear", "encrypted_storage_clear"),
    "EncryptedStorageClear": ("encrypted", "clear", "encrypted_storage_clear"),
    "secure_storage_put": ("encrypted", "put", "secure_storage_put"),
    "SecureStoragePut": ("encrypted", "put", "secure_storage_put"),
    "secure_storage_get": ("encrypted", "get", "secure_storage_get"),
    "SecureStorageGet": ("encrypted", "get", "secure_storage_get"),
    "secure_storage_exists": ("encrypted", "exists", "secure_storage_exists"),
    "SecureStorageExists": ("encrypted", "exists", "secure_storage_exists"),
    "secure_storage_remove": ("encrypted", "remove", "secure_storage_remove"),
    "SecureStorageRemove": ("encrypted", "remove", "secure_storage_remove"),
    "secure_storage_clear": ("encrypted", "clear", "secure_storage_clear"),
    "SecureStorageClear": ("encrypted", "clear", "secure_storage_clear"),
}

_STATE_BACKEND_EXPR_ALIASES = {
    fn: (backend, op, canonical)
    for fn, (backend, op, canonical) in _STATE_BACKEND_STMT_ALIASES.items()
    if op in {"get", "exists"}
}


def _const_string_arg(expr, *, fn_name: str, arg_name: str):
    if not isinstance(expr, _ExprConst) or not isinstance(expr.value, str):
        raise RuntimeError(f"{fn_name} argument '{arg_name}' must be a constant string")
    return expr.value


def _const_reactive_value_arg(expr, *, fn_name: str, arg_name: str):
    if isinstance(expr, _ExprConst):
        if isinstance(expr.value, bool) or not isinstance(expr.value, (int, str)):
            raise RuntimeError(f"{fn_name} argument '{arg_name}' must be a constant string/int or symbol")
        return expr
    if isinstance(expr, (_ExprSymbol, _ExprReactiveGet)):
        return expr
    raise RuntimeError(f"{fn_name} argument '{arg_name}' must be a constant string/int or symbol")


def _const_int_bool_arg(expr, *, fn_name: str, arg_name: str):
    if not isinstance(expr, _ExprConst):
        raise RuntimeError(f"{fn_name} argument '{arg_name}' must be an integer/bool constant")
    value = expr.value
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return int(value)
    raise RuntimeError(f"{fn_name} argument '{arg_name}' must be an integer/bool constant")


def _const_int_arg(expr, *, fn_name: str, arg_name: str):
    if not isinstance(expr, _ExprConst) or not isinstance(expr.value, int) or isinstance(expr.value, bool):
        raise RuntimeError(f"{fn_name} argument '{arg_name}' must be a constant integer")
    return int(expr.value)


def _const_string_kwarg(call: ast.Call, *, fn_name: str, kw: str, default: str = "") -> str:
    for item in call.keywords or []:
        if item.arg == kw:
            parsed = _parse_expr(item.value)
            if not isinstance(parsed, _ExprConst) or not isinstance(parsed.value, str):
                raise RuntimeError(f"{fn_name} keyword '{kw}' must be a constant string")
            return parsed.value
    return default


def _parse_state_backend_stmt_call(fn, call):
    spec = _STATE_BACKEND_STMT_ALIASES.get(fn)
    if spec is None:
        return None
    backend, op, canonical_name = spec
    args = [_parse_expr(a) for a in call.args]
    if op == "put":
        if len(args) != 2:
            raise RuntimeError(
                f'{canonical_name} expects exactly 2 string arguments. Usage: {canonical_name}("key", "value")'
            )
        return _StmtStateBackendPut(
            backend,
            _const_string_arg(args[0], fn_name=canonical_name, arg_name="key"),
            _const_string_arg(args[1], fn_name=canonical_name, arg_name="value"),
        )
    if op == "get":
        if not (1 <= len(args) <= 2):
            raise RuntimeError(
                f'{canonical_name} expects 1 or 2 string arguments. Usage: {canonical_name}("key", "default")'
            )
        default_expr = args[1] if len(args) > 1 else _ExprConst("")
        return _StmtStateBackendGet(
            backend,
            _const_string_arg(args[0], fn_name=canonical_name, arg_name="key"),
            _const_string_arg(default_expr, fn_name=canonical_name, arg_name="default_value"),
        )
    if op == "exists":
        if len(args) != 1:
            raise RuntimeError(
                f'{canonical_name} expects exactly 1 string argument. Usage: {canonical_name}("key")'
            )
        return _StmtStateBackendExists(
            backend,
            _const_string_arg(args[0], fn_name=canonical_name, arg_name="key"),
        )
    if op == "remove":
        if len(args) != 1:
            raise RuntimeError(
                f'{canonical_name} expects exactly 1 string argument. Usage: {canonical_name}("key")'
            )
        return _StmtStateBackendRemove(
            backend,
            _const_string_arg(args[0], fn_name=canonical_name, arg_name="key"),
        )
    if op == "clear":
        if args:
            raise RuntimeError(f"{canonical_name} expects no arguments. Usage: {canonical_name}()")
        return _StmtStateBackendClear(backend)
    raise RuntimeError(f"Unsupported state backend op '{op}'")


def _parse_state_backend_expr_call(fn, node):
    spec = _STATE_BACKEND_EXPR_ALIASES.get(fn)
    if spec is None:
        return None
    backend, op, canonical_name = spec
    args = [_parse_expr(a) for a in node.args]
    if op == "get":
        if not (1 <= len(args) <= 2):
            raise RuntimeError(
                f'{canonical_name} expects 1 or 2 string arguments. Usage: {canonical_name}("key", "default")'
            )
        default_expr = args[1] if len(args) > 1 else _ExprConst("")
        return _ExprStateBackendGet(
            backend,
            _const_string_arg(args[0], fn_name=canonical_name, arg_name="key"),
            _const_string_arg(default_expr, fn_name=canonical_name, arg_name="default_value"),
        )
    if op == "exists":
        if len(args) != 1:
            raise RuntimeError(
                f'{canonical_name} expects exactly 1 string argument. Usage: {canonical_name}("key")'
            )
        return _ExprStateBackendExists(
            backend,
            _const_string_arg(args[0], fn_name=canonical_name, arg_name="key"),
        )
    raise RuntimeError(f"Unsupported state backend expr op '{op}'")


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
            if fn in STATEMENT_FN_BY_DOMAIN["motion"]:
                return _parse_animation_call(call)
            parsed_state_backend = _parse_state_backend_stmt_call(fn, call)
            if parsed_state_backend is not None:
                return parsed_state_backend
            if fn in STATEMENT_FN_BY_DOMAIN["hybrid"].intersection(
                {"observable", "Observable", "reactive_observable", "ReactiveObservable"}
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError(
                        'observable expects exactly 2 arguments. Usage: observable("name", "initial")'
                    )
                name = _const_string_arg(args[0], fn_name="observable", arg_name="name")
                initial = _const_reactive_value_arg(args[1], fn_name="observable", arg_name="initial")
                if not isinstance(initial, _ExprConst):
                    raise RuntimeError("observable argument 'initial' must be a constant string/int")
                return _StmtReactiveObservable(name, initial)
            if fn in STATEMENT_FN_BY_DOMAIN["hybrid"].intersection(
                {"set_observable", "SetObservable", "reactive_set", "ReactiveSet"}
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError(
                        'set_observable expects exactly 2 arguments. Usage: set_observable("name", value)'
                    )
                name = _const_string_arg(args[0], fn_name="set_observable", arg_name="name")
                value = _const_reactive_value_arg(args[1], fn_name="set_observable", arg_name="value")
                return _StmtReactiveSet(name, value)
            if fn in STATEMENT_FN_BY_DOMAIN["hybrid"].intersection(
                {"derived", "Derived", "reactive_derived", "ReactiveDerived"}
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (2 <= len(args) <= 4):
                    raise RuntimeError(
                        "derived expects 2 to 4 arguments. "
                        'Usage: derived("target", "source", "prefix", "suffix")'
                    )
                name = _const_string_arg(args[0], fn_name="derived", arg_name="name")
                source = _const_string_arg(args[1], fn_name="derived", arg_name="source")
                for kw in call.keywords or []:
                    if kw.arg not in {"prefix", "suffix"}:
                        raise RuntimeError(
                            f"derived does not support keyword '{kw.arg}'. Supported keywords: prefix, suffix"
                        )
                prefix = _const_string_kwarg(call, fn_name="derived", kw="prefix", default="")
                suffix = _const_string_kwarg(call, fn_name="derived", kw="suffix", default="")
                if len(args) > 2:
                    prefix = _const_string_arg(args[2], fn_name="derived", arg_name="prefix")
                if len(args) > 3:
                    suffix = _const_string_arg(args[3], fn_name="derived", arg_name="suffix")
                return _StmtReactiveDerived(name, source, prefix, suffix)
            if fn in STATEMENT_FN_BY_DOMAIN["hybrid"].intersection(
                {"listen", "Listen", "reactive_listen", "ReactiveListen"}
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError(
                        'listen expects exactly 2 string arguments. Usage: listen("name", "target_id")'
                    )
                name = _const_string_arg(args[0], fn_name="listen", arg_name="name")
                target_id = _const_string_arg(args[1], fn_name="listen", arg_name="target_id")
                return _StmtReactiveListen(name, target_id)
            if fn in STATEMENT_FN_BY_DOMAIN["hybrid"].intersection(
                {"bind_text", "BindText", "reactive_bind_text", "ReactiveBindText"}
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError(
                        'bind_text expects exactly 2 string arguments. Usage: bind_text("target_id", "name")'
                    )
                target_id = _const_string_arg(args[0], fn_name="bind_text", arg_name="target_id")
                name = _const_string_arg(args[1], fn_name="bind_text", arg_name="name")
                return _StmtReactiveBindText(target_id, name)
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
            if fn in ("pop_to_root", "PopToRoot"):
                if call.args:
                    raise RuntimeError("PopToRoot takes no arguments")
                from .ast import _StmtPopToRoot
                return _StmtPopToRoot()
            if fn in ("clear_stack", "ClearStack"):
                if call.args:
                    raise RuntimeError("ClearStack takes no arguments")
                from .ast import _StmtClearStack
                return _StmtClearStack()
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"open_url", "OpenUrl", "launch_url", "LaunchUrl", "url_launcher", "URLLauncher"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError('open_url expects exactly 1 string argument. Usage: open_url("https://...")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("open_url argument 'url' must be a constant string")
                return _StmtOpenUrl(args[0].value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {
                        "check_connectivity",
                        "CheckConnectivity",
                        "connectivity_check",
                        "ConnectivityCheck",
                        "is_connected",
                        "IsConnected",
                    }
                )
            ):
                if call.args:
                    raise RuntimeError("check_connectivity expects no arguments. Usage: check_connectivity()")
                return _StmtCheckConnectivity()
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {
                        "check_location",
                        "CheckLocation",
                        "check_location_enabled",
                        "CheckLocationEnabled",
                        "location_check",
                        "LocationCheck",
                        "location_enabled",
                        "LocationEnabled",
                        "is_location_enabled",
                        "IsLocationEnabled",
                    }
                )
            ):
                if call.args:
                    raise RuntimeError("check_location expects no arguments. Usage: check_location()")
                return _StmtCheckLocation()
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"check_permission", "CheckPermission", "permission_check", "PermissionCheck"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError(
                        'check_permission expects exactly 1 string argument. Usage: check_permission("android.permission.CAMERA")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("check_permission argument 'permission' must be a constant string")
                return _StmtCheckPermission(args[0].value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"clipboard_set", "ClipboardSet", "set_clipboard", "SetClipboard"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError(
                        'clipboard_set expects exactly 1 string argument. Usage: clipboard_set("value")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("clipboard_set argument 'text' must be a constant string")
                return _StmtClipboardSet(args[0].value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"share_text", "ShareText", "share", "Share"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (1 <= len(args) <= 2):
                    raise RuntimeError(
                        'share_text expects 1 or 2 string arguments. Usage: share_text("text", "Chooser Title")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("share_text argument 'text' must be a constant string")
                chooser_expr = args[1] if len(args) > 1 else _ExprConst("Share via")
                if not isinstance(chooser_expr, _ExprConst) or not isinstance(chooser_expr.value, str):
                    raise RuntimeError("share_text argument 'chooser_title' must be a constant string")
                return _StmtShareText(args[0].value, chooser_expr.value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"share_file", "ShareFile", "share_uri", "ShareUri"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (1 <= len(args) <= 3):
                    raise RuntimeError(
                        "share_file expects 1 to 3 string arguments. "
                        'Usage: share_file("content://...", "Share file via", "*/*")'
                    )
                uri = _const_string_arg(args[0], fn_name="share_file", arg_name="uri")
                chooser_expr = args[1] if len(args) > 1 else _ExprConst("Share file via")
                chooser_title = _const_string_arg(
                    chooser_expr,
                    fn_name="share_file",
                    arg_name="chooser_title",
                )
                mime_expr = args[2] if len(args) > 2 else _ExprConst("*/*")
                mime_type = _const_string_arg(
                    mime_expr,
                    fn_name="share_file",
                    arg_name="mime_type",
                )
                return _StmtShareFile(uri, chooser_title, mime_type)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"open_external", "OpenExternal", "open_uri", "OpenUri"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError(
                        'open_external expects exactly 1 string argument. Usage: open_external("scheme://...")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("open_external argument 'uri' must be a constant string")
                return _StmtOpenExternal(args[0].value)
            if fn == "android_start_activity":
                args = [_parse_expr(a) for a in call.args]
                if call.keywords:
                    raise RuntimeError(
                        "android_start_activity does not support keyword arguments. "
                        "Usage: android_start_activity(intent_expr)"
                    )
                if len(args) != 1:
                    raise RuntimeError(
                        "android_start_activity expects exactly 1 argument. "
                        "Usage: android_start_activity(intent_expr)"
                    )
                return _StmtAndroidStartActivity(args[0])
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"work_enqueue", "WorkEnqueue", "enqueue_work", "EnqueueWork"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (1 <= len(args) <= 2):
                    raise RuntimeError(
                        'work_enqueue expects 1 or 2 arguments. Usage: work_enqueue("work_name", delay_seconds)'
                    )
                name = _const_string_arg(args[0], fn_name="work_enqueue", arg_name="name")
                delay_expr = args[1] if len(args) > 1 else _ExprConst(0)
                delay_seconds = _const_int_arg(
                    delay_expr,
                    fn_name="work_enqueue",
                    arg_name="delay_seconds",
                )
                if delay_seconds < 0:
                    raise RuntimeError("work_enqueue argument 'delay_seconds' must be >= 0")
                return _StmtWorkEnqueue(name, delay_seconds)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"work_cancel", "WorkCancel", "cancel_work", "CancelWork"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError(
                        'work_cancel expects exactly 1 string argument. Usage: work_cancel("work_name")'
                    )
                name = _const_string_arg(args[0], fn_name="work_cancel", arg_name="name")
                return _StmtWorkCancel(name)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"alarm_schedule", "AlarmSchedule", "schedule_alarm", "ScheduleAlarm"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (1 <= len(args) <= 2):
                    raise RuntimeError(
                        'alarm_schedule expects 1 or 2 arguments. Usage: alarm_schedule("alarm_name", trigger_seconds)'
                    )
                name = _const_string_arg(args[0], fn_name="alarm_schedule", arg_name="name")
                trigger_expr = args[1] if len(args) > 1 else _ExprConst(0)
                trigger_seconds = _const_int_arg(
                    trigger_expr,
                    fn_name="alarm_schedule",
                    arg_name="trigger_seconds",
                )
                if trigger_seconds < 0:
                    raise RuntimeError("alarm_schedule argument 'trigger_seconds' must be >= 0")
                return _StmtAlarmSchedule(name, trigger_seconds)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"alarm_cancel", "AlarmCancel", "cancel_alarm", "CancelAlarm"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError(
                        'alarm_cancel expects exactly 1 string argument. Usage: alarm_cancel("alarm_name")'
                    )
                name = _const_string_arg(args[0], fn_name="alarm_cancel", arg_name="name")
                return _StmtAlarmCancel(name)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"job_schedule", "JobSchedule", "schedule_job", "ScheduleJob"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (1 <= len(args) <= 2):
                    raise RuntimeError(
                        "job_schedule expects 1 or 2 integer arguments. "
                        "Usage: job_schedule(job_id, delay_seconds)"
                    )
                job_id = _const_int_arg(args[0], fn_name="job_schedule", arg_name="job_id")
                if job_id <= 0:
                    raise RuntimeError("job_schedule argument 'job_id' must be > 0")
                delay_expr = args[1] if len(args) > 1 else _ExprConst(0)
                delay_seconds = _const_int_arg(
                    delay_expr,
                    fn_name="job_schedule",
                    arg_name="delay_seconds",
                )
                if delay_seconds < 0:
                    raise RuntimeError("job_schedule argument 'delay_seconds' must be >= 0")
                return _StmtJobSchedule(job_id, delay_seconds)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"job_cancel", "JobCancel", "cancel_job", "CancelJob"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError(
                        "job_cancel expects exactly 1 integer argument. Usage: job_cancel(job_id)"
                    )
                job_id = _const_int_arg(args[0], fn_name="job_cancel", arg_name="job_id")
                if job_id <= 0:
                    raise RuntimeError("job_cancel argument 'job_id' must be > 0")
                return _StmtJobCancel(job_id)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"web_set_policy", "WebSetPolicy", "web_policy", "WebPolicy"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) > 4:
                    raise RuntimeError(
                        "web_set_policy expects up to 4 integer/bool arguments. "
                        "Usage: web_set_policy(js_enabled, dom_storage, allow_file_access, allow_cleartext)"
                    )
                js_expr = args[0] if len(args) > 0 else _ExprConst(0)
                dom_expr = args[1] if len(args) > 1 else _ExprConst(0)
                file_expr = args[2] if len(args) > 2 else _ExprConst(0)
                cleartext_expr = args[3] if len(args) > 3 else _ExprConst(0)
                return _StmtWebSetPolicy(
                    _const_int_bool_arg(js_expr, fn_name="web_set_policy", arg_name="js_enabled"),
                    _const_int_bool_arg(dom_expr, fn_name="web_set_policy", arg_name="dom_storage"),
                    _const_int_bool_arg(
                        file_expr,
                        fn_name="web_set_policy",
                        arg_name="allow_file_access",
                    ),
                    _const_int_bool_arg(
                        cleartext_expr,
                        fn_name="web_set_policy",
                        arg_name="allow_cleartext",
                    ),
                )
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"web_load", "WebLoad", "open_web", "OpenWeb"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError(
                        'web_load expects exactly 1 string argument. Usage: web_load("https://...")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("web_load argument 'url' must be a constant string")
                return _StmtWebLoad(args[0].value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {
                        "web_add_js_bridge",
                        "WebAddJsBridge",
                        "web_register_js_bridge",
                        "WebRegisterJsBridge",
                    }
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError(
                        "web_add_js_bridge expects exactly 1 string argument. "
                        'Usage: web_add_js_bridge("ahnali_bridge")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("web_add_js_bridge argument 'bridge_name' must be a constant string")
                return _StmtWebAddJsBridge(args[0].value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"web_choose_file", "WebChooseFile", "web_file_chooser", "WebFileChooser"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) > 1:
                    raise RuntimeError(
                        'web_choose_file expects 0 or 1 string argument. Usage: web_choose_file("*/*")'
                    )
                mime_expr = args[0] if args else _ExprConst("*/*")
                if not isinstance(mime_expr, _ExprConst) or not isinstance(mime_expr.value, str):
                    raise RuntimeError("web_choose_file argument 'mime_type' must be a constant string")
                return _StmtWebChooseFile(mime_expr.value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"web_cookie_set", "WebCookieSet", "web_set_cookie", "WebSetCookie"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError(
                        'web_cookie_set expects exactly 2 string arguments. Usage: web_cookie_set("https://...", "k=v")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("web_cookie_set argument 'url' must be a constant string")
                if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                    raise RuntimeError("web_cookie_set argument 'cookie' must be a constant string")
                return _StmtWebCookieSet(args[0].value, args[1].value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {
                        "create_notification_channel",
                        "CreateNotificationChannel",
                        "notification_channel",
                        "NotificationChannel",
                    }
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError(
                        'create_notification_channel expects exactly 2 string arguments. '
                        'Usage: create_notification_channel("channel_id", "Channel Name")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("create_notification_channel argument 'channel_id' must be a constant string")
                if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                    raise RuntimeError(
                        "create_notification_channel argument 'channel_name' must be a constant string"
                    )
                return _StmtCreateNotificationChannel(args[0].value, args[1].value)
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"notify", "Notify", "send_notification", "SendNotification"}
                )
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (2 <= len(args) <= 3):
                    raise RuntimeError(
                        'notify expects 2 or 3 string arguments. '
                        'Usage: notify("Title", "Body", "channel_id")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("notify argument 'title' must be a constant string")
                if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                    raise RuntimeError("notify argument 'body' must be a constant string")
                channel_expr = args[2] if len(args) > 2 else _ExprConst("ahnali_default")
                if not isinstance(channel_expr, _ExprConst) or not isinstance(channel_expr.value, str):
                    raise RuntimeError("notify argument 'channel_id' must be a constant string")
                return _StmtNotify(args[0].value, args[1].value, channel_expr.value)
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
                "http_get_status",
                "HttpGetStatus",
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError('http_get_status expects exactly 1 string argument. Usage: http_get_status("https://...")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("http_get_status argument 'url' must be a constant string")
                return _StmtHttpGetStatus(args[0].value)
            if fn in (
                "http_get_error",
                "HttpGetError",
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError('http_get_error expects exactly 1 string argument. Usage: http_get_error("https://...")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("http_get_error argument 'url' must be a constant string")
                return _StmtHttpGetError(args[0].value)
            if fn in (
                "http_get_retry",
                "HttpGetRetry",
                "fetch_url_retry",
                "FetchUrlRetry",
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (3 <= len(args) <= 4):
                    raise RuntimeError(
                        'http_get_retry expects 3 or 4 arguments. '
                        'Usage: http_get_retry("https://...", retries, backoff_ms, "fallback")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("http_get_retry argument 'url' must be a constant string")
                if (
                    not isinstance(args[1], _ExprConst)
                    or not isinstance(args[1].value, int)
                    or isinstance(args[1].value, bool)
                ):
                    raise RuntimeError("http_get_retry argument 'retries' must be an integer constant")
                if (
                    not isinstance(args[2], _ExprConst)
                    or not isinstance(args[2].value, int)
                    or isinstance(args[2].value, bool)
                ):
                    raise RuntimeError("http_get_retry argument 'backoff_ms' must be an integer constant")
                default_expr = args[3] if len(args) > 3 else _ExprConst("")
                if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                    raise RuntimeError("http_get_retry argument 'default_value' must be a constant string")
                return _StmtHttpGetRetry(
                    args[0].value,
                    int(args[1].value),
                    int(args[2].value),
                    default_expr.value,
                )
            if fn in (
                "http_get_json_field",
                "HttpGetJsonField",
                "fetch_json_field",
                "FetchJsonField",
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 3:
                    raise RuntimeError(
                        'http_get_json_field expects exactly 3 string arguments. '
                        'Usage: http_get_json_field("https://...", "key", "fallback")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("http_get_json_field argument 'url' must be a constant string")
                if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                    raise RuntimeError("http_get_json_field argument 'key' must be a constant string")
                if not isinstance(args[2], _ExprConst) or not isinstance(args[2].value, str):
                    raise RuntimeError("http_get_json_field argument 'fallback' must be a constant string")
                return _StmtHttpGetJsonField(
                    args[0].value,
                    args[1].value,
                    args[2].value,
                )
            if fn in (
                "http_get_json_field_error",
                "HttpGetJsonFieldError",
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError(
                        'http_get_json_field_error expects exactly 2 string arguments. '
                        'Usage: http_get_json_field_error("https://...", "key")'
                    )
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("http_get_json_field_error argument 'url' must be a constant string")
                if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                    raise RuntimeError("http_get_json_field_error argument 'key' must be a constant string")
                return _StmtHttpGetJsonFieldError(
                    args[0].value,
                    args[1].value,
                )
            if fn in (
                "http_get_route",
                "HttpGetRoute",
                "http_get_with_handlers",
                "HttpGetWithHandlers",
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (3 <= len(args) <= 4):
                    raise RuntimeError(
                        'http_get_route expects 3 or 4 string arguments. '
                        'Usage: http_get_route("https://...", "success_btn", "failure_btn", "fallback")'
                    )
                for idx, label in ((0, "url"), (1, "success_target_id"), (2, "failure_target_id")):
                    if not isinstance(args[idx], _ExprConst) or not isinstance(args[idx].value, str):
                        raise RuntimeError(f"http_get_route argument '{label}' must be a constant string")
                default_expr = args[3] if len(args) > 3 else _ExprConst("")
                if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                    raise RuntimeError("http_get_route argument 'default_value' must be a constant string")
                return _StmtHttpGetRoute(
                    args[0].value,
                    args[1].value,
                    args[2].value,
                    default_expr.value,
                )
            if fn in (
                "http_get_route_async",
                "HttpGetRouteAsync",
                "http_get_with_handlers_async",
                "HttpGetWithHandlersAsync",
            ):
                args = [_parse_expr(a) for a in call.args]
                if not (3 <= len(args) <= 10):
                    raise RuntimeError(
                        "http_get_route_async expects 3 to 10 arguments. "
                        'Usage: http_get_route_async("https://...", "success_btn", "failure_btn", "fallback", "progress_btn", retries, timeout_ms, "GET", "headers", "body")'
                    )
                for idx, label in ((0, "url"), (1, "success_target_id"), (2, "failure_target_id")):
                    if not isinstance(args[idx], _ExprConst) or not isinstance(args[idx].value, str):
                        raise RuntimeError(f"http_get_route_async argument '{label}' must be a constant string")
                default_expr = args[3] if len(args) > 3 else _ExprConst("")
                if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                    raise RuntimeError("http_get_route_async argument 'default_value' must be a constant string")
                progress_expr = args[4] if len(args) > 4 else _ExprConst("")
                if not isinstance(progress_expr, _ExprConst) or not isinstance(progress_expr.value, str):
                    raise RuntimeError("http_get_route_async argument 'progress_target_id' must be a constant string")
                retries_expr = args[5] if len(args) > 5 else _ExprConst(0)
                if (
                    not isinstance(retries_expr, _ExprConst)
                    or not isinstance(retries_expr.value, int)
                    or isinstance(retries_expr.value, bool)
                ):
                    raise RuntimeError("http_get_route_async argument 'retries' must be an integer constant")
                timeout_expr = args[6] if len(args) > 6 else _ExprConst(8000)
                if (
                    not isinstance(timeout_expr, _ExprConst)
                    or not isinstance(timeout_expr.value, int)
                    or isinstance(timeout_expr.value, bool)
                ):
                    raise RuntimeError("http_get_route_async argument 'timeout_ms' must be an integer constant")
                method_expr = args[7] if len(args) > 7 else _ExprConst("GET")
                if not isinstance(method_expr, _ExprConst) or not isinstance(method_expr.value, str):
                    raise RuntimeError("http_get_route_async argument 'method' must be a constant string")
                headers_expr = args[8] if len(args) > 8 else _ExprConst("")
                if not isinstance(headers_expr, _ExprConst) or not isinstance(headers_expr.value, str):
                    raise RuntimeError("http_get_route_async argument 'headers' must be a constant string")
                body_expr = args[9] if len(args) > 9 else _ExprConst("")
                if not isinstance(body_expr, _ExprConst) or not isinstance(body_expr.value, str):
                    raise RuntimeError("http_get_route_async argument 'body' must be a constant string")
                return _StmtHttpGetRouteAsync(
                    args[0].value,
                    args[1].value,
                    args[2].value,
                    default_expr.value,
                    progress_expr.value,
                    int(retries_expr.value),
                    int(timeout_expr.value),
                    method_expr.value,
                    headers_expr.value,
                    body_expr.value,
                )
            if fn in ("http_async_cancel", "HttpAsyncCancel"):
                if len(call.args) > 1:
                    raise RuntimeError(
                        "http_async_cancel expects zero or one token argument. Usage: http_async_cancel() or http_async_cancel(token)"
                    )
                token_expr = _parse_expr(call.args[0]) if call.args else None
                return _StmtHttpAsyncCancel(token_expr)
            if fn in ("http_async_progress", "HttpAsyncProgress"):
                if len(call.args) > 1:
                    raise RuntimeError(
                        "http_async_progress expects zero or one token argument. Usage: http_async_progress() or http_async_progress(token)"
                    )
                token_expr = _parse_expr(call.args[0]) if call.args else None
                return _StmtHttpAsyncProgress(token_expr)
            if fn in ("http_async_error", "HttpAsyncError"):
                if len(call.args) > 1:
                    raise RuntimeError(
                        "http_async_error expects zero or one token argument. Usage: http_async_error() or http_async_error(token)"
                    )
                token_expr = _parse_expr(call.args[0]) if call.args else None
                return _StmtHttpAsyncError(token_expr)
            if fn in ("http_async_status", "HttpAsyncStatus"):
                if len(call.args) > 1:
                    raise RuntimeError(
                        "http_async_status expects zero or one token argument. Usage: http_async_status() or http_async_status(token)"
                    )
                token_expr = _parse_expr(call.args[0]) if call.args else None
                return _StmtHttpAsyncStatus(token_expr)
            if fn in ("http_async_body", "HttpAsyncBody"):
                if len(call.args) > 2:
                    raise RuntimeError(
                        'http_async_body expects up to 2 arguments. Usage: http_async_body(token, "fallback")'
                    )
                token_expr = _parse_expr(call.args[0]) if call.args else None
                fallback_expr = _parse_expr(call.args[1]) if len(call.args) > 1 else _ExprConst("")
                if not isinstance(fallback_expr, _ExprConst) or not isinstance(fallback_expr.value, str):
                    raise RuntimeError("http_async_body argument 'fallback' must be a constant string")
                return _StmtHttpAsyncBody(token_expr, fallback_expr.value)
            if fn in ("http_async_json_field", "HttpAsyncJsonField"):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 3:
                    raise RuntimeError(
                        'http_async_json_field expects exactly 3 arguments. Usage: http_async_json_field(token, "key", "fallback")'
                    )
                if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                    raise RuntimeError("http_async_json_field argument 'key' must be a constant string")
                if not isinstance(args[2], _ExprConst) or not isinstance(args[2].value, str):
                    raise RuntimeError("http_async_json_field argument 'fallback' must be a constant string")
                return _StmtHttpAsyncJsonField(args[0], args[1].value, args[2].value)
            if fn in ("http_async_json_field_error", "HttpAsyncJsonFieldError"):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 2:
                    raise RuntimeError(
                        'http_async_json_field_error expects exactly 2 arguments. Usage: http_async_json_field_error(token, "key")'
                    )
                if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                    raise RuntimeError("http_async_json_field_error argument 'key' must be a constant string")
                return _StmtHttpAsyncJsonFieldError(args[0], args[1].value)
            if fn in ("http_async_json_array_length", "HttpAsyncJsonArrayLength"):
                args = [_parse_expr(a) for a in call.args]
                if not (1 <= len(args) <= 2):
                    raise RuntimeError(
                        "http_async_json_array_length expects 1 or 2 arguments. Usage: http_async_json_array_length(token, fallback)"
                    )
                fallback_expr = args[1] if len(args) > 1 else _ExprConst(0)
                if (
                    not isinstance(fallback_expr, _ExprConst)
                    or not isinstance(fallback_expr.value, int)
                    or isinstance(fallback_expr.value, bool)
                ):
                    raise RuntimeError("http_async_json_array_length argument 'fallback' must be an integer constant")
                return _StmtHttpAsyncJsonArrayLength(args[0], int(fallback_expr.value))
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
                "storage_exists",
                "StorageExists",
                "has_storage",
                "HasStorage",
                "exists_storage",
                "ExistsStorage",
            ):
                args = [_parse_expr(a) for a in call.args]
                if len(args) != 1:
                    raise RuntimeError('storage_exists expects exactly 1 string argument. Usage: storage_exists("key")')
                if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                    raise RuntimeError("storage_exists argument 'key' must be a constant string")
                return _StmtStorageExists(args[0].value)
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
            if fn in (
                "storage_clear",
                "StorageClear",
                "clear_storage",
                "ClearStorage",
            ):
                if call.args:
                    raise RuntimeError("storage_clear expects no arguments. Usage: storage_clear()")
                return _StmtStorageClear()
            if fn in (
                STATEMENT_FN_BY_DOMAIN["capabilities"].intersection(
                    {"request_permissions", "request_permission", "RequestPermissions", "RequestPermission"}
                )
            ):
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
    if isinstance(stmt, ast.For):
        return _desugar_for_loop(stmt)
    if isinstance(stmt, ast.Try):
        return _parse_try_except(stmt)
    if isinstance(stmt, ast.FunctionDef):
        return _parse_function_def(stmt)
    if isinstance(stmt, ast.AsyncFunctionDef):
        return _parse_async_function_def(stmt)
    if isinstance(stmt, ast.AsyncFor):
        return _parse_async_for_stmt(stmt)
    if isinstance(stmt, ast.AsyncWith):
        return _parse_async_with_stmt(stmt)
    if isinstance(stmt, ast.With):
        return _parse_with_stmt(stmt)
    if isinstance(stmt, ast.ClassDef):
        return _parse_class_def(stmt)
    if isinstance(stmt, ast.Return):
        return _parse_return_stmt(stmt)
    raise RuntimeError(f"Unsupported statement: {ast.dump(stmt)}")


def _desugar_for_loop(stmt):
    """Desugar 'for target in range(n): body' into a while loop.

    Transforms:
        for i in range(n):
            body
    Into:
        i = 0
        while i < n:
            body
            i = i + 1

    Only supports 'for X in range(N)' where N is a constant integer.
    """
    if not isinstance(stmt.target, ast.Name):
        raise RuntimeError("for loop target must be a simple name")
    loop_var = stmt.target.id

    if not isinstance(stmt.iter, ast.Call):
        raise RuntimeError("for loop iter must be a range() call")
    if not isinstance(stmt.iter.func, ast.Name) or stmt.iter.func.id != "range":
        raise RuntimeError("for loop iter must be range()")
    if len(stmt.iter.args) != 1:
        raise RuntimeError("for loop range() must have exactly 1 argument (for i in range(n))")

    limit_expr = stmt.iter.args[0]
    if not isinstance(limit_expr, ast.Constant) or not isinstance(limit_expr.value, int):
        raise RuntimeError("for loop range() limit must be a constant integer")
    limit = limit_expr.value

    # Build: i = 0
    init_stmt = ast.Assign(
        targets=[ast.Name(id=loop_var, ctx=ast.Store())],
        value=ast.Constant(value=0),
    )

    # Build: while i < limit: body; i = i + 1
    cond = ast.Compare(
        left=ast.Name(id=loop_var, ctx=ast.Load()),
        ops=[ast.Lt()],
        comparators=[ast.Constant(value=limit)],
    )
    increment = ast.AugAssign(
        target=ast.Name(id=loop_var, ctx=ast.Store()),
        op=ast.Add(),
        value=ast.Constant(value=1),
    )
    while_node = ast.While(
        test=cond,
        body=stmt.body + [increment],
        orelse=[],
    )

    # Parse the desugared AST
    init = _parse_stmt(init_stmt)
    loop = _parse_stmt(while_node)
    if init is None:
        raise RuntimeError("Failed to parse for-loop initialization")
    if loop is None:
        raise RuntimeError("Failed to parse for-loop body")

    # Return as a sequence: init followed by the while loop
    return _StmtForLoop(init, loop)


def _parse_try_except(stmt):
    """Parse ast.Try into _StmtTryExcept.

    Only supports a single except clause with no 'as' binding.
    Finally blocks are not supported.
    """
    if not stmt.handlers:
        raise RuntimeError("try statement must have at least one except clause")
    if len(stmt.handlers) > 1:
        raise RuntimeError("only a single except clause is supported")
    if stmt.finalbody:
        raise RuntimeError("finally blocks are not supported")
    if stmt.orelse:
        raise RuntimeError("else clauses on try are not supported")

    handler = stmt.handlers[0]
    if handler.name is not None:
        raise RuntimeError("except ... as <name> is not supported; use a bare except")

    # Determine exception type
    if handler.type is None:
        exc_type = "java/lang/Exception"  # catchall
    elif isinstance(handler.type, ast.Name):
        exc_type = handler.type.id
    else:
        raise RuntimeError("except clause must be a simple exception type name")

    # Map Python exception names to Smali class descriptors
    exc_type_map = {
        "Exception": "Ljava/lang/Exception;",
        "RuntimeError": "Ljava/lang/RuntimeException;",
        "ValueError": "Ljava/lang/IllegalArgumentException;",
        "TypeError": "Ljava/lang/ClassCastException;",
        "IndexError": "Ljava/lang/IndexOutOfBoundsException;",
        "KeyError": "Ljava/util/NoSuchElementException;",
        "ZeroDivisionError": "Ljava/lang/ArithmeticException;",
        "IOException": "Ljava/io/IOException;",
    }
    dalvik_type = exc_type_map.get(exc_type)
    if dalvik_type is None:
        # Assume it's already a Smali descriptor or wrap it
        if exc_type.startswith("L") and exc_type.endswith(";"):
            dalvik_type = exc_type
        else:
            dalvik_type = f"Ljava/lang/{exc_type};"

    try_body = _parse_stmt_block(stmt.body)
    except_body = _parse_stmt_block(handler.body)

    return _StmtTryExcept(try_body, except_body, dalvik_type)


def _parse_return_stmt(stmt):
    """Parse ast.Return into _StmtReturn."""
    if stmt.value is None:
        return _StmtReturn(None)
    return _StmtReturn(_parse_expr(stmt.value))


def _parse_function_def(stmt):
    """Parse ast.FunctionDef into _StmtFunctionDef.

    All parameters default to int type. Return type is inferred from
    the presence of return statements with values.
    """
    param_names = [arg.arg for arg in stmt.args.args]
    body = _parse_stmt_block(stmt.body)
    return_type = None
    return _StmtFunctionDef(stmt.name, param_names, body, return_type)


def _parse_async_function_def(stmt):
    """Parse ast.AsyncFunctionDef into _StmtAsyncFunctionDef."""
    param_names = [arg.arg for arg in stmt.args.args]
    body = _parse_stmt_block(stmt.body)
    return_type = None
    return _StmtAsyncFunctionDef(stmt.name, param_names, body, return_type)


def _parse_async_for_stmt(stmt):
    """Parse ast.AsyncFor into _StmtAsyncFor."""
    if not isinstance(stmt.target, ast.Name):
        raise RuntimeError("async for loop target must be a simple name")
    target = stmt.target.id
    iterable = _parse_expr(stmt.iter)
    body = _parse_stmt_block(stmt.body)
    return _StmtAsyncFor(target, iterable, body)


def _parse_async_with_stmt(stmt):
    """Parse ast.AsyncWith into _StmtAsyncWith."""
    items = []
    for item in stmt.items:
        context_expr = _parse_expr(item.context_expr)
        if item.optional_vars is not None:
            if not isinstance(item.optional_vars, ast.Name):
                raise RuntimeError("async with target must be a simple name")
            as_var = item.optional_vars.id
        else:
            as_var = None
        items.append((context_expr, as_var))
    body = _parse_stmt_block(stmt.body)
    return _StmtAsyncWith(items, body)


def _parse_with_stmt(stmt):
    """Parse ast.With into _StmtWith."""
    items = []
    for item in stmt.items:
        context_expr = _parse_expr(item.context_expr)
        if item.optional_vars is not None:
            if not isinstance(item.optional_vars, ast.Name):
                raise RuntimeError("with target must be a simple name")
            as_var = item.optional_vars.id
        else:
            as_var = None
        items.append((context_expr, as_var))
    body = _parse_stmt_block(stmt.body)
    return _StmtWith(items, body)


def _parse_class_def(stmt):
    """Parse ast.ClassDef into _StmtClassDef."""
    bases = [base.id for base in stmt.bases if isinstance(base, ast.Name)]
    body = _parse_stmt_block(stmt.body)
    decorators = [d.id if isinstance(d, ast.Name) else None for d in stmt.decorator_list]
    metaclass = None
    for kw in stmt.keywords:
        if kw.arg == "metaclass" and isinstance(kw.value, ast.Name):
            metaclass = kw.value.id
    return _StmtClassDef(stmt.name, bases, body, decorators, metaclass)


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
        parsed_state_backend_expr = _parse_state_backend_expr_call(node.func.id, node)
        if parsed_state_backend_expr is not None:
            return parsed_state_backend_expr
        if node.func.id in EXPR_FN_BY_DOMAIN["hybrid"].intersection(
            {"observable_get", "ObservableGet", "reactive_get", "ReactiveGet"}
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 2):
                raise RuntimeError(
                    'observable_get expects 1 or 2 string arguments. Usage: observable_get("name", "fallback")'
                )
            name = _const_string_arg(args[0], fn_name="observable_get", arg_name="name")
            fallback_expr = args[1] if len(args) > 1 else _ExprConst("")
            fallback = _const_string_arg(
                fallback_expr,
                fn_name="observable_get",
                arg_name="fallback",
            )
            return _ExprReactiveGet(name, fallback)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"permission_granted", "PermissionGranted", "has_permission", "HasPermission"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'permission_granted expects exactly 1 string argument. Usage: permission_granted("android.permission.CAMERA")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("permission_granted argument 'permission' must be a constant string")
            return _ExprPermissionGranted(args[0].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"clipboard_get", "ClipboardGet", "get_clipboard", "GetClipboard"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) > 1:
                raise RuntimeError(
                    'clipboard_get expects 0 or 1 string argument. Usage: clipboard_get("fallback")'
                )
            fallback_expr = args[0] if len(args) > 0 else _ExprConst("")
            if not isinstance(fallback_expr, _ExprConst) or not isinstance(fallback_expr.value, str):
                raise RuntimeError("clipboard_get argument 'fallback' must be a constant string")
            return _ExprClipboardGet(fallback_expr.value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"share_text_result", "ShareTextResult"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 2):
                raise RuntimeError(
                    'share_text_result expects 1 or 2 string arguments. Usage: share_text_result("text", "Chooser Title")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("share_text_result argument 'text' must be a constant string")
            chooser_expr = args[1] if len(args) > 1 else _ExprConst("Share via")
            if not isinstance(chooser_expr, _ExprConst) or not isinstance(chooser_expr.value, str):
                raise RuntimeError("share_text_result argument 'chooser_title' must be a constant string")
            return _ExprShareTextResult(args[0].value, chooser_expr.value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"share_text_error", "ShareTextError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 2):
                raise RuntimeError(
                    'share_text_error expects 1 or 2 string arguments. Usage: share_text_error("text", "Chooser Title")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("share_text_error argument 'text' must be a constant string")
            chooser_expr = args[1] if len(args) > 1 else _ExprConst("Share via")
            if not isinstance(chooser_expr, _ExprConst) or not isinstance(chooser_expr.value, str):
                raise RuntimeError("share_text_error argument 'chooser_title' must be a constant string")
            return _ExprShareTextError(args[0].value, chooser_expr.value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"share_file_result", "ShareFileResult"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 3):
                raise RuntimeError(
                    "share_file_result expects 1 to 3 string arguments. "
                    'Usage: share_file_result("content://...", "Share file via", "*/*")'
                )
            uri = _const_string_arg(args[0], fn_name="share_file_result", arg_name="uri")
            chooser_expr = args[1] if len(args) > 1 else _ExprConst("Share file via")
            chooser_title = _const_string_arg(
                chooser_expr,
                fn_name="share_file_result",
                arg_name="chooser_title",
            )
            mime_expr = args[2] if len(args) > 2 else _ExprConst("*/*")
            mime_type = _const_string_arg(
                mime_expr,
                fn_name="share_file_result",
                arg_name="mime_type",
            )
            return _ExprShareFileResult(uri, chooser_title, mime_type)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"share_file_error", "ShareFileError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 3):
                raise RuntimeError(
                    "share_file_error expects 1 to 3 string arguments. "
                    'Usage: share_file_error("content://...", "Share file via", "*/*")'
                )
            uri = _const_string_arg(args[0], fn_name="share_file_error", arg_name="uri")
            chooser_expr = args[1] if len(args) > 1 else _ExprConst("Share file via")
            chooser_title = _const_string_arg(
                chooser_expr,
                fn_name="share_file_error",
                arg_name="chooser_title",
            )
            mime_expr = args[2] if len(args) > 2 else _ExprConst("*/*")
            mime_type = _const_string_arg(
                mime_expr,
                fn_name="share_file_error",
                arg_name="mime_type",
            )
            return _ExprShareFileError(uri, chooser_title, mime_type)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"open_external_result", "OpenExternalResult", "open_uri_result", "OpenUriResult"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'open_external_result expects exactly 1 string argument. Usage: open_external_result("scheme://...")'
                )
            uri = _const_string_arg(args[0], fn_name="open_external_result", arg_name="uri")
            return _ExprOpenExternalResult(uri)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"open_external_error", "OpenExternalError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'open_external_error expects exactly 1 string argument. Usage: open_external_error("scheme://...")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("open_external_error argument 'uri' must be a constant string")
            return _ExprOpenExternalError(args[0].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"deep_link_get", "DeepLinkGet", "get_deep_link", "GetDeepLink"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) > 1:
                raise RuntimeError(
                    'deep_link_get expects 0 or 1 string argument. Usage: deep_link_get("fallback://...")'
                )
            fallback_expr = args[0] if len(args) > 0 else _ExprConst("")
            if not isinstance(fallback_expr, _ExprConst) or not isinstance(fallback_expr.value, str):
                raise RuntimeError("deep_link_get argument 'fallback' must be a constant string")
            return _ExprDeepLinkGet(fallback_expr.value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"deep_link_error", "DeepLinkError", "get_deep_link_error", "GetDeepLinkError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if args:
                raise RuntimeError("deep_link_error expects no arguments. Usage: deep_link_error()")
            return _ExprDeepLinkError()
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"work_status", "WorkStatus"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'work_status expects exactly 1 string argument. Usage: work_status("work_name")'
                )
            return _ExprWorkStatus(
                _const_string_arg(args[0], fn_name="work_status", arg_name="name")
            )
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"work_error", "WorkError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'work_error expects exactly 1 string argument. Usage: work_error("work_name")'
                )
            return _ExprWorkError(
                _const_string_arg(args[0], fn_name="work_error", arg_name="name")
            )
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"alarm_status", "AlarmStatus"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'alarm_status expects exactly 1 string argument. Usage: alarm_status("alarm_name")'
                )
            return _ExprAlarmStatus(
                _const_string_arg(args[0], fn_name="alarm_status", arg_name="name")
            )
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"alarm_error", "AlarmError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'alarm_error expects exactly 1 string argument. Usage: alarm_error("alarm_name")'
                )
            return _ExprAlarmError(
                _const_string_arg(args[0], fn_name="alarm_error", arg_name="name")
            )
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"job_status", "JobStatus"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    "job_status expects exactly 1 integer argument. Usage: job_status(job_id)"
                )
            job_id = _const_int_arg(args[0], fn_name="job_status", arg_name="job_id")
            if job_id <= 0:
                raise RuntimeError("job_status argument 'job_id' must be > 0")
            return _ExprJobStatus(job_id)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"job_error", "JobError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    "job_error expects exactly 1 integer argument. Usage: job_error(job_id)"
                )
            job_id = _const_int_arg(args[0], fn_name="job_error", arg_name="job_id")
            if job_id <= 0:
                raise RuntimeError("job_error argument 'job_id' must be > 0")
            return _ExprJobError(job_id)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_load_result", "WebLoadResult"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'web_load_result expects exactly 1 string argument. Usage: web_load_result("https://...")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("web_load_result argument 'url' must be a constant string")
            return _ExprWebLoadResult(args[0].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_load_error", "WebLoadError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'web_load_error expects exactly 1 string argument. Usage: web_load_error("https://...")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("web_load_error argument 'url' must be a constant string")
            return _ExprWebLoadError(args[0].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_add_js_bridge_result", "WebAddJsBridgeResult"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    "web_add_js_bridge_result expects exactly 1 string argument. "
                    'Usage: web_add_js_bridge_result("ahnali_bridge")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError(
                    "web_add_js_bridge_result argument 'bridge_name' must be a constant string"
                )
            return _ExprWebAddJsBridgeResult(args[0].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_add_js_bridge_error", "WebAddJsBridgeError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    "web_add_js_bridge_error expects exactly 1 string argument. "
                    'Usage: web_add_js_bridge_error("ahnali_bridge")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError(
                    "web_add_js_bridge_error argument 'bridge_name' must be a constant string"
                )
            return _ExprWebAddJsBridgeError(args[0].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_choose_file_result", "WebChooseFileResult"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) > 1:
                raise RuntimeError(
                    'web_choose_file_result expects 0 or 1 string argument. Usage: web_choose_file_result("*/*")'
                )
            mime_expr = args[0] if args else _ExprConst("*/*")
            if not isinstance(mime_expr, _ExprConst) or not isinstance(mime_expr.value, str):
                raise RuntimeError("web_choose_file_result argument 'mime_type' must be a constant string")
            return _ExprWebChooseFileResult(mime_expr.value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_choose_file_error", "WebChooseFileError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) > 1:
                raise RuntimeError(
                    'web_choose_file_error expects 0 or 1 string argument. Usage: web_choose_file_error("*/*")'
                )
            mime_expr = args[0] if args else _ExprConst("*/*")
            if not isinstance(mime_expr, _ExprConst) or not isinstance(mime_expr.value, str):
                raise RuntimeError("web_choose_file_error argument 'mime_type' must be a constant string")
            return _ExprWebChooseFileError(mime_expr.value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_cookie_set_result", "WebCookieSetResult"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 2:
                raise RuntimeError(
                    'web_cookie_set_result expects exactly 2 string arguments. Usage: web_cookie_set_result("https://...", "k=v")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("web_cookie_set_result argument 'url' must be a constant string")
            if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                raise RuntimeError("web_cookie_set_result argument 'cookie' must be a constant string")
            return _ExprWebCookieSetResult(args[0].value, args[1].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_cookie_set_error", "WebCookieSetError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 2:
                raise RuntimeError(
                    'web_cookie_set_error expects exactly 2 string arguments. Usage: web_cookie_set_error("https://...", "k=v")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("web_cookie_set_error argument 'url' must be a constant string")
            if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                raise RuntimeError("web_cookie_set_error argument 'cookie' must be a constant string")
            return _ExprWebCookieSetError(args[0].value, args[1].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_cookie_get", "WebCookieGet", "web_get_cookie", "WebGetCookie"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 2):
                raise RuntimeError(
                    'web_cookie_get expects 1 or 2 string arguments. Usage: web_cookie_get("https://...", "fallback")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("web_cookie_get argument 'url' must be a constant string")
            fallback_expr = args[1] if len(args) > 1 else _ExprConst("")
            if not isinstance(fallback_expr, _ExprConst) or not isinstance(fallback_expr.value, str):
                raise RuntimeError("web_cookie_get argument 'fallback' must be a constant string")
            return _ExprWebCookieGet(args[0].value, fallback_expr.value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"web_cookie_get_error", "WebCookieGetError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError(
                    'web_cookie_get_error expects exactly 1 string argument. Usage: web_cookie_get_error("https://...")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("web_cookie_get_error argument 'url' must be a constant string")
            return _ExprWebCookieGetError(args[0].value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {
                    "location_enabled",
                    "LocationEnabled",
                    "is_location_enabled",
                    "IsLocationEnabled",
                    "check_location",
                    "CheckLocation",
                    "check_location_enabled",
                    "CheckLocationEnabled",
                    "location_check",
                    "LocationCheck",
                }
            )
        ):
            if node.args:
                raise RuntimeError("location_enabled expects no arguments. Usage: location_enabled()")
            return _ExprLocationEnabled()
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"notify_result", "NotifyResult"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (2 <= len(args) <= 3):
                raise RuntimeError(
                    'notify_result expects 2 or 3 string arguments. '
                    'Usage: notify_result("Title", "Body", "channel_id")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("notify_result argument 'title' must be a constant string")
            if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                raise RuntimeError("notify_result argument 'body' must be a constant string")
            channel_expr = args[2] if len(args) > 2 else _ExprConst("ahnali_default")
            if not isinstance(channel_expr, _ExprConst) or not isinstance(channel_expr.value, str):
                raise RuntimeError("notify_result argument 'channel_id' must be a constant string")
            return _ExprNotifyResult(args[0].value, args[1].value, channel_expr.value)
        if node.func.id in (
            EXPR_FN_BY_DOMAIN["capabilities"].intersection(
                {"notify_error", "NotifyError"}
            )
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (2 <= len(args) <= 3):
                raise RuntimeError(
                    'notify_error expects 2 or 3 string arguments. '
                    'Usage: notify_error("Title", "Body", "channel_id")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("notify_error argument 'title' must be a constant string")
            if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                raise RuntimeError("notify_error argument 'body' must be a constant string")
            channel_expr = args[2] if len(args) > 2 else _ExprConst("ahnali_default")
            if not isinstance(channel_expr, _ExprConst) or not isinstance(channel_expr.value, str):
                raise RuntimeError("notify_error argument 'channel_id' must be a constant string")
            return _ExprNotifyError(args[0].value, args[1].value, channel_expr.value)
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
            "http_get_status",
            "HttpGetStatus",
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError('http_get_status expects exactly 1 string argument. Usage: http_get_status("https://...")')
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("http_get_status argument 'url' must be a constant string")
            return _ExprHttpGetStatus(args[0].value)
        if node.func.id in (
            "http_get_error",
            "HttpGetError",
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError('http_get_error expects exactly 1 string argument. Usage: http_get_error("https://...")')
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("http_get_error argument 'url' must be a constant string")
            return _ExprHttpGetError(args[0].value)
        if node.func.id in (
            "http_get_retry",
            "HttpGetRetry",
            "fetch_url_retry",
            "FetchUrlRetry",
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (3 <= len(args) <= 4):
                raise RuntimeError(
                    'http_get_retry expects 3 or 4 arguments. '
                    'Usage: http_get_retry("https://...", retries, backoff_ms, "fallback")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("http_get_retry argument 'url' must be a constant string")
            if (
                not isinstance(args[1], _ExprConst)
                or not isinstance(args[1].value, int)
                or isinstance(args[1].value, bool)
            ):
                raise RuntimeError("http_get_retry argument 'retries' must be an integer constant")
            if (
                not isinstance(args[2], _ExprConst)
                or not isinstance(args[2].value, int)
                or isinstance(args[2].value, bool)
            ):
                raise RuntimeError("http_get_retry argument 'backoff_ms' must be an integer constant")
            default_expr = args[3] if len(args) > 3 else _ExprConst("")
            if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                raise RuntimeError("http_get_retry argument 'default_value' must be a constant string")
            return _ExprHttpGetRetry(
                args[0].value,
                int(args[1].value),
                int(args[2].value),
                default_expr.value,
            )
        if node.func.id in (
            "http_get_json_field",
            "HttpGetJsonField",
            "fetch_json_field",
            "FetchJsonField",
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 3:
                raise RuntimeError(
                    'http_get_json_field expects exactly 3 string arguments. '
                    'Usage: http_get_json_field("https://...", "key", "fallback")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("http_get_json_field argument 'url' must be a constant string")
            if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                raise RuntimeError("http_get_json_field argument 'key' must be a constant string")
            if not isinstance(args[2], _ExprConst) or not isinstance(args[2].value, str):
                raise RuntimeError("http_get_json_field argument 'fallback' must be a constant string")
            return _ExprHttpGetJsonField(
                args[0].value,
                args[1].value,
                args[2].value,
            )
        if node.func.id in (
            "http_get_json_field_error",
            "HttpGetJsonFieldError",
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 2:
                raise RuntimeError(
                    'http_get_json_field_error expects exactly 2 string arguments. '
                    'Usage: http_get_json_field_error("https://...", "key")'
                )
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("http_get_json_field_error argument 'url' must be a constant string")
            if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                raise RuntimeError("http_get_json_field_error argument 'key' must be a constant string")
            return _ExprHttpGetJsonFieldError(
                args[0].value,
                args[1].value,
            )
        if node.func.id in (
            "http_get_route_async",
            "HttpGetRouteAsync",
            "http_get_with_handlers_async",
            "HttpGetWithHandlersAsync",
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (3 <= len(args) <= 10):
                raise RuntimeError(
                    "http_get_route_async expects 3 to 10 arguments. "
                    'Usage: http_get_route_async("https://...", "success_btn", "failure_btn", "fallback", "progress_btn", retries, timeout_ms, "GET", "headers", "body")'
                )
            for idx, label in ((0, "url"), (1, "success_target_id"), (2, "failure_target_id")):
                if not isinstance(args[idx], _ExprConst) or not isinstance(args[idx].value, str):
                    raise RuntimeError(f"http_get_route_async argument '{label}' must be a constant string")
            default_expr = args[3] if len(args) > 3 else _ExprConst("")
            if not isinstance(default_expr, _ExprConst) or not isinstance(default_expr.value, str):
                raise RuntimeError("http_get_route_async argument 'default_value' must be a constant string")
            progress_expr = args[4] if len(args) > 4 else _ExprConst("")
            if not isinstance(progress_expr, _ExprConst) or not isinstance(progress_expr.value, str):
                raise RuntimeError("http_get_route_async argument 'progress_target_id' must be a constant string")
            retries_expr = args[5] if len(args) > 5 else _ExprConst(0)
            if (
                not isinstance(retries_expr, _ExprConst)
                or not isinstance(retries_expr.value, int)
                or isinstance(retries_expr.value, bool)
            ):
                raise RuntimeError("http_get_route_async argument 'retries' must be an integer constant")
            timeout_expr = args[6] if len(args) > 6 else _ExprConst(8000)
            if (
                not isinstance(timeout_expr, _ExprConst)
                or not isinstance(timeout_expr.value, int)
                or isinstance(timeout_expr.value, bool)
            ):
                raise RuntimeError("http_get_route_async argument 'timeout_ms' must be an integer constant")
            method_expr = args[7] if len(args) > 7 else _ExprConst("GET")
            if not isinstance(method_expr, _ExprConst) or not isinstance(method_expr.value, str):
                raise RuntimeError("http_get_route_async argument 'method' must be a constant string")
            headers_expr = args[8] if len(args) > 8 else _ExprConst("")
            if not isinstance(headers_expr, _ExprConst) or not isinstance(headers_expr.value, str):
                raise RuntimeError("http_get_route_async argument 'headers' must be a constant string")
            body_expr = args[9] if len(args) > 9 else _ExprConst("")
            if not isinstance(body_expr, _ExprConst) or not isinstance(body_expr.value, str):
                raise RuntimeError("http_get_route_async argument 'body' must be a constant string")
            return _ExprHttpGetRouteAsync(
                args[0].value,
                args[1].value,
                args[2].value,
                default_expr.value,
                progress_expr.value,
                int(retries_expr.value),
                int(timeout_expr.value),
                method_expr.value,
                headers_expr.value,
                body_expr.value,
            )
        if node.func.id in (
            "http_async_progress",
            "HttpAsyncProgress",
        ):
            if len(node.args) > 1:
                raise RuntimeError(
                    "http_async_progress expects zero or one token argument. Usage: http_async_progress() or http_async_progress(token)"
                )
            token_expr = _parse_expr(node.args[0]) if node.args else None
            return _ExprHttpAsyncProgress(token_expr)
        if node.func.id in (
            "http_async_error",
            "HttpAsyncError",
        ):
            if len(node.args) > 1:
                raise RuntimeError(
                    "http_async_error expects zero or one token argument. Usage: http_async_error() or http_async_error(token)"
                )
            token_expr = _parse_expr(node.args[0]) if node.args else None
            return _ExprHttpAsyncError(token_expr)
        if node.func.id in (
            "http_async_status",
            "HttpAsyncStatus",
        ):
            if len(node.args) > 1:
                raise RuntimeError(
                    "http_async_status expects zero or one token argument. Usage: http_async_status() or http_async_status(token)"
                )
            token_expr = _parse_expr(node.args[0]) if node.args else None
            return _ExprHttpAsyncStatus(token_expr)
        if node.func.id in (
            "http_async_body",
            "HttpAsyncBody",
        ):
            if len(node.args) > 2:
                raise RuntimeError(
                    'http_async_body expects up to 2 arguments. Usage: http_async_body(token, "fallback")'
                )
            token_expr = _parse_expr(node.args[0]) if node.args else None
            fallback_expr = _parse_expr(node.args[1]) if len(node.args) > 1 else _ExprConst("")
            if not isinstance(fallback_expr, _ExprConst) or not isinstance(fallback_expr.value, str):
                raise RuntimeError("http_async_body argument 'fallback' must be a constant string")
            return _ExprHttpAsyncBody(token_expr, fallback_expr.value)
        if node.func.id in (
            "http_async_json_field",
            "HttpAsyncJsonField",
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 3:
                raise RuntimeError(
                    'http_async_json_field expects exactly 3 arguments. Usage: http_async_json_field(token, "key", "fallback")'
                )
            if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                raise RuntimeError("http_async_json_field argument 'key' must be a constant string")
            if not isinstance(args[2], _ExprConst) or not isinstance(args[2].value, str):
                raise RuntimeError("http_async_json_field argument 'fallback' must be a constant string")
            return _ExprHttpAsyncJsonField(args[0], args[1].value, args[2].value)
        if node.func.id in (
            "http_async_json_field_error",
            "HttpAsyncJsonFieldError",
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 2:
                raise RuntimeError(
                    'http_async_json_field_error expects exactly 2 arguments. Usage: http_async_json_field_error(token, "key")'
                )
            if not isinstance(args[1], _ExprConst) or not isinstance(args[1].value, str):
                raise RuntimeError("http_async_json_field_error argument 'key' must be a constant string")
            return _ExprHttpAsyncJsonFieldError(args[0], args[1].value)
        if node.func.id in (
            "http_async_json_array_length",
            "HttpAsyncJsonArrayLength",
        ):
            args = [_parse_expr(a) for a in node.args]
            if not (1 <= len(args) <= 2):
                raise RuntimeError(
                    "http_async_json_array_length expects 1 or 2 arguments. Usage: http_async_json_array_length(token, fallback)"
                )
            fallback_expr = args[1] if len(args) > 1 else _ExprConst(0)
            if (
                not isinstance(fallback_expr, _ExprConst)
                or not isinstance(fallback_expr.value, int)
                or isinstance(fallback_expr.value, bool)
            ):
                raise RuntimeError("http_async_json_array_length argument 'fallback' must be an integer constant")
            return _ExprHttpAsyncJsonArrayLength(args[0], int(fallback_expr.value))
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
        if node.func.id in (
            "storage_exists",
            "StorageExists",
            "has_storage",
            "HasStorage",
            "exists_storage",
            "ExistsStorage",
        ):
            args = [_parse_expr(a) for a in node.args]
            if len(args) != 1:
                raise RuntimeError('storage_exists expects exactly 1 string argument. Usage: storage_exists("key")')
            if not isinstance(args[0], _ExprConst) or not isinstance(args[0].value, str):
                raise RuntimeError("storage_exists argument 'key' must be a constant string")
            return _ExprStorageExists(args[0].value)
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
    if isinstance(node, ast.List):
        return _ExprListLiteral([_parse_expr(elt) for elt in node.elts])
    if isinstance(node, ast.Dict):
        if len(node.keys) != len(node.values):
            raise RuntimeError("Invalid dict literal")
        return _ExprDictLiteral(
            [(_parse_expr(key), _parse_expr(value)) for key, value in zip(node.keys, node.values)]
        )
    if isinstance(node, ast.Set):
        return _ExprSetLiteral([_parse_expr(elt) for elt in node.elts])
    if isinstance(node, ast.Tuple):
        return _ExprTupleLiteral([_parse_expr(elt) for elt in node.elts])
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.keywords:
            raise RuntimeError("Method-call keyword arguments are not supported")
        recv = _parse_expr(node.func.value)
        args = [recv, *[_parse_expr(a) for a in node.args]]
        return _ExprCall(f"method:{node.func.attr}", args)
    if isinstance(node, ast.Await):
        value = _parse_expr(node.value)
        return _ExprAwait(value)
    if isinstance(node, ast.Yield):
        value = _parse_expr(node.value) if node.value else None
        return _ExprYield(value)
    if isinstance(node, ast.YieldFrom):
        value = _parse_expr(node.value)
        return _ExprYieldFrom(value)
    # Generic function call (user-defined or unknown)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        args = [_parse_expr(a) for a in node.args]
        return _ExprCall(node.func.id, args)
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
