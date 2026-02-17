# Track C Wave 6 Location Capability

Status: Completed  
Date: 2026-02-17

Wave 6 extends capability expansion with a deterministic `Location` helper-call surface and a visible integration flow that combines location + networking + storage.

## Delivered

- New helper-call capability binding:
  - `Caps.Location` -> `Lcom/ahnali/runtime/LocationHelper;->isLocationEnabled(Landroid/app/Activity;)I`
- New DSL APIs:
  - `location_enabled()` / `is_location_enabled()` -> integer expression surface (`1` enabled, `0` disabled/failure)
  - `check_location()` / `check_location_enabled()` / `location_check()` -> statement form
- Lowering integration:
  - capability guard + deterministic helper-call emission for both statement and expression paths
- Helper runtime emission:
  - `LocationHelper.smali` with deterministic provider-check semantics (`gps` then `network`)
  - null context, missing manager, and exceptions map to `0`
- Visible end-to-end flow:
  - `tests/test_track_c_wave6_visible_flow.py` combines `Location + Networking + Storage`
  - deterministic fallback branch uses explicit storage/body fallback strings

## Deterministic Contract

- Return `1` when location provider is enabled (`gps` or `network`).
- Return `0` when:
  - activity context is null
  - location manager is unavailable
  - provider checks fail
  - runtime exception occurs

## Conformance

- `tests/test_track_c_wave6_location.py`
- `tests/test_track_c_wave6_visible_flow.py`
