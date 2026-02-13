from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, assign, call, const, ret
from ir.types import AhnaliType


def test_dsl_typed_args_and_nonvoid_return():
    prog = program([
        method(
            "inc",
            params=["p"],
            param_types=[AhnaliType.INT],
            return_type=AhnaliType.INT,
            body=[
                ret(const(2)),
            ],
        ),
        method(
            "main",
            return_type=None,
            body=[
                assign(
                    "y",
                    call(
                        "inc",
                        args=[const(1)],
                        return_type=AhnaliType.INT,
                        arg_types=[AhnaliType.INT],
                    ),
                ),
            ],
        ),
    ])

    result = alpha_pipeline(prog)
    smali = result["smali_class"]

    assert ".method public static inc(I)I" in smali
    assert "invoke-static {v0}, LTest;->inc(I)I" in smali
