---
tags: [ahnali, api-reference, app-model, build]
---

# 01 — App Model

> [!abstract] What this covers
> The top-level constructors that define your app: `app()`, `activity()`, `ui()`, `state()`, `app_config()`, `run()`, and `simple_activity()`. Also the module-level macros, screen rules, label resolution, and dependency policy.

Related: [[02 - Value Types and Units]] · [[06 - Structure Components]] · [[10 - Navigation and Screens]]

---

## Core Constructors

### `app(activity_spec)`

Creates an `AppSpec` — the root object that the compiler consumes. You pass one or more `activity(...)` specs into it.

```python
from dsl.api import app, activity

app_spec = app(
    activity("MainActivity",
        app_config(),
        ui(text("Hello", id="greeting")),
    ),
)
```

### `activity(name, *parts)`

Creates an activity specification. `parts` can be any mix of:

- `app_config(...)`
- `state(...)`
- `Theme(...)` / `theme(...)`
- `ui(...)`
- event specs (`on_click`, `on_change`, …)
- lifecycle specs (`on_start`, `on_resume`, `on_pause`, `on_stop`, `on_destroy`)
- lists or tuples of any of the above (flattened automatically)

```python
activity(
    "MainActivity",
    app_config(mode="static"),
    state(counter=0),
    Theme(palette={"primary": "#FF2563EB"}),
    ui(text("Hello", id="greeting")),
    on_click("btn", [toast("tapped")]),
)
```

> [!note] Parts order doesn't matter
> The compiler collects and categorizes parts by type, so you can pass them in any order.

### `ui(*items)`

Wraps the widget tree. Every visual element in your app lives under a `ui(...)` call.

```python
ui(
    Column(
        text("Welcome", id="title"),
        button("Continue", id="continue_btn"),
    ),
)
```

### `state(**kwargs)`

Declares global integer state values. Keys must match `[A-Za-z_][A-Za-z0-9_]*` and cannot collide with reserved names (`app_ctx`, `nav_stack`, `nav_size`, `nav_current`) or generated widget field names.

> [!warning] Integer literals only
> State values must be integer literals at compile time. Booleans, strings, and expressions are rejected.

```python
state(counter=0, step=1, max_retries=3)
```

### `run(app_spec, **kwargs)`

Convenience wrapper around `AppSpec.run(...)`. Kicks off the full build pipeline: DSL parsing → Smali emission → APK packaging → install.

```python
from dsl.api import run
run(app_spec)
```

### `simple_activity()`

A sugar builder for very simple one-screen text/button samples. Useful for quick smoke tests.

```python
from dsl.api import simple_activity
simple_activity("Hello World")
```

---

## `app_config()` — Full Signature

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

| Field | Purpose |
|---|---|
| `package` | Android application package name |
| `min_sdk` / `target_sdk` | API level bounds |
| `version_code` / `version_name` | Versioning |
| `debuggable` | Enables debuggable flag |
| `show_action_bar` | Toggle the action bar |
| `label` | App display name (locks label resolution) |
| `uses` | Capability/permission declarations (`Caps.Networking`, etc.) |
| `uninstall_first` | Force reinstall before install |
| `output_apk` | Custom output APK path |
| `signing_mode` | `"debug"` or `"release"` |
| `keystore_*` | Release signing credentials |
| `verify_reproducible` | Verify reproducible build |
| `deps` / `auto_deps` | Dependency policy (see below) |
| `mode` | `"static"` (default) or `"reactive"` |

> [!tip] Use `uses` to declare capabilities
> If your app makes network calls, declares `uses=[Caps.Networking]`. The compiler injects the right manifest permissions and links the helper classes. Without it, you get a compile-time error.

---

## Module-Level Macros

The `dsl.api` module reads these constants from your app module if present. They override defaults and can serve as a centralized config block.

