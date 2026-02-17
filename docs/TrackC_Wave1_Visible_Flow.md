# Track C Wave 1 Visible App Flow

Status: Closed for Wave 1  
Date: 2026-02-17

This flow demonstrates one screen that uses the core Wave 1 capability helpers together:
- `URLLauncher` via `open_url(...)`
- `Connectivity` via `check_connectivity()`
- `Storage` via `storage_put(...)`, `storage_get(...)`, `storage_remove(...)`

## User-visible behavior

- **Save URL** stores a URL and updates status text.
- **Load URL** reads stored URL and shows it in preview text.
- **Clear URL** removes stored URL and updates preview/status text.
- **Check Connectivity** performs connectivity helper call and updates status text.
- **Open URL** launches browser and updates status text.

## Conformance test

- Integration test: `tests/test_track_c_wave1_visible_flow.py`
- Assertions cover:
  - helper-call lowering for all Wave 1 helper methods
  - visible `TextView.setText(...)` updates
  - emitted helper classes for URL launcher, connectivity, and storage
