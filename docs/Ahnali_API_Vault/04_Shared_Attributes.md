---
tags: [ahnali, attributes, style]
---

# Shared Attributes

Back to: [[00_Home]]

This note defines shared attribute groups reused by many components.
Use this with [[14_Component_Attribute_Matrix]].

## Group A: Layout and Positioning

- `id`: unique widget id string.
- `layout`: tuple or shorthand size (`("match", "wrap")`, etc.).
- `width`, `height`: direct size overrides.
- `padding`, `margin`: spacing values.
- `gravity`: integer or named gravity.
- `weight`: linear layout weight for child.
- `weight_sum`: parent weight sum (row/column).
- `align`, `arrangement`: row/column gravity aliases.
- `relative`: RelativeLayout rules list.
- `constraints`: ConstraintLayout mapping.

### `gravity` accepted names

- `center`
- `center_horizontal`
- `center_vertical`
- `start` / `left`
- `end` / `right`
- `top`
- `bottom`

Raw int gravity is also accepted.

### `relative` rule format

List of `(verb, target)` tuples.

Example:

```python
relative=[
    ("align_parent_top", "parent"),
    ("center_horizontal", "parent"),
    ("below", "title"),
]
```

Supported verbs:
- `align_parent_left`, `align_parent_right`, `align_parent_top`, `align_parent_bottom`
- `align_parent_start`, `align_parent_end`
- `center_horizontal`, `center_vertical`, `center_in_parent`
- `align_left`, `align_right`, `align_top`, `align_bottom`
- `left_of`, `right_of`, `above`, `below`
- `align_baseline`
- `align_start`, `align_end`
- `start_of`, `end_of`

### `constraints` mapping keys

Example:

```python
constraints={
    "start_to_start": "parent",
    "end_to_end": "parent",
    "top_to_top": "parent",
    "horizontal_bias": 0.5,
}
```

Supported keys:
- `left_to_left`, `left_to_right`
- `right_to_left`, `right_to_right`
- `top_to_top`, `top_to_bottom`
- `bottom_to_top`, `bottom_to_bottom`
- `start_to_start`, `start_to_end`
- `end_to_start`, `end_to_end`
- `baseline_to_baseline`
- `circle`, `circle_radius`, `circle_angle`
- `horizontal_bias`, `vertical_bias`

## Group B: Text/Typography

- `text_color`
- `text_size`
- `font_family`
- `font_weight`
- `font_style`
- `letter_spacing`
- `line_height`
- `text_alignment`
- `all_caps`
- `max_lines`
- `ellipsize`

### Text value constraints

- `text_size` should use `sp(...)` for reliable behavior.
- `font_style`: `normal`, `italic`, `oblique`.
- `text_alignment`: `inherit`, `gravity`, `text_start`, `text_end`, `center`, `view_start`, `view_end`, or int.
- `ellipsize`: `start`, `middle`, `end`, `marquee`, `none`.

## Group C: Tint and Stateful Colors

- `tint`
- `thumb_tint`
- `track_tint`
- `progress_tint`
- `button_tint`

These accept color values and `ColorState(...)` where supported.

## Group D: Accessibility

- `content_description`
- `important_for_accessibility`
- `accessibility_label` (alias for content description)

`important_for_accessibility` accepted values:
- strings: `auto`, `yes`, `no`, `no_hide_descendants`
- bools: `True`/`False`
- ints: `0`, `1`, `2`, `4`

## Group E: Elevation and Shadow

- `elevation`
- `pressed_elevation`
- `text_shadow_color`
- `text_shadow_radius`
- `text_shadow_dx`
- `text_shadow_dy`

Notes:
- text shadow applies only to text-like widgets.
- `pressed_elevation` lowers through explicit state animator path.

## Group F: Visual Effects

- `opacity` (`0.0..1.0`)
- `border_width`
- `border_color`
- `border_radius` (scalar or 4-corner tuple)
- `ripple_color`
- `blur_radius` (API 31+, otherwise warning + skipped)
- `rotation`
- `scale_x`, `scale_y`
- `translation_x`, `translation_y`
- `clip_to_outline`
- `clip_children`

## Group G: Background Surface

- `background` can be:
  - flat color
  - `ColorState(...)` (default-only fill currently)
  - `Gradient(...)`
- `radius` can be used for rounded shape background.

## Style and Theme Application

- `style=Style(...)` can be applied on widgets.
- `Theme(...)` channels apply by widget family.

Current deterministic precedence:

`inline attrs > style= > Theme channel > widget defaults`

If the same field is set in multiple layers, a lint warning is emitted noting this precedence.

## Theme Channels (Current)

- `text`
- `button`
- `input`
- `selector`
- `progress`
- `icon`
- `container`
- `appbar`
- compatibility channels: `row`, `column`

See also: [[09_Theme_Style_and_Presets]].
