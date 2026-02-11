"""
Anali is an ahead-of-time (AOT) compiler that translates a restricted, declarative, Python-like DSL into Dalvik bytecode.
All UI structure, layout, navigation, and state wiring are statically compiled features, resolved entirely at compile time
with no runtime interpretation. Alongside this, Anali ships a statically linked, capability-scoped support runtime: a small
set of precompiled Smali helper classes that provide access to Android platform services (audio, sensors, storage, WebView,
etc.). This runtime is not a framework engine but a link-time standard library, where only the capabilities referenced in
user code are included in the final APK. As a result, Anali applications have deterministic behavior, minimal binary size,
zero reflection, and native Android performance, while still exposing rich platform features through a strictly analyzable
DSL.
"""

from .ast import *
from .ir_helpers import *
from .ir_helpers import toast as _ir_toast
from .lowering.context import _PythonicContext
from .plugins import load_plugins
from .parser import _parse_handler_ast
from .capabilities import Caps, Perms
from .widgets import (
    _UIAppBar,
    _UIButton,
    _UIButtonBar,
    _UICard,
    _UIColumn,
    _UIContainer,
    _UIDivider,
    _UIFlatButton,
    _UIFloatingActionButton,
    _UIIcon,
    _UIIconButton,
    _UIImage,
    _UIPopupMenuButton,
    _UIProgressBar,
    _UIRaisedButton,
    _UIRadioGroup,
    _UIRow,
    _UIScreen,
    _UISimpleDialog,
    _UISnackbar,
    _UIToast,
    _UIText,
    _UIView,
    AppBar,
    Button,
    ButtonBar,
    Card,
    Checkbox,
    Column,
    Container,
    Divider,
    DropdownButton,
    FlatButton,
    FloatingActionButton,
    Icon,
    IconButton,
    Image,
    PopupMenuButton,
    Presets,
    ProgressBar,
    Radio,
    RadioGroup,
    RaisedButton,
    Row,
    Screen,
    SimpleDialog,
    Slider,
    State,
    Style,
    ColorState,
    Snackbar,
    Switch,
    Text,
    TextField,
    Theme,
    Toast,
    button,
    card,
    column,
    container,
    core,
    divider,
    dp,
    icon,
    image,
    sp,
    px,
    percent,
    fill,
    max_height,
    max_width,
    presets as presets_widget,
    radio,
    row,
    radio_group,
    screen,
    simple_dialog,
    snackbar,
    size,
    state as state_widget,
    style as style_widget,
    color_state,
    text,
    theme as theme_widget,
    toast as _ui_toast,
    progress_bar,
    view,
    wrap,
    wrap_height,
    wrap_width,
    View,
)
import importlib
import inspect
import builtins as _builtins


def toast(*args, **kwargs):
    """
    Dual-purpose toast helper:
    - UI DSL: toast("Hi", duration=0) -> _UIToast
    - IR helper: toast("t", var("ctx"), "Hi", duration=0) -> [IR stmts]
    """
    if len(args) >= 3 or "ctx" in kwargs or "name" in kwargs:
        return _ir_toast(*args, **kwargs)
    return _ui_toast(*args, **kwargs)


