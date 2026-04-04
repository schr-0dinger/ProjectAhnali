# Track C Wave 1: Visible App Flow

Status: Closed for Wave 1
Date: 2026-02-17

Single-screen demo that wires up the Wave 1 helpers together:
- `URLLauncher` via `open_url(...)`
- `Connectivity` via `check_connectivity()`
- `Storage` via `storage_put(...)`, `storage_get(...)`, `storage_remove(...)`

## What the user sees

- **Save URL** — stores a URL, updates status text.
- **Load URL** — reads stored URL, shows it in preview text.
- **Clear URL** — removes stored URL, updates preview/status text.
- **Check Connectivity** — calls connectivity helper, updates status text.
- **Open URL** — launches browser, updates status text.

## Conformance test

- Integration test: `tests/test_track_c_wave1_visible_flow.py`
- Assertions cover:
  - helper-call lowering for all Wave 1 helper methods
  - visible `TextView.setText(...)` updates
  - emitted helper classes for URL launcher, connectivity, and storage
