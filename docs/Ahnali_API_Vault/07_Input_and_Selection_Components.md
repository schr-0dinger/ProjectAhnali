---
tags: [ahnali, components, input]
---

# Input and Selection Components

Back to: [[00_Home]]

See shared attrs: [[04_Shared_Attributes]].

## TextField

Classification: text input (`EditText`).

Constructor:

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

### `input_type` accepted values

- `text`
- `multiline`
- `email`
- `uri`
- `password`
- `text_password`
- `visible_password`
- `number`
- `number_decimal`
- `number_signed`
- `number_decimal_signed`
- `number_password`
- `phone`
- `datetime`
- `date`
- `time`
- integer bitmask (advanced)

### `ime_options` accepted tokens

Pipe/comma-separated string (or int), including:
- `unspecified`, `none`, `go`, `search`, `send`, `next`, `done`, `previous`
- `no_fullscreen`, `no_extract_ui`, `no_enter_action`

Token prefixes are accepted and normalized:
- `ime_action_`, `action_`, `ime_flag_`, `flag_`

Examples:

```python
text_field(id="email", input_type="email", ime_options="done|no_fullscreen")
text_field(id="amount", input_type="number_decimal", numeric_only=True)
text_field(id="pwd", password=True, max_length=64, single_line=True)
```

### `auto_capitalize`

Accepted values:
- bool (`True` => sentences, `False` => none)
- strings: `none`, `characters`, `words`, `sentences`

Rule:
- valid only for text input class.

## Checkbox / Radio / Switch

Constructors:

```python
Checkbox(text="", *, id="checkbox", checked=False, **text_kwargs)
Radio(text="", *, id="radio", checked=False, **text_kwargs)
Switch(text="", *, id="switch", checked=False, **text_kwargs)
```

They support text attrs plus selector/tint attrs (`button_tint`, `thumb_tint`, `track_tint`, etc.).

## Slider

Constructor:

```python
Slider(*, id="slider", value=0, min=0, max=100, **button_kwargs)
```

Supports:
- `thumb_tint`
- `progress_tint`
- `track_tint`
- plus shared visuals.

## RadioGroup

Constructor:

```python
RadioGroup(*items, id="radio_group", orientation="vertical", **column_kwargs)
```

Specific field:
- `orientation`: normalized to lowercase string.

## DropdownButton

Constructor:

```python
DropdownButton(*, id="dropdown", items=None, **button_kwargs)
```

Specific field:
- `items`: item list (stringified in adapter path)

Current note:
- typography surface coverage for dropdown text is still pending in masterplan.

## PopupMenuButton

Constructor:

```python
PopupMenuButton(text="Menu", *, id="popup", items=None, **button_kwargs)
```

Specific field:
- `items`: popup entries

Current note:
- popup menu item text surface coverage is still pending in masterplan.

## ProgressBar

Constructor:

```python
ProgressBar(*, id="progress", value=0, min=0, max=100, indeterminate=False, **view_kwargs)
```

Supports:
- progress tint and indeterminate tint lowering paths
- shared visual attrs where compatible

## ListView (Static v1)

Constructor:

```python
ListView(*, id="list_view", items=None, item_layout="simple_list_item_1", **view_kwargs)
```

### Data rules

- `items` must be `list` or `tuple`
- each item must be static primitive: `str`, `int`, `float`, `bool`
- values are normalized to strings in generated adapter

### `item_layout` rules

- accepted symbolic name: `simple_list_item_1`
- int resource id accepted by constructor, but deterministic lowering path currently only supports `0x1090003` (`simple_list_item_1`)

### Runtime behavior note

- this is static adapter v1
- compile-time dataset only
- no runtime diffing/add/remove API in this phase
