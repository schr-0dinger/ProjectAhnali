from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, assign, call, const, ret, var
from ir.types import AnaliType


def test_dsl_method_params_are_bound():
    prog = program([
        method(
            "id",
            params=["p"],
            param_types=[AnaliType.INT],
            return_type=AnaliType.INT,
            body=[
                ret(var("p")),
            ],
        ),
        method(
            "main",
            return_type=None,
            body=[
                assign(
                    "y",
                    call(
                        "id",
                        args=[const(1)],
                        return_type=AnaliType.INT,
                        arg_types=[AnaliType.INT],
                    ),
                ),
            ],
        ),
    ])

    result = alpha_pipeline(prog)
    smali = result["smali_class"]
    assert ".method public static id(I)I" in smali
