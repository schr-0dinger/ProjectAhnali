#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from dsl.capabilities import CAPABILITY_RUNTIME_ABI_VERSION, default_capability_runtime_mapping
from dsl.runtime.diagnostics import emit_cli_error, emit_cli_info
from emit.smali_runtime_helpers import emit_capability_helper_smali

SNAPSHOT_SCHEMA = "capability_runtime_mapping_v1"
DEFAULT_SNAPSHOT = "cfg/capability_mapping_snapshot_v1.json"
DEFAULT_DOC = "docs/capability_runtime_mapping_v1.md"


def _parse_class_desc(smali: str) -> str:
    for raw in smali.splitlines():
        line = raw.strip()
        if line.startswith(".class "):
            return line.split()[-1]
    raise RuntimeError("Unable to parse class descriptor from emitted smali")


def _parse_method_sigs(smali: str) -> list[str]:
    sigs: set[str] = set()
    for raw in smali.splitlines():
        line = raw.strip()
        if not line.startswith(".method "):
            continue
        token = line.split()[-1]
        if "(" not in token or ")" not in token:
            raise RuntimeError(f"Unable to parse method signature from line: {line}")
        sigs.add(token)
    return sorted(sigs)


def _build_entry(capability: str, binding) -> dict[str, object]:
    entry: dict[str, object] = {
        "capability": capability,
        "mode": binding.mode,
        "permissions": list(binding.permissions),
        "helper_class_desc": binding.helper_class_desc,
        "helper_method": binding.helper_method,
        "helper_sig": binding.helper_sig,
    }

    if binding.mode == "helper_call":
        smali = emit_capability_helper_smali(
            class_desc=binding.helper_class_desc or "",
            helper_method=binding.helper_method or "",
            helper_sig=binding.helper_sig or "",
        )
        emitted_class = _parse_class_desc(smali)
        emitted_methods = _parse_method_sigs(smali)
        expected_method = f"{binding.helper_method}{binding.helper_sig}"

        if emitted_class != binding.helper_class_desc:
            raise RuntimeError(
                f"Capability '{capability}' emitted class mismatch: "
                f"expected {binding.helper_class_desc}, got {emitted_class}"
            )
        if expected_method not in emitted_methods:
            raise RuntimeError(
                f"Capability '{capability}' primary helper method missing in emitted class: "
                f"{expected_method}"
            )

        entry["emitted_class_desc"] = emitted_class
        entry["emitted_methods"] = emitted_methods

    return entry


def build_capability_mapping_snapshot() -> dict[str, object]:
    mapping = default_capability_runtime_mapping()
    entries = [_build_entry(capability, binding) for capability, binding in sorted(mapping.items())]
    return {
        "abi_version": CAPABILITY_RUNTIME_ABI_VERSION,
        "snapshot_schema": SNAPSHOT_SCHEMA,
        "entries": entries,
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
        "Capability mapping snapshot drift detected.\n"
        f"Rebuild snapshot with: PYTHONPATH=. python tools/capability_mapping_contract.py --out {snapshot_path}\n"
        f"{diff}"
    )
    return False, message


def _parse_mapping_rows(doc_text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for raw in doc_text.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        if line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        cap_cell = cells[0]
        if not (cap_cell.startswith("`") and cap_cell.endswith("`")):
            continue
        capability = cap_cell.strip("`").strip()
        if capability:
            rows[capability] = line
    return rows


def _check_docs_contract(snapshot: dict[str, object], docs_path: Path) -> tuple[bool, str]:
    if not docs_path.exists():
        return False, f"Capability mapping document not found: {docs_path}"

    text = docs_path.read_text(encoding="utf-8")
    problems: list[str] = []

    abi_line = f"ABI version: `{CAPABILITY_RUNTIME_ABI_VERSION}`"
    if abi_line not in text:
        problems.append(
            f"capability mapping doc must declare ABI version line '{abi_line}'"
        )

    rows = _parse_mapping_rows(text)
    entries = snapshot.get("entries")
    if not isinstance(entries, list):
        return False, "Generated capability mapping snapshot has invalid 'entries' payload"

    for entry in entries:
        if not isinstance(entry, dict):
            problems.append("snapshot entry is not an object")
            continue
        capability = str(entry.get("capability") or "")
        if not capability:
            problems.append("snapshot entry missing capability name")
            continue

        row = rows.get(capability)
        if row is None:
            problems.append(f"doc row missing for capability '{capability}'")
            continue

        for perm in entry.get("permissions", []):
            if isinstance(perm, str) and perm and perm not in row:
                problems.append(
                    f"doc row for capability '{capability}' missing permission '{perm}'"
                )

        mode = str(entry.get("mode") or "")
        helper_class_desc = str(entry.get("helper_class_desc") or "")
        helper_method = str(entry.get("helper_method") or "")

        if mode == "helper_call":
            if helper_class_desc and helper_class_desc not in row:
                problems.append(
                    f"doc row for capability '{capability}' missing helper class descriptor '{helper_class_desc}'"
                )
            if helper_method and f"{helper_method}(" not in row:
                problems.append(
                    f"doc row for capability '{capability}' missing helper method '{helper_method}(...)'"
                )
        else:
            if "n/a" not in row.lower():
                problems.append(
                    f"doc row for capability '{capability}' should use 'n/a' runtime helper cells for permission_only mode"
                )

    if problems:
        return False, "Capability mapping docs/metadata contract errors: " + "; ".join(problems)
    return True, ""


def check_capability_mapping_contract(snapshot_path: Path, docs_path: Path) -> tuple[bool, str]:
    actual = build_capability_mapping_snapshot()
    ok, message = _check_snapshot(snapshot_path, actual)
    if not ok:
        return False, message
    ok, message = _check_docs_contract(actual, docs_path)
    if not ok:
        return False, message
    return True, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate/check frozen capability runtime mapping snapshot and validate docs/emission contract."
        )
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_SNAPSHOT,
        help=f"Snapshot file path (default: {DEFAULT_SNAPSHOT})",
    )
    parser.add_argument(
        "--doc",
        default=DEFAULT_DOC,
        help=f"Capability mapping docs path (default: {DEFAULT_DOC})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check generated snapshot against --out and validate docs contract.",
    )
    args = parser.parse_args(argv)

    out_path = Path(args.out)
    doc_path = Path(args.doc)
    snapshot = build_capability_mapping_snapshot()

    if args.check:
        ok, message = check_capability_mapping_contract(out_path, doc_path)
        if not ok:
            emit_cli_error(message, code="CapabilityMappingContractError")
            return 1
        emit_cli_info(
            f"Capability mapping snapshot/docs are up to date: {out_path}, {doc_path}",
            code="CapabilityMappingContractOK",
        )
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_snapshot_json(snapshot), encoding="utf-8")
    emit_cli_info(
        f"Wrote capability mapping snapshot: {out_path}",
        code="CapabilityMappingContractWrite",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
