import re

from alpha_pipeline import alpha_pipeline
from dsl.app import (
    program,
    method,
    assign,
    binary,
    compare,
    if_,
    var,
    const,
    call,
    ret,
)
from ir.types import AhnaliType


def _normalize_smali(smali):
    return re.sub(r":[A-Za-z_]+\d+", ":L", smali)


def _build_program():
    m1_body = [
        assign(
            "seed",
            call(
                "seed",
                args=[],
                return_type=AhnaliType.INT,
                arg_types=[],
            ),
        ),
    ]
    for i in range(12):
        m1_body.append(assign(f"a{i}", binary("+", var("seed"), const(i))))
    m1_body.append(if_(compare("<", var("a0"), const(3)), [], []))
    m1_body.append(ret(var("a1")))

    m2_body = [
        assign(
            "seed",
            call(
                "seed",
                args=[],
                return_type=AhnaliType.INT,
                arg_types=[],
            ),
        ),
    ]
    for i in range(10):
        m2_body.append(assign(f"b{i}", binary("+", var("seed"), const(i))))
    m2_body.append(if_(compare("!=", var("b0"), const(0)), [], []))
    m2_body.append(ret(var("b1")))

    return program([
        method("alpha", return_type=AhnaliType.INT, body=m1_body),
        method("beta", return_type=AhnaliType.INT, body=m2_body),
    ])


def test_zeta_determinism_whole_class():
    prog = _build_program()

    r1 = alpha_pipeline(prog)
    r2 = alpha_pipeline(_build_program())

    assert _normalize_smali(r1["smali_class"]) == _normalize_smali(r2["smali_class"])
