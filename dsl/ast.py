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


class _ExprCall:
    """Generic function call (user-defined or unknown builtin)."""
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args


class _ExprListLiteral:
    def __init__(self, elements):
        self.elements = elements


class _ExprDictLiteral:
    def __init__(self, entries):
        self.entries = entries


class _ExprSetLiteral:
    def __init__(self, elements):
        self.elements = elements


class _ExprTupleLiteral:
    def __init__(self, elements):
        self.elements = elements


class _ExprStorageGet:
    def __init__(self, key, default_value):
        self.key = key
        self.default_value = default_value


class _ExprStorageExists:
    def __init__(self, key):
        self.key = key


class _ExprReactiveGet:
    def __init__(self, name, fallback=""):
        self.name = name
        self.fallback = fallback


class _ExprStateBackendGet:
    def __init__(self, backend, key, default_value):
        self.backend = backend
        self.key = key
        self.default_value = default_value


class _ExprStateBackendExists:
    def __init__(self, backend, key):
        self.backend = backend
        self.key = key


class _ExprLocationEnabled:
    def __init__(self):
        pass


class _ExprPermissionGranted:
    def __init__(self, permission):
        self.permission = permission


class _ExprClipboardGet:
    def __init__(self, fallback):
        self.fallback = fallback


class _ExprShareTextResult:
    def __init__(self, text, chooser_title):
        self.text = text
        self.chooser_title = chooser_title


class _ExprShareTextError:
    def __init__(self, text, chooser_title):
        self.text = text
        self.chooser_title = chooser_title


class _ExprShareFileResult:
    def __init__(self, uri, chooser_title, mime_type):
        self.uri = uri
        self.chooser_title = chooser_title
        self.mime_type = mime_type


class _ExprShareFileError:
    def __init__(self, uri, chooser_title, mime_type):
        self.uri = uri
        self.chooser_title = chooser_title
        self.mime_type = mime_type


class _ExprOpenExternalResult:
    def __init__(self, uri):
        self.uri = uri


class _ExprOpenExternalError:
    def __init__(self, uri):
        self.uri = uri


class _ExprDeepLinkGet:
    def __init__(self, fallback):
        self.fallback = fallback


class _ExprDeepLinkError:
    def __init__(self):
        pass


class _ExprWorkStatus:
    def __init__(self, name):
        self.name = name


class _ExprWorkError:
    def __init__(self, name):
        self.name = name


class _ExprAlarmStatus:
    def __init__(self, name):
        self.name = name


class _ExprAlarmError:
    def __init__(self, name):
        self.name = name


class _ExprJobStatus:
    def __init__(self, job_id):
        self.job_id = job_id


class _ExprJobError:
    def __init__(self, job_id):
        self.job_id = job_id


class _ExprWebLoadResult:
    def __init__(self, url):
        self.url = url


class _ExprWebLoadError:
    def __init__(self, url):
        self.url = url


class _ExprWebAddJsBridgeResult:
    def __init__(self, bridge_name):
        self.bridge_name = bridge_name


class _ExprWebAddJsBridgeError:
    def __init__(self, bridge_name):
        self.bridge_name = bridge_name


class _ExprWebChooseFileResult:
    def __init__(self, mime_type):
        self.mime_type = mime_type


class _ExprWebChooseFileError:
    def __init__(self, mime_type):
        self.mime_type = mime_type


class _ExprWebCookieSetResult:
    def __init__(self, url, cookie):
        self.url = url
        self.cookie = cookie


class _ExprWebCookieSetError:
    def __init__(self, url, cookie):
        self.url = url
        self.cookie = cookie


class _ExprWebCookieGet:
    def __init__(self, url, fallback):
        self.url = url
        self.fallback = fallback


class _ExprWebCookieGetError:
    def __init__(self, url):
        self.url = url


class _ExprNotifyResult:
    def __init__(self, title, body, channel_id):
        self.title = title
        self.body = body
        self.channel_id = channel_id


