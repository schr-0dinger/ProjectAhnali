# dsl/app.py

from ir.program import ProgramIR
from ir.field import StaticField
from ir.method import MethodIR
from ir.expr import Call, Const, Var, BinaryOp, Compare, New
from ir.stmt import Return, TryCatch, CallStmt, Throw, StaticFieldSet
from tests.ir_stub import Assign, If, While


def program(methods, fields=None):
    return ProgramIR(methods, fields=fields or [])


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
    ("Landroid/util/Log;", "d", "static"): (
        "I",
        ["Ljava/lang/String;", "Ljava/lang/String;"],
    ),
    ("Ljava/lang/String;", "valueOf", "static"): (
        "Ljava/lang/String;",
        ["I"],
    ),
}


_CTOR_SIGS = {
    "Landroid/widget/TextView;": ["Landroid/content/Context;"],
    "Landroid/widget/Button;": ["Landroid/content/Context;"],
    "Landroid/widget/LinearLayout;": ["Landroid/content/Context;"],
    "Lcom/anali/preview/AnaliClickListener;": [],
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


def button(name, ctx, text):
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
                body.extend(button(vid, var("ctx"), text))
            body.append(add_view(var(self._root_id), var(vid)))

        for kind, button_id, text in self._handlers:
            handler_name = f"onClick_{button_id}"
            body.extend(on_click(var(button_id), handler_name=handler_name))

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


def on_click(view, handler_name="onClick", listener_var="listener"):
    """
    Wire a click listener that calls LTest;->handler_name(View)V.
    Requires support class AnaliClickListener to be emitted by toolchain.
    Returns a list of statements.
    """
    return [
        assign(
            listener_var,
            new(
                "Lcom/anali/preview/AnaliClickListener;",
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
