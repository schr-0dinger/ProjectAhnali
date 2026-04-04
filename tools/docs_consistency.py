#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from dsl.capabilities import CAPABILITY_RUNTIME_ABI_VERSION
from dsl.runtime.diagnostics import emit_cli_error, emit_cli_info

DEFAULT_MASTERPLAN = "docs/Masterplan_All_In_One.md"
DEFAULT_README = "README.md"
DEFAULT_RUNTIME_ABI = "docs/runtime_abi_v1.md"
DEFAULT_CAP_MAPPING = "docs/capability_runtime_mapping_v1.md"
DEFAULT_PROGRAM6B = "docs/Program6B_Task_Breakdown.md"

_EXPECTED_ACTIVE_PROGRAM_ORDER = [
    "program5",
    "program11a",
    "program6a",
    "program6b",
    "program12a",
    "program11b12b",
]
_EXPECTED_DEFERRED_PROGRAM_ORDER = [
    "program7",
    "program8",
    "program9",
    "program10",
]


def _line_to_program_key(line: str) -> str | None:
    text = str(line)
    if "Program 11-B" in text and "12-B" in text:
        return "program11b12b"
    if "Program 11-A" in text:
        return "program11a"
    if "Program 12-A" in text:
        return "program12a"
    if "Program 6-A" in text:
        return "program6a"
    if "Program 6-B" in text:
        return "program6b"
    if "Program 5" in text:
        return "program5"
    if "Program 7" in text:
        return "program7"
    if "Program 8" in text:
        return "program8"
    if "Program 9" in text:
        return "program9"
    if "Program 10" in text:
        return "program10"
    return None


def _extract_order_keys(text: str, *, header: str, item_prefixes: tuple[str, ...]) -> list[str]:
    keys: list[str] = []
    in_section = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip() == header:
            in_section = True
            continue
        if not in_section:
            continue
        if line.startswith("## ") and line.strip() != header:
            break
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith(item_prefixes):
            continue
        key = _line_to_program_key(stripped)
        if key is not None:
            keys.append(key)
    return keys


