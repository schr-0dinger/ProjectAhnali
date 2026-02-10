import re

from alpha_pipeline import alpha_pipeline
from dsl.ir_helpers import program, method, assign, const, var, ret, primitive_cast, call


def _compile_smali(method_ir):
    prog = program([method_ir])
    result = alpha_pipeline(prog)
    return result["smali_class"]


def test_return_wide_from_primitive_cast():
    m = method(
        "main",
        return_type="J",
        body=[
            assign("x", const(1)),
            assign("y", primitive_cast(var("x"), "I", "J")),
            ret(var("y")),
        ],
    )
    smali = _compile_smali(m)
    assert "return-wide" in smali


def test_invoke_move_result_wide():
    m = method(
        "main",
        return_type="J",
        body=[
            assign(
                "x",
                call(
                    "foo",
                    args=[],
                    return_type="J",
                    arg_types=[],
                    invoke_kind="static",
                    owner="LTest;",
                ),
            ),
            ret(var("x")),
        ],
    )
    smali = _compile_smali(m)
    assert re.search(r"invoke-static \{\}, LTest;->foo\(\)J", smali)
    assert "move-result-wide" in smali
    assert "return-wide" in smali
