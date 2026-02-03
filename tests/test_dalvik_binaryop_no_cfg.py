from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign
from ir.expr import BinaryOp, Var, Const
from dalvik.ir import DIf


def test_binaryop_does_not_create_control_flow():
    ir = [
        Assign("x", 1),
        Assign(
            "y",
            BinaryOp("*", Var("x"), Const(3))
        ),
        Assign("z", "y"),
    ]

    result = alpha_pipeline(ir)
    dalvik_blocks = result["dalvik"]

    for block in dalvik_blocks.values():
        for instr in block.instructions:
            # Arithmetic must not introduce branching
            assert not isinstance(instr, DIf)
