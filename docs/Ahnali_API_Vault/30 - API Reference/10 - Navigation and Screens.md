---
tags: [ahnali, api, navigation, screens]
---

# Navigation and Screens

> [!abstract] Moving between screens
> Ahnali uses a compile-time navigation stack. Every screen is declared upfront, transitions are resolved at build time, and the system back button just works.

## Screen declaration

Screens are the top-level containers in a multi-screen app:

```python
from dsl.app import app, activity, ui, Screen, text, button, on_click, Navigate, Back

app(
    activity("Main",
        ui(
            Screen("Home",
                text("Welcome", id="title"),
                button("Go to Settings", id="go_settings"),
            ),
            Screen("Settings",
                text("Settings", id="settings_title"),
                button("Back", id="go_back"),
                transition="slide_left",
            ),
        ),
        on_click("go_settings", [Navigate("Settings")]),
        on_click("go_back", [Back()]),
    ),
)
```

> [!warning] Screen rules
> - If **any** `Screen(...)` is used, **every** top-level item in `ui(...)` must be a screen
> - You can't mix screens and regular widgets at the same level
> - Screen names must be unique — the compiler checks this

## Navigation operations

| Operation | What it does |
|---|---|
| `Navigate("ScreenName")` | Push a new screen onto the stack |
| `Back()` | Pop the current screen off the stack |
| `Replace("ScreenName")` | Replace the current screen (no back to it) |
| `PopToRoot()` | Pop everything except the first screen |
| `ClearStack()` | Pop everything, then navigate to a new screen |

> [!tip] When to use Replace
> Use `Replace` when the user shouldn't be able to go back — like after a login screen or a splash screen.

## Transitions

Screens support a `transition` parameter:

- `fade` — crossfade
- `slide_left` — push from right
- `slide_right` — push from left
- `slide_up` — push from bottom
- `slide_down` — push from top

```python
Screen("Details",
    text("Details", id="details_title"),
    transition="slide_left",
)
```

Transitions lower to `ViewPropertyAnimator` and `ObjectAnimator` under the hood. They're explicit and compile-time — no runtime transition engine.

## System back button

The back button works automatically. When the user presses back, the current screen pops off the stack. If you're on the root screen, the Activity handles it normally.

You can intercept it with `onSystemBack`:

```python
@on_system_back
def handle_back():
    # return 1 to handle (suppress default), 0 to let default behavior run
    if unsaved_changes:
        simple_dialog("Unsaved", "Discard changes?")
        return 1
    return 0
```

The compiler emits an `onBackPressed()` override on the wrapper Activity that calls your handler first. If it returns `1`, `invoke-super` is skipped. If it returns `0`, the default back behavior runs.

## Navigation stack semantics

The stack is a simple LIFO structure managed by the core runtime:

- `Navigate` pushes
- `Back` pops
- `Replace` pops then pushes
- `PopToRoot` pops until one remains
- `ClearStack` pops everything, then pushes the target

Screen uniqueness is enforced at compile time, so you can't navigate to a screen that doesn't exist.

## Learn more

- Screen component: [[30 - API Reference/04 - Structure Components]]
- Animation DSL: [[30 - API Reference/11 - Animation DSL]]
- Events and handlers: [[30 - API Reference/09 - Events and Handlers]]
