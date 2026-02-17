#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

from dsl.capabilities import CAPABILITY_RUNTIME_ABI_VERSION, default_capability_runtime_mapping
from emit.smali_activity import emit_activity_wrapper_smali, emit_event_listener_smali
from emit.smali_runtime_helpers import emit_capability_helper_smali


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


def _build_class_entry(smali: str, source: str) -> dict[str, object]:
    return {
        "class_desc": _parse_class_desc(smali),
        "source": source,
        "methods": _parse_method_sigs(smali),
    }


def _build_wrapper_contract() -> dict[str, object]:
    smali = emit_activity_wrapper_smali(
        activity_desc="Lcom/ahnali/preview/MainActivity;",
        target_desc="LAbiContract;",
        target_sig="(Landroid/app/Activity;)V",
        emit_system_back_bridge=True,
        back_sig="()I",
        back_method="onSystemBack",
    )
    return _build_class_entry(smali, "wrapper")


def _build_listener_contracts() -> list[dict[str, object]]:
    specs = [
        ("click", "Lcom/ahnali/preview/AhnaliClickListener_contract;", "onClick_contract"),
        ("change", "Lcom/ahnali/preview/AhnaliChangeListener_contract;", "onChange_contract"),
        (
            "slider_change",
            "Lcom/ahnali/preview/AhnaliSliderChangeListener_contract;",
            "onSliderChange_contract",
        ),
        (
            "radiogroup_change",
            "Lcom/ahnali/preview/AhnaliRadioGroupChangeListener_contract;",
            "onRadioGroupChange_contract",
        ),
        ("text_change", "Lcom/ahnali/preview/AhnaliTextChangeListener_contract;", "onTextChange_contract"),
        (
            "item_selected",
            "Lcom/ahnali/preview/AhnaliItemSelectedListener_contract;",
            "onItemSelected_contract",
        ),
        ("focus_change", "Lcom/ahnali/preview/AhnaliFocusChangeListener_contract;", "onFocusChange_contract"),
        (
            "menu_item_selected",
            "Lcom/ahnali/preview/AhnaliMenuItemListener_contract;",
            "onMenuItemSelected_contract",
        ),
        ("list_adapter", "Lcom/ahnali/preview/AhnaliListAdapter_contract;", "0x1090003"),
        ("ui_runnable_click", "Lcom/ahnali/preview/AhnaliUiRunnable_contract;", "onClick_contract"),
        ("http_route_async_worker", "Lcom/ahnali/preview/AhnaliHttpRouteAsyncWorker_contract;", "unused"),
    ]
    out: list[dict[str, object]] = []
    for kind, class_desc, target_method in specs:
        smali = emit_event_listener_smali(
            class_desc=class_desc,
            target_desc="LAbiContract;",
            target_method=target_method,
            listener_kind=kind,
        )
        out.append(_build_class_entry(smali, f"listener_kind:{kind}"))
    return out


def _build_capability_helper_contracts() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    mapping = default_capability_runtime_mapping()
    for capability, binding in sorted(mapping.items()):
        if binding.mode != "helper_call":
            continue
        smali = emit_capability_helper_smali(
            class_desc=binding.helper_class_desc or "",
            helper_method=binding.helper_method or "",
            helper_sig=binding.helper_sig or "",
        )
        out.append(_build_class_entry(smali, f"capability:{capability}"))
    return out


def build_runtime_abi_snapshot() -> dict[str, object]:
    classes = [_build_wrapper_contract()]
    classes.extend(_build_listener_contracts())
    classes.extend(_build_capability_helper_contracts())
    classes.sort(key=lambda item: str(item["class_desc"]))
    return {
        "abi_version": CAPABILITY_RUNTIME_ABI_VERSION,
        "snapshot_schema": "runtime_abi_v1_helper_signatures",
        "classes": classes,
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
        "Runtime ABI snapshot drift detected.\n"
        f"Rebuild snapshot with: PYTHONPATH=. python tools/runtime_abi_snapshot.py --out {snapshot_path}\n"
        f"{diff}"
    )
    return False, message


def check_runtime_abi_snapshot(snapshot_path: Path) -> tuple[bool, str]:
    return _check_snapshot(snapshot_path, build_runtime_abi_snapshot())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate/check frozen runtime ABI helper class/method signature snapshot."
    )
    parser.add_argument(
        "--out",
        default="cfg/runtime_abi_snapshot_v1.json",
        help="Snapshot file path (default: cfg/runtime_abi_snapshot_v1.json)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check generated snapshot against --out and fail on drift.",
    )
    args = parser.parse_args(argv)

    out_path = Path(args.out)
    snapshot = build_runtime_abi_snapshot()

    if args.check:
        ok, message = _check_snapshot(out_path, snapshot)
        if not ok:
            print(message, file=sys.stderr)
            return 1
        print(f"Runtime ABI snapshot is up to date: {out_path}")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_snapshot_json(snapshot), encoding="utf-8")
    print(f"Wrote runtime ABI snapshot: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
