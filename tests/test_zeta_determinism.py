import re

from dsl.app import (
    assign,
    binary,
    compare,
    if_,
    var,
    const,
    call,
)
from alpha_pipeline import alpha_pipeline
from ir.types import AnaliType


def _build_pressure_body():
    body = []

    # Seed prevents const-prop from erasing pressure.
    body.append(
        assign(
            "seed",
            call(
                "seed",
                args=[],
                return_type=AnaliType.INT,
                arg_types=[],
            ),
        )
    )

    for i in range(22):
        body.append(assign(f"a{i}", binary("+", var("seed"), const(i))))

    args = [var(f"a{i}") for i in range(8)]
    arg_types = [AnaliType.INT] * len(args)

    body.append(
        if_(
            compare("<", var("a0"), const(10)),
            then=[
                assign(
                    "r",
                    call(
                        "foo",
                        args=args,
                        return_type=AnaliType.INT,
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
                        return_type=AnaliType.INT,
                        arg_types=arg_types,
                    ),
                ),
            ],
        )
    )

    # Merge pressure and force a wide call.
    call_args = [var("r")] + [var(f"a{i}") for i in range(20)]
    call_types = [AnaliType.INT] * len(call_args)
    body.append(
        assign(
            "y",
            call(
                "bar",
                args=call_args,
                return_type=AnaliType.INT,
                arg_types=call_types,
            ),
        )
    )
    body.append(if_(compare("!=", var("y"), const(0)), [], []))

    return body


def _interval_signature(allocator):
    sig = []
    for i in allocator.intervals:
        sig.append(
            (
                repr(i.value),
                i.reg,
                i.spilled,
                i.stack_slot,
            )
        )
    return sorted(sig)


def _normalize_smali(smali):
    # Normalize generated labels that include numeric suffixes.
    return re.sub(r":[A-Za-z_]+\d+", ":L", smali)


def test_zeta_spill_and_determinism():
    r1 = alpha_pipeline(_build_pressure_body())
    r2 = alpha_pipeline(_build_pressure_body())

    # 1. Spills must occur under pressure.
    spilled = [i for i in r1["regalloc"].intervals if i.spilled]
    assert spilled, "Expected spills under register pressure, found none"

    # 2. Determinism: regalloc + emitted Smali must match across runs.
    assert _interval_signature(r1["regalloc"]) == _interval_signature(r2["regalloc"])
    assert _normalize_smali(r1["smali_method"]) == _normalize_smali(r2["smali_method"])
