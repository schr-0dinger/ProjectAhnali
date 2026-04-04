---
tags: [ahnali, capabilities, networking, http]
---

# Networking

> [!abstract] HTTP requests, sync and async
> From simple GET calls to token-scoped async routes with retries, timeouts, and JSON parsing. All deterministic, all compile-time.

## Sync requests

The simplest path:

```python
result = http_get("https://api.example.com/data", "")
```

Returns the response body, or the fallback string on any failure.

Check what happened:

```python
status = http_get_status("https://api.example.com/data")  # HTTP status code, or -1
error = http_get_error("https://api.example.com/data")     # 0 = success
```

Error codes:
- `0` - success
- `1` - invalid input
- `2` - transport/runtime exception
- `3` - non-200 status
- `4` - empty body

## Retry

```python
result = http_get_retry("https://api.example.com/data", retries=3, backoff_ms=1000, default_value="")
```

- Attempts = `max(0, retries) + 1`
- Fixed backoff between attempts (no jitter)
- Returns body on first success, otherwise fallback

## JSON parsing

```python
name = http_get_json_field("https://api.example.com/user", "name", "unknown")
err = http_get_json_field_error("https://api.example.com/user", "name")
```

Error codes extend the base set:
- `5` - malformed payload
- `6` - missing key (or null value)

## Routed handlers

Wire success/failure to UI elements:

```python
http_get_route(
    "https://api.example.com/data",
    "success_btn",    # enabled on success
    "failure_btn",    # enabled on failure
    "Loading...",     # fallback text
)
```

## Async routes

Background worker with UI-thread callbacks:

```python
http_get_route_async(
    "https://api.example.com/data",
    "success_btn",
    "failure_btn",
    "Loading...",
    progress_target_id="progress_bar",
    retries=3,
    timeout_ms=8000,
)
```

This spawns a background thread, posts callbacks to the UI thread, and exposes token-scoped state surfaces.

### Request options

```python
http_get_route_async(
    "https://api.example.com/data",
    "success_btn", "failure_btn", "",
    method="POST",
    headers="Content-Type: application/json\nAccept: application/json",
    body='{"key": "value"}',
)
```

- `method`: defaults to `GET`, accepts `GET`/`POST` (case-insensitive), rejects others
- `headers`: newline-delimited `Key: Value`, malformed lines ignored
- `body`: only applied for `POST`, UTF-8 encoded

### Token-scoped async state

After starting an async route, use the token to check state:

```python
token = http_async_progress(token=None)  # 0..100
status = http_async_status(token=None)   # completion status
body = http_async_body(token=None, fallback="")
error = http_async_error(token=None)
http_async_cancel(token=None)
```

Async JSON adapters:
```python
http_async_json_field(token, key, fallback)
http_async_json_field_error(token, key)
http_async_json_array_length(token, fallback=0)
```

Async error codes extend the base set:
- `7` - cancelled
- `8` - stale/unknown token

## Capability

```python
app_config(uses=[Caps.Networking])
```

Injects `INTERNET` permission and links `Lcom/ahnali/runtime/HttpHelper;`.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Storage: [[40 - Capabilities/03 - Storage]]
- Runtime ABI: [[40 - Capabilities/12 - Runtime ABI]]
