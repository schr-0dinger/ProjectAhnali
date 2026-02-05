import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, assign, const, try_catch


def test_dsl_trycatch_empty_try_rejected():
    prog = program([
        method(
            "main",
            body=[
                try_catch(
                    try_body=[],
                    except_body=[assign("x", const(1))],
                )
            ],
        )
    ])

    with pytest.raises(RuntimeError):
        alpha_pipeline(prog)


def test_dsl_trycatch_invalid_exception_type_rejected():
    prog = program([
        method(
            "main",
            body=[
                try_catch(
                    try_body=[assign("x", const(1))],
                    except_body=[assign("y", const(2))],
                    exception_type="BadType",
                )
            ],
        )
    ])

    with pytest.raises(RuntimeError):
        alpha_pipeline(prog)
