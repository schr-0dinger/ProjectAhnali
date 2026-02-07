from .ast import *
from .ir_helpers import *
from .lowering.context import _PythonicContext
from .parser import _parse_handler_ast
from .widgets import (
    _UIAppBar,
    _UIButton,
    _UIButtonBar,
    _UIColumn,
    _UIFlatButton,
    _UIFloatingActionButton,
    _UIIconButton,
    _UIPopupMenuButton,
    _UIRaisedButton,
    _UIRow,
    _UISimpleDialog,
    _UISnackbar,
    _UIToast,
    _UIText,
    AppBar,
    Button,
    ButtonBar,
    Checkbox,
    Column,
    DropdownButton,
    FlatButton,
    FloatingActionButton,
    IconButton,
    PopupMenuButton,
    Presets,
    Radio,
    RaisedButton,
    Row,
    Slider,
    State,
    Style,
    Switch,
    Text,
    TextField,
    Theme,
    button,
    column,
    presets as presets_widget,
    row,
    state as state_widget,
    style as style_widget,
    text,
    theme as theme_widget,
)


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


class AppSpec:
    def __init__(self, activity_spec: _ActivitySpec):
        self.activity_spec = activity_spec

    def build(self):
        return _build_pythonic_app(self.activity_spec)

    def run(self, **kwargs):
        from apk.toolchain import build_install_run

        return build_install_run(self.build(), **kwargs)


def app(activity_spec: _ActivitySpec):
    return AppSpec(activity_spec)


def run(app_spec: AppSpec, **kwargs):
    return app_spec.run(**kwargs)


def activity(name, *parts):
    return _ActivitySpec(name, *parts)


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


def style(**kwargs):
    return style_widget(**kwargs)


def theme(**kwargs):
    return theme_widget(**kwargs)


def presets(palette=None):
    return presets_widget(palette=palette)


def _build_pythonic_app(activity_spec: _ActivitySpec):
    state_spec = None
    ui_spec = None
    theme_spec = Theme()
    click_specs = []
    resources = {"app_name": "AnaliPreview"}

    for part in activity_spec.parts:
        if isinstance(part, State):
            state_spec = part
        elif isinstance(part, _UISpec):
            ui_spec = part
            for item in part.items:
                if isinstance(item, _UIAppBar) and getattr(item, "text", None):
                    resources["app_name"] = str(item.text)
        elif isinstance(part, Theme):
            theme_spec = part
        elif isinstance(part, _OnClickSpec):
            click_specs.append(part)

    state_spec = state_spec or State()
    ui_spec = ui_spec or _UISpec()

    ctx = _PythonicContext(state_spec, ui_spec, theme_spec)
    return ctx.build_program(click_specs, resources=resources)
