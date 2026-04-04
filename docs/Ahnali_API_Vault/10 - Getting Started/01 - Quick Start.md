---
tags: [ahnali, getting-started, quickstart]
---

# Quick Start

> [!abstract] In 60 seconds
> Install dependencies, write three lines of Python, get an APK.

## Prerequisites

- Python 3.10+
- Android SDK with `aapt2`, `zipalign`, `apksigner` on your PATH
- `smali` and `d8` jars (or on PATH)
- An Android device or emulator for testing

## Install

```bash
git clone <repo-url>
cd ProjectAnali
pip install rich httpx pytest
```

That's it. No build system, no Gradle, no Android Studio required.

## Your first app

Create a file called `myapp.py`:

```python
from dsl.app import app, activity, ui, text

app_spec = app(
    activity(
        "MainActivity",
        ui(
            text("Hello from Ahnali", id="title"),
        ),
    )
)

app_spec.run()
```

Run it:

```bash
PYTHONPATH=. python myapp.py
```

This compiles your DSL to Smali, packages it into an APK, and installs it on your connected device. You should see "Hello from Ahnali" on screen.

## Add a button

```python
from dsl.app import app, activity, ui, text, button, on_click

@on_click("tap")
def handle_tap():
    label.text = "You tapped it"

app_spec = app(
    activity(
        "MainActivity",
        ui(
            text("Tap the button", id="label"),
            button("Tap me", id="tap"),
        ),
        handle_tap,
    )
)

app_spec.run()
```

## Run the tests

```bash
PYTHONPATH=. pytest -q
```

You should see **648 passing**. If anything fails, something's broken — don't ignore it.

## What's next

- Build a real app: [[02 - Your First App]]
- Set up a proper project: [[03 - Project Setup]]
- Understand how the compiler works: [[20 - Core Concepts/01 - How Ahnali Works]]

> [!tip] Connected device?
> `app_spec.run()` needs an adb device in `device` state. Run `adb devices` to check. If nothing's connected, you can still compile — just use `app_spec.build()` instead of `.run()`.
