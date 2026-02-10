from cfg.builder import CFGBuilder
from tests.ir_stub import Assign, If
from ir.expr import BoolOp, Compare, Const, UnaryOp, Var


def test_cfg_if_with_bool_and_short_circuit():
    ir = [
        Assign("x", 0),
        If(
            BoolOp(
                "and",
                Compare("!=", Var("x"), Const(0)),
                Compare("==", Var("x"), Const(1)),
            ),
            then=[Assign("x", 2)],
            else_=[Assign("x", 3)],
        ),
        Assign("z", "x"),
    ]

    cfg = CFGBuilder().build(ir)

    # entry + rhs + then + else + merge + exit
    assert len(cfg.blocks) == 6
    branch_blocks = [b for b in cfg.blocks.values() if b.terminator and b.terminator.kind == "branch"]
    assert len(branch_blocks) == 2


def test_cfg_if_with_not_and_or_short_circuit():
    ir = [
        Assign("x", 0),
        Assign("y", 1),
        If(
            BoolOp(
                "or",
                UnaryOp("not", Compare("==", Var("x"), Const(0))),
                Compare("==", Var("y"), Const(1)),
            ),
            then=[Assign("x", 2)],
            else_=[Assign("x", 3)],
        ),
    ]

    cfg = CFGBuilder().build(ir)

    # entry + rhs + then + else + merge + exit
    assert len(cfg.blocks) == 6
    branch_blocks = [b for b in cfg.blocks.values() if b.terminator and b.terminator.kind == "branch"]
    assert len(branch_blocks) == 2
