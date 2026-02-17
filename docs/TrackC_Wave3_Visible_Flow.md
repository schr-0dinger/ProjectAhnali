# Track C Wave 3 Visible Flow

Status: Completed  
Date: 2026-02-17

This flow validates a visible end-to-end tokened async networking route with deterministic fallback behavior.

## Flow

1. `start_btn` dispatches async route and stores token in state:
   - `async_token = http_get_route_async(..., "ok_btn", "fail_btn", "offline", "progress_btn", retries=2, timeout_ms=2500)`
2. `progress_btn` reads token-scoped progress (`http_async_progress(async_token)`) and updates visible status text.
3. `cancel_btn` issues token-scoped cancellation (`http_async_cancel(async_token)`).
4. `ok_btn` reads token-scoped completion payload (`http_async_status`, `http_async_body`, `http_async_error`) and updates UI.
5. `fail_btn` routes deterministic fallback branch:
   - handles cancel code `7` vs other failures
   - renders fallback body (`offline`)
   - launches help URL via `open_url(...)`

## Determinism

- Token-scoped helper calls prevent stale worker state from being treated as current.
- Failure/cancel branches are deterministic via explicit async error codes.
- `http_async_body(token, fallback)` guarantees a stable fallback string when no valid payload is available.

## Conformance

- `tests/test_track_c_wave3_visible_flow.py`
