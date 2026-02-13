---
tags: [anali, app-model, build]
---

# App Model and Build/Run API

Back to: [[00_Home]]

## Core Constructors

## `app(activity_spec)`
Creates an `AppSpec` container.

## `activity(name, *parts)`
Creates an activity specification. `parts` can include:
- `app_config(...)`
- `state(...)`
- `Theme(...)` / `theme(...)`
- `ui(...)`
- event specs (`on_click`, `on_change`, etc.)
- lists/tuples of event specs

## `ui(*items)`
Wraps widget tree items.

## `state(**kwargs)`
Declares global integer state values.

Important current rule:
- state values must be integer literals at compile time.

## `run(app_spec, **kwargs)`
Convenience wrapper around `AppSpec.run(...)`.

## AppConfig

Signature:

```python
app_config(
    *,
    package="com.anali.preview",
    min_sdk=21,
    target_sdk=33,
    version_code=1,
    version_name="1.0",
    debuggable=False,
    show_action_bar=True,
    label=None,
    uses=None,
    uninstall_first=True,
    output_apk=None,
    signing_mode="debug",
    keystore_path=None,
    keystore_alias="androiddebugkey",
    keystore_pass=None,
    key_pass=None,
    verify_reproducible=False,
    deps=None,
    auto_deps=False,
)
```

### Field Notes

- `package`: Android package id.
- `min_sdk`, `target_sdk`: SDK controls.
- `version_code`, `version_name`: app version metadata.
- `debuggable`: manifest/debug mode flag.
- `show_action_bar`: controls default theme/action bar behavior.
- `label`: app label (resource `app_name`).
- `uses`: explicit capability/permission tokens.
- `uninstall_first`: uninstall before install on run path.
- `output_apk`: write APK to custom path.
- `signing_mode`: signing strategy (`debug` by default).
- `verify_reproducible`: enables reproducibility verification path.
- `deps`: explicit external dependencies (AAR/Maven artifacts).
- `auto_deps`: if `True`, inferred deps are auto-merged; if `False`, missing inferred deps raise errors.

### Module-level Macros Recognized

`dsl.api` reads these if present in your app module:

- `APP_CONFIG` (dict)
- `APP_PACKAGE`
- `APP_MIN_SDK`
- `APP_TARGET_SDK`
- `APP_VERSION_CODE`
- `APP_VERSION_NAME`
- `APP_DEBUGGABLE`
- `APP_SHOW_ACTION_BAR`
- `APP_NO_ACTION_BAR`
- `APP_LABEL`
- `APP_USES`
- `APP_DEPS`
- `APP_AUTO_DEPS`
- `APP_UNINSTALL_FIRST`
- `APP_OUTPUT_APK`
- `APP_KEYSTORE_PATH`
- `APP_KEYSTORE_ALIAS`
- `APP_PLUGINS`

### Dependency Policy

Default: explicit-only.

If a plugin/core surface infers required artifacts and `auto_deps=False`, build fails with a missing dependency error until those artifacts are declared in `deps`/`APP_DEPS`.

## Screen Rules in Build Layer

If any `Screen(...)` is present in `ui(...)`:
- all top-level `ui` items must be `Screen(...)`
- mixing Screen and non-Screen at same level is rejected
- screen names must be unique

## Label Resolution Order

Current effective behavior:
- default `app_name = "AnaliPreview"`
- `AppBar(text=...)` may set label if no explicit label is locked
- `app_config(label=...)` locks label
- module `APP_LABEL` overrides label at build extraction stage

## APK Packaging Pipeline

Current packaging path in toolchain:

1. `aapt2 compile/link` creates `unsigned.apk` with manifest/resources.
2. `classes.dex` is added to `unsigned.apk`.
3. `zipalign -f -p 4` produces `aligned.apk`.
4. `apksigner sign` signs `aligned.apk` into final `signed.apk`.

Notes:
- `zipalign` runs before signing (required ordering).
- Toolchain diagnostics now require `aapt2`, `zipalign`, and `apksigner`.

See also:
- [[11_Navigation_State_and_Screens]]
- [[13_Validation_and_Diagnostics]]
