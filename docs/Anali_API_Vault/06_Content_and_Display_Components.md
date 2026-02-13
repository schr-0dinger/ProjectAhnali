---
tags: [anali, components, content]
---

# Content and Display Components

Back to: [[00_Home]]

See shared attrs: [[04_Shared_Attributes]].

## Text

Classification: text display (`TextView`).

Constructor (full surface):

```python
Text(
    text,
    *,
    id="label",
    layout=None, width=None, height=None,
    padding=None, margin=None, gravity=None, weight=None,
    relative=None, constraints=None,
    text_color=None, background=None, text_size=None, radius=None,
    font_family=None, font_weight=None, font_style=None,
    letter_spacing=None, line_height=None,
    text_alignment=None, all_caps=None, max_lines=None, ellipsize=None,
    tint=None, thumb_tint=None, track_tint=None, progress_tint=None, button_tint=None,
    content_description=None, important_for_accessibility=None, accessibility_label=None,
    elevation=None, pressed_elevation=None,
    text_shadow_color=None, text_shadow_radius=None, text_shadow_dx=None, text_shadow_dy=None,
    opacity=None,
    border_width=None, border_color=None, border_radius=None,
    ripple_color=None, blur_radius=None,
    rotation=None, scale_x=None, scale_y=None,
    translation_x=None, translation_y=None,
    clip_to_outline=None, clip_children=None,
    style=None,
)
```

Example:

```python
text(
    "Dashboard",
    id="title",
    text_size=sp(24),
    font_weight=700,
    letter_spacing=0.02,
    max_lines=1,
    ellipsize="end",
)
```

## View

Classification: generic visual element (`View`).

Constructor:

```python
View(
    *,
    id="view",
    layout=None, width=None, height=None,
    padding=None, margin=None, gravity=None, weight=None,
    relative=None, constraints=None,
    background=None, radius=None,
    tint=None, thumb_tint=None, track_tint=None, progress_tint=None, button_tint=None,
    content_description=None, important_for_accessibility=None, accessibility_label=None,
    elevation=None, pressed_elevation=None,
    text_shadow_color=None, text_shadow_radius=None, text_shadow_dx=None, text_shadow_dy=None,
    opacity=None, border_width=None, border_color=None, border_radius=None,
    ripple_color=None, blur_radius=None,
    rotation=None, scale_x=None, scale_y=None, translation_x=None, translation_y=None,
    clip_to_outline=None, clip_children=None,
    style=None,
)
```

## Button

Classification: action button (`Button`).

Constructor is the full button surface (`text` + optional `icon` + shared attrs).

Example:

```python
button(
    "Save",
    id="save_btn",
    icon="check",
    all_caps=True,
    background="#FF2563EB",
    text_color="#FFFFFFFF",
)
```

## RaisedButton / FlatButton / IconButton / FloatingActionButton

Classification: button variants.

Constructors:

```python
RaisedButton(text, *, id="raised_btn", **button_kwargs)
FlatButton(text, *, id="flat_btn", **button_kwargs)
IconButton(text="*", *, id="icon_btn", **button_kwargs)
FloatingActionButton(text="+", *, id="fab", **button_kwargs)
```

Runtime note:
- these are currently lowered through native/core widget classes and behavior paths.

## AppBar

Classification: top bar/title surface.

Constructor:

```python
AppBar(text, *, id="appbar", inline=False, **text_kwargs)
```

Specific field:
- `inline`: toggles inline title behavior path.

## Icon

Classification: icon-like text symbol.

Constructor:

```python
Icon(name, *, id="icon", **text_kwargs)
```

## Image

Classification: image display (`ImageView`).

Constructor:

```python
Image(*, id="image", src=None, content_description=None, accessibility_label=None, **view_kwargs)
```

`src` accepted forms:
- drawable name string
- integer resource id

## Divider

Classification: separator line.

Constructor:

```python
Divider(*, id="divider", color="#FFD1D5DB", thickness=dp(1), **view_kwargs)
```

## Card and Container

Card and Container are in structure category but are often used as display surfaces.

- `Card(*items, id="card", **kwargs)`
- `Container(*items, id="container", **kwargs)`

Both support background/radius/elevation/effects through shared attrs.
