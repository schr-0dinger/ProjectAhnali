# test/test_programir.py

from alpha_pipeline import alpha_pipeline
from ir.method import MethodIR
from ir.program import ProgramIR
from tests.ir_stub import Assign, If


def test_programir_register_spaces_are_isolated():
    methods = [
        MethodIR(name="foo", body=[Assign("x", 1), If("x", [], [])]),
        MethodIR(name="bar", body=[Assign("y", 2), If("y", [], [])]),
    ]

    result = alpha_pipeline(ProgramIR(methods))
    foo_alloc = result["methods"]["foo"]["regalloc"]
    bar_alloc = result["methods"]["bar"]["regalloc"]

    foo_regs = {i.reg for i in foo_alloc.intervals if i.reg is not None}
    bar_regs = {i.reg for i in bar_alloc.intervals if i.reg is not None}

    assert foo_regs == bar_regs
    assert 0 in foo_regs
