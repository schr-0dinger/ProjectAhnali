---
tags: [ahnali, capabilities, overview]
---

# Capabilities Overview

> [!abstract] How Ahnali talks to Android
> Capabilities are your app's declared access to platform services. Declare what you need, the compiler links the helpers and injects the permissions. If you don't declare it, you can't use it.

## The pattern

```python
from dsl.capabilities import Caps

app(
    activity("Main",
        app_config(uses=[Caps.Networking]),
        ui(button("Fetch", id="btn")),
        on_click("btn", [
            result = http_get("https://api.example.com", ""),
        ]),
    ),
)
```

Two things happen:
1. `INTERNET` permission gets injected into the manifest
2. `Lcom/ahnali/runtime/HttpHelper;` gets compiled into your app

## Helper call vs permission only

**Helper call** capabilities map to runtime classes with methods you can call from handlers. These are the ones you'll use most:

- [[40 - Capabilities/02 - Networking]] - HTTP requests
- [[40 - Capabilities/03 - Storage]] - Key-value storage
- [[40 - Capabilities/04 - Permissions]] - Runtime permission checks
- [[40 - Capabilities/05 - Notifications]] - Push notifications
- [[40 - Capabilities/06 - WebView]] - Web content
- [[40 - Capabilities/07 - Sharing and Intents]] - Share text/files
- [[40 - Capabilities/08 - Clipboard]] - Copy/paste
- [[40 - Capabilities/09 - Location]] - Location provider
- [[40 - Capabilities/10 - Deep Linking]] - Launch URIs
- [[40 - Capabilities/11 - Background Work]] - WorkManager, AlarmManager, JobScheduler

**Permission only** capabilities just inject manifest permissions - no helper class:

- `Caps.Camera` → CAMERA
- `Caps.Microphone` → RECORD_AUDIO
- `Caps.Audio` → RECORD_AUDIO
- `Caps.Video` → CAMERA + RECORD_AUDIO
- `Caps.Sensors` → BODY_SENSORS
- `Caps.FilePicker` → READ_EXTERNAL_STORAGE
- `Caps.Maps` → ACCESS_FINE_LOCATION + ACCESS_COARSE_LOCATION

## Error diagnostics

When you use a capability without declaring it:

```
[CapabilityError] http_get requires Caps.Networking. Fix: add app_config(uses=[Caps.Networking]) to activity(...).
```

The format is always: `[CapabilityError] <api_name> requires Caps.<Capability>. Fix: <instruction>.`

## The helper contract

All helper methods follow the same pattern:

- **Int-returning helpers**: `1` = success, `0` = failure
- **Value-returning helpers**: the value on success, fallback argument on failure
- **Error code helpers**: `0` = success, positive integers for specific error types

This means your handler code can always reason about what happened without catching exceptions.

## Runtime ABI

The helper class signatures are frozen for v1. The snapshot lives in `cfg/runtime_abi_snapshot_v1.json` and CI checks for drift on every push.

> [!info] Full ABI reference
> See [[40 - Capabilities/12 - Runtime ABI]] for the complete signature listing.

## Learn more

- Capabilities system overview: [[20 - Core Concepts/04 - Capabilities System]]
- State management: [[20 - Core Concepts/05 - State Management]]
