# Track C Wave 5 Visible Flow

Status: Completed  
Date: 2026-02-17

This flow validates one visible end-to-end scenario that combines storage, async networking, and connectivity checks while preserving deterministic fallback behavior.

## Flow

1. `seed_cache_btn` stores a deterministic cache fallback value via `storage_put("last_title", "cached-offline")`.
2. `start_btn` calls `check_connectivity()` and dispatches async request-options route:
   - `http_get_route_async(..., "ok_btn", "fail_btn", "offline-payload", "progress_btn", retries=1, timeout_ms=2400, method="POST", headers="X-Demo: wave5", body="{\"mode\":\"demo\"}")`
3. `progress_btn` reads token-scoped progress (`http_async_progress(async_token)`) and updates visible status text.
4. `ok_btn` reads typed async JSON surface:
   - `http_async_json_field(async_token, "title", "cached-offline")`
   - `http_async_json_field_error(async_token, "title")`
   - On success, UI shows parsed value and cache is refreshed via `storage_put`.
   - On non-zero error, UI takes deterministic cache fallback branch via `storage_get("last_title", "cached-offline")`.
5. `fail_btn` reads token-scoped async surfaces:
   - `http_async_error(async_token)`
   - `http_async_body(async_token, "offline-payload")`
   - Cancellation code `7` resolves to cached fallback; non-cancel failures resolve to body fallback.

## Determinism

- Network fallback body is fixed by explicit `offline-payload` fallback argument.
- Cache fallback is fixed by explicit `storage_get(..., "cached-offline")`.
- Async/cancel branch behavior is fixed by explicit error code checks (`0` success, `7` cancelled, otherwise failure branch).
- Route wiring is deterministic because both success/failure/progress targets are emitted as concrete helper classes.

## Conformance

- `tests/test_track_c_wave5_visible_flow.py`
