# Ahnali Benchmarking (Track B)

This repository provides a benchmark harness for deterministic APK size reporting and optional cold-start timing checks.

## Local Usage

Run size-only benchmark (no adb device required):

```bash
PYTHONPATH=. python tools/benchmark_apk.py \
  --threshold-file cfg/benchmark_thresholds.json \
  --report-file build/benchmark/size_report.json \
  --skip-cold-start
```

Run size + cold-start benchmark (adb device/emulator required):

```bash
PYTHONPATH=. python tools/benchmark_apk.py \
  --threshold-file cfg/benchmark_thresholds.json \
  --report-file build/benchmark/cold_start_report.json \
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

## CI Gates

Workflow: `.github/workflows/ci.yml`

- `benchmark-size`: runs on push/PR; enforces deterministic size thresholds.
- `benchmark-cold-start`: runs on `main` pushes and manual dispatch; boots emulator and enforces cold-start threshold.

Each benchmark job uploads JSON artifacts under `build/benchmark/`.