class _SimpleActivity:
    """
    High-level sugar for a single-activity app.
    Hides ctx/root/owner/var from users.
    """

    def __init__(self):
        self._items = []
        self._handlers = []
        self._handler_methods = []
        self._views = {}
        self._view_types = {}
        self._root_id = "root"
        self._counter_enabled = False
        self._counter_field = "counter"
        self._counter_label = "counter"
        self._counter_label_field = "counter_label"
        self._counter_init = 0

    def text(self, text, id="label"):
        self._views[id] = id
        self._view_types[id] = "text"
        self._items.append(("text", id, text))
        return self

    def button(self, text, id="button"):
        self._views[id] = id
        self._view_types[id] = "button"
        self._items.append(("button", id, text))
        return self

    def counter(self, initial=0, id="counter"):
        self._counter_enabled = True
        self._counter_field = id
        self._counter_label = id
        self._counter_label_field = f"{id}_label"
        self._counter_init = initial
        self.text(str(initial), id=id)
        return self

    def on_click_set_text(self, button_id, text):
        self._handlers.append(("set_text", button_id, text))
        return self

    def on_click_increment(self, button_id="button"):
        self._handlers.append(("increment", button_id, None))
        return self

    def build(self):
        body = []
        body.extend(linear_layout(self._root_id, var("ctx"), "vertical"))

        for kind, vid, tval in self._items:
            if kind == "text":
                body.extend(text_view(vid, var("ctx"), tval))
            elif kind == "button":
                body.extend(button_view(vid, var("ctx"), tval))
            body.append(add_view(var(self._root_id), var(vid)))

        for kind, button_id, text_value in self._handlers:
            handler_name = f"onClick_{button_id}"
            body.extend(on_click_view(var(button_id), handler_name=handler_name))

            owner = "Landroid/widget/Button;"

            if kind == "set_text":
                handler_body = [
                    call_stmt(
                        "setText",
                        args=[var("view"), const(text_value)],
                        return_type=None,
                        invoke_kind="virtual",
                        owner=owner,
                    ),
                    ret(),
                ]
            else:
                handler_body = [
                    assign("x", static_get(self._counter_field, "I")),
                    assign("x", binary("+", var("x"), const(1))),
                    static_set(self._counter_field, "I", var("x")),
                    assign(
                        "s",
                        call(
                            "valueOf",
                            args=[var("x")],
                            invoke_kind="static",
                            owner="Ljava/lang/String;",
                        ),
                    ),
                    assign(
                        "lbl",
                        static_get(self._counter_label_field, "Landroid/widget/TextView;"),
                    ),
                    call_stmt(
                        "setText",
                        args=[var("lbl"), var("s")],
                        return_type=None,
                        invoke_kind="virtual",
                        owner="Landroid/widget/TextView;",
                    ),
                    ret(),
                ]
            self._handler_methods.append((handler_name, handler_body))

        methods = [
            method(
                "main",
                params=["ctx"],
                param_types=["Landroid/app/Activity;"],
                return_type=None,
                body=[
                    *body,
                    *(
                        [
                            static_set(
                                self._counter_label_field,
                                "Landroid/widget/TextView;",
                                var(self._counter_label),
                            )
                        ]
                        if self._counter_enabled
                        else []
                    ),
                    set_content_view(var("ctx"), var(self._root_id)),
                    ret(),
                ],
            )
        ]

        fields = []
        if self._counter_enabled:
            fields.append(static_field(self._counter_field, "I", access="private static"))
            fields.append(
                static_field(self._counter_label_field, "Landroid/widget/TextView;", access="private static")
            )

        for name, hbody in self._handler_methods:
            methods.append(click_handler(name, hbody))

        return program(methods, fields=fields)


def simple_activity():
    return _SimpleActivity()


class _UISpec:
    def __init__(self, *items):
        self.items = items


class _OnClickSpec:
    def __init__(self, button_id, stmts):
        self.button_id = button_id
        self.stmts = stmts


class _ActivitySpec:
    def __init__(self, name, *parts):
        self.name = name
        self.parts = parts


class AppConfig:
    def __init__(
        self,
        *,
        package: str = "com.anali.preview",
        min_sdk: int = 21,
        target_sdk: int = 33,
        version_code: int = 1,
        version_name: str = "1.0",
        debuggable: bool = False,
        show_action_bar: bool = True,
        label: str | None = None,
        uses: list[str] | tuple[str, ...] | None = None,
        uninstall_first: bool = True,
        output_apk: str | None = None,
        keystore_path: str | None = None,
        keystore_alias: str = "androiddebugkey",
    ):
        self.package = package
        self.min_sdk = min_sdk
        self.target_sdk = target_sdk
        self.version_code = version_code
        self.version_name = version_name
        self.debuggable = debuggable
        self.show_action_bar = show_action_bar
        self.label = label
        self.uses = list(uses) if uses else []
        self.uninstall_first = uninstall_first
        self.output_apk = output_apk
        self.keystore_path = keystore_path
        self.keystore_alias = keystore_alias


class AppSpec:
    def __init__(self, activity_spec: _ActivitySpec, *, caller_module: str | None = None):
        self.activity_spec = activity_spec
        self.caller_module = caller_module

    def build(self):
        return _build_pythonic_app(self.activity_spec, self.caller_module)

    def run(self, **kwargs):
        from apk.toolchain import build_install_run

        app_config = _extract_app_config(self.activity_spec, self.caller_module)
        config_kwargs = {
            "application_id": app_config.package,
            "min_sdk": app_config.min_sdk,
            "target_sdk": app_config.target_sdk,
            "version_code": app_config.version_code,
            "version_name": app_config.version_name,
            "debuggable": app_config.debuggable,
            "show_action_bar": app_config.show_action_bar,
            "uninstall_first": app_config.uninstall_first,
            "output_apk": app_config.output_apk,
            "keystore_path": app_config.keystore_path,
            "keystore_alias": app_config.keystore_alias,
        }
        config_kwargs = {k: v for k, v in config_kwargs.items() if v is not None}
        config_kwargs.update(kwargs)
        return build_install_run(self.build(), **config_kwargs)


def app(activity_spec: _ActivitySpec):
    caller = inspect.stack()[1].frame.f_globals.get("__name__")
    return AppSpec(activity_spec, caller_module=caller)


