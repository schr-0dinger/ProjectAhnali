---
tags: [ahnali, api-reference, feedback, utility, toast, snackbar, dialog]
---

# 07 — Feedback and Utility

> [!abstract] What this covers
> Runtime helper APIs for quick feedback: `toast`, `snackbar`, `simple_dialog`, and `exit_app`. These are typically called inside event handlers.

Related: [[09 - Events and Handlers]] · [[20 - Core Concepts/04 - Capabilities System]]

> [!note] Capability handlers are documented elsewhere
> The full capability handler set (HTTP, WebView, notifications, storage, permissions, etc.) lives in the Capabilities section. This page covers only the core feedback primitives.

---

## UI Feedback Primitives

### `toast(message, duration=0)`

Shows a short-lived toast message.

```python
toast("Saved successfully")
toast("Item deleted", duration=1)  # long duration
```

Capitalized alias: `Toast(...)`

### `snackbar(message, duration=0)`

Shows a snackbar at the bottom of the screen.

```python
snackbar("Network unavailable")
```

Capitalized alias: `Snackbar(...)`

### `simple_dialog(title, message)`

Shows a basic alert dialog with an OK button.

```python
simple_dialog("Confirm", "Are you sure you want to delete this item?")
```

Capitalized alias: `SimpleDialog(...)`

### `exit_app()`

Terminates the app.

```python
exit_app()
```

---

## Usage in Handlers

These primitives are designed to be called inside event handlers:

```python
@on_click("save_btn")
def save():
    toast("Saved!")

@on_click("delete_btn")
def delete():
    simple_dialog("Delete", "This cannot be undone.")

@on_click("quit_btn")
def quit():
    exit_app()
```

Or as inline attributes:

```python
button("Save", id="save_btn", on_click=toast("Saved!"))
button("Quit", id="quit_btn", on_click=exit_app())
```

---

## See Also

- [[09 - Events and Handlers]] — handler DSL, supported statements
- [[08 - Feedback and Utility Components]] — full capability handler reference (HTTP, WebView, storage, notifications)
