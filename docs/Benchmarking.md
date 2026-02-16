# Ahnali Benchmarking (Track B)

This repository provides a benchmark harness for deterministic APK size reporting and optional cold-start timing checks.

## Local Usage

Run size-only benchmark (no adb device required):

```bash
PYTHONPATH=. python tools/benchmark_apk.py \
  --threshold-file cfg/benchmark_thresholds.json \
  --baseline-file cfg/benchmark_baseline.json \
  --report-file build/benchmark/size_report.json \
  --api 34 \
  --skip-cold-start
```

Run size + cold-start benchmark (adb device/emulator required):

```bash
PYTHONPATH=. python tools/benchmark_apk.py \
  --threshold-file cfg/benchmark_thresholds.json \
  --baseline-file cfg/benchmark_baseline.json \
  --report-file build/benchmark/cold_start_report.json \
  --api 34 \
  --require-cold-start \
  --cold-start-iterations 3
```

If `smali` is not on `PATH`, set `SMALI_JAR=/path/to/smali.jar`.

## Thresholds

Threshold configuration lives in `cfg/benchmark_thresholds.json`.

Current checks:
- signed APK size cap (`max_signed_apk_bytes`)
- classes.dex size cap (`max_classes_dex_bytes`)
- cold-start median cap (`max_cold_start_total_ms`)
- optional regression caps when baseline metrics are available

Current rollout mode:
- Size baseline is locked in `cfg/benchmark_baseline.json` and enforced in CI.
- Signed APK regression cap is active (`max_signed_apk_regression_bytes`).
- Cold-start gate is strict on manual CI dispatch (`workflow_dispatch`) and uses committed baseline reference.

## CI Gates

Workflow: `.github/workflows/ci.yml`

- `benchmark-size`: runs on push/PR; enforces deterministic size thresholds.
- `benchmark-cold-start`: manual dispatch only for now; boots emulator and enforces cold-start threshold.

Each benchmark job uploads JSON artifacts under `build/benchmark/`.
