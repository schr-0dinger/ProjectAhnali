from alpha_pipeline import alpha_pipeline
from ir.expr import Call, Const
from ir.types import AnaliType
from tests.ir_stub import Assign


def test_eta2_typed_call_from_ir():
    ir = [
        Assign(
            "x",
            Call(
                "foo",
                args=[Const(1)],
                return_type=AnaliType.INT,
                arg_types=[AnaliType.INT],
                invoke_kind="static",
                owner="LTest;",
            ),
        )
    ]

    result = alpha_pipeline(ir)
    smali = result["smali"]

    assert "invoke-static {v0}, LTest;->foo(I)I" in smali
    assert "move-result v1" in smali
