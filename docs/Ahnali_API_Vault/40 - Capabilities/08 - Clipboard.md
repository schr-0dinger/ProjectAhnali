---
tags: [ahnali, capabilities, clipboard]
---

# Clipboard

> [!abstract] Copy and paste
> Set text on the system clipboard and read it back with a fallback.

## Setting clipboard

```python
clipboard_set("Copied text!")
set_clipboard("Copied text!")  # alias
```

Maps to `ClipboardHelper.setText(Activity, String) → int`.

## Getting clipboard

```python
text = clipboard_get(fallback="")
text = get_clipboard(fallback="")  # alias
```

Maps to `ClipboardHelper.getText(Activity, String) → String`. Returns the clipboard content, or the fallback if the clipboard is empty or inaccessible.

## Capability

```python
app_config(uses=[Caps.Clipboard])
```

No manifest permissions needed.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Sharing and intents: [[40 - Capabilities/07 - Sharing and Intents]]
