from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, assign, const, try_catch


def test_dsl_trycatch_explicit_exception_type():
    prog = program([
        method(
            "main",
            body=[
                try_catch(
                    try_body=[assign("x", const(1))],
                    except_body=[assign("y", const(2))],
                    exception_type="Ljava/lang/Exception;",
                )
            ],
        )
    ])

    result = alpha_pipeline(prog)
    smali = result["smali_class"]
    assert ".catch Ljava/lang/Exception;" in smali
