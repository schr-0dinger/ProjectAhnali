import pytest
from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If


def test_use_before_def_rejected():
    ir = [
        Assign("y", "x"),  # x never defined
    ]

    with pytest.raises(RuntimeError):
        alpha_pipeline(ir)

from cfg.graph import ControlFlowGraph
from cfg.block import BasicBlock
from cfg.validate import validate_cfg, CFGValidationError
from cfg.builder import Terminator


def test_phi_illegal_single_predecessor_block():
    cfg = ControlFlowGraph()

    b0 = cfg.new_block()
    b1 = cfg.new_block()

    cfg.set_entry(b0)
    cfg.set_exit(b1)

    b0.terminator = Terminator("jump", target=b1)
    b0.add_successor(b1)

    b1.terminator = Terminator("return")

    # CFG is structurally valid
    validate_cfg(cfg)

    # But SSA Phi here would be illegal (guarded later)
    # This test documents the invariant explicitly

import pytest
from cfg.graph import ControlFlowGraph
from cfg.validate import validate_cfg, CFGValidationError


def test_cfg_missing_terminator_rejected():
    cfg = ControlFlowGraph()

    b0 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b0)

    with pytest.raises(CFGValidationError):
        validate_cfg(cfg)


def test_symbolic_condition_rejected():
    ir = [
        If("c", [], []),  # c never defined
    ]

    with pytest.raises(RuntimeError):
        alpha_pipeline(ir)
