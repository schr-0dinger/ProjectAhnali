---
tags: [ahnali, api-reference, values, units, colors, gradients]
---

# 02 - Value Types and Units

> [!abstract] What this covers
> The building blocks you use everywhere: `dp()`, `sp()`, `px()`, `percent()`, `fill()`, `wrap()`, `size()`, spacing formats, color values, `ColorState()`, `Gradient()`, and boolean-like fields.

Related: [[03 - Shared Attributes]] · [[08 - Theme Style and Presets]]

---

## Dimensional Units

### `dp(value)`

Density-independent pixels. The default unit for layout dimensions.

```python
padding=dp(16)
margin=dp(8)
```

### `sp(value)`

Scale-independent pixels. **Use this for text sizing** - it respects the user's system font scale preference.

```python
text_size=sp(16)
```

> [!warning] `sp()` is invalid for layout sizes
> Using `sp()` in `width`, `height`, `padding`, or `margin` is rejected at compile time. Layout sizes must use `dp()` or `px()`.

### `px(value)`

Raw pixels. Use sparingly - only when you need exact pixel control.

```python
border_width=px(1)
```

### `percent(value)`

Percent helper for weighted layout conversion.

> [!important] Context matters
> - Percent **width** is supported only in horizontal `Row`
> - Percent **height** is supported only in vertical `Column`

```python
# Inside a Row - percent of parent width
Row(
    text("Left", width=percent(30)),
    text("Right", width=percent(70)),
)
```

---

## Layout Helpers

### `fill()`

Returns `"match_parent"` - the widget expands to fill its parent.

### `wrap()`

Returns `"wrap"` - the widget sizes to its content.

### `size(width, height)`

Returns a `(width, height)` tuple. Shorthand for setting both dimensions at once.

```python
layout=size(dp(200), dp(100))
```

### Constants

| Constant | Value |
|---|---|
| `max_width` | `"max_width"` |
| `max_height` | `"max_height"` |
| `wrap_width` | `"wrap"` |
| `wrap_height` | `"wrap"` |

---

## Spacing Format (`padding`, `margin`)

Three accepted forms:

| Form | Example | Meaning |
|---|---|---|
| **Single scalar** | `dp(12)` or `12` | All four sides |
| **Pair** | `(dp(16), dp(8))` | `(horizontal, vertical)` |
| **Quad** | `(dp(8), dp(12), dp(8), dp(16))` | `(left, top, right, bottom)` |

Each entry must resolve to `dp(...)` or `px(...)`.

```python
# All sides = 16dp
padding=dp(16)

# Horizontal 16dp, vertical 8dp
padding=(dp(16), dp(8))

# Left 8, top 12, right 8, bottom 16
padding=(dp(8), dp(12), dp(8), dp(16))
```

---

## Layout Size Format (`layout`, `width`, `height`)

The `layout` shorthand accepts:

- String shorthand: `"match"`, `"wrap"`
- Tuple: `(width, height)`

Individual `width` / `height` accept:

| Value | Meaning |
|---|---|
| `"match"`, `"match_parent"`, `"fill"`, `"max"` | Fill parent |
| `"wrap"`, `"wrap_content"` | Wrap content |
| `"max_width"`, `"max_height"` | Max dimension |
| Numeric int/float | Pixels |
| `dp(value)` | Density-independent pixels |
| `px(value)` | Raw pixels |

> [!warning] No `sp()` for layout
> `sp(...)` is explicitly rejected for layout sizes. Use it only for `text_size`.

---

## Color Values

Most color fields accept any of:

| Form | Example |
|---|---|
| **Hex RGB** | `"#FF2563EB"` |
| **Hex RGB (no alpha)** | `"#2563EB"` |
| **Integer ARGB** | `0xFF2563EB` |
| **Palette key** | `"primary"` (resolved through `Theme(palette=...)`) |

```python
# Direct hex
text_color="#FF0F172A"

# Palette key (requires Theme with palette)
background="primary"

# Integer ARGB
background=0xFFFF0000
```

> [!tip] Use palette keys for theming
> Define colors in your `Theme(palette={...})` and reference them by key. This makes theme swaps trivial.

---

## `ColorState(...)`

Stateful color that changes based on widget state.

```python
color_state(
    default="#FF111111",
    pressed="#FF222222",
    disabled="#FF888888",
    selected="#FF0055FF",
    focused="#FF00AAFF",
)
```

| Field | Required | Purpose |
|---|---|---|
| `default` | Yes | Base color |
| `pressed` | No | When widget is pressed |
| `disabled` | No | When widget is disabled |
| `selected` | No | When widget is selected |
| `focused` | No | When widget has focus |

> [!note] Background ColorState limitation
> Background `ColorState` currently uses the default color for fill, with a lint fallback warning for non-default states. See [[12 - Validation and Diagnostics]].

---

## `Gradient(...)`

Creates a drawable gradient background.

```python
gradient("#FF111111", "#FF444444", "top_to_bottom", kind="linear")
```

### Direction Values

| Value | Aliases |
|---|---|
| `left_to_right` | - |
| `right_to_left` | - |
| `top_to_bottom` | - |
| `bottom_to_top` | - |
| `tl_br` | `top_left_bottom_right` |
| `tr_bl` | `top_right_bottom_left` |
| `bl_tr` | `bottom_left_top_right` |
| `br_tl` | `bottom_right_top_left` |

### Kind Values

| Value | Description |
|---|---|
| `linear` | Linear gradient (default) |
| `radial` | Radial gradient from center |
| `sweep` | Sweep (conic) gradient |

```python
# Linear gradient, top to bottom
background=gradient("#FF6366F1", "#FF8B5CF6", "top_to_bottom")

# Radial gradient
background=gradient("#FF6366F1", "#FF1E1B4B", "center", kind="radial")
```

> [!warning] Invalid gradient config is caught at compile time
> Missing colors, unknown directions, or unsupported kinds fail validation. See [[12 - Validation and Diagnostics]].

---

## Boolean-like Fields

Many config flags require strict booleans. The compiler validates these and rejects truthy/falsy substitutes.

| Fields | Example |
|---|---|
| `single_line` | `single_line=True` |
| `password` | `password=True` |
| `numeric_only` | `numeric_only=True` |
| `clip_to_outline` | `clip_to_outline=True` |
| `clip_children` | `clip_children=True` |
| `indeterminate` | `indeterminate=True` |

> [!important] `important_for_accessibility` is special
> This field accepts bool, int, or string forms. See [[03 - Shared Attributes]] for the full list of accepted values.

---

## See Also

- [[03 - Shared Attributes]] - attribute groups A through I
- [[08 - Theme Style and Presets]] - Theme, palette, and style resolution
- [[12 - Validation and Diagnostics]] - compile-time type checks
