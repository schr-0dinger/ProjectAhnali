from alpha_pipeline import alpha_pipeline
from ir.method import MethodIR
from ir.program import ProgramIR
from tests.ir_stub import Assign


def test_program_ir_multiple_methods():
    methods = [
        MethodIR(name="foo", body=[Assign("x", 1)]),
        MethodIR(name="bar", body=[Assign("y", 2)]),
    ]

    program = ProgramIR(methods)
    result = alpha_pipeline(program)

    assert "methods" in result
    assert set(result["methods"].keys()) == {"foo", "bar"}
    assert "smali_class" in result
    assert ".method public static foo()V" in result["smali_class"]
    assert ".method public static bar()V" in result["smali_class"]
