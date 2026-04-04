---
tags: [ahnali, api-reference, theme, style, presets, color-state, gradient]
---

# 08 — Theme, Style, and Presets

> [!abstract] What this covers
> `Theme` with palette and channels, `Style` objects, `ColorState`, `Gradient`, built-in presets, and the resolution order.

Related: [[02 - Value Types and Units]] · [[03 - Shared Attributes]] · [[12 - Validation and Diagnostics]]

---

## `Style(...)`

`Style` is the reusable style bag. Apply it via `style=Style(...)` on any widget.

### Representative Fields

| Category | Fields |
|---|---|
| **Layout/sizing** | `layout`, `width`, `height`, `padding`, `margin`, `gravity`, `weight`, `align`, `arrangement`, `weight_sum`, `relative`, `constraints` |
| **Text/typography** | `text_color`, `text_size`, `font_family`, `font_weight`, `font_style`, `letter_spacing`, `line_height`, `text_alignment`, `all_caps`, `max_lines`, `ellipsize`, `hint_color`, `highlight_color` |
| **Tint/stateful** | `text_tint`, `tint`, `thumb_tint`, `track_tint`, `progress_tint`, `secondary_progress_tint`, `button_tint` |
| **Background/shape** | `background`, `radius`, `border_width`, `border_color`, `border_radius`, `ripple_color`, `opacity`, `blur_radius` |
| **Transforms/clip** | `rotation`, `scale_x`, `scale_y`, `translation_x`, `translation_y`, `clip_to_outline`, `clip_children` |
| **Image-specific** | `scale_type`, `crop`, `center_inside`, `adjust_view_bounds`, `image_alpha`, `image_matrix` |

```python
card_style = Style(
    background="#FFFFFFFF",
    radius=dp(12),
    padding=dp(16),
    elevation=dp(4),
)

card("Content", style=card_style)
```

---

## `Theme(...)`

```python
Theme(
    *,
    palette=None,
    text=None,
    button=None,
    input=None,
    selector=None,
    progress=None,
    icon=None,
    container=None,
    appbar=None,
    row=None,
    column=None,
)
```

### Channel Mapping

| Channel | Applied To |
|---|---|
| `palette` | Named color keys referenced by other fields |
| `text` | All text widgets (merged into channel-specific styles) |
| `button` | `Button`, `RaisedButton`, `FlatButton`, `IconButton`, `FloatingActionButton` |
| `input` | `TextField` (merged with `text`) |
| `selector` | `Checkbox`, `Radio`, `Switch`, `Slider`, `DropdownButton`, `PopupMenuButton`, `RadioGroup` (merged with `text`) |
| `progress` | `ProgressBar` |
| `icon` | `Icon` (merged with `text`) |
| `container` | `Container`, `Card`, `Relative`, `Constraint`, `Frame`, `CoordinatorLayout`, `DrawerLayout`, `RecyclerView`, `FragmentContainer`, `ViewPager`, `Screen` |
| `appbar` | `AppBar` (merged with `text`) |
| `row` / `column` | Backward-compatible overlays merged on top of `container` |

> [!tip] Palette keys are your theme's design tokens
> Define colors in `palette={}` and reference them by key in style fields. This makes theme swaps a one-line change.

```python
Theme(
    palette={
        "primary": "#FF2563EB",
        "on_primary": "#FFFFFFFF",
        "surface": "#FFFFFFFF",
        "text_main": "#FF0F172A",
        "text_muted": "#FF64748B",
    },
    text=Style(text_color="text_main", text_size=sp(16)),
    button=Style(background="primary", text_color="on_primary"),
)
```

---

## `ColorState(...)`

Stateful color for widget states. See [[02 - Value Types and Units]] for full details.

```python
color_state(
    default="#FF2563EB",
    pressed="#FF1D4ED8",
    disabled="#FF94A3B8",
)
```

---

## `Gradient(...)`

Gradient drawable for backgrounds. See [[02 - Value Types and Units]] for full details.

```python
gradient("#FF6366F1", "#FF8B5CF6", "top_to_bottom", kind="linear")
```

---

## Presets

```python
presets(palette=None)
```

Built-in preset style generators:

| Preset | Purpose |
|---|---|
| `PrimaryButton(**overrides)` | Primary action button style |
| `DangerButton(**overrides)` | Destructive action button style |
| `MutedText(**overrides)` | Secondary/muted text style |
| `Card(**overrides)` | Card surface style |

```python
from dsl.api import presets

p = presets()
button("Save", style=p.PrimaryButton())
text("Optional", style=p.MutedText())
```

---

## Resolution Order

> [!important] Deterministic precedence
>
> **inline attrs > `style=` > Theme channel > widget defaults**
>
> When the same field is set at multiple levels, the highest-precedence value wins. Overlap between levels emits lint warnings.

```
Widget constructor kwargs (inline)
        ↓ overrides
    style=Style(...)
        ↓ overrides
    Theme channel (e.g. button=Style(...))
        ↓ overrides
    Widget built-in defaults
```

### Full Example

```python
from dsl.api import Theme, Style, app, activity, ui, text, button, sp

app_spec = app(
    activity(
        "MainActivity",
        Theme(
            palette={
                "primary": "#FF2563EB",
                "on_primary": "#FFFFFFFF",
                "text_main": "#FF0F172A",
            },
            text=Style(text_color="text_main", text_size=sp(16)),
            button=Style(background="primary", text_color="on_primary"),
        ),
        ui(
            text("Hello", id="title"),
            # inline text_color overrides Theme channel
            button("Save", id="save", text_color="#FFFFEE58"),
        ),
    ),
)
```

In this example:
- `text("Hello")` gets `text_color="text_main"` (#FF0F172A) and `text_size=sp(16)` from the `text` Theme channel
- `button("Save")` gets `background="primary"` and `text_color="on_primary"` from the `button` Theme channel, but the inline `text_color="#FFFFEE58"` overrides the theme

> [!note] Overlap warnings
> If the same field is set by both inline attrs and `style=`, or by `style=` and Theme channel, the compiler emits a lint warning. The higher-precedence value still wins.

---

## See Also

- [[02 - Value Types and Units]] — ColorState, Gradient, color formats
- [[03 - Shared Attributes]] — all style-able fields by group
- [[09 - Events and Handlers]] — applying styles to interactive widgets
- [[12 - Validation and Diagnostics]] — style compatibility checks
