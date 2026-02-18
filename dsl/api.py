"""
Ahnali is an ahead-of-time (AOT) compiler that translates a restricted, declarative, Python-like DSL into Dalvik bytecode.
All UI structure, layout, navigation, and state wiring are statically compiled features, resolved entirely at compile time
with no runtime interpretation. Alongside this, Ahnali ships a statically linked, capability-scoped support runtime: a small
set of precompiled Smali helper classes that provide access to Android platform services (audio, sensors, storage, WebView,
etc.). This runtime is not a framework engine but a link-time standard library, where only the capabilities referenced in
user code are included in the final APK. As a result, Ahnali applications have deterministic behavior, minimal binary size,
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
    _UIBottomNavigationView,
    _UICard,
    _UICoordinatorLayout,
    _UIColumn,
    _UIContainer,
    _UIDrawerLayout,
    _UIDivider,
    _UIFlatButton,
    _UIFragmentContainer,
    _UIFloatingActionButton,
    _UIFrame,
    _UIGridView,
    _UIHorizontalScrollView,
    _UIIcon,
    _UIIconButton,
    _UIImage,
    _UIListView,
    _UINavigationBar,
    _UINavigationRail,
    _UINestedScrollView,
    _UIPopupMenuButton,
    _UIProgressBar,
    _UIRaisedButton,
    _UIRecyclerView,
    _UIRadioGroup,
    _UIRow,
    _UIScrollView,
    _UIScreen,
    _UITabLayout,
    _UISimpleDialog,
    _UISlider,
    _UISnackbar,
    _UISwitch,
    _UIToast,
    _UIText,
    _UITextField,
    _UIViewPager,
    _UIView,
    AppBar,
    Button,
    ButtonBar,
    BottomNavigationView,
    Card,
    Checkbox,
    Column,
    CoordinatorLayout,
    Container,
    DrawerLayout,
    Divider,
    DropdownButton,
    FlatButton,
    FloatingActionButton,
    Frame,
    FragmentContainer,
    Gradient,
    GridView,
    HorizontalScrollView,
    Icon,
    IconButton,
    Image,
    ListView,
    NavigationBar,
    NavigationRail,
    NestedScrollView,
    PopupMenuButton,
    Presets,
    ProgressBar,
    Radio,
    RadioGroup,
    RaisedButton,
    RecyclerView,
    Row,
    Screen,
    ScrollView,
    SimpleDialog,
    Slider,
    Snackbar,
    State,
    Style,
    Switch,
    TabLayout,
    ColorState,
    Text,
    TextField,
    Theme,
    Toast,
    View,
    ViewPager,
    button,
    bottom_navigation_view,
    card,
    column,
    color_state,
    coordinator_layout,
    container,
    core,
    drawer_layout,
    divider,
    dp,
    fill,
    fragment_container,
    gradient,
    grid_view,
    horizontal_scroll_view,
    icon,
    image,
    list_view,
    max_height,
    max_width,
    navigation_bar,
    navigation_rail,
    nested_scroll_view,
    percent,
    progress_bar,
    px,
    radio,
    radio_group,
    recycler_view,
    row,
    screen,
    scroll_view,
    simple_dialog,
    size,
    snackbar,
    sp,
    state as state_widget,
    style as style_widget,
    tab_layout,
    text,
    theme as theme_widget,
    toast as _ui_toast,
    view,
    view_pager,
    wrap,
    wrap_height,
    wrap_width,
    frame,
    presets as presets_widget,
)
import importlib
import inspect
import builtins as _builtins
import re


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


class _EventSpec:
    def __init__(self, event_kind, target_id, stmts):
        self.event_kind = event_kind
        self.target_id = target_id
        self.stmts = stmts


class _OnClickSpec(_EventSpec):
    def __init__(self, button_id, stmts):
        super().__init__("click", button_id, stmts)
        self.button_id = button_id


class _LifecycleSpec:
    def __init__(self, lifecycle_kind, stmts):
        self.lifecycle_kind = lifecycle_kind
        self.stmts = stmts


class _ActivitySpec:
    def __init__(self, name, *parts):
        self.name = name
        self.parts = parts


def _sanitize_descriptor_part(value: str, *, fallback: str) -> str:
    text = str(value or "").strip()
    if not text:
        return fallback
    text = re.sub(r"[^A-Za-z0-9_$]", "_", text)
    if not text:
        return fallback
    if text[0].isdigit():
        text = "_" + text
    return text


def _runtime_class_descriptors(*, package: str, activity_name: str) -> dict[str, str]:
    package_parts = [
        _sanitize_descriptor_part(part, fallback="")
        for part in str(package or "").split(".")
    ]
    package_parts = [p for p in package_parts if p]
    if not package_parts:
        package_parts = ["com", "ahnali", "preview"]
    activity_part = _sanitize_descriptor_part(activity_name, fallback="MainActivity")
    package_path = "/".join(package_parts)
    wrapper = f"L{package_path}/{activity_part};"
    program = f"L{package_path}/{activity_part}Program;"
    return {
        "wrapper": wrapper,
        "program": program,
    }


class AppConfig:
    def __init__(
        self,
        *,
        package: str = "com.ahnali.preview",
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
        signing_mode: str = "debug",
        keystore_path: str | None = None,
        keystore_alias: str = "androiddebugkey",
        keystore_pass: str | None = None,
        key_pass: str | None = None,
        verify_reproducible: bool = False,
        deps: list[str] | tuple[str, ...] | None = None,
        auto_deps: bool = False,
        mode: str = "static",
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
        self.signing_mode = signing_mode
        self.keystore_path = keystore_path
        self.keystore_alias = keystore_alias
        self.keystore_pass = keystore_pass
        self.key_pass = key_pass
        self.verify_reproducible = bool(verify_reproducible)
        self.deps = list(deps) if deps else []
        self.auto_deps = bool(auto_deps)
        mode_norm = str(mode).strip().lower()
        if mode_norm not in {"static", "reactive"}:
            raise RuntimeError(
                f"app_config mode must be 'static' or 'reactive', got {mode!r}"
            )
        self.mode = mode_norm


class AppSpec:
    def __init__(self, activity_spec: _ActivitySpec, *, caller_module: str | None = None):
        self.activity_spec = activity_spec
        self.caller_module = caller_module

    def build(self):
        return _build_pythonic_app(self.activity_spec, self.caller_module)

    def run(self, **kwargs):
        from apk.toolchain import build_install_run

        app_config = _extract_app_config(self.activity_spec, self.caller_module)
        class_descs = _runtime_class_descriptors(
            package=app_config.package,
            activity_name=self.activity_spec.name,
        )
        frontend_ir = self.build()
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
            "signing_mode": app_config.signing_mode,
            "keystore_path": app_config.keystore_path,
            "keystore_alias": app_config.keystore_alias,
            "keystore_pass": app_config.keystore_pass,
            "key_pass": app_config.key_pass,
            "verify_reproducible": app_config.verify_reproducible,
        }
        config_kwargs = {k: v for k, v in config_kwargs.items() if v is not None}
        config_kwargs.setdefault("class_name", class_descs["program"])
        config_kwargs.setdefault("wrapper_class_desc", class_descs["wrapper"])
        config_kwargs.setdefault("wrapper_target_desc", class_descs["program"])
        config_kwargs.setdefault("emit_support_classes", False)
        config_kwargs.update(kwargs)
        return build_install_run(frontend_ir, **config_kwargs)


def app(activity_spec: _ActivitySpec):
    caller = inspect.stack()[1].frame.f_globals.get("__name__")
    return AppSpec(activity_spec, caller_module=caller)


def run(app_spec: AppSpec, **kwargs):
    return app_spec.run(**kwargs)


def activity(name, *parts):
    return _ActivitySpec(name, *parts)


def app_config(
    *,
    package: str = "com.ahnali.preview",
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
    signing_mode: str = "debug",
    keystore_path: str | None = None,
    keystore_alias: str = "androiddebugkey",
    keystore_pass: str | None = None,
    key_pass: str | None = None,
    verify_reproducible: bool = False,
    deps: list[str] | tuple[str, ...] | None = None,
    auto_deps: bool = False,
    mode: str = "static",
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
        signing_mode=signing_mode,
        keystore_path=keystore_path,
        keystore_alias=keystore_alias,
        keystore_pass=keystore_pass,
        key_pass=key_pass,
        verify_reproducible=verify_reproducible,
        deps=deps,
        auto_deps=auto_deps,
        mode=mode,
    )


def state(**kwargs):
    return State(**kwargs)


def ui(*items):
    return _UISpec(*items)


def _make_event_spec(event_kind, target_id, stmts=None):
    if stmts is None:
        def decorator(fn):
            return _EventSpec(event_kind, target_id, _parse_handler_ast(fn))
        return decorator
    if callable(stmts):
        return _EventSpec(event_kind, target_id, _parse_handler_ast(stmts))
    return _EventSpec(event_kind, target_id, stmts)


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


def on_change(view_id, stmts=None):
    return _make_event_spec("change", view_id, stmts)


def on_slider_change(view_id, stmts=None):
    return _make_event_spec("slider_change", view_id, stmts)


def on_long_click(view_id, stmts=None):
    return _make_event_spec("long_click", view_id, stmts)


def on_touch(view_id, stmts=None):
    return _make_event_spec("touch", view_id, stmts)


def on_double_tap(view_id, stmts=None):
    return _make_event_spec("double_tap", view_id, stmts)


def on_swipe(view_id, stmts=None):
    return _make_event_spec("swipe", view_id, stmts)


def on_scroll(view_id, stmts=None):
    return _make_event_spec("scroll", view_id, stmts)


def on_fling(view_id, stmts=None):
    return _make_event_spec("fling", view_id, stmts)


def on_pinch(view_id, stmts=None):
    return _make_event_spec("pinch", view_id, stmts)


def on_zoom(view_id, stmts=None):
    return _make_event_spec("zoom", view_id, stmts)


def on_rotate_gesture(view_id, stmts=None):
    return _make_event_spec("rotate_gesture", view_id, stmts)


def on_scale_gesture_detector(view_id, stmts=None):
    return _make_event_spec("scale_gesture_detector", view_id, stmts)


def on_drag(view_id, stmts=None):
    return _make_event_spec("drag", view_id, stmts)


def on_drop(view_id, stmts=None):
    return _make_event_spec("drop", view_id, stmts)


def on_editor_action(view_id, stmts=None):
    return _make_event_spec("editor_action", view_id, stmts)


def on_key(view_id, stmts=None):
    return _make_event_spec("key", view_id, stmts)


def on_text_change(view_id, stmts=None):
    return _make_event_spec("text_change", view_id, stmts)


def on_item_selected(view_id, stmts=None):
    return _make_event_spec("item_selected", view_id, stmts)


def on_menu_item_selected(view_id, stmts=None):
    return _make_event_spec("menu_item_selected", view_id, stmts)


def on_focus_change(view_id, stmts=None):
    return _make_event_spec("focus_change", view_id, stmts)


def _make_lifecycle_spec(lifecycle_kind, stmts=None):
    if stmts is None:
        def decorator(fn):
            return _LifecycleSpec(lifecycle_kind, _parse_handler_ast(fn))
        return decorator
    if callable(stmts):
        return _LifecycleSpec(lifecycle_kind, _parse_handler_ast(stmts))
    return _LifecycleSpec(lifecycle_kind, stmts)


def on_start(stmts=None):
    return _make_lifecycle_spec("start", stmts)


def on_resume(stmts=None):
    return _make_lifecycle_spec("resume", stmts)


def on_pause(stmts=None):
    return _make_lifecycle_spec("pause", stmts)


def on_stop(stmts=None):
    return _make_lifecycle_spec("stop", stmts)


def on_destroy(stmts=None):
    return _make_lifecycle_spec("destroy", stmts)


_INLINE_EVENT_ATTRS = (
    ("on_click", "click"),
    ("on_change", "change"),
    ("on_slider_change", "slider_change"),
    ("on_long_click", "long_click"),
    ("on_touch", "touch"),
    ("on_double_tap", "double_tap"),
    ("on_swipe", "swipe"),
    ("on_scroll", "scroll"),
    ("on_fling", "fling"),
    ("on_pinch", "pinch"),
    ("on_zoom", "zoom"),
    ("on_rotate_gesture", "rotate_gesture"),
    ("on_scale_gesture_detector", "scale_gesture_detector"),
    ("on_drag", "drag"),
    ("on_drop", "drop"),
    ("on_editor_action", "editor_action"),
    ("on_key", "key"),
    ("on_text_change", "text_change"),
    ("on_item_selected", "item_selected"),
    ("on_menu_item_selected", "menu_item_selected"),
    ("on_focus_change", "focus_change"),
)


def _normalize_inline_event_stmts(raw):
    if isinstance(raw, _EventSpec):
        stmts = raw.stmts
        if stmts is None:
            return []
        if isinstance(stmts, (list, tuple)):
            return list(stmts)
        return [stmts]
    if callable(raw):
        return _parse_handler_ast(raw)
    if isinstance(raw, (list, tuple)):
        return list(raw)
    return [raw]


def _collect_inline_event_specs(items):
    out = []

    def _walk(node):
        node_id = getattr(node, "id", None)
        if node_id:
            for attr_name, event_kind in _INLINE_EVENT_ATTRS:
                raw = getattr(node, attr_name, None)
                if raw is None:
                    continue
                if isinstance(raw, _EventSpec):
                    source_kind = getattr(raw, "event_kind", None)
                    source_target = getattr(raw, "target_id", getattr(raw, "button_id", None))
                    if source_kind and source_kind != event_kind:
                        raise RuntimeError(
                            f"Inline event '{attr_name}' on widget id '{node_id}' received "
                            f"event kind '{source_kind}', expected '{event_kind}'."
                        )
                    if source_target and source_target != node_id:
                        raise RuntimeError(
                            f"Inline event '{attr_name}' on widget id '{node_id}' received "
                            f"target id '{source_target}', expected '{node_id}'."
                        )
                stmts = _normalize_inline_event_stmts(raw)
                if event_kind == "click":
                    out.append(_OnClickSpec(node_id, stmts))
                else:
                    out.append(_EventSpec(event_kind, node_id, stmts))

        children = getattr(node, "items", None)
        if isinstance(children, (list, tuple)):
            for child in children:
                # Recurse only into widget-like nodes.
                if hasattr(child, "__dict__"):
                    _walk(child)

    for item in items or []:
        _walk(item)

    return out


def _merge_event_specs(explicit_specs, inline_specs):
    merged = []
    seen = {}
    def _canonical_event_kind(kind):
        # Keep slider alias deterministic with on_change collision semantics.
        if kind == "slider_change":
            return "change"
        # Gesture aliases share one OnTouch listener slot per target.
        if kind in {
            "double_tap",
            "swipe",
            "scroll",
            "fling",
            "pinch",
            "zoom",
            "rotate_gesture",
            "scale_gesture_detector",
        }:
            return "touch"
        # Drag/drop share one OnDrag listener slot per target.
        if kind == "drop":
            return "drag"
        return kind
    for origin, specs in (("explicit", explicit_specs or []), ("inline", inline_specs or [])):
        for spec in specs:
            event_kind = getattr(spec, "event_kind", "click")
            target_id = getattr(spec, "target_id", getattr(spec, "button_id", None))
            key = (_canonical_event_kind(event_kind), target_id)
            if key in seen:
                prev_origin = seen[key]
                raise RuntimeError(
                    f"Duplicate event binding for {event_kind} target '{target_id}' "
                    f"({prev_origin} and {origin}). Keep only one binding."
                )
            seen[key] = origin
            merged.append(spec)
    return merged


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


def PopToRoot():
    from .ast import _StmtPopToRoot
    return _StmtPopToRoot()


def pop_to_root():
    return PopToRoot()


def ClearStack():
    from .ast import _StmtClearStack
    return _StmtClearStack()


def clear_stack():
    return ClearStack()


def Replace(target):
    from .ast import _StmtReplace
    return _StmtReplace(target)


def replace(target):
    return Replace(target)


def Animate(
    target,
    property_name=None,
    value=None,
    *,
    duration=None,
    delay=None,
    interpolator=None,
    **properties,
):
    from .ast import _StmtAnimate

    if property_name is not None:
        if value is None:
            raise RuntimeError("Animate(property_name=...) requires a value")
        if properties:
            raise RuntimeError("Animate cannot mix property_name/value with property kwargs")
        properties = {property_name: value}
    if not properties:
        raise RuntimeError("Animate requires at least one animatable property")

    normalized = {}
    for key, raw in properties.items():
        norm_key = _normalize_anim_property_name(key)
        if norm_key not in {
            "rotate",
            "scale",
            "scale_x",
            "scale_y",
            "translate_x",
            "translate_y",
            "alpha",
            "elevation",
        }:
            raise RuntimeError(f"Unsupported animation property '{key}'")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise RuntimeError(f"Animation property '{key}' must be numeric")
        normalized[norm_key] = float(raw)

    if duration is not None:
        duration = int(duration)
    if delay is not None:
        delay = int(delay)
    if interpolator is not None:
        interpolator = str(interpolator)

    return _StmtAnimate(
        target=str(target),
        properties=normalized,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
    )


def animate(
    target,
    property_name=None,
    value=None,
    *,
    duration=None,
    delay=None,
    interpolator=None,
    **properties,
):
    return Animate(
        target,
        property_name,
        value,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
        **properties,
    )


def FadeIn(target, *, duration=None, delay=None, interpolator=None):
    return Animate(
        target,
        alpha=1.0,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
    )


def fade_in(target, *, duration=None, delay=None, interpolator=None):
    return FadeIn(target, duration=duration, delay=delay, interpolator=interpolator)


def FadeOut(target, *, duration=None, delay=None, interpolator=None):
    return Animate(
        target,
        alpha=0.0,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
    )


def fade_out(target, *, duration=None, delay=None, interpolator=None):
    return FadeOut(target, duration=duration, delay=delay, interpolator=interpolator)


def Rotate(target, value, *, duration=None, delay=None, interpolator=None):
    return Animate(
        target,
        rotate=value,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
    )


def rotate(target, value, *, duration=None, delay=None, interpolator=None):
    return Rotate(target, value, duration=duration, delay=delay, interpolator=interpolator)


def Scale(target, value=None, *, x=None, y=None, duration=None, delay=None, interpolator=None):
    props = {}
    if value is not None:
        props["scale"] = value
    if x is not None:
        props["scale_x"] = x
    if y is not None:
        props["scale_y"] = y
    if not props:
        raise RuntimeError("Scale requires value or x/y")
    return Animate(
        target,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
        **props,
    )


def scale(target, value=None, *, x=None, y=None, duration=None, delay=None, interpolator=None):
    return Scale(
        target,
        value=value,
        x=x,
        y=y,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
    )


def Translate(target, x=None, y=None, *, duration=None, delay=None, interpolator=None):
    props = {}
    if x is not None:
        props["translate_x"] = x
    if y is not None:
        props["translate_y"] = y
    if not props:
        raise RuntimeError("Translate requires x and/or y")
    return Animate(
        target,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
        **props,
    )


def translate(target, x=None, y=None, *, duration=None, delay=None, interpolator=None):
    return Translate(
        target,
        x=x,
        y=y,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
    )


def AnimateElevation(target, value, *, duration=None, delay=None, interpolator=None):
    return Animate(
        target,
        elevation=value,
        duration=duration,
        delay=delay,
        interpolator=interpolator,
    )


def animate_elevation(target, value, *, duration=None, delay=None, interpolator=None):
    return AnimateElevation(target, value, duration=duration, delay=delay, interpolator=interpolator)


def Sequence(*animations):
    from .ast import _StmtAnimationGroup

    if not animations:
        raise RuntimeError("Sequence requires at least one animation")
    return _StmtAnimationGroup("sequence", list(animations))


def sequence(*animations):
    return Sequence(*animations)


def Parallel(*animations):
    from .ast import _StmtAnimationGroup

    if not animations:
        raise RuntimeError("Parallel requires at least one animation")
    return _StmtAnimationGroup("parallel", list(animations))


def parallel(*animations):
    return Parallel(*animations)


def request_permissions(*permissions, request_code=0):
    from .ast import _StmtRequestPermissions
    if len(permissions) == 1 and isinstance(permissions[0], (list, tuple, set)):
        permissions = tuple(permissions[0])
    return _StmtRequestPermissions(list(permissions), request_code=request_code)


def request_permission(permission, request_code=0):
    return request_permissions(permission, request_code=request_code)


def _coerce_reactive_value(value, *, fn_name: str, arg_name: str, allow_symbol: bool = True):
    if allow_symbol and isinstance(value, (_ExprSymbol, _ExprReactiveGet)):
        return value
    if isinstance(value, _ExprConst):
        raw = value.value
        if isinstance(raw, bool) or not isinstance(raw, (int, str)):
            raise RuntimeError(
                f"{fn_name} argument '{arg_name}' must be string/int or symbol; got {raw!r} ({type(raw).__name__})"
            )
        return value
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise RuntimeError(
            f"{fn_name} argument '{arg_name}' must be string/int or symbol; got {value!r} ({type(value).__name__})"
        )
    return _ExprConst(value)


def observable(name: str, initial=""):
    return _StmtReactiveObservable(
        str(name),
        _coerce_reactive_value(
            initial,
            fn_name="observable",
            arg_name="initial",
            allow_symbol=False,
        ),
    )


def reactive_observable(name: str, initial=""):
    return observable(name, initial)


def set_observable(name: str, value):
    return _StmtReactiveSet(
        str(name),
        _coerce_reactive_value(value, fn_name="set_observable", arg_name="value"),
    )


def reactive_set(name: str, value):
    return set_observable(name, value)


def observable_get(name: str, fallback: str = ""):
    return _ExprReactiveGet(str(name), str(fallback))


def reactive_get(name: str, fallback: str = ""):
    return observable_get(name, fallback)


def derived(name: str, source: str, prefix: str = "", suffix: str = ""):
    return _StmtReactiveDerived(
        str(name),
        str(source),
        str(prefix),
        str(suffix),
    )


def reactive_derived(name: str, source: str, prefix: str = "", suffix: str = ""):
    return derived(name, source, prefix=prefix, suffix=suffix)


def listen(name: str, target_id: str):
    return _StmtReactiveListen(str(name), str(target_id))


def reactive_listen(name: str, target_id: str):
    return listen(name, target_id)


def bind_text(target_id: str, name: str):
    return _StmtReactiveBindText(str(target_id), str(name))


def reactive_bind_text(target_id: str, name: str):
    return bind_text(target_id, name)


def open_url(url: str):
    return _StmtOpenUrl(str(url))


def launch_url(url: str):
    return open_url(url)


def check_connectivity():
    return _StmtCheckConnectivity()


def connectivity_check():
    return check_connectivity()


def is_connected():
    return check_connectivity()


def check_location():
    return _StmtCheckLocation()


def check_location_enabled():
    return check_location()


def location_check():
    return check_location()


def location_enabled():
    return _ExprLocationEnabled()


def is_location_enabled():
    return location_enabled()


def check_permission(permission: str):
    return _StmtCheckPermission(str(permission))


def permission_check(permission: str):
    return check_permission(permission)


def permission_granted(permission: str):
    return _ExprPermissionGranted(str(permission))


def has_permission(permission: str):
    return permission_granted(permission)


def clipboard_set(text: str):
    return _StmtClipboardSet(str(text))


def set_clipboard(text: str):
    return clipboard_set(text)


def clipboard_get(fallback: str = ""):
    return _ExprClipboardGet(str(fallback))


def get_clipboard(fallback: str = ""):
    return clipboard_get(fallback)


def share_text(text: str, chooser_title: str = "Share via"):
    return _StmtShareText(str(text), str(chooser_title))


def share(text: str, chooser_title: str = "Share via"):
    return share_text(text, chooser_title)


def share_text_result(text: str, chooser_title: str = "Share via"):
    return _ExprShareTextResult(str(text), str(chooser_title))


def share_text_error(text: str, chooser_title: str = "Share via"):
    return _ExprShareTextError(str(text), str(chooser_title))


def open_external(uri: str):
    return _StmtOpenExternal(str(uri))


def open_uri(uri: str):
    return open_external(uri)


def open_external_error(uri: str):
    return _ExprOpenExternalError(str(uri))


def deep_link_get(fallback: str = ""):
    return _ExprDeepLinkGet(str(fallback))


def get_deep_link(fallback: str = ""):
    return deep_link_get(fallback)


def deep_link_error():
    return _ExprDeepLinkError()


def get_deep_link_error():
    return deep_link_error()


def web_set_policy(
    js_enabled: int | bool = 0,
    dom_storage: int | bool = 0,
    allow_file_access: int | bool = 0,
    allow_cleartext: int | bool = 0,
):
    return _StmtWebSetPolicy(
        int(js_enabled),
        int(dom_storage),
        int(allow_file_access),
        int(allow_cleartext),
    )


def web_policy(
    js_enabled: int | bool = 0,
    dom_storage: int | bool = 0,
    allow_file_access: int | bool = 0,
    allow_cleartext: int | bool = 0,
):
    return web_set_policy(js_enabled, dom_storage, allow_file_access, allow_cleartext)


def web_load(url: str):
    return _StmtWebLoad(str(url))


def open_web(url: str):
    return web_load(url)


def web_load_result(url: str):
    return _ExprWebLoadResult(str(url))


def web_load_error(url: str):
    return _ExprWebLoadError(str(url))


def web_add_js_bridge(bridge_name: str):
    return _StmtWebAddJsBridge(str(bridge_name))


def web_register_js_bridge(bridge_name: str):
    return web_add_js_bridge(bridge_name)


def web_add_js_bridge_result(bridge_name: str):
    return _ExprWebAddJsBridgeResult(str(bridge_name))


def web_add_js_bridge_error(bridge_name: str):
    return _ExprWebAddJsBridgeError(str(bridge_name))


def web_choose_file(mime_type: str = "*/*"):
    return _StmtWebChooseFile(str(mime_type))


def web_file_chooser(mime_type: str = "*/*"):
    return web_choose_file(mime_type)


def web_choose_file_result(mime_type: str = "*/*"):
    return _ExprWebChooseFileResult(str(mime_type))


def web_choose_file_error(mime_type: str = "*/*"):
    return _ExprWebChooseFileError(str(mime_type))


def web_cookie_set(url: str, cookie: str):
    return _StmtWebCookieSet(str(url), str(cookie))


def web_set_cookie(url: str, cookie: str):
    return web_cookie_set(url, cookie)


def web_cookie_set_result(url: str, cookie: str):
    return _ExprWebCookieSetResult(str(url), str(cookie))


def web_cookie_set_error(url: str, cookie: str):
    return _ExprWebCookieSetError(str(url), str(cookie))


def web_cookie_get(url: str, fallback: str = ""):
    return _ExprWebCookieGet(str(url), str(fallback))


def web_get_cookie(url: str, fallback: str = ""):
    return web_cookie_get(url, fallback)


def web_cookie_get_error(url: str):
    return _ExprWebCookieGetError(str(url))


def create_notification_channel(channel_id: str, channel_name: str):
    return _StmtCreateNotificationChannel(str(channel_id), str(channel_name))


def notification_channel(channel_id: str, channel_name: str):
    return create_notification_channel(channel_id, channel_name)


def notify(title: str, body: str, channel_id: str = "ahnali_default"):
    return _StmtNotify(str(title), str(body), str(channel_id))


def send_notification(title: str, body: str, channel_id: str = "ahnali_default"):
    return notify(title, body, channel_id)


def notify_result(title: str, body: str, channel_id: str = "ahnali_default"):
    return _ExprNotifyResult(str(title), str(body), str(channel_id))


def notify_error(title: str, body: str, channel_id: str = "ahnali_default"):
    return _ExprNotifyError(str(title), str(body), str(channel_id))


def http_get(url: str, default_value: str = ""):
    return _ExprHttpGet(str(url), str(default_value))


def fetch_url(url: str, default_value: str = ""):
    return http_get(url, default_value)


def http_get_status(url: str):
    return _ExprHttpGetStatus(str(url))


def http_get_error(url: str):
    return _ExprHttpGetError(str(url))


def http_get_retry(url: str, retries: int, backoff_ms: int, default_value: str = ""):
    return _ExprHttpGetRetry(str(url), int(retries), int(backoff_ms), str(default_value))


def fetch_url_retry(url: str, retries: int, backoff_ms: int, default_value: str = ""):
    return http_get_retry(url, retries, backoff_ms, default_value)


def http_get_json_field(url: str, key: str, fallback: str):
    return _ExprHttpGetJsonField(str(url), str(key), str(fallback))


def fetch_json_field(url: str, key: str, fallback: str):
    return http_get_json_field(url, key, fallback)


def http_get_json_field_error(url: str, key: str):
    return _ExprHttpGetJsonFieldError(str(url), str(key))


def http_get_route(
    url: str,
    success_target_id: str,
    failure_target_id: str,
    default_value: str = "",
):
    return _StmtHttpGetRoute(
        str(url),
        str(success_target_id),
        str(failure_target_id),
        str(default_value),
    )


def http_get_with_handlers(
    url: str,
    success_target_id: str,
    failure_target_id: str,
    default_value: str = "",
):
    return http_get_route(url, success_target_id, failure_target_id, default_value)


def http_get_route_async(
    url: str,
    success_target_id: str,
    failure_target_id: str,
    default_value: str = "",
    progress_target_id: str = "",
    retries: int = 0,
    timeout_ms: int = 8000,
    method: str = "GET",
    headers: str = "",
    body: str = "",
):
    return _StmtHttpGetRouteAsync(
        str(url),
        str(success_target_id),
        str(failure_target_id),
        str(default_value),
        str(progress_target_id),
        int(retries),
        int(timeout_ms),
        str(method),
        str(headers),
        str(body),
    )


def http_get_with_handlers_async(
    url: str,
    success_target_id: str,
    failure_target_id: str,
    default_value: str = "",
    progress_target_id: str = "",
    retries: int = 0,
    timeout_ms: int = 8000,
    method: str = "GET",
    headers: str = "",
    body: str = "",
):
    return http_get_route_async(
        url,
        success_target_id,
        failure_target_id,
        default_value,
        progress_target_id,
        retries,
        timeout_ms,
        method,
        headers,
        body,
    )


def http_async_cancel(token=None):
    return _StmtHttpAsyncCancel(token)


def http_async_progress(token=None):
    return _ExprHttpAsyncProgress(token)


def http_async_error(token=None):
    return _ExprHttpAsyncError(token)


def http_async_status(token=None):
    return _ExprHttpAsyncStatus(token)


def http_async_body(token=None, fallback: str = ""):
    return _ExprHttpAsyncBody(token, str(fallback))


def http_async_json_field(token, key: str, fallback: str):
    return _ExprHttpAsyncJsonField(token, str(key), str(fallback))


def http_async_json_field_error(token, key: str):
    return _ExprHttpAsyncJsonFieldError(token, str(key))


def http_async_json_array_length(token, fallback: int = 0):
    return _ExprHttpAsyncJsonArrayLength(token, int(fallback))


def storage_put(key: str, value: str):
    return _StmtStoragePut(str(key), str(value))


def set_storage(key: str, value: str):
    return storage_put(key, value)


def save_storage(key: str, value: str):
    return storage_put(key, value)


def storage_get(key: str, default_value: str = ""):
    return _ExprStorageGet(str(key), str(default_value))


def storage_exists(key: str):
    return _ExprStorageExists(str(key))


def get_storage(key: str, default_value: str = ""):
    return storage_get(key, default_value)


def load_storage(key: str, default_value: str = ""):
    return storage_get(key, default_value)


def has_storage(key: str):
    return storage_exists(key)


def exists_storage(key: str):
    return storage_exists(key)


def storage_remove(key: str):
    return _StmtStorageRemove(str(key))


def remove_storage(key: str):
    return storage_remove(key)


def delete_storage(key: str):
    return storage_remove(key)


def storage_clear():
    return _StmtStorageClear()


def clear_storage():
    return storage_clear()


def datastore_put(key: str, value: str):
    return _StmtStateBackendPut("datastore", str(key), str(value))


def datastore_get(key: str, default_value: str = ""):
    return _ExprStateBackendGet("datastore", str(key), str(default_value))


def datastore_exists(key: str):
    return _ExprStateBackendExists("datastore", str(key))


def datastore_remove(key: str):
    return _StmtStateBackendRemove("datastore", str(key))


def datastore_clear():
    return _StmtStateBackendClear("datastore")


def file_write(path: str, value: str):
    return _StmtStateBackendPut("file", str(path), str(value))


def file_read(path: str, default_value: str = ""):
    return _ExprStateBackendGet("file", str(path), str(default_value))


def file_exists(path: str):
    return _ExprStateBackendExists("file", str(path))


def file_remove(path: str):
    return _StmtStateBackendRemove("file", str(path))


def file_clear():
    return _StmtStateBackendClear("file")


def sqlite_put(key: str, value: str):
    return _StmtStateBackendPut("sqlite", str(key), str(value))


def sqlite_get(key: str, default_value: str = ""):
    return _ExprStateBackendGet("sqlite", str(key), str(default_value))


def sqlite_exists(key: str):
    return _ExprStateBackendExists("sqlite", str(key))


def sqlite_remove(key: str):
    return _StmtStateBackendRemove("sqlite", str(key))


def sqlite_clear():
    return _StmtStateBackendClear("sqlite")


def room_put(key: str, value: str):
    return _StmtStateBackendPut("room", str(key), str(value))


def room_get(key: str, default_value: str = ""):
    return _ExprStateBackendGet("room", str(key), str(default_value))


def room_exists(key: str):
    return _ExprStateBackendExists("room", str(key))


def room_remove(key: str):
    return _StmtStateBackendRemove("room", str(key))


def room_clear():
    return _StmtStateBackendClear("room")


def encrypted_storage_put(key: str, value: str):
    return _StmtStateBackendPut("encrypted", str(key), str(value))


def encrypted_storage_get(key: str, default_value: str = ""):
    return _ExprStateBackendGet("encrypted", str(key), str(default_value))


def encrypted_storage_exists(key: str):
    return _ExprStateBackendExists("encrypted", str(key))


def encrypted_storage_remove(key: str):
    return _StmtStateBackendRemove("encrypted", str(key))


def encrypted_storage_clear():
    return _StmtStateBackendClear("encrypted")


def secure_storage_put(key: str, value: str):
    return encrypted_storage_put(key, value)


def secure_storage_get(key: str, default_value: str = ""):
    return encrypted_storage_get(key, default_value)


def secure_storage_exists(key: str):
    return encrypted_storage_exists(key)


def secure_storage_remove(key: str):
    return encrypted_storage_remove(key)


def secure_storage_clear():
    return encrypted_storage_clear()


def style(**kwargs):
    return style_widget(**kwargs)


def theme(**kwargs):
    return theme_widget(**kwargs)


def presets(palette=None):
    return presets_widget(palette=palette)


def _normalize_anim_property_name(name):
    key = str(name).strip().lower().replace("-", "_")
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
        "translate_y": "translate_y",
        "translation_y": "translate_y",
        "alpha": "alpha",
        "elevation": "elevation",
    }
    return mapping.get(key, key)

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
    event_specs = []
    lifecycle_specs = []
    resources = {"app_name": "AhnaliPreview"}
    label_locked = False

    for part in activity_spec.parts:
        if isinstance(part, (list, tuple)):
            for subpart in part:
                if isinstance(subpart, _EventSpec):
                    event_specs.append(subpart)
                elif isinstance(subpart, _LifecycleSpec):
                    lifecycle_specs.append(subpart)
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
        elif isinstance(part, _EventSpec):
            event_specs.append(part)
        elif isinstance(part, _LifecycleSpec):
            lifecycle_specs.append(part)

    state_spec = state_spec or State()
    ui_spec = ui_spec or _UISpec()
    inline_event_specs = _collect_inline_event_specs(ui_spec.items)
    event_specs = _merge_event_specs(event_specs, inline_event_specs)
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

    app_cfg = _extract_app_config(activity_spec, caller_module)
    from .capabilities import resolve_runtime_bindings
    runtime_bindings = resolve_runtime_bindings(app_cfg.uses)
    runtime_binding_map = {binding.capability: binding for binding in runtime_bindings}
    plugin_names = _resolve_plugins(activity_spec, caller_module)
    registry = load_plugins(["core", *plugin_names])
    ctx = _PythonicContext(
        state_spec,
        ui_spec,
        theme_spec,
        min_sdk=app_cfg.min_sdk,
        registry=registry,
        runtime_bindings=runtime_binding_map,
        app_mode=app_cfg.mode,
    )
    if has_screens and state_spec.values:
        ctx._lint_warnings.append(
            "State values are global across Screens. Screen-local state is not yet supported."
        )
    program = ctx.build_program(
        event_specs,
        resources=resources,
        lifecycle_specs=lifecycle_specs,
    )
    inferred_required_artifacts, inferred_jar_allowlist = registry.collect_deps(ui_spec.items, event_specs)
    explicit_required_artifacts = set(app_cfg.deps or [])
    if app_cfg.auto_deps:
        final_required_artifacts = set(inferred_required_artifacts)
        final_required_artifacts.update(explicit_required_artifacts)
    else:
        missing_deps = sorted(set(inferred_required_artifacts) - explicit_required_artifacts)
        if missing_deps:
            missing_list = ", ".join(missing_deps)
            raise RuntimeError(
                "External libraries are explicit-only by default. "
                f"Missing declared dependencies: [{missing_list}]. "
                "Declare them with app_config(deps=[...]) or APP_DEPS, "
                "or set app_config(auto_deps=True)/APP_AUTO_DEPS=True."
            )
        final_required_artifacts = set(explicit_required_artifacts)
        final_required_artifacts.update(inferred_required_artifacts)
    from .deps import jar_allowlist_for_artifacts
    final_jar_allowlist = set(inferred_jar_allowlist)
    final_jar_allowlist.update(jar_allowlist_for_artifacts(final_required_artifacts))
    program.required_artifacts = final_required_artifacts
    program.jar_allowlist = final_jar_allowlist
    from .capabilities import (
        DEFAULT_CAPABILITY_REGISTRY,
        infer_permissions_from_handlers,
        infer_permissions_from_ui,
    )
    explicit_perms = DEFAULT_CAPABILITY_REGISTRY.resolve_permissions(app_cfg.uses)
    inferred_perms = [
        *infer_permissions_from_ui(ui_spec.items),
        *infer_permissions_from_handlers(event_specs),
    ]
    seen = set()
    merged = []
    for perm in [*explicit_perms, *inferred_perms]:
        if perm in seen:
            continue
        seen.add(perm)
        merged.append(perm)
    program.permissions = merged
    program.capability_runtime_bindings = runtime_bindings
    program.app_mode = app_cfg.mode
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
    def _normalize_list(value, *, field_name):
        if value is None:
            return []
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(v).strip() for v in value if str(v).strip()]
        raise RuntimeError(f"{field_name} must be a list or comma-separated string")

    def _merge_unique(base, extra):
        out = list(base or [])
        for item in extra or []:
            if item not in out:
                out.append(item)
        return out

    def _normalize_bool(value, *, field_name):
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
        raise RuntimeError(f"{field_name} must be a boolean")

    def _normalize_mode(value):
        mode = str(value).strip().lower()
        if mode not in {"static", "reactive"}:
            raise RuntimeError(
                f"app_config mode must be 'static' or 'reactive', got {value!r}"
            )
        return mode

    cfg = AppConfig()
    extra_uses = []
    extra_deps = []
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
                macro_deps = macro.pop("deps", None)
                extra_uses.extend(_normalize_list(macro_uses, field_name="uses"))
                extra_deps.extend(_normalize_list(macro_deps, field_name="deps"))
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
                ("APP_DEPS", "deps"),
                ("APP_AUTO_DEPS", "auto_deps"),
                ("APP_UNINSTALL_FIRST", "uninstall_first"),
                ("APP_OUTPUT_APK", "output_apk"),
                ("APP_KEYSTORE_PATH", "keystore_path"),
                ("APP_KEYSTORE_ALIAS", "keystore_alias"),
                ("APP_MODE", "mode"),
            ):
                if hasattr(mod, key):
                    value = getattr(mod, key)
                    if key == "APP_NO_ACTION_BAR":
                        value = not bool(value)
                    if key == "APP_USES":
                        extra_uses.extend(_normalize_list(value, field_name="uses"))
                    elif key == "APP_DEPS":
                        extra_deps.extend(_normalize_list(value, field_name="deps"))
                    else:
                        setattr(cfg, attr, value)
    cfg.uses = _merge_unique(cfg.uses, extra_uses)
    cfg.deps = _merge_unique(cfg.deps, extra_deps)
    cfg.auto_deps = _normalize_bool(cfg.auto_deps, field_name="auto_deps")
    cfg.mode = _normalize_mode(cfg.mode)
    return cfg
