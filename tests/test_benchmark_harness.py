from apk.benchmark import (
    evaluate_benchmark_thresholds,
    parse_am_start_output,
    resolve_component_name,
)


def test_parse_am_start_output_extracts_numeric_timings():
    output = """
Status: ok
LaunchState: COLD
Activity: com.ahnali.bench/.MainActivity
ThisTime: 123
TotalTime: 456
WaitTime: 490
Complete
""".strip()
    parsed = parse_am_start_output(output)
    assert parsed == {"ThisTime": 123, "TotalTime": 456, "WaitTime": 490}


def test_resolve_component_name_from_wrapper_desc():
    component = resolve_component_name(
        application_id="com.ahnali.bench",
        activity_class_desc="Lcom/ahnali/bench/MainActivity;",
    )
    assert component == "com.ahnali.bench/.MainActivity"


def test_evaluate_benchmark_thresholds_accepts_metrics_within_limits():
    metrics = {
        "signed_apk_bytes": 1_000_000,
        "classes_dex_bytes": 250_000,
        "cold_start_total_ms_median": 800,
    }
    thresholds = {
        "max_signed_apk_bytes": 2_000_000,
        "max_classes_dex_bytes": 1_000_000,
        "max_cold_start_total_ms": 1_200,
        "require_cold_start": True,
        "max_signed_apk_regression_bytes": 200_000,
        "max_cold_start_regression_ms": 200,
    }
    baseline = {
        "signed_apk_bytes": 900_000,
        "cold_start_total_ms_median": 700,
    }
    failures = evaluate_benchmark_thresholds(
        metrics=metrics,
        thresholds=thresholds,
        baseline_metrics=baseline,
    )
    assert failures == []


def test_evaluate_benchmark_thresholds_flags_missing_required_cold_start():
    metrics = {
        "signed_apk_bytes": 100_000,
        "classes_dex_bytes": 20_000,
    }
    thresholds = {
        "max_signed_apk_bytes": 2_000_000,
        "max_classes_dex_bytes": 1_000_000,
        "require_cold_start": True,
    }
    failures = evaluate_benchmark_thresholds(
        metrics=metrics,
        thresholds=thresholds,
        baseline_metrics={},
    )
    assert any("cold-start benchmark required" in msg for msg in failures)


def test_evaluate_benchmark_thresholds_flags_regressions():
    metrics = {
        "signed_apk_bytes": 1_500_000,
        "classes_dex_bytes": 250_000,
        "cold_start_total_ms_median": 1_050,
    }
    thresholds = {
        "max_signed_apk_bytes": 3_000_000,
        "max_classes_dex_bytes": 1_000_000,
        "max_cold_start_total_ms": 2_000,
        "max_signed_apk_regression_bytes": 100_000,
        "max_cold_start_regression_ms": 100,
        "require_cold_start": False,
    }
    baseline = {
        "signed_apk_bytes": 1_200_000,
        "cold_start_total_ms_median": 900,
    }
    failures = evaluate_benchmark_thresholds(
        metrics=metrics,
        thresholds=thresholds,
        baseline_metrics=baseline,
    )
    assert any("signed_apk regression" in msg for msg in failures)
    assert any("cold-start regression" in msg for msg in failures)
