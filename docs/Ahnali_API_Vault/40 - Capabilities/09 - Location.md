---
tags: [ahnali, capabilities, location]
---

# Location

> [!abstract] Check if location is enabled
> A deterministic check for whether the device's location provider is turned on.

## Checking location

```python
enabled = location_enabled()
enabled = check_location()
enabled = check_location_enabled()
enabled = is_location_enabled()
```

All aliases map to `LocationHelper.isLocationEnabled(Activity) → int`. Returns `1` if the location provider is enabled, `0` otherwise.

> [!note] What this doesn't do
> This checks whether location is enabled on the device - it doesn't request location permissions or fetch GPS coordinates. For permission checks, use [[40 - Capabilities/04 - Permissions]]. For actual location data, you'd need FusedLocationProvider (not yet implemented).

## Capability

```python
app_config(uses=[Caps.Location])
```

Injects `ACCESS_FINE_LOCATION` and `ACCESS_COARSE_LOCATION` permissions and links `Lcom/ahnali/runtime/LocationHelper;`.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Permissions: [[40 - Capabilities/04 - Permissions]]
