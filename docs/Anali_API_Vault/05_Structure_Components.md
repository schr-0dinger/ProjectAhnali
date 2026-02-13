---
tags: [anali, components, structure]
---

# Structure Components

Back to: [[00_Home]]

See shared fields: [[04_Shared_Attributes]].

## Row

Classification: container/layout (horizontal `LinearLayout`).

Constructor:

```python
Row(
    *items,
    id="row",
    layout=None, width=None, height=None,
    padding=None, margin=None,
    gravity=None, align=None, arrangement=None,
    weight_sum=None,
    relative=None, constraints=None,
    background=None, radius=None,
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    elevation=None, pressed_elevation=None,
    text_shadow_color=None, text_shadow_radius=None,
    text_shadow_dx=None, text_shadow_dy=None,
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
row(
    text("Left", id="left", weight=1),
    text("Right", id="right", weight=1),
    id="header_row",
    layout=("match", "wrap"),
    gravity="center_vertical",
    weight_sum=2,
)
```

## Column

Classification: container/layout (vertical `LinearLayout`).

Constructor mirrors `Row` with same attribute surface.

Example:

```python
column(
    text("Title", id="title"),
    text("Subtitle", id="subtitle"),
    id="hero_col",
    padding=(dp(16), dp(12)),
)
```

## Relative

Classification: container/layout (`RelativeLayout`).

Constructor:

```python
Relative(*items, id="relative", ...)
```

Use child `relative=[(...)]` rules to anchor children.

Example:

```python
relative(
    text("Top", id="top", relative=[("align_parent_top", "parent"), ("center_horizontal", "parent")]),
    button("Action", id="action", relative=[("below", "top"), ("center_horizontal", "parent")]),
    id="relative_root",
)
```

## Constraint

Classification: container/layout (`ConstraintLayout`).

Constructor:

```python
Constraint(*items, id="constraint", ...)
```

Use child `constraints={...}` keys from [[04_Shared_Attributes]].

Example:

```python
constraint(
    text("A", id="a", constraints={"top_to_top": "parent", "start_to_start": "parent"}),
    text("B", id="b", constraints={"top_to_bottom": "a", "start_to_start": "parent"}),
    id="constraint_root",
)
```

## Container

Classification: semantic container (currently column-based runtime).

Constructor:

```python
Container(*items, id="container", **kwargs)
```

Inherits column-like container attrs.

## Card

Classification: semantic surface container (currently column-based runtime).

Constructor:

```python
Card(*items, id="card", **kwargs)
```

Default widget style includes white background + radius + padding if not overridden.

## ButtonBar

Classification: button row helper (row wrapper).

Constructor:

```python
ButtonBar(*items, id="button_bar", **kwargs)
```

## ScrollView

Classification: single-child vertical scroll container.

Constructor:

```python
ScrollView(*items, id="scroll_view", **kwargs)
```

Rule:
- exactly one direct child is required.

## HorizontalScrollView

Classification: single-child horizontal scroll container.

Constructor:

```python
HorizontalScrollView(*items, id="horizontal_scroll_view", **kwargs)
```

Rule:
- exactly one direct child is required.

## Screen

Classification: navigation container root.

Constructor:

```python
Screen(name, *items, id=None, transition=None)
```

Transition values:
- `fade`
- `slide_left`
- `slide_right`
- `slide_up`
- `slide_down`

Rules:
- if any `Screen` is used, all top-level `ui(...)` entries must be `Screen`.
- screen names must be unique.

Example:

```python
ui(
    Screen("Home", text("Home", id="home_title")),
    Screen("Settings", text("Settings", id="settings_title"), transition="fade"),
)
```
