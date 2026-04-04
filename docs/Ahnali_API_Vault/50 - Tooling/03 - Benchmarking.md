---
tags: [ahnali, tooling, benchmarking, performance]
---

# Benchmarking

> [!abstract] Two gates: APK size and cold-start time
> Both have hard caps. CI blocks a PR if you blow past them.

## Running locally

**Size only** (no device needed):

```bash
PYTHONPATH=. python tools/benchmark_apk.py \
  --threshold-file cfg/benchmark_thresholds.json \
  --baseline-file cfg/benchmark_baseline.json \
  --report-file build/benchmark/size_report.json \
  --api 34 \
  --skip-cold-start
```

**Size + cold-start** (need adb device/emulator):

```bash
PYTHONPATH=. python tools/benchmark_apk.py \
  --threshold-file cfg/benchmark_thresholds.json \
  --baseline-file cfg/benchmark_baseline.json \
  --report-file build/benchmark/cold_start_report.json \
  --api 34 \
  --require-cold-start \
  --cold-start-iterations 3
```

> [!tip] Smali jar location
> If `smali` isn't on your PATH, set `SMALI_JAR=/path/to/smali.jar`.

## What gets checked

The thresholds file (`cfg/benchmark_thresholds.json`) defines:

- Max signed APK size
- Max classes.dex size
- Max cold-start median time
- Regression limits when a baseline exists

The baseline is locked in `cfg/benchmark_baseline.json`.

## CI enforcement

- **Size gate** - runs on every push/PR, fails if APK or dex exceeds the cap
- **Cold-start gate** - manual dispatch only (needs an emulator), fails if startup exceeds the threshold

Both dump JSON reports into `build/benchmark/`.

## Learn more

- Build and package: [[50 - Tooling/01 - Build and Package]]
- CI gates: [[50 - Tooling/04 - CI Gates]]
