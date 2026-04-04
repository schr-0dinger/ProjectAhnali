---
tags: [ahnali, api-reference, attributes, shared, style]
---

# 03 — Shared Attributes

> [!abstract] What this covers
> Every shared attribute grouped by concern (A through I). These groups are reused across components — see [[13 - Component Attribute Matrix]] for the full component-to-group mapping.

Related: [[02 - Value Types and Units]] · [[13 - Component Attribute Matrix]]

---

## Style Precedence (applies to all groups)

> [!important] Deterministic precedence order
>
> **inline attrs > `style=` > Theme channel > widget defaults**
>
> When the same field is set at multiple levels, the highest-precedence value wins. Overlap between levels emits lint warnings.

```python
# Example of all four levels
Theme(
    text=Style(text_color="#FF000000"),  # Theme channel
)
ui(
    text(
        "Hello",
        id="greeting",
        text_color="#FF0000FF",           # inline attr (wins)
        style=Style(text_color="#FF00FF00"),  # style= (second)
    ),
)
```

---

## Group A: Layout and Positioning

| Attribute | Type | Description |
|---|---|---|
| `id` | `str` | Unique widget identifier |
| `layout` | `str` \| `tuple` | Shorthand for `(width, height)` — accepts `"match"`, `"wrap"`, or tuple |
| `width` / `height` | size value | Individual dimension — see [[02 - Value Types and Units]] |
| `padding` | spacing | Inner spacing — single, pair, or quad |
| `margin` | spacing | Outer spacing — single, pair, or quad |
| `gravity` | `str` \| `int` | Content alignment within the widget |
| `layout_gravity` | `str` \| `int` | Widget alignment within its parent |
| `weight` | `int` | Flex weight in Row/Column |
| `weight_sum` | `int` | Total weight of the parent container |
| `align` | `str` | Row/column gravity alias |
| `arrangement` | `str` | Row/column gravity alias |
| `relative` | `list` | List of `(verb, target)` tuples for RelativeLayout |
| `constraints` | `dict` | ConstraintLayout constraint mapping |
| `z_index` | `int` | Drawing order override |

### `gravity` Accepted Names

`center`, `center_horizontal`, `center_vertical`, `start` / `left`, `end` / `right`, `top`, `bottom`, or raw int value.

### `relative` Rule Format

List of `(verb, target_id)` tuples.

| Verb | Description |
|---|---|
| `align_parent_left` | Align left edge to parent |
| `align_parent_right` | Align right edge to parent |
| `align_parent_top` | Align top edge to parent |
| `align_parent_bottom` | Align bottom edge to parent |
| `align_parent_start` | Align start edge to parent |
| `align_parent_end` | Align end edge to parent |
| `center_horizontal` | Center horizontally in parent |
| `center_vertical` | Center vertically in parent |
| `center_in_parent` | Center in both axes |
| `align_left` | Align left to target |
| `align_right` | Align right to target |
| `align_top` | Align top to target |
| `align_bottom` | Align bottom to target |
| `left_of` | Position to the left of target |
| `right_of` | Position to the right of target |
| `above` | Position above target |
| `below` | Position below target |
| `align_baseline` | Align text baseline to target |
| `align_start` | Align start to target |
| `align_end` | Align end to target |
| `start_of` | Position to the start of target |
| `end_of` | Position to the end of target |

### `constraints` Mapping Keys

| Key | Description |
|---|---|
| `left_to_left` / `left_to_right` | Left edge constraints |
| `right_to_left` / `right_to_right` | Right edge constraints |
| `top_to_top` / `top_to_bottom` | Top edge constraints |
| `bottom_to_top` / `bottom_to_bottom` | Bottom edge constraints |
| `start_to_start` / `start_to_end` | Start edge constraints |
| `end_to_start` / `end_to_end` | End edge constraints |
| `baseline_to_baseline` | Baseline alignment |
| `circle` / `circle_radius` / `circle_angle` | Circular positioning |
| `horizontal_bias` / `vertical_bias` | Bias within constraint range (0.0–1.0) |

```python
# Relative example
relative=[
    ("below", "title"),
    ("align_parent_start"),
]

# Constraint example
constraints={
    "top_to_top": "parent",
    "left_to_left": "parent",
    "right_to_right": "parent",
    "horizontal_bias": 0.5,
}
```

---

## Group B: Typography

| Attribute | Type | Description |
|---|---|---|
| `text_color` | color | Text color |
| `text_size` | `sp(...)` | Font size — **must use `sp()`** |
| `font_family` | `str` | Font family name |
| `font_weight` | `str` \| `int` | Weight: `normal`, `bold`, or numeric |
| `font_style` | `str` | `normal`, `italic`, `oblique` |
| `letter_spacing` | `float` | Extra spacing between characters (em units) |
| `line_height` | `float` \| `sp(...)` | Line spacing |
| `text_alignment` | `str` | `text_start`, `text_end`, `center`, `view_start`, `view_end` |
| `all_caps` | `bool` | Force uppercase |
| `max_lines` | `int` | Maximum number of lines |
| `ellipsize` | `str` | `start`, `middle`, `end`, `marquee`, `none` |
| `hint_color` | color | Hint text color (TextField) |
| `highlight_color` | color | Text selection highlight color |

