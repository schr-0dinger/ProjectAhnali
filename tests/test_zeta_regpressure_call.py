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


def test_zeta_spill_across_branch_call():
    """
    ZETA stress test:
    - Force >16 live values before a call in both branches
    - Ensure spills survive across call path
    - Ensure all call args and uses have registers after allocation
    """

    body = []

    # Create register pressure: a0..a20 => 21 live SSA values
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
    for i in range(21):
        body.append(assign(f"a{i}", binary("+", var("seed"), const(i))))

    args = [var(f"a{i}") for i in range(8)]
    arg_types = [AhnaliType.INT] * len(args)

    body.append(
        if_(
            compare("<", var("a0"), const(10)),
            then=[
                assign(
                    "r",
                    call(
                        "foo",
                        args=args,
                        return_type=AhnaliType.INT,
                        arg_types=arg_types,
                    ),
                ),
            ],
            else_=[
                assign(
                    "r",
                    call(
                        "foo",
                        args=args,
                        return_type=AhnaliType.INT,
                        arg_types=arg_types,
                    ),
                ),
            ],
        )
    )

    # Force many live values across the merge via a second call
    call_args = [var("r")] + [var(f"a{i}") for i in range(20)]
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

    # 1. Ensure spills happened under pressure
    spilled = [i for i in allocator.intervals if i.spilled]
    assert spilled, "Expected spills under register pressure, found none"

    # 2. Ensure DInvoke exists
    assert any(
        instr.__class__.__name__ == "DInvoke"
        for b in dalvik_blocks.values()
        for instr in b.instructions
    ), "Expected DInvoke in lowered Dalvik"

    # 3. No SSA value used without a register
    for block in dalvik_blocks.values():
        for instr in block.instructions:
            for attr in ("src", "lhs", "rhs", "cond", "value"):
                if hasattr(instr, attr):
                    d = getattr(instr, attr)
                    if d is None:
                        continue
                    if hasattr(d, "reg"):
                        assert d.reg is not None, f"SSA value {d.ssa} used without register"

            if hasattr(instr, "args"):
                for d in instr.args:
                    if hasattr(d, "reg"):
                        assert d.reg is not None, f"Call argument {d.ssa} used without register"
