---
tags: [ahnali, components, structure]
---

# Structure Components

Back to: [[00_Home]]

See shared fields: [[04_Shared_Attributes]].

## Core Layout Containers

- `Row(*items, id="row", ...)`
- `Column(*items, id="column", ...)`
- `Relative(*items, id="relative", ...)`
- `Constraint(*items, id="constraint", ...)`
- `Frame(*items, id="frame", ...)`
- `CoordinatorLayout(*items, id="coordinator_layout", ...)`

`Row` and `Column` support `align`, `arrangement`, `weight_sum`.

## Semantic Containers

- `Container(*items, id="container", **kwargs)`
- `Card(*items, id="card", **kwargs)`
- `ButtonBar(*items, id="button_bar", **kwargs)`

## Scroll Containers

- `ScrollView(*items, id="scroll_view", **kwargs)`
- `HorizontalScrollView(*items, id="horizontal_scroll_view", **kwargs)`
- `NestedScrollView(*items, id="nested_scroll_view", **kwargs)`

Rules:
- each requires exactly one direct child

## Paging and Navigation Surfaces

- `ViewPager(*items, id="view_pager", initial_page=0, **kwargs)`
- `TabLayout(id="tab_layout", tabs=[...], selected_index=0, **kwargs)`
- `BottomNavigationView(id="bottom_navigation_view", items=[...], selected_index=0, **kwargs)`
- `NavigationBar(id="navigation_bar", items=[...], selected_index=0, **kwargs)`
- `NavigationRail(id="navigation_rail", items=[...], selected_index=0, **kwargs)`

Rules:
- `ViewPager` needs at least one page; `initial_page` must be int in range
- tab/navigation `items`/`tabs` must be non-empty static primitive labels
- `selected_index` must be int in range

## Drawer and Fragment Host

- `DrawerLayout(*items, id="drawer_layout", **kwargs)`
- `FragmentContainer(*items, id="fragment_container", **kwargs)`

Rules:
- `DrawerLayout` requires exactly two direct children: `(content, drawer)`
- `FragmentContainer` accepts no direct children in deterministic v1

## Static Data Containers

- `ListView(...)`, `GridView(...)`, `RecyclerView(...)` are documented in [[07_Input_and_Selection_Components]] but often used as structural roots in screens.

## Screen

```python
Screen(name, *items, id=None, transition=None)
```

Supported transitions:
- `fade`
- `slide_left`
- `slide_right`
- `slide_up`
- `slide_down`

Rules:
- if any `Screen` is used, all top-level `ui(...)` items must be screens
- screen names must be unique

Example:

```python
ui(
    Screen("Home", text("Home", id="home_title")),
    Screen("Settings", text("Settings", id="settings_title"), transition="fade"),
)
```