class _ExprNotifyError:
    def __init__(self, title, body, channel_id):
        self.title = title
        self.body = body
        self.channel_id = channel_id


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


class _ExprHttpGetRetry:
    def __init__(self, url, retries, backoff_ms, default_value):
        self.url = url
        self.retries = retries
        self.backoff_ms = backoff_ms
        self.default_value = default_value


class _ExprHttpGetJsonField:
    def __init__(self, url, key, fallback):
        self.url = url
        self.key = key
        self.fallback = fallback


class _ExprHttpGetJsonFieldError:
    def __init__(self, url, key):
        self.url = url
        self.key = key


class _ExprHttpGetRouteAsync:
    def __init__(
        self,
        url,
        success_target_id,
        failure_target_id,
        default_value="",
        progress_target_id="",
        retries=0,
        timeout_ms=8000,
        method="GET",
        headers="",
        body="",
    ):
        self.url = url
        self.success_target_id = success_target_id
        self.failure_target_id = failure_target_id
        self.default_value = default_value
        self.progress_target_id = progress_target_id
        self.retries = retries
        self.timeout_ms = timeout_ms
        self.method = method
        self.headers = headers
        self.body = body


class _ExprHttpAsyncProgress:
    def __init__(self, token=None):
        self.token = token


class _ExprHttpAsyncError:
    def __init__(self, token=None):
        self.token = token


class _ExprHttpAsyncStatus:
    def __init__(self, token=None):
        self.token = token


class _ExprHttpAsyncBody:
    def __init__(self, token=None, fallback=""):
        self.token = token
        self.fallback = fallback


class _ExprHttpAsyncJsonField:
    def __init__(self, token=None, key="", fallback=""):
        self.token = token
        self.key = key
        self.fallback = fallback


class _ExprHttpAsyncJsonFieldError:
    def __init__(self, token=None, key=""):
        self.token = token
        self.key = key


class _ExprHttpAsyncJsonArrayLength:
    def __init__(self, token=None, fallback=0):
        self.token = token
        self.fallback = fallback


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


class _StmtCheckLocation:
    def __init__(self):
        pass


class _StmtCheckPermission:
    def __init__(self, permission):
        self.permission = permission


class _StmtCreateNotificationChannel:
    def __init__(self, channel_id, channel_name):
        self.channel_id = channel_id
        self.channel_name = channel_name


class _StmtNotify:
    def __init__(self, title, body, channel_id):
        self.title = title
        self.body = body
        self.channel_id = channel_id


class _StmtClipboardSet:
    def __init__(self, text):
        self.text = text


class _StmtShareText:
    def __init__(self, text, chooser_title):
        self.text = text
        self.chooser_title = chooser_title


class _StmtShareFile:
    def __init__(self, uri, chooser_title, mime_type):
        self.uri = uri
        self.chooser_title = chooser_title
        self.mime_type = mime_type


class _StmtOpenExternal:
    def __init__(self, uri):
        self.uri = uri


class _StmtAndroidStartActivity:
    def __init__(self, intent):
        self.intent = intent


class _StmtWorkEnqueue:
    def __init__(self, name, delay_seconds):
        self.name = name
        self.delay_seconds = delay_seconds


class _StmtWorkCancel:
    def __init__(self, name):
        self.name = name


class _StmtAlarmSchedule:
    def __init__(self, name, trigger_seconds):
        self.name = name
        self.trigger_seconds = trigger_seconds


class _StmtAlarmCancel:
    def __init__(self, name):
        self.name = name


class _StmtJobSchedule:
    def __init__(self, job_id, delay_seconds):
        self.job_id = job_id
        self.delay_seconds = delay_seconds


class _StmtJobCancel:
    def __init__(self, job_id):
        self.job_id = job_id


class _StmtWebSetPolicy:
    def __init__(self, js_enabled, dom_storage, allow_file_access, allow_cleartext):
        self.js_enabled = js_enabled
        self.dom_storage = dom_storage
        self.allow_file_access = allow_file_access
        self.allow_cleartext = allow_cleartext


