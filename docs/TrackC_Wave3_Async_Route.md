# Track C Wave 3 Async Route (Initial Slice)

Status: Started  
Date: 2026-02-17

Wave 3 begins with a non-blocking networking route primitive:
- `http_get_route_async(url, "success_btn", "failure_btn", fallback)`
- `http_async_cancel()`
- `http_async_progress()`
- `http_async_error()`

## Contract

- Valid only inside `@on_click(...)` handlers.
- Requires `Caps.Networking`.
- Dispatches route evaluation in a background thread.
- Posts success/failure callback handlers to UI thread (`Activity.runOnUiThread`).
- Uses existing deterministic networking helpers (`httpGetStatus`, `httpGet`, `httpGetError`) inside async worker.
- Cancellation/progress/error are deterministic global async surfaces for current worker lifecycle.

## Generated helper classes

- `Lcom/ahnali/preview/AhnaliHttpRouteAsyncWorker;` (`Runnable` worker)
- `Lcom/ahnali/preview/AhnaliUiRunnable_<target_id>;` (`Runnable` click callback proxy)
- `Lcom/ahnali/runtime/HttpHelper;->startAsync(Ljava/lang/Runnable;)I` (thread dispatch helper)
- `Lcom/ahnali/runtime/HttpHelper;->cancelAsync()I`
- `Lcom/ahnali/runtime/HttpHelper;->getAsyncProgress()I`
- `Lcom/ahnali/runtime/HttpHelper;->getAsyncError()I`

## Deterministic async error codes

- `0`: success
- `1`: invalid input
- `2`: transport/runtime exception
- `3`: non-200 HTTP status
- `4`: empty body
- `7`: cancelled

## Conformance

- `tests/test_track_c_wave3_async_route.py`

## Next Steps

1. Add per-request async token contract (token returned by async start; token-scoped cancel/progress/error).
2. Add deterministic progress callback wiring for async route (`on_progress` target).
3. Add deterministic completion payload handoff (`status/body/error`) into callback handlers.
4. Add timeout/retry controls for async worker and map outcomes to explicit error codes.
5. Close Wave 3 with one visible tokened async demo flow and extended conformance tests.
