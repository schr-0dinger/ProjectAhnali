# tests/test_dce_basic.py

import pytest
from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If
from ir.expr import Compare, Const, BinaryOp, Var
from passes.dce import eliminate_dead_code
from dalvik.ir import DConst, DAdd, DMove


def test_dce_removes_unused_const():
    ir = [
        Assign("x", 1),
    ]

    result = alpha_pipeline(ir)
    dalvik = result["dalvik"]

    eliminate_dead_code(dalvik)

    instrs = [i for b in dalvik.values() for i in b.instructions]

    assert not any(isinstance(i, DConst) for i in instrs)


def test_dce_removes_unused_binaryop():
    ir = [
        Assign("x", 1),
        Assign("y", BinaryOp("+", Var("x"), Const(2))),
    ]

    result = alpha_pipeline(ir)
    dalvik = result["dalvik"]

    eliminate_dead_code(dalvik)

    instrs = [i for b in dalvik.values() for i in b.instructions]

    assert not any(isinstance(i, DAdd) for i in instrs)


def test_dce_preserves_used_binaryop():
    """
    Ensure BinaryOp is preserved if its result is used by a LIVE instruction.
    """
    ir = [
        Assign("x", 1),
        Assign("y", BinaryOp("+", Var("x"), Const(2))),
        Assign("z", "y"),
        # ANCHOR: both branches empty, but condition uses z
        If(Compare("==", Var("z"), Const(0)), [], []),
    ]

    result = alpha_pipeline(ir)
    dalvik = result["dalvik"]

    eliminate_dead_code(dalvik)
    eliminate_dead_code(dalvik)

    instrs = [i for b in dalvik.values() for i in b.instructions]

    assert any(isinstance(i, DAdd) for i in instrs)


def test_dce_does_not_remove_phi_targets():
    """
    Ensure that variables resolved via Phi moves are not deleted
    if the result is used.
    """
    ir = [
        Assign("x", 1),
        If(
            Compare("==", Var("x"), Const(1)),
            [Assign("y", 2)],
            [Assign("y", 3)],
        ),
        Assign("z", "y"),
        # ANCHOR: use z
        If(Compare("==", Var("z"), Const(5)), [], []),
    ]

    result = alpha_pipeline(ir)
    dalvik = result["dalvik"]

    eliminate_dead_code(dalvik)

    instrs = [i for b in dalvik.values() for i in b.instructions]

    assert any(isinstance(i, DMove) for i in instrs)


def test_dce_runs_to_fixpoint():
    """
    Verify that DCE recursively deletes dead chains: a -> b -> c (dead)
    """
    ir = [
        Assign("a", 1),
        Assign("b", "a"),
        Assign("c", "b"),
    ]

    result = alpha_pipeline(ir)
    dalvik = result["dalvik"]

    eliminate_dead_code(dalvik)

    instrs = [i for b in dalvik.values() for i in b.instructions]

    # Only return-void should remain
    assert len(instrs) <= 1
