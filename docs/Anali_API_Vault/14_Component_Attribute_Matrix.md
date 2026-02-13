---
tags: [anali, api, matrix, components]
---

# Component Attribute Matrix

Back to: [[00_Home]]

Use with [[04_Shared_Attributes]].

## Shared Group Legend

- `A`: Layout and positioning
- `B`: Text/typography
- `C`: Tint/state color
- `D`: Accessibility
- `E`: Elevation/shadow
- `F`: Visual effects and transforms
- `G`: Background surface

## Matrix

| Component | Category | Shared Groups | Specific Attributes |
| --- | --- | --- | --- |
| `Text` / `text(...)` | Content | A, B, C, D, E, F, G | `text` |
| `View` / `view(...)` | Generic visual | A, C, D, E, F, G | none |
| `Button` / `button(...)` | Action | A, B, C, D, E, F, G | `text`, `icon` |
| `RaisedButton` / `raised_button(...)` | Action variant | A, B, C, D, E, F, G | `text` |
| `FlatButton` / `flat_button(...)` | Action variant | A, B, C, D, E, F, G | `text` |
| `IconButton` / `icon_button(...)` | Action variant | A, B, C, D, E, F, G | `text` |
| `FloatingActionButton` / `floating_action_button(...)` | Action variant | A, B, C, D, E, F, G | `text`, internal `floating=True` |
| `Icon` / `icon(...)` | Content icon text | A, B, C, D, E, F, G | `name` |
| `Image` / `image(...)` | Content image | A, C, D, E, F, G | `src` |
| `Divider` / `divider(...)` | Content separator | A, C, D, E, F, G | `color`, `thickness` |
| `Row` / `row(...)` | Layout container | A, D, E, F, G | `items`, `align`, `arrangement`, `weight_sum` |
| `Column` / `column(...)` | Layout container | A, D, E, F, G | `items`, `align`, `arrangement`, `weight_sum` |
| `Relative` / `relative(...)` | Layout container | A, D, E, F, G | `items` |
| `Constraint` / `constraint(...)` | Layout container | A, D, E, F, G | `items` |
| `Container` / `container(...)` | Semantic container | A, D, E, F, G | `items` |
| `Card` / `card(...)` | Semantic surface | A, D, E, F, G | `items` |
| `ButtonBar` / `button_bar(...)` | Layout helper | A, D, E, F, G | `items` |
| `ScrollView` / `scroll_view(...)` | Scroll container | A, C, D, E, F, G | `items` (exactly one) |
| `HorizontalScrollView` / `horizontal_scroll_view(...)` | Scroll container | A, C, D, E, F, G | `items` (exactly one) |
| `TextField` / `text_field(...)` | Input | A, B, C, D, E, F, G | `text`, `hint`, `input_type`, `ime_options`, `max_length`, `single_line`, `password`, `auto_capitalize`, `numeric_only` |
| `Checkbox` / `checkbox(...)` | Input/select | A, B, C, D, E, F, G | `text`, `checked` |
| `Radio` / `radio(...)` | Input/select | A, B, C, D, E, F, G | `text`, `checked` |
| `Switch` / `switch(...)` | Input/select | A, B, C, D, E, F, G | `text`, `checked` |
| `Slider` / `slider(...)` | Input/select | A, B, C, D, E, F, G | `value`, `min`, `max` |
| `RadioGroup` / `radio_group(...)` | Input/select container | A, D, E, F, G | `items`, `orientation` |
| `DropdownButton` / `dropdown_button(...)` | Selection | A, B, C, D, E, F, G | `items` |
| `PopupMenuButton` / `popup_menu_button(...)` | Selection/action | A, B, C, D, E, F, G | `text`, `items` |
| `ProgressBar` / `progress_bar(...)` | Feedback | A, C, D, E, F, G | `value`, `min`, `max`, `indeterminate` |
| `ListView` / `list_view(...)` | Data list (static v1) | A, C, D, E, F, G | `items`, `item_layout` |
| `Screen` / `screen(...)` | Navigation root | fixed screen container fields | `name`, `id` (optional), `transition`, `items` |

## Per-Component Signature Snippets

## Text

```python
text(text, id="label", ..., style=None)
```

## Button

```python
button(text, id="button", icon=None, ..., style=None)
```

## View

```python
view(id="view", ..., style=None)
```

## Row / Column

```python
row(*items, id="row", align=None, arrangement=None, weight_sum=None, ..., style=None)
column(*items, id="column", align=None, arrangement=None, weight_sum=None, ..., style=None)
```

## Relative / Constraint

```python
relative(*items, id="relative", ..., style=None)
constraint(*items, id="constraint", ..., style=None)
```

## Scroll Containers

```python
scroll_view(*items, id="scroll_view", **kwargs)
horizontal_scroll_view(*items, id="horizontal_scroll_view", **kwargs)
```

## Input Set

```python
text_field(text="", id="input", hint=None, input_type=None, ime_options=None,
           max_length=None, single_line=None, password=False,
           auto_capitalize=None, numeric_only=False, **kwargs)

checkbox(text="", id="checkbox", checked=False, **kwargs)
radio(text="", id="radio", checked=False, **kwargs)
switch(text="", id="switch", checked=False, **kwargs)
slider(id="slider", value=0, min=0, max=100, **kwargs)
radio_group(*items, id="radio_group", orientation="vertical", **kwargs)
```

## Selection/Popup

```python
dropdown_button(id="dropdown", items=None, **kwargs)
popup_menu_button(text="Menu", id="popup", items=None, **kwargs)
```

## Feedback/Data

```python
progress_bar(id="progress", value=0, min=0, max=100, indeterminate=False, **kwargs)
list_view(id="list_view", items=None, item_layout="simple_list_item_1", **kwargs)
```

## AppBar / Variants

```python
app_bar(title, id="appbar", **kwargs)
floating_action_button(text="+", id="fab", **kwargs)
raised_button(text, id="raised_btn", **kwargs)
flat_button(text, id="flat_btn", **kwargs)
icon_button(icon_text="*", id="icon_btn", **kwargs)
```

## Utility Notes

- `simple_dialog(title, message)`, `toast(message, duration=0)`, `snackbar(message, duration=0)` are handler statements.
- `exit_app()` is a handler statement.
- `style(...)`, `theme(...)`, `color_state(...)`, `gradient(...)`, `presets(...)`, `state(...)` are configuration/value constructors.
