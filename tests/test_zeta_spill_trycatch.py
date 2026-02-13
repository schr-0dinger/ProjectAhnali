from dsl.app import (
    assign,
    binary,
    compare,
    if_,
    var,
    const,
    call,
    try_catch,
    throw,
)
from alpha_pipeline import alpha_pipeline
from ir.types import AhnaliType


def test_zeta_spill_across_trycatch_edges():
    body = []

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
    for i in range(19):
        body.append(assign(f"a{i}", binary("+", var("seed"), const(i))))

    call_args = [var("a0")] + [var(f"a{i}") for i in range(1, 19)]
    call_types = [AhnaliType.INT] * len(call_args)

    body.append(
        try_catch(
            try_body=[
                assign("x", binary("+", var("a1"), var("a2"))),
                assign(
                    "y",
                    call(
                        "bar",
                        args=call_args,
                        return_type=AhnaliType.INT,
                        arg_types=call_types,
                    ),
                ),
                if_(compare("!=", var("y"), const(0)), [], []),
                assign(
                    "e",
                    call(
                        "make",
                        args=[],
                        return_type=AhnaliType.OBJECT,
                        arg_types=[],
                    ),
                ),
                throw(var("e")),
            ],
            handlers=[
                (None, [assign("h", const(1))]),
            ],
        )
    )

    result = alpha_pipeline(body)
    allocator = result["regalloc"]
    dalvik_blocks = result["dalvik"]
    cfg = result["cfg"]

    assert cfg.try_regions, "Expected try regions in CFG"

    spilled = [i for i in allocator.intervals if i.spilled]
    assert spilled, "Expected spills under register pressure, found none"

    saw_throw = False
    for block in dalvik_blocks.values():
        for instr in block.instructions:
            if instr.__class__.__name__ == "DThrow":
                saw_throw = True
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

    assert saw_throw, "Expected DThrow in lowered Dalvik"


def test_zeta_spill_across_nested_trycatch_and_handlers():
    body = []

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
    for i in range(20):
        body.append(assign(f"a{i}", binary("+", var("seed"), const(i))))

    call_args = [var("a0")] + [var(f"a{i}") for i in range(1, 20)]
    call_types = [AhnaliType.INT] * len(call_args)

    body.append(
        try_catch(
            try_body=[
                try_catch(
                    try_body=[
                        assign("x", binary("+", var("a1"), var("a2"))),
                        assign(
                            "y",
                            call(
                                "bar",
                                args=call_args,
                                return_type=AhnaliType.INT,
                                arg_types=call_types,
                            ),
                        ),
                        if_(compare("!=", var("y"), const(0)), [], []),
                        assign(
                            "e",
                            call(
                                "make",
                                args=[],
                                return_type=AhnaliType.OBJECT,
                                arg_types=[],
                            ),
                        ),
                        throw(var("e")),
                    ],
                    handlers=[
                        ("Ljava/lang/RuntimeException;", [assign("h0", const(0))]),
                    ],
                ),
            ],
            handlers=[
                (None, [assign("h1", const(1))]),
            ],
        )
    )

    result = alpha_pipeline(body)
    allocator = result["regalloc"]
    dalvik_blocks = result["dalvik"]
    cfg = result["cfg"]

    assert len(cfg.try_regions) >= 2, "Expected nested try regions in CFG"

    spilled = [i for i in allocator.intervals if i.spilled]
    assert spilled, "Expected spills under register pressure, found none"

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
