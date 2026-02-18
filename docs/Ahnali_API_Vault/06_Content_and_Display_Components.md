---
tags: [ahnali, components, content]
---

# Content and Display Components

Back to: [[00_Home]]

See shared attrs: [[04_Shared_Attributes]].

## Text

Classification: text display (`TextView`).

```python
Text(text, *, id="label", ..., style=None)
text(text, *, id="label", ..., style=None)
```

Supports full text typography, tint, accessibility, visual effects, transforms, and inline event attrs.

## View

Classification: generic visual element (`View`).

```python
View(*, id="view", ..., style=None)
view(*, id="view", ..., style=None)
```

## Button Family

- `Button(text, *, id="button", icon=None, ..., style=None)`
- `RaisedButton(text, *, id="raised_btn", **button_kwargs)`
- `FlatButton(text, *, id="flat_btn", **button_kwargs)`
- `IconButton(icon_text="*", *, id="icon_btn", **button_kwargs)`
- `FloatingActionButton(text="+", *, id="fab", **button_kwargs)`

## AppBar

```python
AppBar(title, *, id="appbar", inline=False, **text_kwargs)
app_bar(title, *, id="appbar", inline=False, **text_kwargs)
```

## Icon

```python
Icon(name, *, id="icon", **text_kwargs)
icon(name, *, id="icon", **text_kwargs)
```

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
```

Notes:
- `src`: drawable name string or int resource id
- `scale_type`: `matrix`, `fit_xy`, `fit_start`, `fit_center`, `fit_end`, `center`, `center_crop`, `center_inside`
- `image_alpha`: integer `[0,255]`

## Divider

```python
Divider(*, id="divider", color="#FFD1D5DB", thickness=dp(1), **view_kwargs)
```

## Other Display-Like Surfaces

- `Card(...)`
- `Container(...)`
- `ProgressBar(...)`

These are documented in their main sections but support display-oriented attrs (background, elevation, opacity, border, transforms).
