---
tags: [ahnali, tooling, build, packaging]
---

# Build and Package

> [!abstract] From Smali to signed APK
> The toolchain chains together aapt2, d8, zipalign, and apksigner. You call `build()` or `run()` - it handles the rest.

## The pipeline

```
Smali files (emitted by compiler)
    ↓
d8 → classes.dex
    ↓
aapt2 compile → compiled resources
    ↓
aapt2 link → unsigned.apk (with manifest + resources + dex)
    ↓
zipalign → aligned APK
    ↓
apksigner → signed APK
```

## Debug vs release

**Debug mode** (default):
- Auto-generates a debug keystore on first use
- Signs with the debug key
- `debuggable=true` in the manifest

**Release mode**:
- You provide your own keystore
- Configure in `app_config`:

```python
app_config(
    signing_mode="release",
    keystore_path="/path/to/release.keystore",
    keystore_alias="mykey",
    keystore_pass="password",
    key_pass="password",
)
```

## Reproducibility

The toolchain supports reproducibility hash checks for unsigned archive content. Enable with `verify_reproducible=True` in `app_config`.

## Resource handling

- Strings, colors, dimens, and styles are written from the DSL
- Stable ID paths are supported for resources
- Resource merge from AAR dependencies works through d8

## Runtime plan artifact

When a program is built through the Pythonic app path and carries Phase 1 metadata, the build directory includes `runtime_plan.json`.

That report captures:
- the merged feature-usage profile
- the selected runtime modules
- the runtime-module names
- the app mode used during build

This is the easiest way to confirm what the analyzer/runtime-selector layer decided for a given build.

## AAR dependencies

The toolchain resolves AARs, merges their manifests, extracts symbols, and generates `R$*` classes. Transitive AAR inference works through manifest closure.

## Learn more

- Project setup: [[10 - Getting Started/03 - Project Setup]]
- Testing: [[50 - Tooling/02 - Testing]]
- Benchmarking: [[50 - Tooling/03 - Benchmarking]]
