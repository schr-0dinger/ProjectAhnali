# Benchmarking

We track two things: APK size and cold-start time. Both have hard caps, and CI will block a PR if you blow past them.

## Running locally

Size check only (no device needed):

```bash
PYTHONPATH=. python tools/benchmark_apk.py \
  --threshold-file cfg/benchmark_thresholds.json \
  --baseline-file cfg/benchmark_baseline.json \
  --report-file build/benchmark/size_report.json \
  --api 34 \
  --skip-cold-start
```

Size + cold-start (need an adb device or emulator):

```bash
PYTHONPATH=. python tools/benchmark_apk.py \
  --threshold-file cfg/benchmark_thresholds.json \
  --baseline-file cfg/benchmark_baseline.json \
  --report-file build/benchmark/cold_start_report.json \
  --api 34 \
  --require-cold-start \
  --cold-start-iterations 3
```

If `smali` isn't on your PATH, point `SMALI_JAR` at the jar.

## What gets checked

The thresholds file (`cfg/benchmark_thresholds.json`) defines the caps:

- Max signed APK size
- Max classes.dex size
- Max cold-start median time
- Regression limits when a baseline exists

Right now the size baseline is locked in `cfg/benchmark_baseline.json` and enforced on every push/PR. Cold-start only runs on manual CI dispatch since it needs an emulator.

## CI

`.github/workflows/ci.yml` runs two benchmark jobs:

- **benchmark-size** — automatic on push/PR, fails if APK or dex exceeds the cap
- **benchmark-cold-start** — manual dispatch only, boots an emulator and checks startup time

Both dump JSON reports into `build/benchmark/`.
