---
tags: [ahnali, getting-started, setup]
---

# Project Setup

> [!abstract] What you need
> Python, the Android SDK, and a handful of command-line tools. That's the whole toolchain.

## Python

3.10 or newer. Create a venv if you want - the project doesn't care either way.

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install rich httpx pytest
```

Those three are the only external dependencies. `rich` for nicer output, `httpx` for HTTP helpers, `pytest` for tests.

## Android SDK

You need the Android SDK with these tools on your PATH:

- `aapt2` - resource compilation and APK packaging
- `zipalign` - APK alignment
- `apksigner` - APK signing
- `adb` - device communication

If you have Android Studio installed, these are in `$ANDROID_HOME/build-tools/<version>/`. Add that to your PATH.

## Smali and D8

You need the `smali` and `d8` jars. You can grab them from the [smali GitHub releases](https://github.com/JesusFreke/smali/releases) and the [R8 releases](https://r8.googlesource.com/r8).

Put them somewhere on your PATH, or set environment variables:

```bash
export SMALI_JAR=/path/to/smali.jar
export D8_JAR=/path/to/d8.jar
```

> [!tip] Smali jar without Main-Class manifest
> If your smali jar doesn't have a `Main-Class` manifest entry, the toolchain falls back to running it via classpath with explicit main class. It just works - you don't need to configure anything.

## Verify your setup

```bash
PYTHONPATH=. pytest -q
```

All 648 tests should pass. If they don't, something's off with your environment.

## Debug keystore

The toolchain auto-generates a debug keystore on first use. You don't need to manage this yourself unless you're doing release signing.

For release builds, configure your keystore in `app_config`:

```python
app_config(
    signing_mode="release",
    keystore_path="/path/to/release.keystore",
    keystore_alias="mykey",
    keystore_pass="password",
    key_pass="password",
)
```

## Project structure

Once you're set up, here's what you're working with:

```
dsl/        - DSL constructs, widgets, lowering
ir/         - Intermediate representation
cfg/        - Control flow graph
ssa/        - SSA construction
dalvik/     - Dalvik IR
passes/     - Compiler passes (liveness, regalloc, DCE)
emit/       - Smali emission
tests/      - 156 test files
tools/      - Build tooling, benchmarks, CI helpers
docs/       - This vault
```

## Next steps

- Build your first app: [[02 - Your First App]]
- Understand the pipeline: [[20 - Core Concepts/02 - Compiler Pipeline]]
