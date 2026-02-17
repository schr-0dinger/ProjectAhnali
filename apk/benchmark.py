from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import time
from typing import Any

from apk.toolchain import (
    _activity_name_from_desc,
    _adb_path,
    _collect_toolchain_diagnostics,
    _zip_content_digest,
    emit_build_dir_from_program,
    package_apk_from_dex,
    run_smali,
)
from dsl.app import assign, const
from dsl.runtime.diagnostics import emit_cli_exception, emit_cli_info


BENCHMARK_SCHEMA_VERSION = "1.0.0"

DEFAULT_THRESHOLDS = {
    "max_signed_apk_bytes": 15_000_000,
    "max_classes_dex_bytes": 8_000_000,
    "max_cold_start_total_ms": 2_500,
    "max_signed_apk_regression_bytes": 262_144,
    "max_cold_start_regression_ms": 250,
    "require_cold_start": False,
}


@dataclass(frozen=True)
class BenchmarkArtifacts:
    build_dir: Path
    dex_path: Path
    signed_apk_path: Path
    unsigned_apk_path: Path


def parse_am_start_output(text: str) -> dict[str, int]:
    fields: dict[str, int] = {}
    for raw in (text or "").splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key not in {"ThisTime", "TotalTime", "WaitTime"}:
            continue
        token = value.split()[0] if value else ""
        if not token:
            continue
        try:
            fields[key] = int(token)
        except ValueError:
            continue
    return fields


