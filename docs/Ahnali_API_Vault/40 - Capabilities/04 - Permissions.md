---
tags: [ahnali, capabilities, permissions]
---

# Permissions

> [!abstract] Runtime permission checks
> Check if a permission is granted, request permissions, and handle the results - all at the DSL level.

## Checking permissions

```python
granted = permission_granted("android.permission.CAMERA")
granted = has_permission("android.permission.CAMERA")
granted = check_permission("android.permission.CAMERA")
```

All three are aliases - they map to `Lcom/ahnali/runtime/PermissionHelper;->isGranted(Activity, String) → int`.

Returns `1` if granted, `0` if denied.

## Requesting permissions

```python
request_permission("android.permission.CAMERA", request_code=0)
request_permissions("android.permission.CAMERA", "android.permission.RECORD_AUDIO", request_code=0)
```

These trigger the Android runtime permission dialog. The result flows through the normal event system.

## Capability

```python
app_config(uses=[Caps.Permissions])
```

No manifest permissions are injected by this capability itself - it just links the helper class that checks runtime grant state.

> [!tip] Permission-only capabilities
> Some capabilities like `Caps.Camera` or `Caps.Location` inject manifest permissions but don't have helper classes. Use `Caps.Permissions` when you need to check grant state at runtime.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Location: [[40 - Capabilities/09 - Location]]
- Runtime ABI: [[40 - Capabilities/12 - Runtime ABI]]
