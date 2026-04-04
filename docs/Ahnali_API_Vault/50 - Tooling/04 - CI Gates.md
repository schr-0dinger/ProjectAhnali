---
tags: [ahnali, tooling, ci, github-actions]
---

# CI Gates

> [!abstract] What blocks a merge
> CI runs on every push and PR. If any gate fails, the PR doesn't merge.

## Automatic gates (push/PR)

| Gate | What it does |
|---|---|
| **Tests** | Runs `pytest -q`. All 648 must pass. |
| **Benchmark size** | Checks APK and dex size against thresholds. |
| **Python library policy** | Verifies no unauthorized dependencies. |
| **ABI snapshot** | Checks helper class signatures haven't drifted. |
| **Capability mapping** | Verifies capability-to-runtime mapping is consistent. |
| **Docs consistency** | Checks that masterplan/README/ABI docs match code reality. |
| **Scope matrix** | Validates v1 scope tracking is up to date. |

## Manual gates (workflow dispatch)

| Gate | What it does |
|---|---|
| **Cold-start benchmark** | Boots an emulator, measures app startup time, checks against threshold. |

## What happens when a gate fails

The PR gets a red X. No merge until it's green. There's no "merge anyway" override - if CI says no, it's no.

## Artifacts

Benchmark jobs upload JSON reports to `build/benchmark/` as GitHub artifacts. You can download them to see detailed numbers.

## Learn more

- Testing: [[50 - Tooling/02 - Testing]]
- Benchmarking: [[50 - Tooling/03 - Benchmarking]]
- Python library policy: [[50 - Tooling/05 - Python Library Policy]]
