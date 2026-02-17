# Track C Wave 2 Visible App Flow

Status: Closed for Wave 2  
Date: 2026-02-17

This flow demonstrates one screen that combines Wave 2 networking response routing with Wave 1 storage and URL launch helpers:
- `Storage` via `storage_put(...)`, `storage_get(...)`
- `Networking` response routing via `http_get_route(...)`
- `URLLauncher` via `open_url(...)`

## User-visible behavior

- **Save URL** stores homepage URL and updates status text.
- **Load URL** reads stored homepage URL with deterministic storage fallback and updates preview/status text.
- **Probe Route** runs network routing:
  - success branch updates status text to success message
  - fallback branch updates preview/status text with deterministic fallback values
- **Open URL** launches browser and updates status text.

## Deterministic fallback branch

- Routing uses `http_get_route("https://example.com/health", "probe_ok_btn", "probe_fail_btn", "offline")`.
- Failure branch handler (`probe_fail_btn`) always writes visible fallback markers:
  - `preview_label.text = "offline"`
  - `status_label.text = "Network route: fallback"`

## Conformance test

- Integration test: `tests/test_track_c_wave2_visible_flow.py`
- Assertions cover:
  - helper-call lowering for storage + networking route + URL launch
  - success/fallback route handler wiring
  - visible `TextView.setText(...)` updates
  - emitted runtime helper classes for storage/networking/url launch