def run(app_spec: AppSpec, **kwargs):
    return app_spec.run(**kwargs)


def activity(name, *parts):
    return _ActivitySpec(name, *parts)


def app_config(
    *,
    package: str = "com.anali.preview",
    min_sdk: int = 21,
    target_sdk: int = 33,
    version_code: int = 1,
    version_name: str = "1.0",
    debuggable: bool = False,
    show_action_bar: bool = True,
    label: str | None = None,
    uses: list[str] | tuple[str, ...] | None = None,
    uninstall_first: bool = True,
    output_apk: str | None = None,
    keystore_path: str | None = None,
    keystore_alias: str = "androiddebugkey",
):
    return AppConfig(
        package=package,
        min_sdk=min_sdk,
        target_sdk=target_sdk,
        version_code=version_code,
        version_name=version_name,
        debuggable=debuggable,
        show_action_bar=show_action_bar,
        label=label,
        uses=uses,
        uninstall_first=uninstall_first,
        output_apk=output_apk,
        keystore_path=keystore_path,
        keystore_alias=keystore_alias,
    )


def state(**kwargs):
    return State(**kwargs)


def ui(*items):
    return _UISpec(*items)


def on_click(button_id, stmts=None):
    if stmts is None:

        def decorator(fn):
            return _OnClickSpec(button_id, _parse_handler_ast(fn))

        return decorator
    if callable(stmts):
        return _OnClickSpec(button_id, _parse_handler_ast(stmts))
    return _OnClickSpec(button_id, stmts)


def on_click_map(mapping):
    specs = []
    for button_id, stmts in mapping.items():
        if callable(stmts):
            stmts = _parse_handler_ast(stmts)
        specs.append(_OnClickSpec(button_id, stmts))
    return specs


def Navigate(target):
    from .ast import _StmtNavigate
    return _StmtNavigate(target)


def navigate(target):
    return Navigate(target)


def Back():
    from .ast import _StmtBack
    return _StmtBack()


def back():
    return Back()


def Replace(target):
    from .ast import _StmtReplace
    return _StmtReplace(target)


def replace(target):
    return Replace(target)


def request_permissions(*permissions, request_code=0):
    from .ast import _StmtRequestPermissions
    if len(permissions) == 1 and isinstance(permissions[0], (list, tuple, set)):
        permissions = tuple(permissions[0])
    return _StmtRequestPermissions(list(permissions), request_code=request_code)


def request_permission(permission, request_code=0):
    return request_permissions(permission, request_code=request_code)


def style(**kwargs):
    return style_widget(**kwargs)


def theme(**kwargs):
    return theme_widget(**kwargs)


def presets(palette=None):
    return presets_widget(palette=palette)