| Macro | Type | Purpose |
|---|---|---|
| `APP_CONFIG` | `dict` | Full config dict (merged with `app_config()` kwargs) |
| `APP_PACKAGE` | `str` | Package name |
| `APP_MIN_SDK` | `int` | Minimum SDK |
| `APP_TARGET_SDK` | `int` | Target SDK |
| `APP_VERSION_CODE` | `int` | Version code |
| `APP_VERSION_NAME` | `str` | Version name |
| `APP_DEBUGGABLE` | `bool` | Debuggable flag |
| `APP_SHOW_ACTION_BAR` | `bool` | Show action bar |
| `APP_NO_ACTION_BAR` | `bool` | Hide action bar |
| `APP_LABEL` | `str` | App display name |
| `APP_USES` | `list` | Capabilities |
| `APP_DEPS` | `list` | Explicit dependencies |
| `APP_AUTO_DEPS` | `bool` | Auto-dependency inference |
| `APP_UNINSTALL_FIRST` | `bool` | Uninstall before install |
| `APP_OUTPUT_APK` | `str` | Output APK path |
| `APP_KEYSTORE_PATH` | `str` | Keystore path |
| `APP_KEYSTORE_ALIAS` | `str` | Keystore alias |
| `APP_PLUGINS` | `list` | Plugin list |
| `APP_MODE` | `str` | `"static"` or `"reactive"` |

> [!note] Resolution order
> `app_config()` kwargs take precedence over module-level macros, which take precedence over defaults.

---

## Screen Rules

If **any** `Screen(...)` appears in `ui(...)`, the compiler enforces:

1. **All top-level `ui` items must be `Screen(...)`** — mixing screens and non-screens at the same level is rejected.
2. **Screen names must be unique** — duplicates fail at compile time.

```python
# ✅ Valid — all top-level items are Screens
ui(
    Screen("Home", text("Home", id="home_title")),
    Screen("Settings", text("Settings", id="settings_title"), transition="fade"),
)

# ❌ Invalid — mixing Screen and non-Screen
ui(
    Screen("Home", text("Home")),
    text("Orphan"),  # rejected!
)
```

See [[10 - Navigation and Screens]] for full navigation semantics.

---

## Label Resolution Order

The app display label resolves in this order (first match wins):

1. `APP_LABEL` module constant (highest priority)
2. `app_config(label=...)` explicit argument
3. `AppBar(text=...)` if present and not explicitly locked
4. Default: `"AhnaliPreview"`

> [!tip] Lock your label early
> Set `app_config(label="My App")` to prevent `AppBar` text from accidentally overriding your app name.

---

## Dependency Policy

### `deps` and `auto_deps`

- **Default behavior**: explicit-only. Only dependencies you list in `deps` (or `APP_DEPS`) are included.
- **`auto_deps=True`**: the compiler infers dependencies from your code and merges them with explicit `deps`.
- **`auto_deps=False`** (default): if the compiler detects inferred dependencies that you haven't declared, the build fails with a clear error telling you what to add.

```python
app_config(
    deps=["com.google.android.material:material:1.9.0"],
    auto_deps=True,  # merge inferred deps with explicit list
)
```

> [!warning] Don't rely on auto_deps for production
> Explicit `deps` gives you deterministic, reproducible builds. Use `auto_deps=True` during development, then pin everything for release.

---

## APK Packaging Pipeline

The build pipeline produces a signed APK through these steps:

1. `aapt2 compile/link` → `unsigned.apk` with resources and manifest
2. `classes.dex` is added
3. `zipalign -f -p 4` → aligned APK
4. `apksigner sign` → final signed APK

---

## See Also

- [[02 - Value Types and Units]] — dp, sp, colors, gradients
- [[06 - Structure Components]] — Row, Column, Screen, and layout containers
- [[08 - Theme Style and Presets]] — Theme, Style, and presets
- [[10 - Navigation and Screens]] — Navigate, Back, Screen transitions
- [[12 - Validation and Diagnostics]] — compile-time checks
