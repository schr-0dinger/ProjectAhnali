import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, assign, call, call_stmt, const, ret
from ir.types import AhnaliType
from passes.type_inference import TypeInferenceError
from passes.type_verify import TypeVerificationError


def test_dsl_call_arg_types_length_mismatch_rejected():
    prog = program([
        method(
            "main",
            return_type=None,
            body=[
                assign(
                    "y",
                    call(
                        "foo",
                        args=[const(1)],
                        return_type=AhnaliType.INT,
                        arg_types=[],
                    ),
                ),
            ],
        )
    ])

    with pytest.raises((RuntimeError, TypeVerificationError, TypeInferenceError)):
        alpha_pipeline(prog)


def test_dsl_void_call_cannot_assign():
    prog = program([
        method(
            "main",
            return_type=None,
            body=[
                assign(
                    "y",
                    call(
                        "foo",
                        args=[],
                        return_type=None,
                        arg_types=[],
                    ),
                ),
            ],
        )
    ])

    with pytest.raises((RuntimeError, TypeVerificationError, TypeInferenceError)):
        alpha_pipeline(prog)


def test_dsl_nonvoid_call_must_assign():
    prog = program([
        method(
            "main",
            return_type=None,
            body=[
                call_stmt(
                    "foo",
                    args=[],
                    return_type=AhnaliType.INT,
                    arg_types=[],
                ),
            ],
        )
    ])

    with pytest.raises((RuntimeError, TypeVerificationError, TypeInferenceError)):
        alpha_pipeline(prog)


def test_dsl_void_method_cannot_return_value():
    prog = program([
        method(
            "main",
            return_type=None,
            body=[
                ret(const(1)),
            ],
        )
    ])

    with pytest.raises((RuntimeError, TypeVerificationError, TypeInferenceError)):
        alpha_pipeline(prog)


def test_dsl_nonvoid_method_must_return_value():
    prog = program([
        method(
            "main",
            return_type=AhnaliType.INT,
            body=[
                ret(),
            ],
        )
    ])

    with pytest.raises((RuntimeError, TypeVerificationError, TypeInferenceError)):
        alpha_pipeline(prog)
