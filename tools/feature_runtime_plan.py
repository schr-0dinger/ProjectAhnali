#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from dsl.analyzer import analyze_features, select_runtime_modules
from dsl.runtime.diagnostics import emit_cli_error, emit_cli_info


def build_feature_runtime_plan_from_source(source_text: str) -> dict[str, object]:
    profile = analyze_features(source_text)
    modules = select_runtime_modules(profile)
    return {
        "schema_version": "feature_runtime_plan/1",
        "feature_usage_profile": profile.to_dict(),
        "selected_runtime_modules": [asdict(module) for module in modules],
        "runtime_module_names": [module.name for module in modules],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze Python source and emit the Phase 1 feature/runtime selection plan."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to a Python source file to analyze.",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Optional JSON output path. If omitted, prints JSON to stdout.",
    )
    args = parser.parse_args(argv)

    source_path = Path(args.source)
    if not source_path.exists():
        emit_cli_error(f"Source file not found: {source_path}", code="FeatureRuntimePlanError")
        return 1

    payload = build_feature_runtime_plan_from_source(source_path.read_text(encoding="utf-8"))
    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json_text, encoding="utf-8")
        emit_cli_info(
            f"Wrote feature/runtime plan: {out_path}",
            code="FeatureRuntimePlanWrite",
        )
        return 0

    print(json_text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