class _StmtWebLoad:
    def __init__(self, url):
        self.url = url


class _StmtWebAddJsBridge:
    def __init__(self, bridge_name):
        self.bridge_name = bridge_name


class _StmtWebChooseFile:
    def __init__(self, mime_type):
        self.mime_type = mime_type


class _StmtWebCookieSet:
    def __init__(self, url, cookie):
        self.url = url
        self.cookie = cookie


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


class _StmtStorageExists:
    def __init__(self, key):
        self.key = key


class _StmtStorageClear:
    def __init__(self):
        pass


class _StmtReactiveObservable:
    def __init__(self, name, initial):
        self.name = name
        self.initial = initial


class _StmtReactiveSet:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class _StmtReactiveDerived:
    def __init__(self, name, source, prefix="", suffix=""):
        self.name = name
        self.source = source
        self.prefix = prefix
        self.suffix = suffix


class _StmtReactiveListen:
    def __init__(self, name, target_id):
        self.name = name
        self.target_id = target_id


class _StmtReactiveBindText:
    def __init__(self, target_id, name):
        self.target_id = target_id
        self.name = name


class _StmtStateBackendPut:
    def __init__(self, backend, key, value):
        self.backend = backend
        self.key = key
        self.value = value


class _StmtStateBackendGet:
    def __init__(self, backend, key, default_value):
        self.backend = backend
        self.key = key
        self.default_value = default_value


class _StmtStateBackendRemove:
    def __init__(self, backend, key):
        self.backend = backend
        self.key = key


class _StmtStateBackendExists:
    def __init__(self, backend, key):
        self.backend = backend
        self.key = key


class _StmtStateBackendClear:
    def __init__(self, backend):
        self.backend = backend


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


class _StmtHttpGetRouteAsync:
    def __init__(
        self,
        url,
        success_target_id,
        failure_target_id,
        default_value="",
        progress_target_id="",
        retries=0,
        timeout_ms=8000,
        method="GET",
        headers="",
        body="",
    ):
        self.url = url
        self.success_target_id = success_target_id
        self.failure_target_id = failure_target_id
        self.default_value = default_value
        self.progress_target_id = progress_target_id
        self.retries = retries
        self.timeout_ms = timeout_ms
        self.method = method
        self.headers = headers
        self.body = body


class _StmtHttpGetRetry:
    def __init__(self, url, retries, backoff_ms, default_value):
        self.url = url
        self.retries = retries
        self.backoff_ms = backoff_ms
        self.default_value = default_value


class _StmtHttpGetJsonField:
    def __init__(self, url, key, fallback):
        self.url = url
        self.key = key
        self.fallback = fallback


class _StmtHttpGetJsonFieldError:
    def __init__(self, url, key):
        self.url = url
        self.key = key


class _StmtHttpAsyncCancel:
    def __init__(self, token=None):
        self.token = token


class _StmtHttpAsyncProgress:
    def __init__(self, token=None):
        self.token = token


class _StmtHttpAsyncError:
    def __init__(self, token=None):
        self.token = token


class _StmtHttpAsyncStatus:
    def __init__(self, token=None):
        self.token = token


class _StmtHttpAsyncBody:
    def __init__(self, token=None, fallback=""):
        self.token = token
        self.fallback = fallback


class _StmtHttpAsyncJsonField:
    def __init__(self, token=None, key="", fallback=""):
        self.token = token
        self.key = key
        self.fallback = fallback


class _StmtHttpAsyncJsonFieldError:
    def __init__(self, token=None, key=""):
        self.token = token
        self.key = key


class _StmtHttpAsyncJsonArrayLength:
    def __init__(self, token=None, fallback=0):
        self.token = token
        self.fallback = fallback


class _StmtNavigate:
    def __init__(self, target):
        self.target = target


class _StmtBack:
    def __init__(self):
        pass


class _StmtPopToRoot:
    def __init__(self):
        pass


class _StmtClearStack:
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


