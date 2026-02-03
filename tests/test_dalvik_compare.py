from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from ir.expr import Compare, Var
from dalvik.ir import DIf


def test_dalvik_lowering_of_compare_branch():
    ir = [
        Assign("x", 0),
        Assign("y", 1),
        If(
            Compare("<", Var("x"), Var("y")),
            then=[Assign("x", 2)],
            else_=[Assign("x", 3)],
        ),
        Assign("z", "x"),
    ]

    result = alpha_pipeline(ir)
    dalvik_blocks = result["dalvik"]

    branch_instrs = []
    for block in dalvik_blocks.values():
        for instr in block.instructions:
            if isinstance(instr, DIf):
                branch_instrs.append(instr)

    assert len(branch_instrs) == 1

    instr = branch_instrs[0]
    assert instr.cmp is not None
    assert instr.cond is None

    op, lhs, rhs = instr.cmp
    assert op == "<"
