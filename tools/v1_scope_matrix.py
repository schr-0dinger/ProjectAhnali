#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from dsl.runtime.diagnostics import emit_cli_error, emit_cli_info

SCHEMA_VERSION = "v1_scope_matrix/1"
DEFAULT_MASTERPLAN = "Masterplan_All_In_One.md"
DEFAULT_MATRIX = "cfg/v1_scope_matrix.yaml"
DEFAULT_SCOPE_FLAGS = {
    "static_default": True,
    "reactive_opt_in": True,
    "no_implicit_diff": True,
}

_RE_SECTION = re.compile(r"^###\s+(8\.\d+)\s+")
_RE_MARKER = re.compile(r"^\s*-\s*(⚠️|❌)\s*(.+?)\s*$")
_RE_MILESTONE = re.compile(r"^###\s+Milestone\s+([A-Z]):")


def _slugify(value: str) -> str:
    out = value.lower()
    out = out.replace("`", "")
    out = out.replace("(", " ")
    out = out.replace(")", " ")
    out = out.replace("/", " ")
    out = out.replace("+", " ")
    out = re.sub(r"[^a-z0-9]+", "-", out).strip("-")
    return out or "item"


def _extract_inventory_window(lines: list[str]) -> tuple[int, int]:
    start = -1
    end = -1
    for i, raw in enumerate(lines):
        if raw.startswith("## 8) Ahnali API Master Inventory"):
            start = i
            continue
        if start >= 0 and raw.startswith("## 13)"):
            end = i
            break
    if start < 0 or end < 0:
        raise RuntimeError("Unable to locate API inventory window (## 8 ... ## 13) in masterplan")
    return start, end


def _extract_inventory_items(masterplan: Path) -> list[dict[str, Any]]:
    lines = masterplan.read_text(encoding="utf-8").splitlines()
    start, end = _extract_inventory_window(lines)
    seen: dict[str, int] = {}
    section = ""
    out: list[dict[str, Any]] = []

    for idx in range(start, end):
        line = lines[idx]
        section_match = _RE_SECTION.match(line)
        if section_match:
            section = section_match.group(1)
            continue
        if not section:
            continue
        marker_match = _RE_MARKER.match(line)
        if not marker_match:
            continue
        marker = marker_match.group(1)
        label = marker_match.group(2).lstrip("\ufe0f ").strip()
        key = f"{section}:{_slugify(label)}"
        seen[key] = seen.get(key, 0) + 1
        suffix = seen[key]
        item_id = key if suffix == 1 else f"{key}#{suffix}"
        out.append(
            {
                "id": item_id,
                "section": section,
                "label": label,
                "marker": marker,
                "source_ref": f"{masterplan}:{idx + 1}",
            }
        )
    return out


def _extract_milestone_de_items(masterplan: Path) -> list[dict[str, Any]]:
    lines = masterplan.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    current_milestone = ""
    seen: dict[str, int] = {}
    for idx, line in enumerate(lines):
        m = _RE_MILESTONE.match(line)
        if m:
            current_milestone = m.group(1)
            continue
        if current_milestone not in {"D", "E"}:
            continue
        marker_match = _RE_MARKER.match(line)
        if not marker_match:
            # stop milestone block at next heading
            if line.startswith("### ") or line.startswith("## "):
                current_milestone = ""
            continue
        marker = marker_match.group(1)
        label = marker_match.group(2).lstrip("\ufe0f ").strip()
        section = f"Milestone-{current_milestone}"
        key = f"{section}:{_slugify(label)}"
        seen[key] = seen.get(key, 0) + 1
        suffix = seen[key]
        item_id = key if suffix == 1 else f"{key}#{suffix}"
        out.append(
            {
                "id": item_id,
                "section": section,
                "label": label,
                "marker": marker,
                "source_ref": f"{masterplan}:{idx + 1}",
            }
        )
    return out


def _default_entry(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "section": item["section"],
        "label": item["label"],
        "marker": item["marker"],
        "source_ref": item["source_ref"],
        "status": "planned",
        "api_symbol": f"TBD::{item['id']}",
        "lowering_target": "TBD",
        "runtime_helper": "none",
        "permissions": [],
        "tests_required": [],
        "docs_required": [],
    }


