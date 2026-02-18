---
tags: [ahnali, app-model, build]
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
- event specs (`on_click`, `on_change`, ...)
- lifecycle specs (`on_start`, `on_resume`, `on_pause`, `on_stop`, `on_destroy`)
- lists/tuples of the above specs

## `ui(*items)`
Wraps widget tree items.

## `state(**kwargs)`
Declares global integer state values.

Current rule:
- state values must be integer literals at compile time.

## `run(app_spec, **kwargs)`
Convenience wrapper around `AppSpec.run(...)`.

## Optional Sugar: `simple_activity()`
Small convenience builder for very simple one-screen text/button samples.

## AppConfig

Signature:

```python
app_config(
    *,
    package="com.ahnali.preview",
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
    mode="static",  # "static" | "reactive"
)
```

### Field Notes

- `deps` + `auto_deps`: explicit dependency policy and inferred-deps merge behavior.
- `uses`: capability/permission declarations.
- `mode`: `static` (default) or `reactive`.

Reactive guardrail:
- using reactive statements in static mode raises `[ReactiveModeError]`.

### Module-level Macros Recognized

`dsl.api` reads these if present in app module:

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
- `APP_MODE`

## Dependency Policy

Default: explicit-only.

If inferred dependencies are required and `auto_deps=False`, build fails until they are declared in `deps`/`APP_DEPS`.

## Screen Rules in Build Layer

If any `Screen(...)` is present in `ui(...)`:
- all top-level `ui` items must be `Screen(...)`
- mixing Screen and non-Screen at same level is rejected
- screen names must be unique

## Label Resolution Order

Current behavior:
- default `app_name = "AhnaliPreview"`
- `AppBar(text=...)` can set label if not explicitly locked
- `app_config(label=...)` locks label
- `APP_LABEL` overrides during app-config extraction

## APK Packaging Pipeline

1. `aapt2 compile/link` creates `unsigned.apk` with resources/manifest.
2. `classes.dex` is added.
3. `zipalign -f -p 4` produces aligned APK.
4. `apksigner sign` signs final APK.

See also:
- [[10_Events_and_Handler_DSL]]
- [[11_Navigation_State_and_Screens]]
- [[13_Validation_and_Diagnostics]]
