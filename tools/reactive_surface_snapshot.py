#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from dsl.parser_dispatch import EXPR_FN_BY_DOMAIN, STATEMENT_FN_BY_DOMAIN
from dsl.runtime.diagnostics import emit_cli_error, emit_cli_info


REACTIVE_SURFACE_ABI_VERSION = "1.0.0"


def build_reactive_surface_snapshot() -> dict[str, object]:
    return {
        "abi_version": REACTIVE_SURFACE_ABI_VERSION,
        "snapshot_schema": "reactive_surface_v1",
        "mode_contract": {
            "default": "static",
            "allowed": ["static", "reactive"],
            "static_default": True,
            "reactive_opt_in": True,
            "no_implicit_diff": True,
        },
        "dsl_symbols": {
            "statements": [
                "observable",
                "set_observable",
                "derived",
                "listen",
                "bind_text",
            ],
            "expressions": [
                "observable_get",
            ],
        },
        "parser_dispatch": {
            "statement_aliases": sorted(STATEMENT_FN_BY_DOMAIN.get("hybrid", set())),
            "expression_aliases": sorted(EXPR_FN_BY_DOMAIN.get("hybrid", set())),
        },
        "ast_contract": {
            "statement_nodes": [
                "_StmtReactiveObservable",
                "_StmtReactiveSet",
                "_StmtReactiveDerived",
                "_StmtReactiveListen",
                "_StmtReactiveBindText",
            ],
            "expression_nodes": [
                "_ExprReactiveGet",
            ],
        },
    }


def _snapshot_json(snapshot: dict[str, object]) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True) + "\n"


def _check_snapshot(snapshot_path: Path, actual: dict[str, object]) -> tuple[bool, str]:
    if not snapshot_path.exists():
        return False, f"Snapshot file not found: {snapshot_path}"
    try:
        expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON in snapshot file {snapshot_path}: {exc}"
    if expected == actual:
        return True, ""

    expected_text = _snapshot_json(expected)
    actual_text = _snapshot_json(actual)
    diff = "\n".join(
        difflib.unified_diff(
            expected_text.splitlines(),
            actual_text.splitlines(),
            fromfile=str(snapshot_path),
            tofile="generated",
            lineterm="",
        )
    )
    message = (
        "Reactive surface snapshot drift detected.\n"
        f"Rebuild snapshot with: PYTHONPATH=. python tools/reactive_surface_snapshot.py --out {snapshot_path}\n"
        f"{diff}"
    )
    return False, message


def check_reactive_surface_snapshot(snapshot_path: Path) -> tuple[bool, str]:
    return _check_snapshot(snapshot_path, build_reactive_surface_snapshot())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate/check frozen reactive surface snapshot for mode-gated DSL APIs."
    )
    parser.add_argument(
        "--out",
        default="cfg/reactive_surface_snapshot_v1.json",
        help="Snapshot file path (default: cfg/reactive_surface_snapshot_v1.json)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check generated snapshot against --out and fail on drift.",
    )
    args = parser.parse_args(argv)

    out_path = Path(args.out)
    snapshot = build_reactive_surface_snapshot()

    if args.check:
        ok, message = _check_snapshot(out_path, snapshot)
        if not ok:
            emit_cli_error(message, code="ReactiveSurfaceSnapshotError")
            return 1
        emit_cli_info(
            f"Reactive surface snapshot is up to date: {out_path}",
            code="ReactiveSurfaceSnapshotOK",
        )
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_snapshot_json(snapshot), encoding="utf-8")
    emit_cli_info(
        f"Wrote reactive surface snapshot: {out_path}",
        code="ReactiveSurfaceSnapshotWrite",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