def _merge_with_existing(expected_items: list[dict[str, Any]], existing: dict[str, Any] | None) -> dict[str, Any]:
    existing_map: dict[str, dict[str, Any]] = {}
    if existing and isinstance(existing.get("entries"), list):
        for entry in existing["entries"]:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                existing_map[entry["id"]] = entry

    entries: list[dict[str, Any]] = []
    for item in expected_items:
        base = _default_entry(item)
        prev = existing_map.get(item["id"])
        if prev:
            for k in (
                "status",
                "api_symbol",
                "lowering_target",
                "runtime_helper",
                "permissions",
                "tests_required",
                "docs_required",
            ):
                if k not in prev:
                    continue
                val = prev[k]
                if k in {"api_symbol", "lowering_target", "runtime_helper"} and (val is None or val == ""):
                    continue
                if k in {"permissions", "tests_required", "docs_required"} and not isinstance(val, list):
                    continue
                base[k] = val
        entries.append(base)

    entries.sort(key=lambda x: str(x["id"]))
    scope_flags = dict(DEFAULT_SCOPE_FLAGS)
    if isinstance(existing, dict) and isinstance(existing.get("scope_flags"), dict):
        existing_flags = existing.get("scope_flags") or {}
        for key in DEFAULT_SCOPE_FLAGS.keys():
            raw = existing_flags.get(key, DEFAULT_SCOPE_FLAGS[key])
            scope_flags[key] = bool(raw)

    return {
        "schema_version": SCHEMA_VERSION,
        "masterplan_path": DEFAULT_MASTERPLAN,
        "scope_flags": scope_flags,
        "entries": entries,
    }


def build_v1_scope_matrix(masterplan: Path, existing_matrix: Path | None = None) -> dict[str, Any]:
    expected = _extract_inventory_items(masterplan)
    expected.extend(_extract_milestone_de_items(masterplan))
    expected.sort(key=lambda x: str(x["id"]))

    existing_obj = None
    if existing_matrix and existing_matrix.exists():
        existing_obj = json.loads(existing_matrix.read_text(encoding="utf-8"))
    return _merge_with_existing(expected, existing_obj)


def _load_matrix(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{path} must contain valid JSON-compatible YAML for deterministic checks. Parse error: {exc}"
        ) from exc


def _validate_done_links(entry: dict[str, Any], repo_root: Path) -> list[str]:
    problems: list[str] = []
    tests = entry.get("tests_required")
    docs = entry.get("docs_required")
    if not isinstance(tests, list) or not tests:
        problems.append("status=done requires non-empty tests_required")
    if not isinstance(docs, list) or not docs:
        problems.append("status=done requires non-empty docs_required")

    for rel in tests if isinstance(tests, list) else []:
        if not isinstance(rel, str) or not rel:
            problems.append("tests_required entries must be non-empty strings")
            continue
        if not rel.startswith("tests/"):
            problems.append(
                f"tests_required entry must be under tests/ so CI pytest discovery executes it: {rel}"
            )
        if not rel.endswith(".py"):
            problems.append(f"tests_required entry must be a Python test module: {rel}")
        if rel.startswith("tests/") and Path(rel).name and not Path(rel).name.startswith("test_"):
            problems.append(
                f"tests_required entry must follow pytest discovery naming (test_*.py): {rel}"
            )
        if not (repo_root / rel).exists():
            problems.append(f"tests_required path not found: {rel}")
    for rel in docs if isinstance(docs, list) else []:
        if not isinstance(rel, str) or not rel:
            problems.append("docs_required entries must be non-empty strings")
            continue
        if not (repo_root / rel).exists():
            problems.append(f"docs_required path not found: {rel}")
    return problems