class _StmtForLoop:
    """Desugared for-loop: init_stmt + while_loop_stmt."""
    def __init__(self, init_stmt, while_loop_stmt):
        self.init_stmt = init_stmt
        self.while_loop_stmt = while_loop_stmt


class _StmtTryExcept:
    """try/except block. exception_type is the caught exception class name
    (e.g. 'java/lang/Exception'), try_body and except_body are stmt lists."""
    def __init__(self, try_body, except_body, exception_type="java/lang/Exception"):
        self.try_body = try_body
        self.except_body = except_body
        self.exception_type = exception_type


class _StmtFunctionDef:
    """User-defined function. params is a list of (name, type_desc) tuples."""
    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.params = params  # list of param names
        self.body = body
        self.return_type = return_type


class _StmtReturn:
    """Return from a function. value is None for void returns."""
    def __init__(self, value=None):
        self.value = value


class _StmtAsyncFunctionDef:
    """Async user-defined function. params is a list of param names."""
    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type


class _ExprAwait:
    """Await expression for coroutines."""
    def __init__(self, value):
        self.value = value


class _ExprYield:
    """Yield expression for generators."""
    def __init__(self, value):
        self.value = value


class _ExprYieldFrom:
    """Yield from expression for delegating to sub-generators."""
    def __init__(self, value):
        self.value = value


class _StmtAsyncFor:
    """Async for loop: async for item in iterable:"""
    def __init__(self, target, iterable, body):
        self.target = target
        self.iterable = iterable
        self.body = body


class _StmtAsyncWith:
    """Async with statement: async with context as item:"""
    def __init__(self, items, body):
        self.items = items
        self.body = body


class _StmtWith:
    """With statement: with context as item:"""
    def __init__(self, items, body):
        self.items = items
        self.body = body


class _ExprStarred:
    """Starred expression (*args or **kwargs in call)."""
    def __init__(self, value, is_kwargs=False):
        self.value = value
        self.is_kwargs = is_kwargs


class _ExprArguments:
    """Function arguments with *args and **kwargs support."""
    def __init__(self, args, vararg=None, kwarg=None):
        self.args = args
        self.vararg = vararg
        self.kwarg = kwarg


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
            _ExprStorageExists,
            _ExprStateBackendGet,
            _ExprStateBackendExists,
            _ExprLocationEnabled,
            _ExprPermissionGranted,
            _ExprClipboardGet,
            _ExprDeepLinkGet,
            _ExprDeepLinkError,
            _ExprWorkStatus,
            _ExprWorkError,
            _ExprAlarmStatus,
            _ExprAlarmError,
            _ExprJobStatus,
            _ExprJobError,
            _ExprShareTextResult,
            _ExprShareTextError,
            _ExprShareFileResult,
            _ExprShareFileError,
            _ExprOpenExternalResult,
            _ExprOpenExternalError,
            _ExprWebLoadResult,
            _ExprWebLoadError,
            _ExprWebAddJsBridgeResult,
            _ExprWebAddJsBridgeError,
            _ExprWebChooseFileResult,
            _ExprWebChooseFileError,
            _ExprWebCookieSetResult,
            _ExprWebCookieSetError,
            _ExprWebCookieGet,
            _ExprWebCookieGetError,
            _ExprNotifyResult,
            _ExprNotifyError,
            _ExprHttpGet,
            _ExprHttpGetStatus,
            _ExprHttpGetError,
            _ExprHttpGetRetry,
            _ExprHttpGetJsonField,
            _ExprHttpGetJsonFieldError,
            _ExprHttpGetRouteAsync,
            _ExprHttpAsyncProgress,
            _ExprHttpAsyncError,
            _ExprHttpAsyncStatus,
            _ExprHttpAsyncBody,
            _ExprHttpAsyncJsonField,
            _ExprHttpAsyncJsonFieldError,
            _ExprHttpAsyncJsonArrayLength,
            _ExprConst,
        ),
    ):
        return value
    return _ExprConst(value)
