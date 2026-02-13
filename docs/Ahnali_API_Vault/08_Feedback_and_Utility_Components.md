---
tags: [ahnali, feedback, utility]
---

# Feedback and Utility Components

Back to: [[00_Home]]

## Toast

API:

```python
toast(message, duration=0)
Toast(message, duration=0)
```

Usage:
- usually inside handlers
- `duration` is integer duration flag passed to runtime toast path

Example:

```python
@on_click("save")
def save_handler():
    toast("Saved", 0)
```

## Snackbar

API:

```python
snackbar(message, duration=0)
Snackbar(message, duration=0)
```

Usage:
- handler feedback surface
- in core/native path this is lowered through current runtime behavior (project previously tested fallback paths)

## SimpleDialog

API:

```python
simple_dialog(title, message)
SimpleDialog(title, message)
```

Usage:
- handler feedback dialog

Example:

```python
@on_click("delete")
def delete_handler():
    simple_dialog("Confirm", "Delete item?")
```

## Exit App

API:

```python
exit_app()
```

Usage:
- handler statement; emits explicit app-exit action path

## Permissions Requests

APIs:

```python
request_permission(permission, request_code=0)
request_permissions(*permissions, request_code=0)
```

Accepted forms:
- varargs: `request_permissions("android.permission.CAMERA", "android.permission.RECORD_AUDIO")`
- single list/tuple/set
- optional request code

Example:

```python
@on_click("ask_cam")
def ask_cam_handler():
    request_permission("android.permission.CAMERA", request_code=7)
```

See handler constraints in [[10_Events_and_Handler_DSL]].