def check_v1_scope_matrix(masterplan: Path, matrix_path: Path) -> tuple[bool, str]:
    if not matrix_path.exists():
        return False, f"Scope matrix not found: {matrix_path}"
    matrix = _load_matrix(matrix_path)

    if matrix.get("schema_version") != SCHEMA_VERSION:
        return False, f"Unexpected schema_version in {matrix_path}. Expected {SCHEMA_VERSION}."

    entries = matrix.get("entries")
    if not isinstance(entries, list):
        return False, f"{matrix_path} must contain a top-level 'entries' list"
    scope_flags = matrix.get("scope_flags")
    if not isinstance(scope_flags, dict):
        return False, f"{matrix_path} must contain a top-level 'scope_flags' object"
    for key, expected_value in DEFAULT_SCOPE_FLAGS.items():
        if key not in scope_flags:
            return False, f"{matrix_path} scope_flags is missing '{key}'"
        raw = scope_flags.get(key)
        if not isinstance(raw, bool):
            return False, f"{matrix_path} scope_flags['{key}'] must be a boolean"
        if raw is not expected_value:
            return False, (
                f"{matrix_path} scope_flags['{key}'] must be {expected_value} "
                f"for guardrail-first policy"
            )

    expected = build_v1_scope_matrix(masterplan, existing_matrix=None)
    expected_entries = expected["entries"]
    expected_by_id = {e["id"]: e for e in expected_entries}
    actual_by_id = {}
    required_keys = {
        "id",
        "section",
        "label",
        "marker",
        "source_ref",
        "status",
        "api_symbol",
        "lowering_target",
        "runtime_helper",
        "permissions",
        "tests_required",
        "docs_required",
    }

    for entry in entries:
        if not isinstance(entry, dict):
            return False, "All scope matrix entries must be objects"
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            return False, "Every scope matrix entry must include a non-empty string 'id'"
        if entry_id in actual_by_id:
            return False, f"Duplicate scope matrix id: {entry_id}"
        missing = sorted(required_keys.difference(entry.keys()))
        if missing:
            return False, f"Entry {entry_id} is missing required keys: {', '.join(missing)}"
        actual_by_id[entry_id] = entry

    expected_ids = set(expected_by_id.keys())
    actual_ids = set(actual_by_id.keys())
    missing_ids = sorted(expected_ids.difference(actual_ids))
    extra_ids = sorted(actual_ids.difference(expected_ids))
    if missing_ids or extra_ids:
        msg = []
        if missing_ids:
            msg.append(f"Matrix missing entries present in masterplan: {missing_ids[:10]}")
        if extra_ids:
            msg.append(f"Matrix has extra entries not present in masterplan: {extra_ids[:10]}")
        return False, "; ".join(msg)

    repo_root = Path(".")
    allowed_status = {"planned", "in_progress", "done", "deferred", "blocked"}
    for entry_id in sorted(expected_ids):
        expected_entry = expected_by_id[entry_id]
        actual_entry = actual_by_id[entry_id]
        for key in ("section", "label", "marker", "source_ref"):
            if actual_entry.get(key) != expected_entry.get(key):
                return False, (
                    f"Matrix/masterplan mismatch for {entry_id} key '{key}': "
                    f"expected {expected_entry.get(key)!r}, got {actual_entry.get(key)!r}"
                )
        status = actual_entry.get("status")
        if status not in allowed_status:
            return False, f"Entry {entry_id} has invalid status {status!r} (allowed: {sorted(allowed_status)})"
        for list_key in ("permissions", "tests_required", "docs_required"):
            if not isinstance(actual_entry.get(list_key), list):
                return False, f"Entry {entry_id} field '{list_key}' must be a list"
        if status == "done":
            issues = _validate_done_links(actual_entry, repo_root=repo_root)
            if issues:
                return False, f"Entry {entry_id} invalid done contract: {'; '.join(issues)}"

    return True, ""


def _json_text(obj: dict[str, Any]) -> str:
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build/check v1 scope matrix derived from Masterplan_All_In_One.md. "
            "The matrix file is stored as JSON-compatible YAML for deterministic parsing."
        )
    )
    parser.add_argument("--masterplan", default=DEFAULT_MASTERPLAN)
    parser.add_argument("--matrix", default=DEFAULT_MATRIX)
    parser.add_argument("--sync", action="store_true", help="Write matrix file (preserving existing progress fields).")
    parser.add_argument("--check", action="store_true", help="Validate matrix/masterplan consistency and done contracts.")
    args = parser.parse_args(argv)

    if args.sync and args.check:
        emit_cli_error(
            "Use either --sync or --check, not both.",
            code="ScopeMatrixArgsError",
        )
        return 2

    masterplan = Path(args.masterplan)
    matrix = Path(args.matrix)

    if args.sync:
        snapshot = build_v1_scope_matrix(masterplan, existing_matrix=matrix)
        matrix.parent.mkdir(parents=True, exist_ok=True)
        matrix.write_text(_json_text(snapshot), encoding="utf-8")
        emit_cli_info(
            f"Wrote v1 scope matrix: {matrix}",
            code="ScopeMatrixWrite",
        )
        return 0

    if args.check:
        ok, message = check_v1_scope_matrix(masterplan, matrix)
        if not ok:
            emit_cli_error(
                message,
                code="ScopeMatrixCheckError",
                hint=(
                    "Re-sync with: "
                    f"PYTHONPATH=. python tools/v1_scope_matrix.py --sync "
                    f"--masterplan {masterplan} --matrix {matrix}"
                ),
            )
            return 1
        emit_cli_info(
            f"v1 scope matrix is up to date and valid: {matrix}",
            code="ScopeMatrixOK",
        )
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
