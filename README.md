# Ahnali

A Python-to-Android compiler. You write Python, it emits Smali, you get an APK. No Java, no Kotlin, no Gradle - just a straight shot from DSL to Dalvik bytecode.

## What it actually does

```python
from dsl.app import app, activity, ui, text, button, on_click, state

app(
    activity("Main",
        state("counter", 0),
        ui(
            text("Count: 0", id="label"),
            button("Tap me", id="btn"),
        ),
        on_click("btn", [
            # increment counter, update label
        ]),
    ),
)
```

This compiles to Smali, gets packaged with `aapt2`, signed, and you have a working APK. The whole UI, navigation, state, and event handling is resolved at compile time. There's no interpreter sitting in your app at runtime figuring out what a button means.

## How the compiler works

```
Python DSL → IR → CFG → SSA → Typed SSA → Dalvik IR → Smali → APK
```

Each step is its own phase. Nothing skips ahead. Every phase has validation that blocks if something's wrong. The Smali emitter doesn't try to be clever - it just prints what the verified IR tells it to.

The pipeline handles:
- Control flow (if/while)
- Arithmetic and comparisons
- Typed calls and returns
- Exception handling (try/catch/throw)
- Register allocation with spilling
- Dead code elimination
- Constant/copy propagation
- CFG simplification

## What you can build right now

**UI:** 30+ widgets - text, buttons, inputs, checkboxes, sliders, dropdowns, images, progress bars, scroll views, list views, cards, app bars, drawers, tab layouts. Typography, theming, gradients, borders, ripples, shadows, opacity, and explicit animations.

**Platform stuff:** networking (sync + async with retries), storage (SharedPreferences, DataStore, SQLite, Room, encrypted), permissions, notifications, clipboard, sharing/intents, WebView with JS bridge, deep links, background work (WorkManager, AlarmManager, JobScheduler), location.

**State & lifecycle:** static state, lifecycle hooks (on_start through on_destroy), navigation stack with push/pop/replace.

There's also an opt-in reactive mode if you need it, but static is the default and reactive doesn't change how static apps behave.

## Running tests

```
PYTHONPATH=. pytest
```

Current: 648 passing, 3 skipped.

## Building an APK

The toolchain chains together `aapt2`, `d8`, `zipalign`, and `apksigner`. There's a `build_install_run()` helper in the codebase that does the full flow. You'll need the Android SDK on your PATH for the packaging steps.

## Project structure

```
dsl/        - Frontend: widgets, DSL constructs, lowering to IR
ir/         - Intermediate representation (expr, stmt, method, program)
cfg/        - Control flow graph construction and validation
ssa/        - SSA construction and verification
dalvik/     - Dalvik IR, blocks, method representation
passes/     - Compiler passes: liveness, regalloc, DCE, SSA opts
emit/       - Smali emission
tests/      - Everything test-related (156 files)
tools/      - Build tooling, benchmark harness, CI helpers
docs/       - All documentation
cfg/        - Config files: ABI snapshots, benchmark baselines, scope matrix
```

## Design decisions I stand by

- **Correctness over features.** A phase that can't validate its output doesn't pass. No exceptions.
- **No shortcuts.** Nothing goes straight from DSL to Smali. Every transformation has to earn its place in the pipeline.
- **Dumb emission.** The Smali emitter doesn't make decisions. It prints what the IR says. If the IR is wrong, an earlier phase should've caught it.
- **Static by default.** Everything is resolved at compile time. Reactive mode exists but you have to explicitly ask for it.

## What's not happening (at least not yet)

JNI/native bridges, embedded Python, camera/audio/video pipelines, maps, Bluetooth, biometrics - all deferred. The focus right now is locking down the static compiler and the capability surfaces that are already implemented. There's a masterplan in `docs/` if you want to see where things are headed.

## Immediate Plan (Next)

1) ✅ **Program 5** - State and lifecycle hooks (closed).
2) ✅ **Program 11-A** - Docs/API reference freeze (closed).
3) ✅ **Program 6-A** - Capability depth (closed).
4) ⚠️ **Program 6-B** - Capability breadth closure/freeze (in progress).
5) ⚠️ **Program 12-A** - Docs consistency gate (in progress).
6) ⚠️ **Program 11-B + 12-B** - Final static-v1 release hardening (in progress).

## Deferred Beyond V1

1) ⚠️ **Program 7** - Motion backlog: deferred until static compiler/toolchain is frozen.
2) ⚠️ **Program 8** - Advanced/system/security/debug backlog: deferred beyond current release train.
3) ⚠️ **Program 9 / Milestone D** - Deterministic NDK/JNI bridge: deferred to post-v1.
4) ⚠️ **Program 10 / Milestone E** - Optional bounded Python plugin: deferred to post-v1.

## ABI and Capability Contracts

- Runtime ABI: `docs/runtime_abi_v1.md`
- Capability mapping: `docs/capability_runtime_mapping_v1.md`
- Both are frozen for v1. CI checks for drift on every push.

## Python dependencies

Minimal by design. `rich` for nicer output, `httpx` for the HTTP helpers, `pytest` for tests. That's it. No reactive frameworks, no DI containers, no web frameworks. There's a policy file (`cfg/python_library_policy.json`) and a CI gate that enforces it.

---

Last updated: 2026-03-10
