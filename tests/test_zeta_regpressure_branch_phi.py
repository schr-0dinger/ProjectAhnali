import pytest

from dsl.app import (
    assign,
    binary,
    compare,
    if_,
    ret,
    var,
    const,
    call,
)
from alpha_pipeline import alpha_pipeline
from ir.types import AhnaliType


def test_zeta_spill_across_branch_phi():
    """
    ZETA-2 stress test:
    - Force >16 live values before a branch
    - Ensure spills survive across phi merge
    - Ensure no SSA value is used without reload
    """

    body = []

    # --- Create register pressure ---
    # a0..a17 => 18 live SSA values
    body.append(
        assign(
            "seed",
            call(
                "seed",
                args=[],
                return_type=AhnaliType.INT,
                arg_types=[],
            ),
        )
    )
    for i in range(18):
        body.append(assign(f"a{i}", binary("+", var("seed"), const(i))))

    # --- Branch that defines x on both sides ---
    body.append(
        if_(
            compare("<", var("a0"), const(10)),
            then=[
                assign("x", binary("+", var("a1"), var("a2"))),
            ],
            else_=[
                assign("x", binary("+", var("a3"), var("a4"))),
            ],
        )
    )

    # --- Force x and many a's to be live after merge via a typed call ---
    call_args = [var("x")] + [var(f"a{i}") for i in range(18)]
    call_types = [AhnaliType.INT] * len(call_args)
    body.append(
        assign(
            "y",
            call(
                "bar",
                args=call_args,
                return_type=AhnaliType.INT,
                arg_types=call_types,
            ),
        )
    )
    body.append(if_(compare("!=", var("y"), const(0)), [], []))

    result = alpha_pipeline(body)

    dalvik_blocks = result["dalvik"]
    allocator = result["regalloc"]

    # -------------------------------------------------
    # Assertions
    # -------------------------------------------------

    # 1. Ensure spills actually happened
    spilled = [i for i in allocator.intervals if i.spilled]
    assert spilled, "Expected spills under register pressure, found none"

    # 2. No SSA value used without having a register or spill slot
    for block in dalvik_blocks.values():
        for instr in block.instructions:
            for attr in ("src", "lhs", "rhs", "cond", "value"):
                if hasattr(instr, attr):
                    d = getattr(instr, attr)
                    if d is None:
                        continue
                    if hasattr(d, "reg"):
                        assert (
                            d.reg is not None
                        ), f"SSA value {d.ssa} used without register after allocation"

            if hasattr(instr, "args"):
                for d in instr.args:
                    if hasattr(d, "reg"):
                        assert (
                            d.reg is not None
                        ), f"Call argument {d.ssa} used without register"

    # 3. Phi lowering correctness:
    #    Phi must lower to DMove before use
    phi_moves = []
    for block in dalvik_blocks.values():
        for instr in block.instructions:
            if instr.__class__.__name__ == "DMove":
                phi_moves.append(instr)

    assert phi_moves, "Expected phi-lowering DMove instructions, found none"

    # 4. Ensure a branch remains after lowering
    smali = result["smali_method"]
    assert "if-" in smali, "Branch instruction missing in Smali output"
