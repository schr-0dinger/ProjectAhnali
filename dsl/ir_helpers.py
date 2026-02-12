from ir.expr import BinaryOp, BoolOp, Call, Compare, Const, New, NewArray, PrimitiveCast, StaticFieldGet, UnaryOp, Var
from ir.field import StaticField
from ir.method import MethodIR
from ir.program import ProgramIR
from ir.stmt import CallStmt, Return, StaticFieldSet, Throw, TryCatch
from tests.ir_stub import Assign, If, While

from .android.signatures import _CTOR_SIGS, _resolve_signature


def program(
    methods,
    fields=None,
    support_classes=None,
    method_class_map=None,
    lint_warnings=None,
    resources=None,
    resource_ids=None,
    resource_colors=None,
    resource_color_ids=None,
    resource_dimens=None,
    resource_dimen_ids=None,
    resource_styles=None,
    resource_style_ids=None,
):
    return ProgramIR(
        methods,
        fields=fields or [],
        support_classes=support_classes or [],
        method_class_map=method_class_map or {},
        lint_warnings=lint_warnings or [],
        resources=resources or {},
        resource_ids=resource_ids or {},
        resource_colors=resource_colors or {},
        resource_color_ids=resource_color_ids or {},
        resource_dimens=resource_dimens or {},
        resource_dimen_ids=resource_dimen_ids or {},
        resource_styles=resource_styles or {},
        resource_style_ids=resource_style_ids or {},
    )


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


def new(class_desc, args=None, arg_types=None):
    if arg_types is None:
        try:
            _, arg_types = _resolve_signature(
                "<init>",
                args or [],
                return_type=None,
                arg_types=None,
                invoke_kind="direct",
                owner=class_desc,
            )
        except RuntimeError:
            arg_types = None
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


def instance_of(value, desc):
    from ir.expr import InstanceOf
    return InstanceOf(value, desc)


def new_array(length, elem_desc, array_desc=None):
    return NewArray(length=length, elem_desc=elem_desc, array_desc=array_desc)


def filled_new_array(args, elem_desc, array_desc=None):
    from ir.expr import FilledNewArray
    return FilledNewArray(args=args, elem_desc=elem_desc, array_desc=array_desc)


def array_length(array):
    from ir.expr import ArrayLength
    return ArrayLength(array)


def primitive_cast(value, from_desc, to_desc):
    return PrimitiveCast(value=value, from_desc=from_desc, to_desc=to_desc)


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
        if key in ("match", "match_parent", "fill", "max", "max_width", "max_height"):
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
    return event_handler(
        name,
        body,
        params=["view"],
        param_types=["Landroid/view/View;"],
    )


def event_handler(name, body, *, params=None, param_types=None, return_type=None):
    return method(
        name,
        params=params or [],
        param_types=param_types or [],
        return_type=return_type,
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


def on_change_view(view, handler_name="onChange", listener_var="listener", listener_class_desc="Lcom/anali/preview/AnaliChangeListener;"):
    return [
        assign(
            listener_var,
            new(
                listener_class_desc,
                args=[],
            ),
        ),
        call_stmt(
            "setOnCheckedChangeListener",
            args=[view, var(listener_var)],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/widget/CompoundButton;",
        ),
    ]


def on_text_change_view(view, handler_name="onTextChange", listener_var="listener", listener_class_desc="Lcom/anali/preview/AnaliTextChangeListener;"):
    return [
        assign(
            listener_var,
            new(
                listener_class_desc,
                args=[],
            ),
        ),
        call_stmt(
            "addTextChangedListener",
            args=[view, var(listener_var)],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/widget/TextView;",
        ),
    ]


def on_item_selected_view(view, handler_name="onItemSelected", listener_var="listener", listener_class_desc="Lcom/anali/preview/AnaliItemSelectedListener;"):
    return [
        assign(
            listener_var,
            new(
                listener_class_desc,
                args=[],
            ),
        ),
        call_stmt(
            "setOnItemSelectedListener",
            args=[view, var(listener_var)],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/widget/AdapterView;",
        ),
    ]


def on_focus_change_view(view, handler_name="onFocusChange", listener_var="listener", listener_class_desc="Lcom/anali/preview/AnaliFocusChangeListener;"):
    return [
        assign(
            listener_var,
            new(
                listener_class_desc,
                args=[],
            ),
        ),
        call_stmt(
            "setOnFocusChangeListener",
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

def bool_and(left, right):
    return BoolOp("and", left, right)

def bool_or(left, right):
    return BoolOp("or", left, right)

def bool_not(value):
    return UnaryOp("not", value)


def try_catch(try_body, except_body=None, exception_type=None, handlers=None):
    return TryCatch(try_body, except_body, exception_type, handlers)


def throw(value):
    return Throw(value)


def navigate(target):
    from dsl.ast import _StmtNavigate
    return _StmtNavigate(target)


def back():
    from dsl.ast import _StmtBack
    return _StmtBack()


def replace(target):
    from dsl.ast import _StmtReplace
    return _StmtReplace(target)


def request_permissions(*permissions, request_code=0):
    from dsl.ast import _StmtRequestPermissions
    if len(permissions) == 1 and isinstance(permissions[0], (list, tuple, set)):
        permissions = tuple(permissions[0])
    return _StmtRequestPermissions(list(permissions), request_code=request_code)


def request_permission(permission, request_code=0):
    return request_permissions(permission, request_code=request_code)
