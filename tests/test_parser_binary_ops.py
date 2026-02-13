import ast

from dsl.ast import _ExprBinary
from dsl.parser import _parse_expr


def _parse(src):
    return _parse_expr(ast.parse(src, mode="eval").body)


def test_parser_accepts_extended_binary_ops():
    assert _parse("a & b").op == "&"
    assert _parse("a | b").op == "|"
    assert _parse("a ^ b").op == "^"
    assert _parse("a << 1").op == "<<"
    assert _parse("a >> 1").op == ">>"
    assert _parse("a // 2").op == "/"


def test_parser_accepts_ushr_helper_call():
    expr = _parse("ushr(a, 3)")
    assert isinstance(expr, _ExprBinary)
    assert expr.op == ">>>"
