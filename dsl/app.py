# dsl/app.py

import ast
import inspect
import textwrap
from typing import List, Dict, Any
from .widgets import (
    _UIText,
    _UIButton,
    _UIRow,
    _UIColumn,
    _UIAppBar,
    _UIFloatingActionButton,
    _UIRaisedButton,
    _UIFlatButton,
    _UIIconButton,
    _UITextField,
    _UICheckbox,
    _UIRadio,
    _UISwitch,
    _UISlider,
    _UIDropdownButton,
    _UIButtonBar,
    _UIPopupMenuButton,
    _UISimpleDialog,
    _UIToast,
    _UISnackbar,
    Text,
    Button,
    Row,
    Column,
    AppBar,
    FloatingActionButton,
    RaisedButton,
    FlatButton,
    IconButton,
    TextField,
    Checkbox,
    Radio,
    Switch,
    Slider,
    DropdownButton,
    ButtonBar,
    PopupMenuButton,
    State,
    Style,
    Theme,
    Presets,
    text,
    button,
    row,
    column,
    state as state_widget,
    style as style_widget,
    theme as theme_widget,
    presets as presets_widget,
)
from ir.program import ProgramIR
from ir.field import StaticField
from ir.method import MethodIR
from ir.expr import Call, Const, Var, BinaryOp, Compare, New, StaticFieldGet
from ir.stmt import Return, TryCatch, CallStmt, Throw, StaticFieldSet
from tests.ir_stub import Assign, If, While


def program(methods, fields=None, support_classes=None):
    return ProgramIR(methods, fields=fields or [], support_classes=support_classes or [])


def method(name, *, params=None, param_types=None, return_type=None, body=None):
    return MethodIR(
        name=name,
        params=params or [],
        body=body or [],
        return_type=return_type,
        param_types=param_types or [],
    )


def const(value):
    return Const(value)


def var(name):
    return Var(name)


def assign(name, expr):
    return Assign(name, expr)


def call(
    name,
    args,
    *,
    return_type=None,
    arg_types=None,
    invoke_kind="static",
    owner="LTest;",
):
    return_type, arg_types = _resolve_signature(
        name,
        args,
        return_type=return_type,
        arg_types=arg_types,
        invoke_kind=invoke_kind,
        owner=owner,
    )
    return Call(
        name,
        args=args,
        return_type=return_type,
        arg_types=arg_types,
        invoke_kind=invoke_kind,
        owner=owner,
    )


def call_stmt(
    name,
    args,
    *,
    return_type=None,
    arg_types=None,
    invoke_kind="static",
    owner="LTest;",
):
    return_type, arg_types = _resolve_signature(
        name,
        args,
        return_type=return_type,
        arg_types=arg_types,
        invoke_kind=invoke_kind,
        owner=owner,
    )
    return CallStmt(
        Call(
            name,
            args=args,
            return_type=return_type,
            arg_types=arg_types,
            invoke_kind=invoke_kind,
            owner=owner,
        )
    )


def ret(value=None):
    return Return(value)


def _resolve_signature(name, args, *, return_type, arg_types, invoke_kind, owner):
    key = (owner, name, invoke_kind)
    if key not in _METHOD_SIGS:
        return return_type, arg_types

    sig_ret, sig_args = _METHOD_SIGS[key]

    if return_type is None:
        return_type = sig_ret
    elif sig_ret is not None and return_type != sig_ret:
        raise RuntimeError(
            f"Call return_type mismatch for {owner}->{name}: "
            f"{return_type} vs {sig_ret}"
        )

    if arg_types is None:
        arg_types = sig_args
    elif sig_args is not None and list(arg_types) != list(sig_args):
        # Allow StringBuilder.append overload (int vs string)
        if key == ("Ljava/lang/StringBuilder;", "append", "virtual") and list(arg_types) == ["I"]:
            key = ("Ljava/lang/StringBuilder;", "append", "virtual#int")
            sig_ret, sig_args = _METHOD_SIGS[key]
        else:
            raise RuntimeError(
                f"Call arg_types mismatch for {owner}->{name}: "
                f"{arg_types} vs {sig_args}"
            )

    # Basic arity sanity
    if arg_types is not None:
        expected = len(args)
        if invoke_kind in ("virtual", "direct"):
            if len(arg_types) not in (expected, expected - 1):
                raise RuntimeError(
                    f"Call arg_types length does not match args for instance invoke "
                    f"{owner}->{name}"
                )
        elif len(arg_types) != expected:
            raise RuntimeError(
                f"Call arg_types length does not match args for {owner}->{name}"
            )

    return return_type, arg_types


