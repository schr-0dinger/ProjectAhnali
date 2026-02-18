---
tags: [ahnali, theme, style, presets]
---

# Theme, Style, and Presets

Back to: [[00_Home]]

## `Style(...)`

`Style` is the reusable style bag used by `style(...)` and theme channels.

Representative fields:
- layout/sizing: `layout`, `width`, `height`, `padding`, `margin`, `gravity`, `weight`, `align`, `arrangement`, `weight_sum`, `relative`, `constraints`
- text/typography: `text_color`, `text_size`, `font_family`, `font_weight`, `font_style`, `letter_spacing`, `line_height`, `text_alignment`, `all_caps`, `max_lines`, `ellipsize`, `hint_color`, `highlight_color`
- tint/stateful: `text_tint`, `tint`, `thumb_tint`, `track_tint`, `progress_tint`, `secondary_progress_tint`, `button_tint`
- background/shape/effects: `background`, `radius`, `border_width`, `border_color`, `border_radius`, `ripple_color`, `opacity`, `blur_radius`
- transforms/clip: `rotation`, `scale_x`, `scale_y`, `translation_x`, `translation_y`, `clip_to_outline`, `clip_children`
- image-specific: `scale_type`, `crop`, `center_inside`, `adjust_view_bounds`, `image_alpha`, `image_matrix`

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

Channel mapping highlights:
- `appbar`: merged with `text` for `AppBar`
- `input`: merged with `text` for `TextField`
- `selector`: merged with `text` for `Checkbox`/`Radio`/`Switch`; also used for `Slider`, `DropdownButton`, `PopupMenuButton`, `RadioGroup`
- `progress`: `ProgressBar`
- `icon`: merged with `text` for `Icon`
- `container`: containers/layout surfaces (`Container`, `Card`, `Relative`, `Constraint`, `Frame`, `CoordinatorLayout`, `DrawerLayout`, `RecyclerView`, `FragmentContainer`, `ViewPager`, `Screen`)
- `row` / `column`: backward-compatible overlays merged on top of `container`

## `presets(...)`

```python
presets(palette=None)
```

Built-in preset methods:
- `PrimaryButton(**overrides)`
- `DangerButton(**overrides)`
- `MutedText(**overrides)`
- `Card(**overrides)`

## Merge/Precedence Rule

Lowering precedence is deterministic:

`inline attrs > style= > Theme channel > widget defaults`

Overlap emits lint warnings.

## Example

```python
from dsl.app import Theme, Style, app, activity, ui, text, button, sp

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
            button("Save", id="save", text_color="#FFFFEE58"),  # inline override
        ),
    )
)
```

See also:
- [[04_Shared_Attributes]]
- [[13_Validation_and_Diagnostics]]
