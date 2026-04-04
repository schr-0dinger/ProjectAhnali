---
tags: [ahnali, api-reference, components, content, display, text, button, image]
---

# 05 - Content and Display

> [!abstract] What this covers
> The widgets that show things on screen: `Text`, `View`, the Button family, `AppBar`, `Icon`, `Image`, and `Divider`.

Related: [[03 - Shared Attributes]] · [[13 - Component Attribute Matrix]]

---

## Text

```python
Text(text, *, id="label", ..., style=None)
text(text, *, id="label", ..., style=None)  # lowercase alias
```

Classification: `TextView`.

Supports full typography (Group B), tint (Group C), accessibility (Group D), elevation (Group E), visual effects (Group F), background (Group G), and inline events (Group I).

```python
text("Hello, World", id="greeting",
    text_size=sp(24),
    text_color="#FF0F172A",
    font_weight="bold",
    text_alignment="center",
)
```

> [!tip] Use `text()` alias for brevity
> The lowercase `text()` is the idiomatic form. `Text()` is the capitalized alias.

---

## View

```python
View(*, id="view", ..., style=None)
view(*, id="view", ..., style=None)
```

Classification: generic `View`. A blank visual element - useful for spacers, dividers, or custom backgrounds.

```python
# Spacer
view(height=dp(16))

# Colored bar
view(
    layout=size(fill(), dp(4)),
    background="#FF2563EB",
    radius=dp(2),
)
```

---

## Button Family

All buttons support Groups A, B, C, D, E, F, G, and I.

### `Button`

```python
Button(text, *, id="button", icon=None, ..., style=None)
button(text, *, id="button", icon=None, ..., style=None)
```

Standard button with optional icon.

```python
button("Save", id="save_btn", icon="save_icon")
```

### `RaisedButton`

```python
RaisedButton(text, *, id="raised_btn", **button_kwargs)
raised_button(text, *, id="raised_btn", **button_kwargs)
```

Elevated button with shadow.

### `FlatButton`

```python
FlatButton(text, *, id="flat_btn", **button_kwargs)
flat_button(text, *, id="flat_btn", **button_kwargs)
```

No elevation, minimal chrome.

### `IconButton`

```python
IconButton(icon_text="*", *, id="icon_btn", **button_kwargs)
icon_button(icon_text="*", *, id="icon_btn", **button_kwargs)
```

Icon-only button. `icon_text` is the icon character/name.

### `FloatingActionButton`

```python
FloatingActionButton(text="+", *, id="fab", **button_kwargs)
floating_action_button(text="+", *, id="fab", **button_kwargs)
```

Circular FAB. `text` is the icon character (e.g., `"+"`).

> [!example] Button family at a glance
> ```python
> Row(
>     button("Standard", id="std"),
>     raised_button("Raised", id="raised"),
>     flat_button("Flat", id="flat"),
>     icon_button("★", id="icon"),
>     floating_action_button("+", id="fab"),
> )
> ```

---

## AppBar

```python
AppBar(title, *, id="appbar", inline=False, **text_kwargs)
app_bar(title, *, id="appbar", inline=False, **text_kwargs)
```

Top app bar. `inline=False` (default) uses the system action bar; `inline=True` renders as a widget within the layout.

```python
AppBar("My App", id="appbar")

# Inline AppBar as a widget
Column(
    app_bar("My App", inline=True),
    text("Content below"),
)
```

> [!note] AppBar affects label resolution
> If `app_config(label=...)` is not set, `AppBar(text=...)` can set the app label. See [[01 - App Model]] for the resolution order.

---

## Icon

```python
Icon(name, *, id="icon", **text_kwargs)
icon(name, *, id="icon", **text_kwargs)
```

Renders as a text widget with an icon font. `name` is the icon character/name.

```python
icon("★", id="star", text_size=sp(24), text_color="#FFF59E0B")
```

---

## Image

```python
Image(
    *,
    id="image",
    src=None,
    scale_type=None,
    crop=None,
    center_inside=None,
    adjust_view_bounds=None,
    image_alpha=None,
    image_matrix=None,
    content_description=None,
    accessibility_label=None,
    **view_kwargs,
)
image(...)  # lowercase alias
```

| Attribute | Type | Description |
|---|---|---|
| `src` | `str` \| `int` | Drawable name or int resource ID |
| `scale_type` | `str` | See scale types below |
| `crop` | - | Shorthand for `center_crop` |
| `center_inside` | - | Shorthand for `center_inside` |
| `adjust_view_bounds` | `bool` | Adjust bounds to match image aspect ratio |
| `image_alpha` | `int` | `[0, 255]` - image-specific alpha (separate from widget `opacity`) |
| `image_matrix` | `list` | 9-number affine matrix |

### `scale_type` Values

| Value | Behavior |
|---|---|
| `matrix` | Use `image_matrix` for transformation |
| `fit_xy` | Stretch to fit, ignore aspect ratio |
| `fit_start` | Fit maintaining aspect ratio, align to start |
| `fit_center` | Fit maintaining aspect ratio, center |
| `fit_end` | Fit maintaining aspect ratio, align to end |
| `center` | Center, no scaling |
| `center_crop` | Scale and crop to fill |
| `center_inside` | Scale to fit inside |

```python
image(
    src="hero_image",
    scale_type="center_crop",
    adjust_view_bounds=True,
    content_description="Hero banner",
    layout=size(fill(), dp(200)),
)
```

> [!note] `image_alpha` vs `opacity`
> `image_alpha` is `[0, 255]` and applies only to the image content. `opacity` (Group F) is `[0.0, 1.0]` and applies to the entire widget including background.

---

## Divider

```python
Divider(*, id="divider", color="#FFD1D5DB", thickness=dp(1), **view_kwargs)
divider(*, id="divider", color="#FFD1D5DB", thickness=dp(1), **view_kwargs)
```

A thin horizontal or vertical line. `thickness` controls the stroke width.

```python
divider(color="#FFE2E8F0", thickness=dp(1))
```

---

## See Also

- [[03 - Shared Attributes]] - groups A through I
- [[04 - Structure Components]] - layout containers
- [[06 - Input and Selection]] - TextField, Checkbox, Slider, etc.
- [[13 - Component Attribute Matrix]] - full component-to-group mapping
