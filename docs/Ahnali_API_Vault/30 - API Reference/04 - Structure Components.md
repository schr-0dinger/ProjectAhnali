---
tags: [ahnali, api-reference, components, structure, layout, containers]
---

# 04 - Structure Components

> [!abstract] What this covers
> Layout containers, semantic wrappers, scroll surfaces, paging/navigation surfaces, and `Screen` with transitions. These are the bones of your UI tree.

Related: [[03 - Shared Attributes]] · [[10 - Navigation and Screens]] · [[13 - Component Attribute Matrix]]

---

## Core Layout Containers

### `Row(*items, id="row", ...)`

Horizontal linear layout. Children are laid out left-to-right.

```python
Row(
    text("Left"),
    text("Right"),
    align="center",
    weight_sum=2,
)
```

Supports: `align`, `arrangement`, `weight_sum`. Child `weight` distributes remaining space.

### `Column(*items, id="column", ...)`

Vertical linear layout. Children are laid out top-to-bottom.

```python
Column(
    text("Title", id="title"),
    text("Subtitle", id="subtitle"),
    padding=dp(16),
)
```

Supports: `align`, `arrangement`, `weight_sum`.

### `Relative(*items, id="relative", ...)`

RelativeLayout - children position themselves relative to siblings or parent using `relative=[(verb, target), ...]`.

```python
Relative(
    text("Title", id="title"),
    text("Subtitle", id="subtitle", relative=[("below", "title")]),
)
```

> [!tip] Prefer Constraint over Relative
> `Constraint` is more powerful and performs better. Use `Relative` only for simple sibling-relative positioning.

### `Constraint(*items, id="constraint", ...)`

ConstraintLayout - children use `constraints={...}` dicts for flexible, performant layouts.

```python
Constraint(
    text("Title", id="title", constraints={
        "top_to_top": "parent",
        "left_to_left": "parent",
        "right_to_right": "parent",
    }),
    text("Body", id="body", constraints={
        "top_to_bottom": "title",
        "left_to_left": "parent",
        "right_to_right": "parent",
    }),
)
```

### `Frame(*items, id="frame", ...)`

FrameLayout - children stack on top of each other. Last child draws on top.

```python
Frame(
    image(src="background", layout=fill()),
    text("Overlay text", gravity="center"),
)
```

### `CoordinatorLayout(*items, id="coordinator_layout", ...)`

CoordinatorLayout - supports coordinated motion between child views (e.g., collapsing app bars).

---

## Semantic Containers

### `Container(*items, id="container", **kwargs)`

Generic semantic container. Use when `Row`/`Column`/`Frame` don't fit.

### `Card(*items, id="card", **kwargs)`

Material-style card surface. Typically has elevation, rounded corners, and a background.

### `ButtonBar(*items, id="button_bar", **kwargs)`

Horizontal row optimized for button placement.

---

## Scroll Containers

### `ScrollView(*items, ...)`

Vertical scroll container.

### `HorizontalScrollView(*items, ...)`

Horizontal scroll container.

### `NestedScrollView(*items, ...)`

Scroll container that supports nested scrolling (e.g., inside a CoordinatorLayout).

> [!warning] Single-child rule
> Each scroll container requires **exactly one direct child**. Wrap multiple children in a `Column` or `Row` first.

```python
# ✅ Correct - single Column child
ScrollView(
    Column(
        text("Line 1"),
        text("Line 2"),
        text("Line 3"),
    ),
)

# ❌ Wrong - multiple direct children
ScrollView(
    text("Line 1"),
    text("Line 2"),  # rejected!
)
```

---

## Paging and Navigation Surfaces

### `ViewPager(*items, id="view_pager", initial_page=0, **kwargs)`

Swipeable page container. Each child is a page.

> [!important] Rules
> - Needs at least one page
> - `initial_page` must be an int in range `[0, len(items))`

### `TabLayout(id="tab_layout", tabs=[...], selected_index=0, **kwargs)`

Tab bar. `tabs` must be a non-empty list of static primitive labels.

### `BottomNavigationView(id="bottom_navigation_view", items=[...], selected_index=0, **kwargs)`

Bottom navigation bar with icon+label items.

### `NavigationBar(id="navigation_bar", items=[...], selected_index=0, **kwargs)`

Material 3 navigation bar.

### `NavigationRail(id="navigation_rail", items=[...], selected_index=0, **kwargs)`

Material 3 navigation rail (vertical, for tablets/foldables).

> [!note] Navigation items must be static primitives
> `items`/`tabs` must be non-empty lists of strings or other static primitives. Dynamic lists are not supported.

---

## Drawer and Fragment Host

### `DrawerLayout(*items, id="drawer_layout", **kwargs)`

> [!warning] Two-child rule
> Requires **exactly two direct children**: `(content, drawer)`.

```python
DrawerLayout(
    Column(               # content (first child)
        text("Main content"),
    ),
    Column(               # drawer (second child)
        text("Drawer item 1"),
        text("Drawer item 2"),
    ),
)
```

### `FragmentContainer(*items, id="fragment_container", **kwargs)`

> [!important] No children in v1
> `FragmentContainer` accepts **no direct children** in the deterministic v1 pipeline. It acts as a host for runtime fragment transactions.

---

## `Screen` with Transitions

```python
Screen(name, *items, id=None, transition=None)
```

The root of a navigable screen. `name` must be unique across all screens.

### Supported Transitions

| Value | Effect |
|---|---|
| `fade` | Crossfade between screens |
| `slide_left` | New screen slides in from right |
| `slide_right` | New screen slides in from left |
| `slide_up` | New screen slides in from bottom |
| `slide_down` | New screen slides in from top |

### Screen Rules

1. If **any** `Screen` is used, **all** top-level `ui(...)` items must be `Screen(...)`
2. Screen names must be unique
3. Widget IDs must not collide across screens

```python
ui(
    Screen("Home",
        Column(
            text("Welcome", id="home_title"),
            button("Go to Settings", id="go_settings"),
        ),
    ),
    Screen("Settings",
        Column(
            text("Settings", id="settings_title"),
            button("Back", id="go_back"),
        ),
        transition="slide_left",
    ),
)
```

See [[10 - Navigation and Screens]] for navigation stack semantics and operations.

---

## See Also

- [[03 - Shared Attributes]] - groups A through I
- [[10 - Navigation and Screens]] - Navigate, Back, Replace, PopToRoot, ClearStack
- [[13 - Component Attribute Matrix]] - full component-to-group mapping
