import pytest

from alpha_pipeline import alpha_pipeline
from ir.expr import Call
from ir.stmt import Throw
from ir.expr import Var
from ir.types import AhnaliType
from tests.ir_stub import Assign, TryCatch


def test_throw_lowering_emits_throw():
    ir = [
        Assign(
            "e",
            Call(
                "make",
                args=[],
                return_type=AhnaliType.OBJECT,
                arg_types=[],
            ),
        ),
        TryCatch(
            try_body=[Throw(Var("e"))],
            except_body=[Assign("x", 1)],
        ),
    ]

    result = alpha_pipeline(ir)
    smali = result["smali"]
    assert "throw v" in smali


def test_throw_requires_object_type():
    ir = [
        Assign(
            "e",
            Call(
                "make",
                args=[],
                return_type=AhnaliType.INT,
                arg_types=[],
            ),
        ),
        TryCatch(
            try_body=[Throw(Var("e"))],
            except_body=[Assign("x", 1)],
        ),
    ]

    with pytest.raises(RuntimeError):
        alpha_pipeline(ir)
