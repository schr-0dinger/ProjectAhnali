---
tags: [ahnali, navigation, state, screens]
---

# Navigation, State, and Screens

Back to: [[00_Home]]

## State

```python
state(counter=0, step=1)
```

Constraints:
- keys must match `[A-Za-z_][A-Za-z0-9_]*`
- reserved names rejected: `app_ctx`, `nav_stack`, `nav_size`, `nav_current`
- keys cannot collide with generated widget field names
- values must be integer literals (`bool` rejected)

## Navigation Statements

- `Navigate(target)` / `navigate(target)`
- `Back()` / `back()`
- `Replace(target)` / `replace(target)`
- `PopToRoot()` / `pop_to_root()`
- `ClearStack()` / `clear_stack()`

Used inside handlers.

## Screen Graph Rules

- if one `Screen(...)` exists, all top-level `ui(...)` entries must be screens
- duplicate screen names are rejected
- generated nav stack fields are static and deterministic (`nav_stack`, `nav_size`, `nav_current`)

## Screen Transition Values

`Screen(..., transition=...)` supports:
- `fade`
- `slide_left`
- `slide_right`
- `slide_up`
- `slide_down`

Unsupported names fail compile-time validation.

## Example

```python
from dsl.app import app, activity, ui, Screen, text, button, on_click, Navigate, Back, PopToRoot, state

@on_click("go_settings")
def go_settings():
    Navigate("Settings")

@on_click("go_back")
def go_back():
    Back()

@on_click("go_root")
def go_root():
    PopToRoot()

app_spec = app(
    activity(
        "MainActivity",
        state(counter=0),
        ui(
            Screen("Home", text("Home", id="home_title"), button("Settings", id="go_settings")),
            Screen("Settings", text("Settings", id="settings_title"), button("Back", id="go_back"), button("Root", id="go_root"), transition="slide_left"),
        ),
        go_settings,
        go_back,
        go_root,
    )
)
```

## Known Lint Behavior

When screens are combined with global state, build emits a warning:
- state remains global across screens
- screen-local state is not yet supported
