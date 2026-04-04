# Track C Wave 3: Async Route

Status: Completed
Date: 2026-02-17

Tokened non-blocking route dispatch with deterministic cancellation, progress, and payload surfaces.

Core APIs:
- `http_get_route_async(url, "success_btn", "failure_btn", fallback, progress_btn, retries, timeout_ms)`
- `http_async_cancel(token)`
- `http_async_progress(token)`
- `http_async_error(token)`
- `http_async_status(token)`
- `http_async_body(token, fallback)`

## Contract

- Only valid inside `@on_click(...)` handlers.
- Requires `Caps.Networking`.
- Route dispatch allocates a token and runs in a background worker thread.
- Success/failure/progress callbacks are posted on the UI thread via `Activity.runOnUiThread(...)`.
- Async state is token-scoped and deterministic (`cancel/progress/error/status/body`).
- Worker supports deterministic retry count (`retries`) and timeout control (`timeout_ms`, clamped to default when non-positive).

## Generated helper/runtime surfaces

- `Lcom/ahnali/preview/AhnaliHttpRouteAsyncWorker;` (`Runnable` worker)
- `Lcom/ahnali/preview/AhnaliUiRunnable_<target_id>;` (`Runnable` click callback proxy)
- `Lcom/ahnali/runtime/HttpHelper;->nextAsyncToken()I`
- `Lcom/ahnali/runtime/HttpHelper;->getCurrentAsyncToken()I`
- `Lcom/ahnali/runtime/HttpHelper;->startAsync(Ljava/lang/Runnable;)I`
- `Lcom/ahnali/runtime/HttpHelper;->startAsyncWithToken(ILjava/lang/Runnable;)I`
- `Lcom/ahnali/runtime/HttpHelper;->cancelAsync(I)I`
- `Lcom/ahnali/runtime/HttpHelper;->getAsyncProgress(I)I`
- `Lcom/ahnali/runtime/HttpHelper;->getAsyncError(I)I`
- `Lcom/ahnali/runtime/HttpHelper;->getAsyncStatus(I)I`
- `Lcom/ahnali/runtime/HttpHelper;->getAsyncBody(ILjava/lang/String;)Ljava/lang/String;`
- Timeout-aware fetch methods used by worker:
  - `httpGetWithTimeout(...)`
  - `httpGetStatusWithTimeout(...)`
  - `httpGetErrorWithTimeout(...)`

## Deterministic async error codes

- `0`: success
- `1`: invalid input
- `2`: transport/runtime exception
- `3`: non-200 HTTP status
- `4`: empty body
- `7`: cancelled
- `8`: stale/unknown token

## Conformance

- `tests/test_track_c_wave3_async_route.py`
- `tests/test_track_c_wave3_visible_flow.py`

## Follow-up

Wave 4 (async concurrency, request options, typed adapters): `docs/TrackC_Wave4_Async_Concurrency.md`.
