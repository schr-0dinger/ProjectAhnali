---
tags: [ahnali, getting-started, tutorial]
---

# Your First App

> [!abstract] What we're building
> A counter app with two screens, navigation, and persistent state. Nothing fancy — it covers the essentials.

## Step 1: The basics

Start with a single screen and a counter:

```python
from dsl.app import app, activity, ui, state, text, button, on_click

@on_click("inc")
def increment():
    count = count + 1
    label.text = f"Count: {count}"

app_spec = app(
    activity(
        "MainActivity",
        state(count=0),
        ui(
            text("Count: 0", id="label", text_size=sp(24)),
            button("+", id="inc"),
        ),
        increment,
    )
)

app_spec.run()
```

> [!note] How state works
> `state(count=0)` declares a compile-time integer field. The handler `count = count + 1` reads and writes that field. Everything is resolved at compile time — there's no runtime state engine sitting in your app.

## Step 2: Add theming

Make it look less like 2010:

```python
from dsl.app import app, activity, ui, state, text, button, on_click
from dsl.widgets import Theme, Style
from dsl.colors import colors

@on_click("inc")
def increment():
    count = count + 1
    label.text = f"Count: {count}"

app_spec = app(
    activity(
        "MainActivity",
        Theme(
            palette={
                "bg": colors.zinc_100,
                "card": colors.white,
                "primary": colors.blue_600,
                "text": colors.slate_900,
            },
            text=Style(text_color="text", text_size=16),
            button=Style(text_color="white", background="primary", radius=16),
        ),
        state(count=0),
        ui(
            text("Count: 0", id="label", text_size=sp(24), padding=(24, 24, 24, 24)),
            button("+", id="inc", padding=(16, 12, 16, 12)),
        ),
        increment,
    )
)
```

Theme resolution is deterministic: inline attributes win over `style=`, which wins over theme channels, which win over widget defaults.

## Step 3: Add a second screen

```python
from dsl.app import app, activity, ui, state, text, button, on_click, Screen, Navigate, Back

@on_click("go_settings")
def go_settings():
    Navigate("Settings")

@on_click("go_back")
def go_back():
    Back()

app_spec = app(
    activity(
        "MainActivity",
        ui(
            Screen("Home",
                text("Home", id="home_title", text_size=sp(24)),
                button("Settings", id="go_settings"),
            ),
            Screen("Settings",
                text("Settings", id="settings_title", text_size=sp(24)),
                button("Back", id="go_back"),
                transition="slide_left",
            ),
        ),
        go_settings,
        go_back,
    )
)
```

> [!warning] Screen rules
> If you use `Screen(...)`, every top-level item in `ui(...)` must be a screen. You can't mix screens and regular widgets at the same level. Screen names must be unique.

## Step 4: Add capabilities

Let's persist the counter using storage:

```python
from dsl.app import app, activity, ui, state, text, button, on_click, app_config
from dsl.capabilities import Caps

@on_click("inc")
def increment():
    count = count + 1
    label.text = f"Count: {count}"
    storage_put("counter", count)

@on_click("load")
def load():
    val = storage_get("counter", "0")
    count = int(val)
    label.text = f"Count: {count}"

app_spec = app(
    activity(
        "MainActivity",
        app_config(uses=[Caps.Storage]),
        state(count=0),
        ui(
            text("Count: 0", id="label"),
            button("+", id="inc"),
            button("Load", id="load"),
        ),
        increment,
        load,
    )
)
```

The `app_config(uses=[Caps.Storage])` declaration tells the compiler to inject the right manifest permissions and link the storage helper class.

## Step 5: Build and run

```bash
PYTHONPATH=. python myapp.py
```

This compiles, packages, signs, and installs the APK. If you want to just compile without installing:

```python
app_spec.build()
```

## What you've covered

- App and activity structure
- State declaration and mutation
- Theming with palettes and styles
- Multi-screen navigation
- Capability-scoped platform access (storage)
- Build and run

## Where to go from here

- Full API reference: [[00 - Home|back to Home]]
- How the compiler actually works: [[20 - Core Concepts/01 - How Ahnali Works]]
- All available capabilities: [[40 - Capabilities/01 - Overview]]
