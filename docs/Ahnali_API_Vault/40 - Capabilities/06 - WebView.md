---
tags: [ahnali, capabilities, webview, web]
---

# WebView

> [!abstract] Web content in your app
> Load URLs, set policy, register JS bridges, handle file choosers, and manage cookies - all through deterministic helper calls.

## Loading URLs

```python
web_load("https://example.com")
open_web("https://example.com")  # alias
result = web_load_result("https://example.com")
error = web_load_error("https://example.com")
```

## Setting policy

```python
web_set_policy(
    js_enabled=1,
    dom_storage=1,
    allow_file_access=0,
    allow_cleartext=0,
)
web_policy(js_enabled=1, dom_storage=1)  # alias
```

Controls JavaScript, DOM storage, file access, and cleartext traffic.

## JS bridge

```python
web_add_js_bridge("myBridge")
web_register_js_bridge("myBridge")  # alias
result = web_add_js_bridge_result("myBridge")
error = web_add_js_bridge_error("myBridge")
```

Registers a JavaScript interface on the WebView with policy-constrained access.

## File chooser

```python
web_choose_file(mime_type="*/*")
web_file_chooser(mime_type="*/*")  # alias
result = web_choose_file_result(mime_type="*/*")
error = web_choose_file_error(mime_type="*/*")
```

## Cookie management

```python
web_cookie_set("https://example.com", "session=abc123")
web_set_cookie("https://example.com", "session=abc123")  # alias
result = web_cookie_set_result("https://example.com")
error = web_cookie_set_error("https://example.com")

cookie = web_cookie_get("https://example.com", fallback="")
cookie = web_get_cookie("https://example.com", fallback="")  # alias
error = web_cookie_get_error("https://example.com")
```

## Capability

```python
app_config(uses=[Caps.Web])
```

Aliases: `Caps.WebView`. Injects `INTERNET` permission and links `Lcom/ahnali/runtime/WebHelper;`.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Deep linking: [[40 - Capabilities/10 - Deep Linking]]
