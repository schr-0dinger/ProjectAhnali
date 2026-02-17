# Track C Wave 3 Async Route (Initial Slice)

Status: Started  
Date: 2026-02-17

Wave 3 begins with a non-blocking networking route primitive:
- `http_get_route_async(url, "success_btn", "failure_btn", fallback)`

## Contract

- Valid only inside `@on_click(...)` handlers.
- Requires `Caps.Networking`.
- Dispatches route evaluation in a background thread.
- Posts success/failure callback handlers to UI thread (`Activity.runOnUiThread`).
- Uses existing deterministic networking helpers (`httpGetStatus`, `httpGet`, `httpGetError`) inside async worker.

## Generated helper classes

- `Lcom/ahnali/preview/AhnaliHttpRouteAsyncWorker;` (`Runnable` worker)
- `Lcom/ahnali/preview/AhnaliUiRunnable_<target_id>;` (`Runnable` click callback proxy)
- `Lcom/ahnali/runtime/HttpHelper;->startAsync(Ljava/lang/Runnable;)I` (thread dispatch helper)

## Conformance

- `tests/test_track_c_wave3_async_route.py`
