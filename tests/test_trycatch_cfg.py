from cfg.builder import CFGBuilder
from tests.ir_stub import TryCatch, Assign


def test_trycatch_populates_exceptional_edges():
    ir = [
        TryCatch(
            try_body=[Assign("x", 1)],
            except_body=[Assign("y", 2)],
        )
    ]

    cfg = CFGBuilder().build(ir)

    assert len(cfg.try_regions) == 1
    start, end, handler, exc_type = cfg.try_regions[0]
    assert exc_type is None
    assert handler in start.exceptional_successors
