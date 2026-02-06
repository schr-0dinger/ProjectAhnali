# dsl/app.py

import ast
from typing import List, Dict, Any
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

class _StateSpec:
    def __init__(self, **kwargs):
        self.values = kwargs


class _UIText:
    def __init__(self, text, *, id="label"):
        self.id = id
        self.text = text


class _UIButton:
    def __init__(self, text, *, id="button"):
        self.id = id
        self.text = text


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
    return _StateSpec(**kwargs)


def ui(*items):
    return _UISpec(*items)


def text(text, *, id="label"):
    return _UIText(text, id=id)


def button(text, *, id="button"):
    return _UIButton(text, id=id)


def on_click(button_id, stmts):
    return _OnClickSpec(button_id, stmts)


def _build_pythonic_app(activity_spec: _ActivitySpec):
    state_spec = None
    ui_spec = None
    click_specs = []

    for part in activity_spec.parts:
        if isinstance(part, _StateSpec):
            state_spec = part
        elif isinstance(part, _UISpec):
            ui_spec = part
        elif isinstance(part, _OnClickSpec):
            click_specs.append(part)

    state_spec = state_spec or _StateSpec()
    ui_spec = ui_spec or _UISpec()

    ctx = _PythonicContext(state_spec, ui_spec)
    return ctx.build_program(click_specs)


class _PythonicContext:
    def __init__(self, state_spec: _StateSpec, ui_spec: _UISpec):
        self.state_spec = state_spec
        self.ui_spec = ui_spec
        self.view_types = {}
        self.view_fields = {}
        self.root_id = "root"

    def _view_desc(self, kind):
        if kind == "text":
            return "Landroid/widget/TextView;"
        if kind == "button":
            return "Landroid/widget/Button;"
        return "Landroid/view/View;"

    def build_program(self, click_specs):
        body = []
        fields = []

        body.extend(linear_layout(self.root_id, var("ctx"), "vertical"))

        # UI creation
        for item in self.ui_spec.items:
            if isinstance(item, _UIText):
                self.view_types[item.id] = "text"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(text_view(item.id, var("ctx"), item.text))
                body.append(add_view(var(self.root_id), var(item.id)))
            elif isinstance(item, _UIButton):
                self.view_types[item.id] = "button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(button_view(item.id, var("ctx"), item.text))
                body.append(add_view(var(self.root_id), var(item.id)))

        # Store static refs for views
        for vid, field_name in self.view_fields.items():
            desc = self._view_desc(self.view_types[vid])
            fields.append(static_field(field_name, desc, access="private static"))
            body.append(static_set(field_name, desc, var(vid)))

        # State fields
        for name, value in self.state_spec.values.items():
            fields.append(static_field(name, "I", access="private static"))
            body.append(static_set(name, "I", const(value)))

        # Wire click handlers
        handler_methods = []
        support_classes = []
        for spec in click_specs:
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

    def _compile_stmts(self, stmts):
        out = []
        for stmt in stmts:
            stmt = stmt.strip()
            if "+=" in stmt or "-=" in stmt:
                out.extend(self._compile_inc(stmt))
            elif "=" in stmt and any(op in stmt for op in ["+", "-"]) and "f" not in stmt:
                out.extend(self._compile_assign_binary(stmt))
            elif ".text" in stmt and "=" in stmt:
                out.extend(self._compile_set_text(stmt))
            else:
                raise RuntimeError(f"Unsupported statement: {stmt}")
        out.append(ret())
        return out

    def _compile_inc(self, stmt):
        # e.g., count += 1
        if "+=" in stmt:
            name, value = [s.strip() for s in stmt.split("+=")]
            op = "+"
        else:
            name, value = [s.strip() for s in stmt.split("-=")]
            op = "-"
        delta = int(value)
        return [
            assign("x", static_get(name, "I")),
            assign("x", binary(op, var("x"), const(delta))),
            static_set(name, "I", var("x")),
        ]

    def _compile_assign_binary(self, stmt):
        # e.g., count = count + 1
        lhs, rhs = [s.strip() for s in stmt.split("=", 1)]
        if "+" in rhs:
            a, b = [s.strip() for s in rhs.split("+", 1)]
            op = "+"
        elif "-" in rhs:
            a, b = [s.strip() for s in rhs.split("-", 1)]
            op = "-"
        else:
            raise RuntimeError(f"Unsupported binary assignment: {stmt}")

        if a != lhs:
            raise RuntimeError(f"Only self-assign supported: {stmt}")
        delta = int(b)
        return [
            assign("x", static_get(lhs, "I")),
            assign("x", binary(op, var("x"), const(delta))),
            static_set(lhs, "I", var("x")),
        ]

    def _compile_set_text(self, stmt):
        # e.g., label.text = f"Count: {count}"
        lhs, rhs = [s.strip() for s in stmt.split("=", 1)]
        view_id = lhs.split(".")[0].strip()
        view_desc = self._view_desc(self.view_types.get(view_id, "text"))
        view_field = self.view_fields.get(view_id)
        if view_field is None:
            raise RuntimeError(f"Unknown view id: {view_id}")

        if rhs.startswith("f\"") or rhs.startswith("f'"):
            text = rhs[2:-1]
            return self._compile_fstring_set_text(view_desc, view_field, text)

        # plain string
        plain = rhs.strip("'\"")
        return [
            assign("v", static_get(view_field, view_desc)),
            call_stmt(
                "setText",
                args=[var("v"), const(plain)],
                return_type=None,
                invoke_kind="virtual",
                owner=view_desc,
            ),
        ]

    def _compile_fstring_set_text(self, view_desc, view_field, text):
        # support one or more {var} placeholders
        import re
        parts = []
        last = 0
        for m in re.finditer(r"{([^}]+)}", text):
            if m.start() > last:
                parts.append(("str", text[last:m.start()]))
            parts.append(("var", m.group(1).strip()))
            last = m.end()
        if last < len(text):
            parts.append(("str", text[last:]))

        stmts = [
            assign(
                "sb",
                new("Ljava/lang/StringBuilder;", args=[], arg_types=[]),
            )
        ]
        for kind, value in parts:
            if kind == "str" and value:
                stmts.append(
                    assign(
                        "sb",
                        call(
                            "append",
                            args=[var("sb"), const(value)],
                            return_type="Ljava/lang/StringBuilder;",
                            arg_types=["Ljava/lang/String;"],
                            invoke_kind="virtual",
                            owner="Ljava/lang/StringBuilder;",
                        ),
                    )
                )
            elif kind == "var":
                stmts.append(assign("x", static_get(value, "I")))
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


def layout_params(width, height, parent="LinearLayout"):
    if parent == "RelativeLayout":
        desc = "Landroid/widget/RelativeLayout$LayoutParams;"
    elif parent == "ConstraintLayout":
        desc = "Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;"
    else:
        desc = "Landroid/widget/LinearLayout$LayoutParams;"
    return new(
        desc,
        args=[const(width), const(height)],
    )


def set_layout_params(view, params, owner="Landroid/view/View;"):
    return call_stmt(
        "setLayoutParams",
        args=[view, params],
        return_type=None,
        invoke_kind="virtual",
        owner=owner,
    )


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
