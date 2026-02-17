# Track C Wave 7 Permissions Capability

Status: Completed  
Date: 2026-02-17

Wave 7 closes the `Permissions` capability slice as a deterministic helper-call surface and adds a visible integration flow combining permissions + storage + URL launch fallback routing.

## Delivered

- New helper-call capability binding:
  - `Caps.Permissions` -> `Lcom/ahnali/runtime/PermissionHelper;->isGranted(Landroid/app/Activity;Ljava/lang/String;)I`
- New DSL APIs:
  - `permission_granted(permission)` / `has_permission(permission)` -> integer expression surface (`1` granted, `0` denied/error)
  - `check_permission(permission)` / `permission_check(permission)` -> statement form
- Lowering integration:
  - capability guard + deterministic helper-call emission for statement and expression paths
- Helper runtime emission:
  - `PermissionHelper.smali` with deterministic runtime permission probe using `Activity.checkCallingOrSelfPermission(...)`
  - null context/null permission/exception maps to `0`
- Visible end-to-end flow:
  - `tests/test_track_c_wave7_visible_flow.py` combines `Permissions + Storage + URLLauncher`
  - deterministic fallback branch uses explicit storage fallback strings

## Deterministic Contract

- Return `1` when the requested permission is granted.
- Return `0` when:
  - activity context is null
  - permission string is null
  - permission is denied
  - runtime exception occurs

## Conformance

- `tests/test_track_c_wave7_permissions.py`
- `tests/test_track_c_wave7_visible_flow.py`
