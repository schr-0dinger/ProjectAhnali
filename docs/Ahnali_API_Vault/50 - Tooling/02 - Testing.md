---
tags: [ahnali, tooling, testing]
---

# Testing

> [!abstract] 691 tests, 164 test files
> If it's not tested, it doesn't exist. Every phase has focused tests and at least one integration smoke.

## Running tests

```bash
PYTHONPATH=. pytest -q
```

Current: **691 passed**.

## What's tested

### Compiler pipeline
- CFG construction and validation
- Dominance analysis
- Phi insertion
- SSA construction and verification
- Type inference and verification
- SSA optimization (const/copy propagation, coalescing)
- Dalvik lowering
- Dead code elimination
- CFG simplification
- Liveness analysis
- Register allocation with spilling
- Smali emission (opcodes, invoke families, switches, monitors)

### DSL and lowering
- Widget construction and attribute handling
- Event listener generation
- Navigation operations
- Theme and style resolution
- Animation DSL
- Bounded Android binding lowering (`android_uri_parse`, `android_intent_view`, `android_intent_chooser`, `android_start_activity`)
- Input configuration
- Accessibility surface
- Visual effects
- Validation and linting

### Capabilities
- All 18 Track C waves
- Visible integration flows per wave
- Runtime ABI conformance
- Capability mapping contract
- Permission inference

### Toolchain
- APK packaging
- Manifest wiring
- Signing (debug and release)
- JAR launchers
- Benchmark harness
- Feature/runtime plan tooling and emitted build reports
- CI gates (scope matrix, capability drift, docs consistency, library policy)

## Negative tests

The project includes negative tests that verify the compiler correctly rejects invalid input:
- Invalid call signatures
- Invalid try/catch structures
- Capability errors (using APIs without declaring capabilities)
- Reactive mode errors (using reactive APIs in static mode)

## Device integration

Some tests require a connected adb device:
- `test_http_helper_device_integration.py` - runs HttpHelper on real device
- Cold-start benchmark - boots emulator and measures startup time

Skip these with `pytest -q --ignore=tests/test_http_helper_device_integration.py`.

## Phase 1 runtime-plan inspection

You can inspect the analyzer/runtime-selector layer directly with:

```bash
PYTHONPATH=. python tools/feature_runtime_plan.py --source path/to/file.py
```

Build outputs for Pythonic app builds also include `runtime_plan.json` when Phase 1 metadata is available.

## Learn more

- Benchmarking: [[50 - Tooling/03 - Benchmarking]]
- CI gates: [[50 - Tooling/04 - CI Gates]]
