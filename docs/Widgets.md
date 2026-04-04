# Widgets and Styling

Reference for every widget in the DSL, what it maps to at runtime, and how to style things.

## Widgets

### Containers

`Row(*items)` — horizontal LinearLayout.
`Column(*items)` — vertical LinearLayout.
`Container(*items)` — generic container.
`Card(*items)` — container with rounded corners and elevation.
`Relative(*items)` — RelativeLayout.
`Constraint(*items)` — ConstraintLayout.
`FrameLayout(*items)` — FrameLayout.
`ScrollView(child)` — single child, enforced at compile time.
`HorizontalScrollView(child)` — same, horizontal.

### Inputs

`Text(text, id=...)` — TextView.
`Button(text, id=...)` — Button.
`TextField(text="", id=..., hint=...)` — EditText.
`Checkbox(text, id=..., checked=False)` — CheckBox.
`Radio(text, id=..., checked=False)` — RadioButton.
`RadioGroup(*items, id=...)` — RadioGroup.
`Switch(text, id=..., checked=False)` — Switch.
`Slider(id=..., value=0, min=0, max=100)` — SeekBar.
`DropdownButton(id=..., items=...)` — Spinner.
`PopupMenuButton(text="Menu", id=..., items=...)` — Button with popup menu.
`Image(id=..., src=...)` — ImageView.
`ProgressBar(id=..., indeterminate=False)` — ProgressBar.

### Structural

`AppBar(title, id=...)` — Toolbar.
`FloatingActionButton(text="+", id=...)` — ImageButton fallback.
`RaisedButton(text, id=...)` — Button.
`FlatButton(text, id=...)` — Button.
`IconButton(icon_text="*", id=...)` — ImageButton.
`ButtonBar(*items, id=...)` — horizontal LinearLayout of buttons.
`ListView(items=[...], item_layout=...)` — static RecyclerView adapter.

## Layout

Every widget takes these:

- `layout` — `(width, height)` where each can be an int (px), `"match"`, `"wrap"`, or `"fill"`.
- `padding` / `margin` — `(left, top, right, bottom)` in pixels.
- `gravity` / `layout_gravity` — raw Android gravity ints.
- `weight` — LinearLayout weight.
- `percent` — for ConstraintLayout/Relative.

## Styling

Colors accept int ARGB, hex strings (`"#RRGGBB"` / `"#AARRGGBB"`), or palette key references.

Common style fields:
- `text_color`, `text_size` (sp), `background`, `radius` (corners)
- `font_family`, `font_weight`, `font_style`, `letter_spacing`, `line_height`
- `text_alignment`, `max_lines`, `ellipsize`, `all_caps`
- `tint`, `thumb_tint`, `track_tint`, `progress_tint`, `button_tint`
- `elevation`, `opacity`, `border_width`, `border_color`, `border_radius`
- `ripple_color`, `clip_to_outline`, `blur_radius` (API 31+)
- `rotation`, `scale_x`, `scale_y`, `translation_x`, `translation_y`
- `content_description`, `important_for_accessibility`

### ColorState

For stateful colors:

```python
ColorState(default="#000000", pressed="#333333", disabled="#999999")
```

Works on text_color, tint, background, and progress fields.

### Theme

```python
Theme(
    palette={"primary": "#2196F3", "bg": "#FAFAFA"},
    text=Style(text_color="primary", text_size=16),
    button=Style(text_color="white", radius=16),
)
```

Resolution order: inline attrs > style= > theme channel > widget defaults.

### Presets

```python
p = presets()
p.PrimaryButton()
p.DangerButton()
p.MutedText()
p.Card()
```

## Events

- `on_click` — Button, FAB, raised/flat/icon buttons, popup menu trigger
- `on_change` — Switch, Checkbox, Radio, Slider, RadioGroup
- `on_text_change` — TextField
- `on_item_selected` — Dropdown
- `on_menu_item_selected` — PopupMenu
- `on_focus_change` — any focusable widget

All handlers are named functions. No lambdas, no dynamic registration.

## Handler actions

Inside event handlers:

- `toast("message")` — android.widget.Toast
- `snackbar("message")` — Toast fallback until Material is bundled
- `simple_dialog("Title", "Message")` — AlertDialog.Builder
- `log("message")` — android.util.Log

## Runtime class mapping

| DSL Widget | Runtime Class |
|---|---|
| Text | TextView |
| Button | Button |
| AppBar | Toolbar |
| FloatingActionButton | ImageButton |
| RaisedButton | Button |
| FlatButton | Button |
| IconButton | ImageButton |
| TextField | EditText |
| Checkbox | CheckBox |
| Radio | RadioButton |
| Switch | Switch |
| Slider | SeekBar |
| DropdownButton | Spinner |
| Image | ImageView |
| ProgressBar | ProgressBar |
| PopupMenuButton | Button |
| SimpleDialog | AlertDialog.Builder |
| Snackbar | Toast (fallback) |

## Colors

```python
from dsl.colors import colors

colors.blue_600
colors.emerald_500
colors.slate_900
colors.zinc_100
# ... etc
```

## Example

```python
from dsl.widgets import Text, Button, Row, Column, Theme, Style, presets
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
            },
            text=Style(text_color="bg", text_size=16),
            button=Style(text_color="white", text_size=16, radius=16),
        ),
        ui(
            Text("Count: 0", id="label", padding=(24, 24, 24, 24)),
            Row(
                Button("+", id="inc", style=presets().PrimaryButton()),
                Button("-", id="dec", style=presets().DangerButton()),
            ),
        ),
    )
)
```
