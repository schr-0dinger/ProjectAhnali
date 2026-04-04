---
tags: [ahnali, api-reference, components, input, selection, forms]
---

# 06 - Input and Selection

> [!abstract] What this covers
> All interactive input widgets: `TextField`, `Checkbox`, `Radio`, `Switch`, `Slider`, `RadioGroup`, `DropdownButton`, `PopupMenuButton`, `ProgressBar`, `ListView`, `GridView`, and `RecyclerView`.

Related: [[03 - Shared Attributes]] · [[09 - Events and Handlers]] · [[13 - Component Attribute Matrix]]

---

## TextField

```python
TextField(
    text="",
    *,
    id="input",
    hint=None,
    input_type=None,
    ime_options=None,
    max_length=None,
    single_line=None,
    password=False,
    auto_capitalize=None,
    numeric_only=False,
    **text_kwargs,
)
text_field(...)  # lowercase alias
```

### `input_type` Values

| Category | Values |
|---|---|
| **Text** | `text`, `multiline`, `email`, `uri` |
| **Password** | `password`, `text_password`, `visible_password` |
| **Number** | `number`, `number_decimal`, `number_signed`, `number_decimal_signed`, `number_password` |
| **Other** | `phone`, `datetime`, `date`, `time` |
| **Raw** | Integer bitmask (advanced) |

### `ime_options` Tokens

Combinable with `|` or `,`:

`unspecified`, `none`, `go`, `search`, `send`, `next`, `done`, `previous`, `no_fullscreen`, `no_extract_ui`, `no_enter_action`

### `auto_capitalize`

| Value | Behavior |
|---|---|
| `True` / `False` | Enable/disable |
| `"none"` | No auto-capitalization |
| `"characters"` | Capitalize every character |
| `"words"` | Capitalize first letter of each word |
| `"sentences"` | Capitalize first letter of each sentence |

> [!warning] `auto_capitalize` is text-only
> Valid only for text input class. Using it with `number` or `phone` input types is rejected.

```python
text_field(
    id="email_input",
    hint="Enter your email",
    input_type="email",
    ime_options="next",
    max_length=100,
)
```

---

## Checkbox / Radio / Switch

```python
Checkbox(text="", *, id="checkbox", checked=False, **text_kwargs)
checkbox(text="", *, id="checkbox", checked=False, **text_kwargs)

Radio(text="", *, id="radio", checked=False, **text_kwargs)
radio(text="", *, id="radio", checked=False, **text_kwargs)

Switch(text="", *, id="switch", checked=False, **text_kwargs)
switch(text="", *, id="switch", checked=False, **text_kwargs)
```

All three support `on_change` inline events and the explicit `on_change` decorator.

```python
checkbox("Remember me", id="remember", checked=True)
switch("Dark mode", id="dark_mode", on_change=log("toggled"))
```

---

## Slider

```python
Slider(*, id="slider", value=0, min=0, max=100, **button_kwargs)
slider(*, id="slider", value=0, min=0, max=100, **button_kwargs)
```

Supports `on_change` and `on_slider_change` events.

```python
slider(id="volume", value=50, min=0, max=100)
```

---

## RadioGroup

```python
RadioGroup(*items, id="radio_group", orientation="vertical", **column_kwargs)
radio_group(*items, id="radio_group", orientation="vertical", **column_kwargs)
```

Container for `Radio` widgets. `orientation` is normalized to lowercase string (`"vertical"` or `"horizontal"`).

```python
radio_group(
    radio("Option A", id="opt_a"),
    radio("Option B", id="opt_b"),
    radio("Option C", id="opt_c"),
    orientation="vertical",
)
```

---

## DropdownButton

```python
DropdownButton(*, id="dropdown", items=None, **button_kwargs)
dropdown_button(*, id="dropdown", items=None, **button_kwargs)
```

Button that shows a dropdown list on click. `items` must be a static list of primitives.

```python
dropdown_button(
    id="color_picker",
    items=["Red", "Green", "Blue"],
    on_item_selected=log("selected"),
)
```

> [!note] Dropdown typography surface is partial
> Text-typography customization on dropdown items is still incomplete. The button itself supports full typography (Group B).

---

## PopupMenuButton

```python
PopupMenuButton(text="Menu", *, id="popup", items=None, **button_kwargs)
popup_menu_button(text="Menu", *, id="popup", items=None, **button_kwargs)
```

> [!warning] Auto-wiring vs explicit handler conflict
> The popup auto-wires click behavior unless an explicit `on_click` is bound. If you bind both `on_click` and `on_menu_item_selected` to the same popup ID, the compiler rejects it.

```python
popup_menu_button(
    text="Options",
    id="options_menu",
    items=["Edit", "Delete", "Share"],
    on_menu_item_selected=log("menu item"),
)
```

> [!note] Popup menu item typography surface is partial
> Similar to DropdownButton, item-level typography customization is incomplete.

---

## ProgressBar

```python
ProgressBar(*, id="progress", value=0, min=0, max=100, indeterminate=False, **view_kwargs)
progress_bar(*, id="progress", value=0, min=0, max=100, indeterminate=False, **view_kwargs)
```

| Attribute | Description |
|---|---|
| `value` | Current progress |
| `min` | Minimum value |
| `max` | Maximum value |
| `indeterminate` | Spinning/unknown progress mode |

```python
# Determinate
progress_bar(id="download_progress", value=45, max=100)

# Indeterminate (spinner)
progress_bar(id="loading", indeterminate=True)
```

---

## ListView / GridView / RecyclerView

```python
ListView(*, id="list_view", items=None, item_layout="simple_list_item_1", **view_kwargs)
list_view(*, id="list_view", items=None, item_layout="simple_list_item_1", **view_kwargs)

GridView(*, id="grid_view", items=None, item_layout="simple_list_item_1", num_columns=2, **view_kwargs)
grid_view(*, id="grid_view", items=None, item_layout="simple_list_item_1", num_columns=2, **view_kwargs)

RecyclerView(*, id="recycler_view", items=None, **view_kwargs)
recycler_view(*, id="recycler_view", items=None, **view_kwargs)
```

### Data Rules

> [!important] Items must be static primitives
> - `items` must be a `list` or `tuple`
> - Each item must be a static primitive: `str`, `int`, `float`, `bool`
> - Dynamic or computed lists are not supported

### `item_layout` Rules

| Value | Description |
|---|---|
| `simple_list_item_1` | Symbolic name (accepted) |
| `0x1090003` | Int resource ID for `simple_list_item_1` |

> [!note] Deterministic lowering currently supports only the `simple_list_item_1` path
> Custom item layouts are not yet supported in the deterministic pipeline.

### `GridView` Additional Rule

- `num_columns` must be an integer `>= 1`

```python
list_view(
    id="items",
    items=["Apple", "Banana", "Cherry", "Date"],
    item_layout="simple_list_item_1",
)

grid_view(
    id="grid",
    items=["A", "B", "C", "D", "E", "F"],
    num_columns=3,
)
```

---

## See Also

- [[03 - Shared Attributes]] - groups A through I
- [[09 - Events and Handlers]] - on_change, on_item_selected, on_menu_item_selected
- [[12 - Validation and Diagnostics]] - input validation, data validation
- [[13 - Component Attribute Matrix]] - full component-to-group mapping
