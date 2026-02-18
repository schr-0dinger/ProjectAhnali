---
tags: [ahnali, feedback, utility]
---

# Feedback and Utility Components

Back to: [[00_Home]]

This page covers runtime helper APIs that are commonly used inside handlers.

## UI Feedback Primitives

```python
toast(message, duration=0)
snackbar(message, duration=0)
simple_dialog(title, message)
exit_app()
```

Capitalized aliases also exist: `Toast`, `Snackbar`, `SimpleDialog`.

## Permissions and Capability Checks

```python
request_permission(permission, request_code=0)
request_permissions(*permissions, request_code=0)

check_permission(permission)
permission_granted(permission) / has_permission(permission)

check_connectivity() / is_connected()
check_location() / check_location_enabled()
location_enabled() / is_location_enabled()
```

## URL / Intents / Clipboard / Sharing

```python
open_url(url) / launch_url(url)
open_external(uri) / open_uri(uri)
open_external_error(uri)

clipboard_set(text) / set_clipboard(text)
clipboard_get(fallback="") / get_clipboard(fallback="")

share_text(text, chooser_title="Share via") / share(...)
share_text_result(...)
share_text_error(...)
```

## WebView Helper Surface

```python
web_set_policy(js_enabled=0, dom_storage=0, allow_file_access=0, allow_cleartext=0)
web_load(url) / open_web(url)
web_load_result(url)
web_load_error(url)

web_add_js_bridge(name) / web_register_js_bridge(name)
web_add_js_bridge_result(name)
web_add_js_bridge_error(name)

web_choose_file(mime_type="*/*") / web_file_chooser(...)
web_choose_file_result(...)
web_choose_file_error(...)

web_cookie_set(url, cookie) / web_set_cookie(...)
web_cookie_set_result(...)
web_cookie_set_error(...)
web_cookie_get(url, fallback="") / web_get_cookie(...)
web_cookie_get_error(url)
```

## Notifications

```python
create_notification_channel(channel_id, channel_name)
notification_channel(channel_id, channel_name)

notify(title, body, channel_id="ahnali_default")
send_notification(...)
notify_result(...)
notify_error(...)
```

## HTTP Helpers

### Sync/Expression-style

```python
http_get(url, default_value="") / fetch_url(...)
http_get_status(url)
http_get_error(url)
http_get_retry(url, retries, backoff_ms, default_value="") / fetch_url_retry(...)
http_get_json_field(url, key, fallback) / fetch_json_field(...)
http_get_json_field_error(url, key)
```

### Routed Handler-style

```python
http_get_route(url, success_target_id, failure_target_id, default_value="")
http_get_route_async(
    url,
    success_target_id,
    failure_target_id,
    default_value="",
    progress_target_id="",
    retries=0,
    timeout_ms=8000,
    method="GET",
    headers="",
    body="",
)
```

`http_get_route*` must be used inside click handlers and target ids must resolve to valid click handlers.

### Async Token Helpers

```python
http_async_cancel(token=None)
http_async_progress(token=None)
http_async_error(token=None)
http_async_status(token=None)
http_async_body(token=None, fallback="")
http_async_json_field(token, key, fallback)
http_async_json_field_error(token, key)
http_async_json_array_length(token, fallback=0)
```

## Storage and State Backends

### Primary storage

```python
storage_put / storage_get / storage_exists / storage_remove / storage_clear
# aliases: set_storage/get_storage/load_storage/has_storage/exists_storage/delete_storage/clear_storage
```

### Backend-specific helpers

```python
datastore_put/get/exists/remove/clear
file_write/read/exists/remove/clear
sqlite_put/get/exists/remove/clear
room_put/get/exists/remove/clear
encrypted_storage_put/get/exists/remove/clear
secure_storage_put/get/exists/remove/clear
```
