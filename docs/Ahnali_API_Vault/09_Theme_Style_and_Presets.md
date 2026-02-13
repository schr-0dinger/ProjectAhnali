---
tags: [ahnali, theme, style, presets]
---

# Theme, Style, and Presets

Back to: [[00_Home]]

## `Style(...)`

`Style` contains reusable overrides for almost all visual/layout fields.

Constructor fields:

- layout/sizing:
  - `layout`, `width`, `height`, `padding`, `margin`, `gravity`, `weight`, `align`, `arrangement`, `weight_sum`, `relative`, `constraints`
- text/typography:
  - `text_color`, `text_size`, `font_family`, `font_weight`, `font_style`, `letter_spacing`, `line_height`, `text_alignment`, `all_caps`, `max_lines`, `ellipsize`
- background/shape:
  - `background`, `radius`, `border_width`, `border_color`, `border_radius`, `ripple_color`
- tint/stateful color:
  - `tint`, `thumb_tint`, `track_tint`, `progress_tint`, `button_tint`
- elevation/effects:
  - `elevation`, `pressed_elevation`, `text_shadow_color`, `text_shadow_radius`, `text_shadow_dx`, `text_shadow_dy`, `opacity`, `blur_radius`
- transforms/clip:
  - `rotation`, `scale_x`, `scale_y`, `translation_x`, `translation_y`, `clip_to_outline`, `clip_children`

## `Theme(...)`

Constructor:

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

Channels:
- `text`: text-like widgets
- `button`: button-like widgets
- `input`: text input widgets
- `selector`: checkbox/radio/switch families
- `progress`: progress/slider families
- `icon`: icon text surface
- `container`: containers/card/relative/constraint/screen
- `appbar`: app bar widgets
- compatibility channels: `row`, `column` (merged with container)

## `presets(...)`

```python
presets(palette=None)
```

Preset methods currently provided:
- `PrimaryButton(**overrides)`
- `DangerButton(**overrides)`
- `MutedText(**overrides)`
- `Card(**overrides)`

## Style Merge and Precedence

At lowering time:

`inline attrs > style= > Theme channel > widget defaults`

If a field exists in multiple layers, a lint warning is emitted describing precedence.

## Example: Theme + Inline Override

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
            button("Save", id="save", text_color="#FFFFEE58"),  # inline overrides theme text_color
        ),
    )
)
```

See also:
- [[04_Shared_Attributes]]
- [[13_Validation_and_Diagnostics]]