> [!warning] `text_size` must use `sp()`
> Using `dp()` or raw numbers for `text_size` is rejected at compile time.

---

## Group C: Tint and Stateful Colors

| Attribute | Common On |
|---|---|
| `text_tint` | Text, Icon |
| `tint` | Generic views, Image |
| `thumb_tint` | Slider, Switch |
| `track_tint` | Slider, Switch |
| `progress_tint` | ProgressBar |
| `secondary_progress_tint` | ProgressBar |
| `button_tint` | Checkbox, Radio, Switch, Button |

All accept color values and `ColorState(...)` where supported.

---

## Group D: Accessibility

| Attribute | Description |
|---|---|
| `content_description` | Accessibility description text |
| `accessibility_label` | Fallback alias for `content_description` |
| `important_for_accessibility` | Controls accessibility importance |

### `important_for_accessibility` Accepted Values

| Form | Values |
|---|---|
| **Strings** | `auto`, `yes`, `no`, `no_hide_descendants` |
| **Bools** | `True`, `False` |
| **Ints** | `0` (auto), `1` (yes), `2` (no), `4` (no_hide_descendants) |

```python
content_description="Submit form button"
important_for_accessibility="yes"
```

> [!tip] Always set `content_description` for interactive widgets
> Screen readers depend on it. Buttons, checkboxes, switches, and image views should all have descriptions.

---

## Group E: Elevation and Shadow

| Attribute | Description |
|---|---|
| `elevation` | Z-axis elevation in dp |
| `pressed_elevation` | Elevation when pressed |
| `text_shadow_color` | Shadow color for text |
| `text_shadow_radius` | Shadow blur radius |
| `text_shadow_dx` | Shadow horizontal offset |
| `text_shadow_dy` | Shadow vertical offset |

---

## Group F: Visual Effects and Transforms

| Attribute | Type | Description |
|---|---|---|
| `opacity` | `float` | `0.0` (transparent) to `1.0` (opaque) |
| `border_width` | size | Border stroke width |
| `border_color` | color | Border color |
| `border_radius` | size | Corner radius |
| `ripple_color` | color | Ripple effect color |
| `blur_radius` | `float` | Blur radius — **API 31+ only** |
| `rotation` | `float` | Rotation in degrees |
| `scale_x` / `scale_y` | `float` | Scale factors |
| `translation_x` / `translation_y` | size | Translation offsets |
| `clip_to_outline` | `bool` | Clip content to rounded outline |
| `clip_children` | `bool` | Clip child views to bounds (container widgets only) |

> [!warning] `blur_radius` requires API 31+
> If `min_sdk < 31`, blur is skipped with a warning. See [[12 - Validation and Diagnostics]].

> [!note] `clip_children` is container-only
> Setting `clip_children` on non-container widgets is rejected at compile time.

---

## Group G: Background Surface

| Attribute | Description |
|---|---|
| `background` | Flat color, `ColorState(...)`, or `Gradient(...)` |
| `radius` | Rounds the background shape corners |

```python
# Flat color
background="#FFF1F5F9"

# ColorState
background=color_state(default="#FFFFFF", pressed="#F1F5F9")

# Gradient
background=gradient("#FF6366F1", "#FF8B5CF6", "top_to_bottom")
```

---

## Group H: Image-Specific Display

| Attribute | Description |
|---|---|
| `scale_type` | `matrix`, `fit_xy`, `fit_start`, `fit_center`, `fit_end`, `center`, `center_crop`, `center_inside` |
| `crop` | Shorthand for `center_crop` |
| `center_inside` | Shorthand for `center_inside` |
| `adjust_view_bounds` | Adjust view bounds to match image aspect ratio |
| `image_alpha` | Alpha value `[0, 255]` |
| `image_matrix` | 9-number affine transformation matrix |

See [[05 - Content and Display]] for the `Image` component details.

---

## Group I: Inline Event Attributes

Widgets can carry inline handlers directly as constructor kwargs:

| Attribute | Fires On |
|---|---|
| `on_click` | Tap/click |
| `on_change` | State change (checkbox, switch, slider, radio) |
| `on_text_change` | Text input change (TextField) |
| `on_item_selected` | Item selection (Dropdown) |
| `on_menu_item_selected` | Menu item selection (PopupMenu) |
| `on_focus_change` | Focus gain/loss |

```python
button("Save", id="save_btn", on_click=toast("Saved!"))
checkbox("Remember me", id="remember", on_change=log("changed"))
```

> [!warning] Inline + explicit conflict
> If you bind both an inline attribute and an explicit event spec (e.g., `on_click(target_id, ...)`) to the same widget, the compiler rejects it as a duplicate binding. See [[09 - Events and Handlers]].

Extended explicit decorators (`on_touch`, `on_swipe`, `on_drag`, etc.) exist beyond these inline attrs — see [[09 - Events and Handlers]].

---

## See Also

- [[02 - Value Types and Units]] — dp, sp, colors, gradients
- [[05 - Content and Display]] — Text, Button, Image components
- [[06 - Input and Selection]] — TextField, Checkbox, Slider components
- [[08 - Theme Style and Presets]] — Theme, Style, and precedence
- [[09 - Events and Handlers]] — full event decorator system
- [[13 - Component Attribute Matrix]] — which groups each component supports
