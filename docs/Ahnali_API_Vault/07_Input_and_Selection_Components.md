---
tags: [ahnali, components, input]
---

# Input and Selection Components

Back to: [[00_Home]]

See shared attrs: [[04_Shared_Attributes]].

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
```

`input_type` values:
- `text`, `multiline`, `email`, `uri`
- `password`, `text_password`, `visible_password`
- `number`, `number_decimal`, `number_signed`, `number_decimal_signed`, `number_password`
- `phone`, `datetime`, `date`, `time`
- or integer bitmask

`ime_options` tokens (combinable with `|`/`,`):
- `unspecified`, `none`, `go`, `search`, `send`, `next`, `done`, `previous`
- `no_fullscreen`, `no_extract_ui`, `no_enter_action`

`auto_capitalize`:
- bool or one of `none`, `characters`, `words`, `sentences`
- valid only for text input class

## Checkbox / Radio / Switch

```python
Checkbox(text="", *, id="checkbox", checked=False, **text_kwargs)
Radio(text="", *, id="radio", checked=False, **text_kwargs)
Switch(text="", *, id="switch", checked=False, **text_kwargs)
```

## Slider

```python
Slider(*, id="slider", value=0, min=0, max=100, **button_kwargs)
```

## RadioGroup

```python
RadioGroup(*items, id="radio_group", orientation="vertical", **column_kwargs)
```

`orientation` is normalized to lowercase string.

## Dropdown and Popup

```python
DropdownButton(*, id="dropdown", items=None, **button_kwargs)
PopupMenuButton(text="Menu", *, id="popup", items=None, **button_kwargs)
```

Notes:
- `items` are static values (stringified in lowering)
- popup auto-wires click behavior unless explicit `on_click` is bound
- explicit `on_click` and `on_menu_item_selected` on same popup id are rejected

## Progress and Static Data Views

```python
ProgressBar(*, id="progress", value=0, min=0, max=100, indeterminate=False, **view_kwargs)

ListView(*, id="list_view", items=None, item_layout="simple_list_item_1", **view_kwargs)
GridView(*, id="grid_view", items=None, item_layout="simple_list_item_1", num_columns=2, **view_kwargs)
RecyclerView(*, id="recycler_view", items=None, **view_kwargs)
```

Data rules (`ListView`/`GridView`/`RecyclerView`):
- `items` must be list/tuple
- each item must be static primitive: `str`, `int`, `float`, `bool`

`item_layout` rules:
- symbolic `simple_list_item_1` accepted
- int resource id accepted at constructor level
- deterministic lowering currently supports `0x1090003` (`simple_list_item_1`) path

`GridView` additional rule:
- `num_columns` must be integer `>= 1`
