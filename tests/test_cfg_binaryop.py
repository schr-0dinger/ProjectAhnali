from cfg.builder import CFGBuilder
from tests.ir_stub import Assign
from ir.expr import BinaryOp, Var, Const


def test_cfg_accepts_binaryop_assignment():
    ir = [
        Assign("x", 1),
        Assign(
            "y",
            BinaryOp("+", Var("x"), Const(2))
        ),
        Assign("z", "y"),
    ]

    cfg = CFGBuilder().build(ir)

    # Straight-line code → exactly entry + exit
    assert len(cfg.blocks) == 2

    entry = cfg.entry
    exit = cfg.exit

    # All statements should be in entry block
    assert len(entry.statements) == 3
    assert entry.terminator is not None
    assert exit.terminator is not None
