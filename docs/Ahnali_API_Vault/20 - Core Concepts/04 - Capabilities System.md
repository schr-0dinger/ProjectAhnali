---
tags: [ahnali, capabilities, permissions]
---

# Capabilities System

> [!abstract] What capabilities are
> Capabilities are your app's declared access to Android platform services. You declare what you need, the compiler links the right helpers and injects the right permissions. If you don't declare it, you can't use it.

## How it works

```python
from dsl.capabilities import Caps

app(
    activity("Main",
        app_config(uses=[Caps.Networking, Caps.Storage]),
        ui(
            text("Loading...", id="status"),
            button("Fetch", id="fetch_btn"),
        ),
        on_click("fetch_btn", [
            http_get("https://api.example.com/data", ""),
        ]),
    ),
)
```

Two things happen here:

1. **Manifest permissions** — `INTERNET` gets injected into the AndroidManifest.xml
2. **Helper class linking** — `Lcom/ahnali/runtime/HttpHelper;` gets compiled into your app

If you try to call `http_get` without `Caps.Networking`, the compiler stops you with a clear error:

```
[CapabilityError] http_get requires Caps.Networking. Fix: add app_config(uses=[Caps.Networking]) to activity(...).
```

## Capability types

Capabilities fall into two categories:

**Helper call** — maps to a runtime helper class with methods:
- Networking, Storage, URL Launcher, Connectivity, Location, Permissions, Notifications, Clipboard, Sharing, WebView, Deep Linking, WorkManager, AlarmManager, JobScheduler

**Permission only** — just injects manifest permissions, no helper class:
- Camera, Microphone, Audio, Video, Sensors, FilePicker, Maps

## The helper contract

Every helper class follows the same pattern:

- Methods return `1` on success, `0` on failure (for int-returning helpers)
- Methods return the requested value on success, a fallback on failure (for value-returning helpers)
- Error code methods return deterministic error codes (`0` = success, `1` = invalid input, `2` = transport error, etc.)

This means your handler code can always reason about what happened:

```python
result = http_get("https://api.example.com", "")
error = http_get_error("https://api.example.com")
# error == 0 means success
# error == 1 means bad input
# error == 2 means network failure
# error == 3 means non-200 status
# error == 4 means empty body
```

## Async networking

The networking capability includes a full async surface with token-scoped state:

```python
http_get_route_async(
    "https://api.example.com/data",
    "success_handler",    # button to enable on success
    "failure_handler",    # button to enable on failure
    "Loading...",         # fallback text
    progress_target_id="progress_bar",
    retries=3,
    timeout_ms=8000,
)
```

The background worker runs on a separate thread, posts callbacks to the UI thread, and exposes token-scoped progress/error/status/body surfaces.

## All capabilities

| Capability | What it gives you |
|---|---|
| `Caps.URLLauncher` | Open URLs in browser |
| `Caps.Connectivity` | Check network connection |
| `Caps.Storage` | Key-value storage (6 backends) |
| `Caps.Networking` | HTTP requests (sync + async) |
| `Caps.Location` | Check if location is enabled |
| `Caps.Permissions` | Check runtime permission grants |
| `Caps.Notifications` | Post notifications and channels |
| `Caps.Clipboard` | Copy and paste |
| `Caps.Sharing` | Share text/files, open URIs |
| `Caps.Web` | WebView, JS bridge, file chooser, cookies |
| `Caps.DeepLinking` | Handle launch URIs |
| `Caps.WorkManager` | Background work scheduling |
| `Caps.AlarmManager` | Alarm scheduling |
| `Caps.JobScheduler` | Job scheduling |

## Learn more

- Full capability reference: [[40 - Capabilities/01 - Overview]]
- Runtime ABI contract: [[40 - Capabilities/12 - Runtime ABI]]
- How Ahnali works: [[20 - Core Concepts/01 - How Ahnali Works]]
