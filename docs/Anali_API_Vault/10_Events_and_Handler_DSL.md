---
tags: [anali, events, handlers]
---

# Events and Handler DSL

Back to: [[00_Home]]

## Event Decorators

- `on_click(button_id, stmts=None)`
- `on_click_map(mapping)`
- `on_change(view_id, stmts=None)`
- `on_text_change(view_id, stmts=None)`
- `on_item_selected(view_id, stmts=None)`
- `on_menu_item_selected(view_id, stmts=None)`
- `on_focus_change(view_id, stmts=None)`

`stmts` can be:
- omitted + decorator function body (AST-parsed)
- callable
- prebuilt stmt list

## Target Type Constraints

Compile-time checks enforce target widget kinds:

- `on_click`: clickable kinds only
- `on_change`: checkbox/switch/radio/slider/radio_group
- `on_text_change`: text_field
- `on_item_selected`: dropdown
- `on_menu_item_selected`: popup_button
- `on_focus_change`: view-level focus target

Unknown ids fail at compile time.

## Supported Handler Statements (AST)

Current parser supports:
- assignment: `x = ...`
- augmented assignment: `x += 1`, `x -= 1`, etc.
- view text set: `label.text = ...`
- `if` / `else`
- `while`
- `toast(...)`
- `snackbar(...)`
- `simple_dialog(...)`
- `log(tag, message)`
- `Navigate(...)` / `navigate(...)`
- `Back()` / `back()`
- `Replace(...)` / `replace(...)`
- animation calls (`animate`, helpers, `sequence`, `parallel`)
- `request_permission(...)` / `request_permissions(...)`
- `exit_app()`

Unsupported statements/expressions fail at compile time.

## Expression Support in Handlers

Supported expression forms include:
- constants
- symbols
- binary math (`+`, `-`, `*`, `/`, `%`)
- comparisons (`==`, `!=`, `>`, `<`, etc. single compare)
- boolean ops (`and`, `or`)
- unary (`not`, unary `-` for integer constants)
- f-strings (limited AST conversion)

## Example

```python
from dsl.app import on_click, on_change, on_text_change, toast, navigate

@on_click("save")
def save_handler():
    counter = counter + 1
    title.text = f"Saved {counter} times"
    toast("Saved", 0)

@on_change("enabled")
def enabled_handler():
    title.text = "Enabled changed"

@on_text_change("query")
def query_handler():
    if counter > 10:
        navigate("Summary")
```

## `on_click_map(...)`

Bulk mapping form:

```python
specs = on_click_map({
    "inc": lambda: None,
    "dec": lambda: None,
})
```

Returns a list of event specs.

## Notes

- Handlers are named/static by design.
- Runtime dynamic callback registration is intentionally not part of this model.
- Compile-time id validation is mandatory.
