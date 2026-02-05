from cfg.graph import ControlFlowGraph
from cfg.builder import Terminator
from cfg.validate import validate_cfg
from cfg.dominance import compute_dominators


def _build_linear_cfg():
    cfg = ControlFlowGraph()

    b0 = cfg.new_block()
    b1 = cfg.new_block()
    b2 = cfg.new_block()

    cfg.set_entry(b0)
    cfg.set_exit(b2)

    b0.terminator = Terminator("jump", target=b1)
    b0.add_successor(b1)

    b1.terminator = Terminator("jump", target=b2)
    b1.add_successor(b2)

    b2.terminator = Terminator("return")

    return cfg, b0, b1, b2


def test_exceptional_edges_do_not_affect_validation():
    cfg, b0, b1, b2 = _build_linear_cfg()

    # Add an exceptional edge; validation should still pass
    b1.add_exceptional_successor(b2)

    assert validate_cfg(cfg)


def test_exceptional_edges_are_ignored_by_dominance():
    cfg, b0, b1, b2 = _build_linear_cfg()

    # Exceptional edge that would bypass b1 if it were considered
    b0.add_exceptional_successor(b2)

    dom = compute_dominators(cfg)

    # Dominance should still be computed over normal edges only
    assert b1 in dom[b2]
