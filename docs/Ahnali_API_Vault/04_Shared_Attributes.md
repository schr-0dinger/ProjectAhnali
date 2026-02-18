---
tags: [ahnali, attributes, style]
---

# Shared Attributes

Back to: [[00_Home]]

This note defines shared attribute groups reused by many components.
Use with [[14_Component_Attribute_Matrix]].

## Group A: Layout and Positioning

- `id`
- `layout`, `width`, `height`
- `padding`, `margin`
- `gravity`, `layout_gravity`
- `weight`, `weight_sum`
- `align`, `arrangement` (row/column gravity aliases)
- `relative`
- `constraints`
- `z_index`

### `gravity` accepted names

- `center`, `center_horizontal`, `center_vertical`
- `start`/`left`, `end`/`right`
- `top`, `bottom`
- raw int value also accepted

### `relative` rule format

List of `(verb, target)` tuples.

Supported verbs:
- `align_parent_left`, `align_parent_right`, `align_parent_top`, `align_parent_bottom`
- `align_parent_start`, `align_parent_end`
- `center_horizontal`, `center_vertical`, `center_in_parent`
- `align_left`, `align_right`, `align_top`, `align_bottom`
- `left_of`, `right_of`, `above`, `below`
- `align_baseline`, `align_start`, `align_end`, `start_of`, `end_of`

### `constraints` mapping keys

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

- `text_color`, `text_size`
- `font_family`, `font_weight`, `font_style`
- `letter_spacing`, `line_height`
- `text_alignment`
- `all_caps`, `max_lines`, `ellipsize`
- `hint_color`, `highlight_color`

Notes:
- `text_size` should use `sp(...)`.
- `font_style`: `normal`, `italic`, `oblique`.
- `ellipsize`: `start`, `middle`, `end`, `marquee`, `none`.

## Group C: Tint and Stateful Colors

- `text_tint`
- `tint`
- `thumb_tint`
- `track_tint`
- `progress_tint`
- `secondary_progress_tint`
- `button_tint`

These accept color values and `ColorState(...)` where supported.

## Group D: Accessibility

- `content_description`
- `accessibility_label` (fallback alias)
- `important_for_accessibility`

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

## Group F: Visual Effects and Transforms

- `opacity` (`0.0..1.0`)
- `border_width`, `border_color`, `border_radius`
- `ripple_color`
- `blur_radius` (API 31+, otherwise warning + skipped)
- `rotation`
- `scale_x`, `scale_y`
- `translation_x`, `translation_y`
- `clip_to_outline`, `clip_children`

`clip_children` only works on container-like kinds.

## Group G: Background Surface

- `background` can be flat color, `ColorState(...)`, or `Gradient(...)`
- `radius` rounds background shape

## Group H: Image-Specific Display

- `scale_type`
- `crop`
- `center_inside`
- `adjust_view_bounds`
- `image_alpha` (0..255)
- `image_matrix` (9-number affine matrix)

## Group I: Inline Event Attributes

Widgets can carry inline handlers:
- `on_click`
- `on_change`
- `on_text_change`
- `on_item_selected`
- `on_menu_item_selected`
- `on_focus_change`

Extended explicit decorators also exist (`on_touch`, `on_swipe`, `on_drag`, etc.); see [[10_Events_and_Handler_DSL]].

## Style and Theme Application

- `style=Style(...)` can be applied on widgets.
- `Theme(...)` channels apply by widget family.

Deterministic precedence:

`inline attrs > style= > Theme channel > widget defaults`

Overlap emits lint warnings.

## Theme Channels (Current)

- `text`
- `button`
- `input`
- `selector`
- `progress`
- `icon`
- `container`
- `appbar`
- compatibility: `row`, `column`

See also: [[09_Theme_Style_and_Presets]].
