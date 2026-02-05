from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, assign, call, const, ret
from ir.types import AnaliType


def test_dsl_method_and_typed_call():
    prog = program([
        method(
            "foo",
            return_type=AnaliType.INT,
            body=[
                assign("x", const(1)),
                ret(const(1)),
            ],
        ),
        method(
            "main",
            return_type=None,
            body=[
                assign(
                    "y",
                    call(
                        "foo",
                        args=[],
                        return_type=AnaliType.INT,
                        arg_types=[],
                    ),
                ),
            ],
        ),
    ])

    result = alpha_pipeline(prog)
    smali = result["smali_class"]

    assert ".method public static foo()I" in smali
    assert ".method public static main()V" in smali
    assert "invoke-static {}, LTest;->foo()I" in smali
