from __future__ import annotations

from ir.expr import Call


DEFAULT_IGNORED_RETURN_ALLOWLIST: set[tuple[str, str, str]] = {
    ("Landroid/util/Log;", "d", "static"),
    ("Landroid/util/Log;", "i", "static"),
    ("Landroid/util/Log;", "w", "static"),
    ("Landroid/util/Log;", "e", "static"),
}

_custom_allowlist: set[tuple[str, str, str]] = set()


def set_ignored_return_allowlist(items: set[tuple[str, str, str]] | None) -> None:
    global _custom_allowlist
    _custom_allowlist = set(items or [])


def allow_ignored_return(expr: Call) -> bool:
    key = (expr.owner, expr.func_name, expr.invoke_kind)
    return key in DEFAULT_IGNORED_RETURN_ALLOWLIST or key in _custom_allowlist