def check_docs_consistency(
    *,
    masterplan_path: Path,
    readme_path: Path,
    runtime_abi_path: Path,
    capability_mapping_path: Path,
    program6b_path: Path,
) -> tuple[bool, str]:
    missing = [
        str(p)
        for p in (
            masterplan_path,
            readme_path,
            runtime_abi_path,
            capability_mapping_path,
            program6b_path,
        )
        if not p.exists()
    ]
    if missing:
        return False, f"Required doc files not found: {missing}"

    masterplan = masterplan_path.read_text(encoding="utf-8")
    readme = readme_path.read_text(encoding="utf-8")
    runtime_abi = runtime_abi_path.read_text(encoding="utf-8")
    capability_mapping = capability_mapping_path.read_text(encoding="utf-8")
    program6b = program6b_path.read_text(encoding="utf-8")

    errors: list[str] = []

    mp_active_order = _extract_order_keys(
        masterplan,
        header="## 16) Immediate Unified Execution Plan",
        item_prefixes=tuple(f"{i}." for i in range(1, 11)),
    )
    rd_active_order = _extract_order_keys(
        readme,
        header="## Immediate Plan (Next)",
        item_prefixes=tuple(f"{i})" for i in range(1, 11)),
    )
    mp_deferred_order = _extract_order_keys(
        masterplan,
        header="## 17) Deferred Beyond V1",
        item_prefixes=tuple(f"{i}." for i in range(1, 11)),
    )
    rd_deferred_order = _extract_order_keys(
        readme,
        header="## Deferred Beyond V1",
        item_prefixes=tuple(f"{i})" for i in range(1, 11)),
    )

    if mp_active_order != _EXPECTED_ACTIVE_PROGRAM_ORDER:
        errors.append(
            "Masterplan active v1 plan order mismatch. "
            f"Expected {_EXPECTED_ACTIVE_PROGRAM_ORDER}, got {mp_active_order}"
        )
    if rd_active_order != _EXPECTED_ACTIVE_PROGRAM_ORDER:
        errors.append(
            "README active v1 plan order mismatch. "
            f"Expected {_EXPECTED_ACTIVE_PROGRAM_ORDER}, got {rd_active_order}"
        )
    if mp_deferred_order != _EXPECTED_DEFERRED_PROGRAM_ORDER:
        errors.append(
            "Masterplan deferred plan order mismatch. "
            f"Expected {_EXPECTED_DEFERRED_PROGRAM_ORDER}, got {mp_deferred_order}"
        )
    if rd_deferred_order != _EXPECTED_DEFERRED_PROGRAM_ORDER:
        errors.append(
            "README deferred plan order mismatch. "
            f"Expected {_EXPECTED_DEFERRED_PROGRAM_ORDER}, got {rd_deferred_order}"
        )

    if "runtime_abi_v1.md" not in masterplan:
        errors.append("Masterplan must reference runtime_abi_v1.md")
    if "docs/capability_runtime_mapping_v1.md" not in masterplan:
        errors.append("Masterplan must reference docs/capability_runtime_mapping_v1.md")
    if "cfg/v1_scope_matrix.yaml" not in masterplan:
        errors.append("Masterplan must reference cfg/v1_scope_matrix.yaml")

    if "runtime_abi_v1.md" not in readme:
        errors.append("README must reference runtime_abi_v1.md")
    if "docs/capability_runtime_mapping_v1.md" not in readme:
        errors.append("README must reference docs/capability_runtime_mapping_v1.md")

    if "docs/capability_runtime_mapping_v1.md" not in runtime_abi:
        errors.append("runtime_abi_v1.md must reference docs/capability_runtime_mapping_v1.md")
    if f'CAPABILITY_RUNTIME_ABI_VERSION = "{CAPABILITY_RUNTIME_ABI_VERSION}"' not in runtime_abi:
        errors.append(
            "runtime_abi_v1.md must declare the ABI version constant line matching code"
        )

    if "runtime_abi_v1.md" not in capability_mapping:
        errors.append("capability_runtime_mapping doc must reference runtime_abi_v1.md")
    if f"ABI version: `{CAPABILITY_RUNTIME_ABI_VERSION}`" not in capability_mapping:
        errors.append(
            "capability_runtime_mapping doc ABI version line must match code"
        )
    if "cfg/v1_scope_matrix.yaml" not in program6b:
        errors.append("Program6B task breakdown must reference cfg/v1_scope_matrix.yaml")
    if "source of truth" not in program6b.lower():
        errors.append("Program6B task breakdown must describe the scope matrix as the source of truth")
    if "Deferred Beyond V1" not in readme:
        errors.append("README must include a Deferred Beyond V1 section")
    if "## 17) Deferred Beyond V1" not in masterplan:
        errors.append("Masterplan must include a Deferred Beyond V1 section")

    if errors:
        return False, "Docs consistency errors: " + "; ".join(errors)
    return True, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate consistency across masterplan, README, ABI, and capability mapping docs."
    )
    parser.add_argument("--masterplan", default=DEFAULT_MASTERPLAN)
    parser.add_argument("--readme", default=DEFAULT_README)
    parser.add_argument("--runtime-abi", default=DEFAULT_RUNTIME_ABI)
    parser.add_argument("--capability-doc", default=DEFAULT_CAP_MAPPING)
    parser.add_argument("--program6b-doc", default=DEFAULT_PROGRAM6B)
    args = parser.parse_args(argv)

    ok, message = check_docs_consistency(
        masterplan_path=Path(args.masterplan),
        readme_path=Path(args.readme),
        runtime_abi_path=Path(args.runtime_abi),
        capability_mapping_path=Path(args.capability_doc),
        program6b_path=Path(args.program6b_doc),
    )
    if not ok:
        emit_cli_error(message, code="DocsConsistencyError")
        return 1
    emit_cli_info("Docs consistency check passed.", code="DocsConsistencyOK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
