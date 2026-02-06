# dsl/app.py

from ir.program import ProgramIR
from ir.method import MethodIR
from ir.expr import Call, Const, Var, BinaryOp, Compare, New
from ir.stmt import Return, TryCatch, CallStmt, Throw
from tests.ir_stub import Assign, If, While


def program(methods):
    return ProgramIR(methods)


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
    return New(class_desc, args=args or [], arg_types=arg_types or [])


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
                assign(
                    "tv",
                    new(
                        "Landroid/widget/TextView;",
                        args=[var("ctx")],
                        arg_types=["Landroid/content/Context;"],
                    ),
                ),
                call_stmt(
                    "setText",
                    args=[var("tv"), const(message)],
                    return_type=None,
                    arg_types=["Ljava/lang/CharSequence;"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/TextView;",
                ),
                call_stmt(
                    "setContentView",
                    args=[var("ctx"), var("tv")],
                    return_type=None,
                    arg_types=["Landroid/view/View;"],
                    invoke_kind="virtual",
                    owner="Landroid/app/Activity;",
                ),
                ret(),
            ],
        )
    ])


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