def _resolve_plugins(activity_spec: _ActivitySpec, caller_module: str | None):
    plugins = []
    if caller_module:
        try:
            mod = importlib.import_module(caller_module)
        except Exception:
            mod = None
        if mod is not None and hasattr(mod, "APP_PLUGINS"):
            value = getattr(mod, "APP_PLUGINS")
            if isinstance(value, (list, tuple, set)):
                plugins.extend([str(p).strip() for p in value if str(p).strip()])
            elif isinstance(value, str):
                plugins.extend([p.strip() for p in value.split(",") if p.strip()])
    # preserve order, drop duplicates
    seen = set()
    out = []
    for name in plugins:
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _build_pythonic_app(activity_spec: _ActivitySpec, caller_module: str | None = None):
    state_spec = None
    ui_spec = None
    theme_spec = Theme()
    click_specs = []
    resources = {"app_name": "AnaliPreview"}
    label_locked = False

    for part in activity_spec.parts:
        if isinstance(part, (list, tuple)):
            for subpart in part:
                if isinstance(subpart, _OnClickSpec):
                    click_specs.append(subpart)
            continue
        if isinstance(part, State):
            state_spec = part
        elif isinstance(part, _UISpec):
            ui_spec = part
            for item in part.items:
                if isinstance(item, _UIAppBar) and getattr(item, "text", None):
                    if not label_locked:
                        resources["app_name"] = str(item.text)
        elif isinstance(part, AppConfig):
            if part.label:
                resources["app_name"] = str(part.label)
                label_locked = True
            # AppConfig is handled in AppSpec.run; ignore during build.
            pass
        elif isinstance(part, Theme):
            theme_spec = part
        elif isinstance(part, _OnClickSpec):
            click_specs.append(part)

    state_spec = state_spec or State()
    ui_spec = ui_spec or _UISpec()
    has_screens = any(isinstance(item, _UIScreen) for item in ui_spec.items)
    if has_screens:
        non_screens = [item for item in ui_spec.items if not isinstance(item, _UIScreen)]
        if non_screens:
            raise RuntimeError(
                "ui() cannot mix Screen(...) with non-screen items. "
                "Wrap all UI inside Screen(...) entries or remove Screen(...) entirely."
            )
        seen_names = set()
        dupes = set()
        for item in ui_spec.items:
            name = str(item.name)
            if name in seen_names:
                dupes.add(name)
            seen_names.add(name)
        if dupes:
            duped = ", ".join(sorted(dupes))
            raise RuntimeError(f"Screen names must be unique. Duplicate names: [{duped}]")

    if caller_module:
        try:
            mod = importlib.import_module(caller_module)
        except Exception:
            mod = None
        if mod is not None and hasattr(mod, "APP_LABEL"):
            resources["app_name"] = str(getattr(mod, "APP_LABEL"))
            label_locked = True

    plugin_names = _resolve_plugins(activity_spec, caller_module)
    registry = load_plugins(["core", *plugin_names])
    ctx = _PythonicContext(state_spec, ui_spec, theme_spec, registry=registry)
    if has_screens and state_spec.values:
        ctx._lint_warnings.append(
            "State values are global across Screens. Screen-local state is not yet supported."
        )
    program = ctx.build_program(click_specs, resources=resources)
    required_artifacts, jar_allowlist = registry.collect_deps(ui_spec.items, click_specs)
    program.required_artifacts = required_artifacts
    program.jar_allowlist = jar_allowlist
    app_cfg = _extract_app_config(activity_spec, caller_module)
    from .capabilities import (
        DEFAULT_CAPABILITY_REGISTRY,
        infer_permissions_from_handlers,
        infer_permissions_from_ui,
    )
    explicit_perms = DEFAULT_CAPABILITY_REGISTRY.resolve_permissions(app_cfg.uses)
    inferred_perms = [
        *infer_permissions_from_ui(ui_spec.items),
        *infer_permissions_from_handlers(click_specs),
    ]
    seen = set()
    merged = []
    for perm in [*explicit_perms, *inferred_perms]:
        if perm in seen:
            continue
        seen.add(perm)
        merged.append(perm)
    program.permissions = merged
    return program


def _install_units_into_builtins():
    # Make common DSL units/helpers available without explicit imports.
    for name in (
        "dp",
        "sp",
        "px",
        "percent",
        "fill",
        "wrap",
        "max_width",
        "max_height",
        "wrap_width",
        "wrap_height",
        "size",
    ):
        if name in globals():
            setattr(_builtins, name, globals()[name])


_install_units_into_builtins()


def _extract_app_config(activity_spec: _ActivitySpec, caller_module: str | None) -> AppConfig:
    def _normalize_uses(value):
        if value is None:
            return []
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(v).strip() for v in value if str(v).strip()]
        raise RuntimeError("uses must be a list or comma-separated string")

    def _merge_uses(base, extra):
        out = list(base or [])
        for item in extra or []:
            if item not in out:
                out.append(item)
        return out

    cfg = AppConfig()
    extra_uses = []
    for part in activity_spec.parts:
        if isinstance(part, AppConfig):
            cfg = part
    if caller_module:
        try:
            mod = importlib.import_module(caller_module)
        except Exception:
            mod = None
        if mod is not None:
            macro = getattr(mod, "APP_CONFIG", None)
            if isinstance(macro, dict):
                macro = dict(macro)
                macro_uses = macro.pop("uses", None)
                extra_uses.extend(_normalize_uses(macro_uses))
                cfg = AppConfig(**{**cfg.__dict__, **macro})
            for key, attr in (
                ("APP_PACKAGE", "package"),
                ("APP_MIN_SDK", "min_sdk"),
                ("APP_TARGET_SDK", "target_sdk"),
                ("APP_VERSION_CODE", "version_code"),
                ("APP_VERSION_NAME", "version_name"),
                ("APP_DEBUGGABLE", "debuggable"),
                ("APP_SHOW_ACTION_BAR", "show_action_bar"),
                ("APP_NO_ACTION_BAR", "show_action_bar"),
                ("APP_LABEL", "label"),
                ("APP_USES", "uses"),
                ("APP_UNINSTALL_FIRST", "uninstall_first"),
                ("APP_OUTPUT_APK", "output_apk"),
                ("APP_KEYSTORE_PATH", "keystore_path"),
                ("APP_KEYSTORE_ALIAS", "keystore_alias"),
            ):
                if hasattr(mod, key):
                    value = getattr(mod, key)
                    if key == "APP_NO_ACTION_BAR":
                        value = not bool(value)
                    if key == "APP_USES":
                        extra_uses.extend(_normalize_uses(value))
                    else:
                        setattr(cfg, attr, value)
    cfg.uses = _merge_uses(cfg.uses, extra_uses)
    return cfg