_METHOD_SIGS = {
    ("Landroid/widget/TextView;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/TextView;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/EditText;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/EditText;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/EditText;", "setHint", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/CheckBox;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/CheckBox;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/CheckBox;", "setChecked", "virtual"): (None, ["Z"]),
    ("Landroid/widget/RadioButton;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/RadioButton;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/RadioButton;", "setChecked", "virtual"): (None, ["Z"]),
    ("Landroid/widget/Switch;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Switch;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/Switch;", "setChecked", "virtual"): (None, ["Z"]),
    ("Landroid/widget/SeekBar;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/SeekBar;", "setMax", "virtual"): (None, ["I"]),
    ("Landroid/widget/SeekBar;", "setProgress", "virtual"): (None, ["I"]),
    ("Landroid/widget/Spinner;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/ImageButton;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Toolbar;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Toolbar;", "setTitle", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/view/View;", "setContentDescription", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/Button;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Button;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/app/Activity;", "setContentView", "virtual"): (None, ["Landroid/view/View;"]),
    ("Landroid/app/Activity;", "setTitle", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/Toast;", "makeText", "static"): (
        "Landroid/widget/Toast;",
        ["Landroid/content/Context;", "Ljava/lang/CharSequence;", "I"],
    ),
    ("Landroid/widget/Toast;", "show", "virtual"): (None, []),
    ("Landroid/widget/LinearLayout;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/LinearLayout;", "setOrientation", "virtual"): (None, ["I"]),
    ("Landroid/view/ViewGroup;", "addView", "virtual"): (None, ["Landroid/view/View;"]),
    ("Landroid/view/View;", "setOnClickListener", "virtual"): (
        None,
        ["Landroid/view/View$OnClickListener;"],
    ),
    ("Landroid/view/View;", "setPadding", "virtual"): (
        None,
        ["I", "I", "I", "I"],
    ),
    ("Landroid/widget/TextView;", "setGravity", "virtual"): (None, ["I"]),
    ("Landroid/view/View;", "setLayoutParams", "virtual"): (
        None,
        ["Landroid/view/ViewGroup$LayoutParams;"],
    ),
    ("Landroid/app/AlertDialog$Builder;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/app/AlertDialog$Builder;", "setTitle", "virtual"): ("Landroid/app/AlertDialog$Builder;", ["Ljava/lang/CharSequence;"]),
    ("Landroid/app/AlertDialog$Builder;", "setMessage", "virtual"): ("Landroid/app/AlertDialog$Builder;", ["Ljava/lang/CharSequence;"]),
    ("Landroid/app/AlertDialog$Builder;", "show", "virtual"): ("Landroid/app/AlertDialog;", []),
    ("Landroid/util/Log;", "d", "static"): (
        "I",
        ["Ljava/lang/String;", "Ljava/lang/String;"],
    ),
    ("Ljava/lang/String;", "valueOf", "static"): (
        "Ljava/lang/String;",
        ["I"],
    ),
    ("Ljava/lang/StringBuilder;", "<init>", "direct"): (None, []),
    ("Ljava/lang/StringBuilder;", "append", "virtual"): ("Ljava/lang/StringBuilder;", ["Ljava/lang/String;"]),
    ("Ljava/lang/StringBuilder;", "append", "virtual#int"): ("Ljava/lang/StringBuilder;", ["I"]),
    ("Ljava/lang/StringBuilder;", "toString", "virtual"): ("Ljava/lang/String;", []),
}


_CTOR_SIGS = {
    "Landroid/widget/TextView;": ["Landroid/content/Context;"],
    "Landroid/widget/Button;": ["Landroid/content/Context;"],
    "Landroid/widget/EditText;": ["Landroid/content/Context;"],
    "Landroid/widget/CheckBox;": ["Landroid/content/Context;"],
    "Landroid/widget/RadioButton;": ["Landroid/content/Context;"],
    "Landroid/widget/Switch;": ["Landroid/content/Context;"],
    "Landroid/widget/SeekBar;": ["Landroid/content/Context;"],
    "Landroid/widget/Spinner;": ["Landroid/content/Context;"],
    "Landroid/widget/ImageButton;": ["Landroid/content/Context;"],
    "Landroid/widget/Toolbar;": ["Landroid/content/Context;"],
    "Landroid/app/AlertDialog$Builder;": ["Landroid/content/Context;"],
    "Landroid/widget/LinearLayout;": ["Landroid/content/Context;"],
    "Lcom/anali/preview/AnaliClickListener;": [],
    "Ljava/lang/StringBuilder;": [],
    "Landroid/widget/RelativeLayout;": ["Landroid/content/Context;"],
    "Landroidx/constraintlayout/widget/ConstraintLayout;": ["Landroid/content/Context;"],
    "Landroid/widget/LinearLayout$LayoutParams;": ["I", "I"],
    "Landroid/widget/RelativeLayout$LayoutParams;": ["I", "I"],
    "Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;": ["I", "I"],
}


def new(class_desc, args=None, arg_types=None):
    if arg_types is None:
        arg_types = _CTOR_SIGS.get(class_desc)
    return New(class_desc, args=args or [], arg_types=arg_types or [])


def static_field(name, desc, access="private static"):
    return StaticField(name, desc, access=access)


def static_get(name, desc, owner="LTest;"):
    from ir.expr import StaticFieldGet
    return StaticFieldGet(owner, name, desc)


def static_set(name, desc, value, owner="LTest;"):
    return StaticFieldSet(owner, name, desc, value)


def field_get(obj, owner, name, desc):
    from ir.expr import FieldGet
    return FieldGet(obj, name, desc, owner)


def field_set(obj, owner, name, desc, value):
    from ir.stmt import FieldSet
    return FieldSet(obj, name, desc, owner, value)


def array_get(array, index, elem_desc):
    from ir.expr import ArrayGet
    return ArrayGet(array, index, elem_desc)


def array_set(array, index, elem_desc, value):
    from ir.stmt import ArraySet
    return ArraySet(array, index, elem_desc, value)


def check_cast(value, desc):
    from ir.expr import CheckCast
    return CheckCast(value, desc)


def hello_world_activity(message="Hello, Anali!"):
    """
    Compiler-driven HelloWorld Activity:
    - new TextView(ctx)
    - setText(message)
    - setContentView(view)
    """
    from ir.types import AnaliType

    return program([
        method(
            "main",
            params=["ctx"],
            param_types=["Landroid/app/Activity;"],
            return_type=None,
            body=[
                *text_view("tv", var("ctx"), message),
                set_content_view(var("ctx"), var("tv")),
                ret(),
            ],
        )
    ])


def text_view(name, ctx, text):
    """
    Build a TextView and set text.
    Returns a list of statements.
    """
    return [
        assign(
            name,
            new(
                "Landroid/widget/TextView;",
                args=[ctx],
            ),
        ),
        call_stmt(
            "setText",
            args=[var(name), const(text)],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/widget/TextView;",
        ),
    ]


def button_view(name, ctx, text):
    """
    Build a Button and set text.
    Returns a list of statements.
    """
    return [
        assign(
            name,
            new(
                "Landroid/widget/Button;",
                args=[ctx],
            ),
        ),
        call_stmt(
            "setText",
            args=[var(name), const(text)],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/widget/Button;",
        ),
    ]


def set_content_view(ctx, view):
    return call_stmt(
        "setContentView",
        args=[ctx, view],
        return_type=None,
        invoke_kind="virtual",
        owner="Landroid/app/Activity;",
    )


def toast(name, ctx, text, duration=0):
    """
    Create and show a Toast. duration: 0 (SHORT) or 1 (LONG).
    Returns a list of statements.
    """
    return [
        assign(
            name,
            call(
                "makeText",
                args=[ctx, const(text), const(duration)],
                invoke_kind="static",
                owner="Landroid/widget/Toast;",
            ),
        ),
        call_stmt(
            "show",
            args=[var(name)],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/widget/Toast;",
        ),
    ]


def log_d(tag, msg, name="_log"):
    """
    Log.d(tag, msg) with return value ignored.
    Returns a list with a single assign to a dummy name.
    """
    return [
        assign(
            name,
            call(
                "d",
                args=[const(tag), const(msg)],
                invoke_kind="static",
                owner="Landroid/util/Log;",
            ),
        )
    ]


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

        for kind, vid, text in self._items:
            if kind == "text":
                body.extend(text_view(vid, var("ctx"), text))
            elif kind == "button":
                body.extend(button_view(vid, var("ctx"), text))
            body.append(add_view(var(self._root_id), var(vid)))

        for kind, button_id, text in self._handlers:
            handler_name = f"onClick_{button_id}"
            body.extend(on_click_view(var(button_id), handler_name=handler_name))

            owner = "Landroid/widget/Button;"

            if kind == "set_text":
                handler_body = [
                    call_stmt(
                        "setText",
                        args=[var("view"), const(text)],
                        return_type=None,
                        invoke_kind="virtual",
                        owner=owner,
                    ),
                    ret(),
                ]
            else:
                # increment counter and update label
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
            fields.append(static_field(self._counter_label_field, "Landroid/widget/TextView;", access="private static"))

        for name, hbody in self._handler_methods:
            methods.append(click_handler(name, hbody))

        return program(methods, fields=fields)


def simple_activity():
    return _SimpleActivity()


# ------------------------------------------------------------
# Pythonic DSL layer (Phase 1)
# ------------------------------------------------------------

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

    for part in activity_spec.parts:
        if isinstance(part, State):
            state_spec = part
        elif isinstance(part, _UISpec):
            ui_spec = part
        elif isinstance(part, Theme):
            theme_spec = part
        elif isinstance(part, _OnClickSpec):
            click_specs.append(part)

    state_spec = state_spec or State()
    ui_spec = ui_spec or _UISpec()

    ctx = _PythonicContext(state_spec, ui_spec, theme_spec)
    return ctx.build_program(click_specs)


class _PythonicContext:
    def __init__(self, state_spec: State, ui_spec: _UISpec, theme_spec: Theme):
        self.state_spec = state_spec
        self.ui_spec = ui_spec
        self.theme_spec = theme_spec
        self.view_types = {}
        self.view_fields = {}
        self.root_id = "root"

    def _view_desc(self, kind):
        if kind == "text":
            return "Landroid/widget/TextView;"
        if kind == "button":
            return "Landroid/widget/Button;"
        if kind == "app_bar":
            return "Landroid/widget/Toolbar;"
        if kind == "fab":
            return "Landroid/widget/ImageButton;"
        if kind == "raised_button":
            return "Landroid/widget/Button;"
        if kind == "flat_button":
            return "Landroid/widget/Button;"
        if kind == "icon_button":
            return "Landroid/widget/ImageButton;"
        if kind == "text_field":
            return "Landroid/widget/EditText;"
        if kind == "checkbox":
            return "Landroid/widget/CheckBox;"
        if kind == "radio":
            return "Landroid/widget/RadioButton;"
        if kind == "switch":
            return "Landroid/widget/Switch;"
        if kind == "slider":
            return "Landroid/widget/SeekBar;"
        if kind == "dropdown":
            return "Landroid/widget/Spinner;"
        if kind == "popup_button":
            return "Landroid/widget/Button;"
        return "Landroid/view/View;"

    def build_program(self, click_specs):
        body = []
        fields = []

        body.extend(linear_layout(self.root_id, var("ctx"), "vertical"))

        # UI creation (recursive)
        body.extend(self._build_ui_items(self.root_id, self.ui_spec.items))

        # Store static refs for views
        for vid, field_name in self.view_fields.items():
            desc = self._view_desc(self.view_types[vid])
            fields.append(static_field(field_name, desc, access="private static"))
            body.append(static_set(field_name, desc, var(vid)))

        fields.append(static_field("app_ctx", "Landroid/app/Activity;", access="private static"))
        body.append(static_set("app_ctx", "Landroid/app/Activity;", var("ctx")))

        # State fields
        for name, value in self.state_spec.values.items():
            fields.append(static_field(name, "I", access="private static"))
            body.append(static_set(name, "I", const(value)))

        # Wire click handlers
        handler_methods = []
        support_classes = []
        for spec in click_specs:
            if spec.button_id not in self.view_types:
                known = ", ".join(sorted(self.view_types.keys()))
                raise RuntimeError(
                    f"on_click target '{spec.button_id}' not found in ui() ids. "
                    f"Known ids: [{known}]"
                )
            clickable_kinds = {
                "button",
                "raised_button",
                "flat_button",
                "icon_button",
                "fab",
                "popup_button",
            }
            if self.view_types.get(spec.button_id) not in clickable_kinds:
                raise RuntimeError(
                    f"on_click target '{spec.button_id}' is not a button (kind={self.view_types.get(spec.button_id)})."
                )
            handler_name = f"onClick_{spec.button_id}"
            listener_desc = f"Lcom/anali/preview/AnaliClickListener_{spec.button_id};"
            body.extend(on_click_view(var(spec.button_id), handler_name=handler_name, listener_class_desc=listener_desc))
            support_classes.append((listener_desc, handler_name))
            handler_methods.append((handler_name, self._compile_stmts(spec.stmts)))

        # Main method
        methods = [
            method(
                "main",
                params=["ctx"],
                param_types=["Landroid/app/Activity;"],
                return_type=None,
                body=[
                    *body,
                    set_content_view(var("ctx"), var(self.root_id)),
                    ret(),
                ],
            )
        ]

        for name, hbody in handler_methods:
            methods.append(click_handler(name, hbody))

        return program(methods, fields=fields, support_classes=support_classes)

    def _build_ui_items(self, parent_id, items):
        body = []
        for item in items:
            if isinstance(item, _UIText):
                self.view_types[item.id] = "text"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(text_view(item.id, var("ctx"), item.text))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIButton):
                self.view_types[item.id] = "button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(button_view(item.id, var("ctx"), item.text))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIAppBar):
                self.view_types[item.id] = "app_bar"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/Toolbar;", args=[var("ctx")])),
                        call_stmt(
                            "setTitle",
                            args=[var(item.id), const(item.text)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/Toolbar;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIFloatingActionButton):
                self.view_types[item.id] = "fab"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/ImageButton;", args=[var("ctx")])),
                        call_stmt(
                            "setContentDescription",
                            args=[var(item.id), const(item.text)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/view/View;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIRaisedButton):
                self.view_types[item.id] = "raised_button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(button_view(item.id, var("ctx"), item.text))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIFlatButton):
                self.view_types[item.id] = "flat_button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(button_view(item.id, var("ctx"), item.text))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIIconButton):
                self.view_types[item.id] = "icon_button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/ImageButton;", args=[var("ctx")])),
                        call_stmt(
                            "setContentDescription",
                            args=[var(item.id), const(item.text)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/view/View;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UITextField):
                self.view_types[item.id] = "text_field"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/EditText;", args=[var("ctx")])),
                        call_stmt(
                            "setText",
                            args=[var(item.id), const(item.text or "")],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/EditText;",
                        ),
                    ]
                )
                if item.hint:
                    body.append(
                        call_stmt(
                            "setHint",
                            args=[var(item.id), const(item.hint)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/EditText;",
                        )
                    )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UICheckbox):
                self.view_types[item.id] = "checkbox"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/CheckBox;", args=[var("ctx")])),
                        call_stmt(
                            "setText",
                            args=[var(item.id), const(item.text or "")],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/CheckBox;",
                        ),
                        call_stmt(
                            "setChecked",
                            args=[var(item.id), const(1 if item.checked else 0)],
                            return_type=None,
                            arg_types=["Z"],
                            invoke_kind="virtual",
                            owner="Landroid/widget/CheckBox;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIRadio):
                self.view_types[item.id] = "radio"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/RadioButton;", args=[var("ctx")])),
                        call_stmt(
                            "setText",
                            args=[var(item.id), const(item.text or "")],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/RadioButton;",
                        ),
                        call_stmt(
                            "setChecked",
                            args=[var(item.id), const(1 if item.checked else 0)],
                            return_type=None,
                            arg_types=["Z"],
                            invoke_kind="virtual",
                            owner="Landroid/widget/RadioButton;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UISwitch):
                self.view_types[item.id] = "switch"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/Switch;", args=[var("ctx")])),
                        call_stmt(
                            "setText",
                            args=[var(item.id), const(item.text or "")],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/Switch;",
                        ),
                        call_stmt(
                            "setChecked",
                            args=[var(item.id), const(1 if item.checked else 0)],
                            return_type=None,
                            arg_types=["Z"],
                            invoke_kind="virtual",
                            owner="Landroid/widget/Switch;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UISlider):
                self.view_types[item.id] = "slider"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/SeekBar;", args=[var("ctx")])),
                        call_stmt(
                            "setMax",
                            args=[var(item.id), const(int(item.max) - int(item.min))],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/SeekBar;",
                        ),
                        call_stmt(
                            "setProgress",
                            args=[var(item.id), const(int(item.value) - int(item.min))],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/SeekBar;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIDropdownButton):
                self.view_types[item.id] = "dropdown"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend([assign(item.id, new("Landroid/widget/Spinner;", args=[var("ctx")]))])
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIButtonBar):
                self.view_types[item.id] = "row"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(linear_layout(item.id, var("ctx"), "horizontal"))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
                body.extend(self._build_ui_items(item.id, item.items))
            elif isinstance(item, _UIPopupMenuButton):
                self.view_types[item.id] = "popup_button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(button_view(item.id, var("ctx"), item.text))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIRow):
                self.view_types[item.id] = "row"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(linear_layout(item.id, var("ctx"), "horizontal"))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
                body.extend(self._build_ui_items(item.id, item.items))
            elif isinstance(item, _UIColumn):
                self.view_types[item.id] = "column"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(linear_layout(item.id, var("ctx"), "vertical"))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
                body.extend(self._build_ui_items(item.id, item.items))
            else:
                raise RuntimeError(f"Unsupported UI item: {item}")
        return body

    def _compile_stmts(self, stmts):
        out = []
        for stmt in stmts:
            if isinstance(stmt, str):
                raise RuntimeError("String statements are deprecated; use AST builder objects.")
            if isinstance(stmt, _StmtAssign):
                out.extend(self._compile_assign_stmt(stmt))
            elif isinstance(stmt, _StmtSetText):
                out.extend(self._compile_set_text_stmt(stmt))
            elif isinstance(stmt, _StmtToast):
                out.extend(self._compile_toast_stmt(stmt))
            elif isinstance(stmt, _StmtSnackbar):
                out.extend(self._compile_snackbar_stmt(stmt))
            elif isinstance(stmt, _StmtSimpleDialog):
                out.extend(self._compile_dialog_stmt(stmt))
            else:
                raise RuntimeError(f"Unsupported statement: {stmt}")
        out.append(ret())
        return out

    def _apply_view_layout(self, item):
        out = []
        theme_style = Style()
        if isinstance(item, _UIText):
            theme_style = self.theme_spec.text
        elif isinstance(item, _UIButton):
            theme_style = self.theme_spec.button
        elif isinstance(item, _UIRow):
            theme_style = self.theme_spec.row
        elif isinstance(item, _UIColumn):
            theme_style = self.theme_spec.column

        item_style = item.style if getattr(item, "style", None) else None
        style = theme_style.merged(item_style)

        padding_value = item.padding if item.padding is not None else style.padding
        gravity_value = item.gravity if item.gravity is not None else style.gravity
        layout_value = item.layout if item.layout is not None else style.layout
        margin_value = item.margin if item.margin is not None else style.margin
        text_color_value = item.text_color if getattr(item, "text_color", None) is not None else style.text_color
        background_value = item.background if getattr(item, "background", None) is not None else style.background
        radius_value = item.radius if getattr(item, "radius", None) is not None else style.radius
        text_size_value = item.text_size if getattr(item, "text_size", None) is not None else style.text_size

        if padding_value:
            left, top, right, bottom = padding_value
            out.append(padding(var(item.id), left, top, right, bottom))
        if gravity_value is not None:
            out.append(gravity(var(item.id), gravity_value))

        palette = self.theme_spec.palette
        bg_color = _parse_color(background_value, palette)
        txt_color = _parse_color(text_color_value, palette)

        if bg_color is not None and radius_value is not None:
            bg_name = f"bg_{item.id}"
            out.append(assign(bg_name, new("Landroid/graphics/drawable/GradientDrawable;", args=[])))
            out.append(
                call_stmt(
                    "setColor",
                    args=[var(bg_name), const(bg_color)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/graphics/drawable/GradientDrawable;",
                )
            )
            out.append(
                call_stmt(
                    "setCornerRadius",
                    args=[var(bg_name), const(_float_bits(radius_value))],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/graphics/drawable/GradientDrawable;",
                )
            )
            out.append(
                call_stmt(
                    "setBackground",
                    args=[var(item.id), var(bg_name)],
                    return_type=None,
                    arg_types=["Landroid/graphics/drawable/Drawable;"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
        elif bg_color is not None:
            out.append(
                call_stmt(
                    "setBackgroundColor",
                    args=[var(item.id), const(bg_color)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )

        if txt_color is not None:
            out.append(
                call_stmt(
                    "setTextColor",
                    args=[var(item.id), const(txt_color)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/TextView;",
                )
            )

        if text_size_value is not None:
            out.append(
                call_stmt(
                    "setTextSize",
                    args=[var(item.id), const(_float_bits(text_size_value))],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/TextView;",
                )
            )

        if layout_value:
            width, height = layout_value
            lp_name = f"lp_{item.id}"
            out.append(assign(lp_name, layout_params(width, height, parent="LinearLayout")))
            if margin_value:
                ml, mt, mr, mb = margin_value
                out.append(set_margins(var(lp_name), ml, mt, mr, mb))
            out.append(set_layout_params(var(item.id), var(lp_name)))
        return out

    def _compile_assign_stmt(self, stmt):
        if isinstance(stmt.value, _ExprConst):
            return [static_set(stmt.target.name, "I", const(stmt.value.value))]
        if isinstance(stmt.value, _ExprBinary):
            # only support state = state +/- const
            if stmt.value.lhs.name != stmt.target.name:
                raise RuntimeError("Only self-assign supported")
            op = stmt.value.op
            rhs = stmt.value.rhs
            prefix = []
            if isinstance(rhs, _ExprConst):
                rhs_expr = const(rhs.value)
            elif isinstance(rhs, _ExprSymbol):
                rhs_expr = var("rhs")
                prefix.append(assign("rhs", static_get(rhs.name, "I")))
            else:
                raise RuntimeError("Only const or name RHS supported")
            return [
                *prefix,
                assign("x", static_get(stmt.target.name, "I")),
                assign("x", binary(op, var("x"), rhs_expr)),
                static_set(stmt.target.name, "I", var("x")),
            ]
        raise RuntimeError("Only binary/const assignments are supported")

    def _compile_set_text_stmt(self, stmt):
        view_id = stmt.view.name
        view_desc = self._view_desc(self.view_types.get(view_id, "text"))
        view_field = self.view_fields.get(view_id)
        if view_field is None:
            raise RuntimeError(f"Unknown view id: {view_id}")
        if isinstance(stmt.value, _ExprConst):
            return [
                assign("v", static_get(view_field, view_desc)),
                call_stmt(
                    "setText",
                    args=[var("v"), const(stmt.value.value)],
                    return_type=None,
                    invoke_kind="virtual",
                    owner=view_desc,
                ),
            ]
        if isinstance(stmt.value, _ExprFormat):
            return self._compile_format_set_text(view_desc, view_field, stmt.value)
        raise RuntimeError("Unsupported set_text value")

    def _compile_toast_stmt(self, stmt):
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            *toast("toast_obj", var("ctx"), stmt.message, stmt.duration),
        ]

    def _compile_snackbar_stmt(self, stmt):
        # Framework fallback until Material dependency is bundled.
        return self._compile_toast_stmt(_StmtToast(stmt.message, stmt.duration))

    def _compile_dialog_stmt(self, stmt):
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign("dlg", new("Landroid/app/AlertDialog$Builder;", args=[var("ctx")])),
            assign(
                "dlg",
                call(
                    "setTitle",
                    args=[var("dlg"), const(stmt.title)],
                    invoke_kind="virtual",
                    owner="Landroid/app/AlertDialog$Builder;",
                ),
            ),
            assign(
                "dlg",
                call(
                    "setMessage",
                    args=[var("dlg"), const(stmt.message)],
                    invoke_kind="virtual",
                    owner="Landroid/app/AlertDialog$Builder;",
                ),
            ),
            assign(
                "_dlg_obj",
                call(
                    "show",
                    args=[var("dlg")],
                    invoke_kind="virtual",
                    owner="Landroid/app/AlertDialog$Builder;",
                ),
            ),
        ]

    def _compile_format_set_text(self, view_desc, view_field, fmt):
        stmts = [
            assign(
                "sb",
                new("Ljava/lang/StringBuilder;", args=[], arg_types=[]),
            )
        ]
        for part in fmt.parts:
            if isinstance(part, _ExprConst):
                if part.value:
                    stmts.append(
                        assign(
                            "sb",
                            call(
                                "append",
                                args=[var("sb"), const(part.value)],
                                return_type="Ljava/lang/StringBuilder;",
                                arg_types=["Ljava/lang/String;"],
                                invoke_kind="virtual",
                                owner="Ljava/lang/StringBuilder;",
                            ),
                        )
                    )
            elif isinstance(part, _ExprSymbol):
                stmts.append(assign("x", static_get(part.name, "I")))
                stmts.append(
                    assign(
                        "sb",
                        call(
                            "append",
                            args=[var("sb"), var("x")],
                            return_type="Ljava/lang/StringBuilder;",
                            arg_types=["I"],
                            invoke_kind="virtual",
                            owner="Ljava/lang/StringBuilder;",
                        ),
                    )
                )
        stmts.append(
            assign(
                "s",
                call(
                    "toString",
                    args=[var("sb")],
                    return_type="Ljava/lang/String;",
                    arg_types=[],
                    invoke_kind="virtual",
                    owner="Ljava/lang/StringBuilder;",
                ),
            )
        )
        stmts.append(assign("v", static_get(view_field, view_desc)))
        stmts.append(
            call_stmt(
                "setText",
                args=[var("v"), var("s")],
                return_type=None,
                invoke_kind="virtual",
                owner=view_desc,
            )
        )
        return stmts


# -------------------------------
# AST-based expression builder
# -------------------------------

class _ExprSymbol:
    def __init__(self, name):
        self.name = name

    def __add__(self, other):
        return _ExprBinary(self, "+", _coerce_expr(other))

    def __sub__(self, other):
        return _ExprBinary(self, "-", _coerce_expr(other))

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
    if isinstance(value, (_ExprSymbol, _ExprBinary, _ExprCompare, _ExprFormat, _ExprConst)):
        return value
    return _ExprConst(value)


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
        if not isinstance(value, (_ExprConst, _ExprSymbol)):
            raise RuntimeError("Only const or name increments are supported")
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
            if fn == "toast":
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
            if fn == "snackbar":
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
            if fn == "simple_dialog":
                args = [_parse_expr(a) for a in call.args]
                if len(args) < 2:
                    raise RuntimeError("simple_dialog requires title and message")
                if not isinstance(args[0], _ExprConst) or not isinstance(args[1], _ExprConst):
                    raise RuntimeError("simple_dialog args must be constants")
                return _StmtSimpleDialog(args[0].value, args[1].value)
        return None
    if isinstance(stmt, ast.Pass):
        return None
    raise RuntimeError(f"Unsupported statement: {ast.dump(stmt)}")


def _parse_expr(node):
    if isinstance(node, ast.Constant):
        return _ExprConst(node.value)
    if isinstance(node, ast.Name):
        return _ExprSymbol(node.id)
    if isinstance(node, ast.BinOp):
        lhs = _parse_expr(node.left)
        rhs = _parse_expr(node.right)
        if not isinstance(lhs, _ExprSymbol):
            raise RuntimeError("Only binary ops with a name on the left are supported")
        if not isinstance(rhs, (_ExprConst, _ExprSymbol)):
            raise RuntimeError("Only binary ops with a const or name on the right are supported")
        return _ExprBinary(lhs, _binop_symbol(node.op), rhs)
    if isinstance(node, ast.Compare):
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise RuntimeError("Only single comparisons are supported")
        lhs = _parse_expr(node.left)
        rhs = _parse_expr(node.comparators[0])
        if not isinstance(lhs, (_ExprSymbol, _ExprConst)) or not isinstance(rhs, (_ExprSymbol, _ExprConst)):
            raise RuntimeError("Only simple name/const comparisons are supported")
        return _ExprCompare(lhs, _cmpop_symbol(node.ops[0]), rhs)
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
    raise RuntimeError("Only + and - are supported")


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


def linear_layout(name, ctx, orientation="vertical"):
    """
    Build a LinearLayout and set orientation.
    orientation: "vertical" or "horizontal"
    Returns a list of statements.
    """
    orient = 1 if orientation == "vertical" else 0
    return [
        assign(
            name,
            new(
                "Landroid/widget/LinearLayout;",
                args=[ctx],
            ),
        ),
        call_stmt(
            "setOrientation",
            args=[var(name), const(orient)],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/widget/LinearLayout;",
        ),
    ]


def row_layout(name, ctx):
    return linear_layout(name, ctx, "horizontal")


def column_layout(name, ctx):
    return linear_layout(name, ctx, "vertical")


def add_view(parent, child):
    return call_stmt(
        "addView",
        args=[parent, child],
        return_type=None,
        invoke_kind="virtual",
        owner="Landroid/view/ViewGroup;",
    )


def padding(view, left, top, right, bottom):
    return call_stmt(
        "setPadding",
        args=[view, const(left), const(top), const(right), const(bottom)],
        return_type=None,
        invoke_kind="virtual",
        owner="Landroid/view/View;",
    )


def gravity(view, value):
    return call_stmt(
        "setGravity",
        args=[view, const(value)],
        return_type=None,
        invoke_kind="virtual",
        owner="Landroid/widget/TextView;",
    )


def _lp_size(value):
    if isinstance(value, str):
        key = value.lower().strip()
        if key in ("match", "match_parent", "fill"):
            return -1
        if key in ("wrap", "wrap_content"):
            return -2
        raise RuntimeError(f"Unknown layout size: {value}")
    return int(value)


def layout_params(width, height, parent="LinearLayout"):
    if parent == "RelativeLayout":
        desc = "Landroid/widget/RelativeLayout$LayoutParams;"
    elif parent == "ConstraintLayout":
        desc = "Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;"
    else:
        desc = "Landroid/widget/LinearLayout$LayoutParams;"
    return new(
        desc,
        args=[const(_lp_size(width)), const(_lp_size(height))],
    )


def set_layout_params(view, params, owner="Landroid/view/View;"):
    return call_stmt(
        "setLayoutParams",
        args=[view, params],
        return_type=None,
        invoke_kind="virtual",
        owner=owner,
    )


def set_margins(params, left, top, right, bottom):
    return call_stmt(
        "setMargins",
        args=[params, const(left), const(top), const(right), const(bottom)],
        return_type=None,
        arg_types=["I", "I", "I", "I"],
        invoke_kind="virtual",
        owner="Landroid/view/ViewGroup$MarginLayoutParams;",
    )


def _parse_color(value, palette):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        key = value.strip()
        if key in palette:
            key = palette[key]
        if key.startswith("#"):
            hexstr = key[1:]
            if len(hexstr) == 6:
                return int("FF" + hexstr, 16)
            if len(hexstr) == 8:
                return int(hexstr, 16)
        raise RuntimeError(f"Unsupported color: {value}")
    raise RuntimeError(f"Unsupported color type: {type(value)}")


def _float_bits(value):
    import struct
    return struct.unpack(">I", struct.pack(">f", float(value)))[0]


def relative_layout(name, ctx):
    return [
        assign(
            name,
            new(
                "Landroid/widget/RelativeLayout;",
                args=[ctx],
            ),
        )
    ]


def constraint_layout(name, ctx):
    return [
        assign(
            name,
            new(
                "Landroidx/constraintlayout/widget/ConstraintLayout;",
                args=[ctx],
            ),
        )
    ]


def click_handler(name, body):
    """
    Define a click handler method with signature:
    static name(Landroid/view/View;)V
    """
    return method(
        name,
        params=["view"],
        param_types=["Landroid/view/View;"],
        return_type=None,
        body=body,
    )


def on_click_view(view, handler_name="onClick", listener_var="listener", listener_class_desc="Lcom/anali/preview/AnaliClickListener;"):
    """
    Wire a click listener that calls LTest;->handler_name(View)V.
    Requires support class AnaliClickListener to be emitted by toolchain.
    Returns a list of statements.
    """
    return [
        assign(
            listener_var,
            new(
                listener_class_desc,
                args=[],
            ),
        ),
        call_stmt(
            "setOnClickListener",
            args=[view, var(listener_var)],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/view/View;",
        ),
    ]


def if_(cond, then, else_):
    return If(cond, then, else_)


def while_(cond, body):
    return While(cond, body)


def binary(op, left, right):
    return BinaryOp(op, left, right)


def compare(op, left, right):
    return Compare(op, left, right)


def try_catch(try_body, except_body=None, exception_type=None, handlers=None):
    return TryCatch(try_body, except_body, exception_type, handlers)


def throw(value):
    return Throw(value)