def has_adb_device(adb_path: str | None = None) -> bool:
    adb = adb_path or _adb_path()
    try:
        result = subprocess.run(
            [adb, "devices"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return False
    lines = [line.strip() for line in result.stdout.splitlines()[1:]]
    for line in lines:
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return True
    return False


def resolve_component_name(
    *,
    application_id: str,
    activity_name: str | None = None,
    activity_class_desc: str | None = None,
) -> str:
    if activity_name:
        if "/" in activity_name:
            return activity_name
        if activity_name.startswith("."):
            return f"{application_id}/{activity_name}"
        return f"{application_id}/{activity_name}"
    if activity_class_desc:
        resolved = _activity_name_from_desc(activity_class_desc, application_id)
        return f"{application_id}/{resolved}"
    return f"{application_id}/.MainActivity"


def build_benchmark_apk(
    *,
    out_dir: Path,
    class_name: str,
    wrapper_class_desc: str,
    application_id: str,
    api: int | None,
    smali_jar: str | None,
) -> BenchmarkArtifacts:
    frontend_ir = [assign("x", const(1))]
    build_dir = emit_build_dir_from_program(
        frontend_ir,
        out_dir=out_dir,
        class_name=class_name,
        emit_wrapper=True,
        wrapper_class_desc=wrapper_class_desc,
        wrapper_target_sig="()V",
    )
    dex_path = run_smali(
        build_dir / "smali",
        out_dir=build_dir / "classes.dex",
        smali_jar=smali_jar,
        api=api,
    )
    signed_apk = package_apk_from_dex(
        dex_path,
        out_dir=build_dir,
        application_id=application_id,
        api=api,
        activity_class_desc=wrapper_class_desc,
        verify_reproducible=True,
        reproducible_digest_path=build_dir / "unsigned.apk.sha256",
    )
    return BenchmarkArtifacts(
        build_dir=build_dir,
        dex_path=Path(dex_path),
        signed_apk_path=Path(signed_apk),
        unsigned_apk_path=build_dir / "unsigned.apk",
    )


def _load_json(path: Path | None, default: dict[str, Any]) -> dict[str, Any]:
    if path is None or not path.exists():
        return dict(default)
    return json.loads(path.read_text(encoding="utf-8"))


def _store_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def evaluate_benchmark_thresholds(
    *,
    metrics: dict[str, Any],
    thresholds: dict[str, Any],
    baseline_metrics: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []

    signed_size = int(metrics["signed_apk_bytes"])
    dex_size = int(metrics["classes_dex_bytes"])
    cold_median = metrics.get("cold_start_total_ms_median")

    max_signed = thresholds.get("max_signed_apk_bytes")
    if max_signed is not None and signed_size > int(max_signed):
        failures.append(
            f"signed_apk_bytes {signed_size} exceeds max_signed_apk_bytes {int(max_signed)}"
        )

    max_dex = thresholds.get("max_classes_dex_bytes")
    if max_dex is not None and dex_size > int(max_dex):
        failures.append(
            f"classes_dex_bytes {dex_size} exceeds max_classes_dex_bytes {int(max_dex)}"
        )

    require_cold = bool(thresholds.get("require_cold_start", False))
    max_cold = thresholds.get("max_cold_start_total_ms")
    if cold_median is None:
        if require_cold:
            failures.append("cold-start benchmark required but no cold-start metric was collected")
    else:
        if max_cold is not None and int(cold_median) > int(max_cold):
            failures.append(
                f"cold_start_total_ms_median {int(cold_median)} exceeds max_cold_start_total_ms {int(max_cold)}"
            )

    baseline = baseline_metrics or {}
    base_signed = baseline.get("signed_apk_bytes")
    if base_signed is not None:
        max_reg = thresholds.get("max_signed_apk_regression_bytes")
        if max_reg is not None:
            reg = signed_size - int(base_signed)
            if reg > int(max_reg):
                failures.append(
                    f"signed_apk regression {reg} bytes exceeds max_signed_apk_regression_bytes {int(max_reg)}"
                )

    base_cold = baseline.get("cold_start_total_ms_median")
    if base_cold is not None and cold_median is not None:
        max_cold_reg = thresholds.get("max_cold_start_regression_ms")
        if max_cold_reg is not None:
            reg = int(cold_median) - int(base_cold)
            if reg > int(max_cold_reg):
                failures.append(
                    f"cold-start regression {reg} ms exceeds max_cold_start_regression_ms {int(max_cold_reg)}"
                )

    return failures


def _install_apk(adb: str, signed_apk: Path, application_id: str) -> None:
    subprocess.run([adb, "uninstall", application_id], check=False, capture_output=True, text=True)
    subprocess.run([adb, "install", "-r", str(signed_apk)], check=True, capture_output=True, text=True)


def measure_cold_start(
    *,
    adb: str,
    component: str,
    application_id: str,
    iterations: int,
) -> dict[str, Any]:
    samples_total: list[int] = []
    samples_wait: list[int] = []

    for _ in range(iterations):
        subprocess.run([adb, "shell", "am", "force-stop", application_id], check=False)
        result = subprocess.run(
            [adb, "shell", "am", "start", "-W", "-n", component],
            check=True,
            capture_output=True,
            text=True,
        )
        parsed = parse_am_start_output(result.stdout)
        total = parsed.get("TotalTime")
        if total is None:
            raise RuntimeError(
                "Unable to parse TotalTime from `adb shell am start -W` output; "
                "cold-start benchmark cannot continue."
            )
        samples_total.append(int(total))
        wait = parsed.get("WaitTime")
        if wait is not None:
            samples_wait.append(int(wait))

    return {
        "samples_total_ms": samples_total,
        "samples_wait_ms": samples_wait,
        "cold_start_total_ms_min": min(samples_total),
        "cold_start_total_ms_max": max(samples_total),
        "cold_start_total_ms_median": int(statistics.median(samples_total)),
        "cold_start_wait_ms_median": (
            int(statistics.median(samples_wait)) if samples_wait else None
        ),
    }


def run_benchmark(
    *,
    out_dir: Path,
    report_file: Path,
    threshold_file: Path | None,
    baseline_file: Path | None,
    write_baseline_if_missing: bool,
    class_name: str,
    wrapper_class_desc: str,
    application_id: str,
    activity_name: str | None,
    api: int | None,
    smali_jar: str | None,
    skip_cold_start: bool,
    require_cold_start: bool,
    cold_start_iterations: int,
) -> dict[str, Any]:
    diagnostics = _collect_toolchain_diagnostics(require_adb=(not skip_cold_start))
    if diagnostics:
        raise RuntimeError("Toolchain diagnostics failed: " + "; ".join(diagnostics))

    build_start = time.perf_counter()
    artifacts = build_benchmark_apk(
        out_dir=out_dir,
        class_name=class_name,
        wrapper_class_desc=wrapper_class_desc,
        application_id=application_id,
        api=api,
        smali_jar=smali_jar,
    )
    build_wall_ms = int((time.perf_counter() - build_start) * 1000)

    metrics: dict[str, Any] = {
        "build_wall_ms": build_wall_ms,
        "signed_apk_bytes": artifacts.signed_apk_path.stat().st_size,
        "classes_dex_bytes": artifacts.dex_path.stat().st_size,
        "unsigned_apk_bytes": (
            artifacts.unsigned_apk_path.stat().st_size
            if artifacts.unsigned_apk_path.exists()
            else None
        ),
        "unsigned_apk_content_sha256": (
            _zip_content_digest(artifacts.unsigned_apk_path)
            if artifacts.unsigned_apk_path.exists()
            else None
        ),
    }

    component = resolve_component_name(
        application_id=application_id,
        activity_name=activity_name,
        activity_class_desc=wrapper_class_desc,
    )
    cold_start_collected = False
    if not skip_cold_start:
        adb = _adb_path()
        if not has_adb_device(adb):
            if require_cold_start:
                raise RuntimeError(
                    "Cold-start benchmark required but no adb device is in `device` state."
                )
        else:
            _install_apk(adb, artifacts.signed_apk_path, application_id)
            cold = measure_cold_start(
                adb=adb,
                component=component,
                application_id=application_id,
                iterations=max(1, int(cold_start_iterations)),
            )
            metrics.update(cold)
            cold_start_collected = True

    thresholds = _load_json(threshold_file, DEFAULT_THRESHOLDS)
    if require_cold_start:
        thresholds["require_cold_start"] = True
    baseline_payload = _load_json(baseline_file, {}) if baseline_file else {}
    baseline_metrics = baseline_payload.get("metrics", {})

    failures = evaluate_benchmark_thresholds(
        metrics=metrics,
        thresholds=thresholds,
        baseline_metrics=baseline_metrics,
    )

    report = {
        "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
        "inputs": {
            "application_id": application_id,
            "activity_component": component,
            "class_name": class_name,
            "wrapper_class_desc": wrapper_class_desc,
            "api": api,
            "cold_start_iterations": int(cold_start_iterations),
            "cold_start_collected": cold_start_collected,
        },
        "metrics": metrics,
        "thresholds": thresholds,
        "baseline_file": str(baseline_file) if baseline_file else None,
        "failures": failures,
        "passed": not failures,
    }
    _store_json(report_file, report)

    if baseline_file and write_baseline_if_missing and not baseline_file.exists():
        baseline_payload = {
            "benchmark_schema_version": BENCHMARK_SCHEMA_VERSION,
            "metrics": {
                "signed_apk_bytes": metrics["signed_apk_bytes"],
                "classes_dex_bytes": metrics["classes_dex_bytes"],
                "cold_start_total_ms_median": metrics.get("cold_start_total_ms_median"),
            },
        }
        _store_json(baseline_file, baseline_payload)

    if failures:
        raise RuntimeError("Benchmark gate failed:\n- " + "\n- ".join(failures))
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic APK size and optional cold-start benchmarks."
    )
    parser.add_argument("--out-dir", default="build/benchmark", help="Build output directory.")
    parser.add_argument(
        "--report-file",
        default="build/benchmark/benchmark_report.json",
        help="Path to write benchmark report JSON.",
    )
    parser.add_argument(
        "--threshold-file",
        default="cfg/benchmark_thresholds.json",
        help="JSON file containing benchmark thresholds.",
    )
    parser.add_argument(
        "--baseline-file",
        default="cfg/benchmark_baseline.json",
        help="Optional JSON baseline file for regression checks.",
    )
    parser.add_argument(
        "--write-baseline-if-missing",
        action="store_true",
        help="If baseline file does not exist, write current metrics as initial baseline.",
    )
    parser.add_argument("--class-name", default="LBench;", help="Class descriptor for emitted main class.")
    parser.add_argument(
        "--wrapper-class-desc",
        default="Lcom/ahnali/bench/MainActivity;",
        help="Wrapper activity class descriptor.",
    )
    parser.add_argument("--application-id", default="com.ahnali.bench", help="Application id/package name.")
    parser.add_argument(
        "--activity-name",
        default=None,
        help="Optional activity name for cold-start launch component. Defaults to wrapper descriptor resolution.",
    )
    parser.add_argument("--api", type=int, default=21, help="Android API level for smali/toolchain.")
    parser.add_argument("--smali-jar", default=None, help="Path to smali jar/binary. Defaults to $SMALI_JAR.")
    parser.add_argument(
        "--skip-cold-start",
        action="store_true",
        help="Skip adb install/start cold-start measurements.",
    )
    parser.add_argument(
        "--require-cold-start",
        action="store_true",
        help="Fail if cold-start metrics cannot be collected.",
    )
    parser.add_argument(
        "--cold-start-iterations",
        type=int,
        default=3,
        help="Number of `am start -W` cold-start samples when cold-start is enabled.",
    )
    parser.add_argument(
        "--print-report",
        action="store_true",
        help="Print JSON report to stdout after run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    report_file = Path(args.report_file)
    threshold_file = Path(args.threshold_file) if args.threshold_file else None
    baseline_file = Path(args.baseline_file) if args.baseline_file else None
    smali_resolved = args.smali_jar or os.environ.get("SMALI_JAR")

    try:
        report = run_benchmark(
            out_dir=out_dir,
            report_file=report_file,
            threshold_file=threshold_file,
            baseline_file=baseline_file,
            write_baseline_if_missing=bool(args.write_baseline_if_missing),
            class_name=args.class_name,
            wrapper_class_desc=args.wrapper_class_desc,
            application_id=args.application_id,
            activity_name=args.activity_name,
            api=args.api,
            smali_jar=smali_resolved,
            skip_cold_start=bool(args.skip_cold_start),
            require_cold_start=bool(args.require_cold_start),
            cold_start_iterations=max(1, int(args.cold_start_iterations)),
        )
    except Exception as exc:
        emit_cli_exception(
            exc,
            code="BenchmarkError",
            hint="Use --print-report and inspect cfg/benchmark_thresholds.json / cfg/benchmark_baseline.json.",
        )
        return 1

    if args.print_report:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        emit_cli_info(
            f"Benchmark completed successfully. Report: {report_file}",
            code="BenchmarkOK",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
