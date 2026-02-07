# Widgets and Styling

This document lists the Pythonic DSL widgets and styling options.

## Core Widgets

`State(**kwargs)`  
Defines app state variables.

`Text(text, *, id="label", layout=None, padding=None, margin=None, gravity=None, text_color=None, background=None, text_size=None, radius=None, style=None)`  
Text view widget.

`Button(text, *, id="button", layout=None, padding=None, margin=None, gravity=None, text_color=None, background=None, text_size=None, radius=None, style=None)`  
Button widget.

`Row(*items, id="row", layout=None, padding=None, margin=None, gravity=None, background=None, radius=None, style=None)`  
Horizontal container (LinearLayout).

`Column(*items, id="column", layout=None, padding=None, margin=None, gravity=None, background=None, radius=None, style=None)`  
Vertical container (LinearLayout).

`AppBar(title, id="appbar", ...)`  
App bar widget. Current runtime class: `android.widget.Toolbar` (framework fallback).

`FloatingActionButton(text="+", id="fab", ...)`  
Floating action button widget. Current runtime class: `android.widget.ImageButton` (framework fallback).

`RaisedButton(text, id="raised_btn", ...)`  
Raised button widget. Current runtime class: `android.widget.Button` (framework fallback).

`FlatButton(text, id="flat_btn", ...)`  
Flat button widget. Current runtime class: `android.widget.Button` (framework fallback).

`IconButton(icon_text="*", id="icon_btn", ...)`  
Icon button widget. Current runtime class: `android.widget.ImageButton` (framework fallback).

`TextField(text="", id="input", hint=None, ...)`  
Text input widget. Runtime class: `android.widget.EditText`.

`Checkbox(text="", id="checkbox", checked=False, ...)`  
Checkbox widget. Runtime class: `android.widget.CheckBox`.

`Radio(text="", id="radio", checked=False, ...)`  
Radio widget. Runtime class: `android.widget.RadioButton`.

`Switch(text="", id="switch", checked=False, ...)`  
Switch widget. Runtime class: `android.widget.Switch`.

`Slider(id="slider", value=0, min=0, max=100, ...)`  
Slider widget. Runtime class: `android.widget.SeekBar` (framework fallback).

`DropdownButton(id="dropdown", items=None, ...)`  
Dropdown widget. Runtime class: `android.widget.Button` (fallback).

`ButtonBar(*items, id="button_bar", ...)`  
Button row widget. Runtime class: horizontal `LinearLayout`.

`PopupMenuButton(text="Menu", id="popup", items=None, ...)`  
Popup menu trigger widget. Current runtime class: `android.widget.Button` (menu behavior fallback).

## Layout Helpers

`layout`  
Tuple `(width, height)` where each value can be an `int` or one of:
`"match"`, `"match_parent"`, `"fill"`, `"wrap"`, `"wrap_content"`.

`padding` / `margin`  
Tuples `(left, top, right, bottom)` in pixels.

`gravity`  
Raw Android gravity int (e.g. `17` for center).

## Styling

`text_color`, `background`  
Accept int ARGB or hex strings `"#RRGGBB"` / `"#AARRGGBB"` or palette keys.

`text_size`  
Float/number in sp.

`radius`  
Float/number used for rounded corners (GradientDrawable).

### Style

`Style(...)`  
Reusable style object. Any field can be provided:
`layout`, `padding`, `margin`, `gravity`, `text_color`, `background`, `text_size`, `radius`.

### Theme

`Theme(palette=..., text=Style(...), button=Style(...), row=Style(...), column=Style(...))`  
Applies default styles per widget type. `palette` is a dict of color names to hex strings or ints.

### Presets

`presets(palette=None)`  
Helper with built-in style presets:

- `PrimaryButton(**overrides)`
- `DangerButton(**overrides)`
- `MutedText(**overrides)`
- `Card(**overrides)`

## Handler Actions

Use in `@on_click` handlers:

- `toast("message", duration=0)`  
  Runtime: `android.widget.Toast`.
- `snackbar("message", duration=0)`  
  Runtime fallback: `Toast` until Material dependency is bundled.
- `simple_dialog("Title", "Message")`  
  Runtime: `android.app.AlertDialog$Builder`.

## Mapping Status

Requested Material widgets are exposed in DSL now. Current runtime uses framework-safe fallbacks where needed:

| DSL Widget | Current Runtime Class |
| --- | --- |
| AppBar | `android.widget.Toolbar` |
| FloatingActionButton | `android.widget.ImageButton` |
| RaisedButton | `android.widget.Button` |
| FlatButton | `android.widget.Button` |
| IconButton | `android.widget.ImageButton` |
| TextField | `android.widget.EditText` |
| Checkbox | `android.widget.CheckBox` |
| Radio | `android.widget.RadioButton` |
| Switch | `android.widget.Switch` |
| Slider | `android.widget.SeekBar` |
| SimpleDialog | `android.app.AlertDialog$Builder` |
| PopupMenuButton | `android.widget.Button` |
| DropdownButton | `android.widget.Button` |
| ButtonBar | `android.widget.LinearLayout` |
| Toast | `android.widget.Toast` |
| Snackbar | `Toast` fallback |

## Colors

`from dsl.colors import colors` provides named hex strings:

- `colors.blue_600`, `colors.blue_500`
- `colors.emerald_500`, `colors.red_500`
- `colors.slate_900`, `colors.slate_700`, `colors.slate_500`
- `colors.zinc_100`, `colors.zinc_200`
- `colors.white`, `colors.black`

## Example

```python
from dsl.widgets import State, Text, Button, Row, Column, Theme, Style, presets
from dsl.colors import colors
from dsl.app import app, activity, ui

app_spec = app(
    activity(
        "MainActivity",
        Theme(
            palette={
                "bg": colors.zinc_100,
                "card": colors.white,
                "primary": colors.blue_600,
                "text": colors.slate_900,
                "muted": colors.slate_500,
                "on_primary": colors.white,
            },
            text=Style(text_color="text", text_size=16),
            button=Style(text_color="on_primary", text_size=16, radius=16),
            row=Style(background="card", radius=20),
            column=Style(background="card", radius=14),
        ),
        State(count=0, step=2),
        ui(
            Text("Count: 0", id="label", padding=(24, 24, 24, 24)),
            Row(
                Button("+", id="inc", style=presets().PrimaryButton()),
                Button("-", id="dec", style=presets().DangerButton()),
                id="actions",
                style=presets().Card(padding=(8, 8, 8, 8)),
            ),
            Column(
                Text("Hello", id="text", text_color="muted"),
                id="footer",
                style=presets().Card(padding=(16, 8, 16, 8)),
            ),
        ),
    )
)
```
