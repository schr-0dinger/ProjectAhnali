---
tags: [ahnali, values, units, colors]
---

# Value Types and Units

Back to: [[00_Home]]

## Units

## `dp(...)`
Density-independent pixels.

## `sp(...)`
Scale-independent pixels (text sizing).

## `px(...)`
Raw pixels.

## `percent(...)`
Percent helper for weighted layout conversion:
- percent width is supported only in horizontal rows
- percent height is supported only in vertical columns

## Layout Helpers

## `fill()`
Returns `"match_parent"`.

## `wrap()`
Returns `"wrap"`.

## `size(width, height)`
Returns tuple `(width, height)`.

Also available constants:
- `max_width = "max_width"`
- `max_height = "max_height"`
- `wrap_width = "wrap"`
- `wrap_height = "wrap"`

## Spacing Format (`padding`, `margin`)

Accepted values:
- single scalar: `dp(12)` or `12` (converted to dp)
- pair: `(horizontal, vertical)`
- quad: `(left, top, right, bottom)`

Each entry must resolve to `dp(...)` or `px(...)`.

Examples:

```python
padding=dp(12)
padding=(dp(16), dp(8))
margin=(dp(12), dp(8), dp(12), dp(8))
```

## Layout Size Format (`layout`, `width`, `height`)

`layout` accepts:
- shorthand string: `"match"`, `"wrap"`
- tuple: `(width, height)`

Size values accept:
- `"match"`, `"match_parent"`, `"fill"`, `"max"`, `"max_width"`, `"max_height"`
- `"wrap"`, `"wrap_content"`
- numeric px ints/floats
- `dp(...)` / `px(...)`

Rules:
- `sp(...)` is invalid for layout size.
- `Percent` goes through weight conversion path, not direct size.

## Color Values

Most color fields accept:
- hex string `"#RRGGBB"` or `"#AARRGGBB"`
- integer ARGB
- theme palette key (when used with `Theme(palette=...)`)

## `ColorState(...)`

```python
color_state(
    default="#FF111111",
    pressed="#FF222222",
    disabled="#FF888888",
    selected="#FF0055FF",
    focused="#FF00AAFF",
)
```

Fields:
- `default` (required)
- `pressed`, `disabled`, `selected`, `focused` (optional)

## `Gradient(...)`

```python
gradient("#FF111111", "#FF444444", "top_to_bottom")
```

Direction values:
- `left_to_right`
- `right_to_left`
- `top_to_bottom`
- `bottom_to_top`
- `tl_br`, `tr_bl`, `bl_tr`, `br_tl`
- aliases: `top_left_bottom_right`, `top_right_bottom_left`, `bottom_left_top_right`, `bottom_right_top_left`

## Boolean-like Fields

Some fields require strict bools (not arbitrary ints/strings), for example:
- `single_line`, `password`, `numeric_only`
- `clip_to_outline`, `clip_children`
- many flags in widget attrs and style

For `important_for_accessibility`, accepted forms are broader (see [[04_Shared_Attributes]]).
