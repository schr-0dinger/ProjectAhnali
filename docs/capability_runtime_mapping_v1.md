# Ahnali Capability Runtime Mapping v1

Status: Frozen for v1  
Effective date: 2026-02-16  
ABI version: `1.0.0`

This document defines the canonical capability-to-runtime mapping used by Ahnali v1.

## Contract

- Canonical capability names are stable in v1.
- Aliases are accepted compatibility inputs and resolve to canonical names.
- Permissions are deterministic and ordered.
- Runtime helper integration mode is capability-specific (`permission_only` or `helper_call`).
- Track C Wave 1 introduces initial helper-call bindings for URL launcher, connectivity checks, and storage put/get.

## Mapping Table (v1)

| Canonical Capability | Accepted Aliases | Permissions | Runtime Helper Class | Runtime Helper Method/Sig | Mode |
|---|---|---|---|---|---|
| `Camera` | `Camera` | `android.permission.CAMERA` | n/a | n/a | `permission_only` |
| `Microphone` | `Microphone` | `android.permission.RECORD_AUDIO` | n/a | n/a | `permission_only` |
| `Audio` | `Audio` | `android.permission.RECORD_AUDIO` | n/a | n/a | `permission_only` |
| `Video` | `Video` | `android.permission.CAMERA`, `android.permission.RECORD_AUDIO` | n/a | n/a | `permission_only` |
| `WebView` | `WebView` | `android.permission.INTERNET` | n/a | n/a | `permission_only` |
| `Sensors` | `Sensors` | `android.permission.BODY_SENSORS` | n/a | n/a | `permission_only` |
| `Storage` | `Storage` | `android.permission.READ_EXTERNAL_STORAGE`, `android.permission.WRITE_EXTERNAL_STORAGE` | `Lcom/ahnali/runtime/StorageHelper;` | `putString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`, `getString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;` | `helper_call` |
| `FilePicker` | `FilePicker`, `File Picker` | `android.permission.READ_EXTERNAL_STORAGE` | n/a | n/a | `permission_only` |
| `Connectivity` | `Connectivity` | `android.permission.ACCESS_NETWORK_STATE`, `android.permission.INTERNET` | `Lcom/ahnali/runtime/ConnectivityHelper;` | `isConnected(Landroid/app/Activity;)I` | `helper_call` |
| `URLLauncher` | `URLLauncher`, `URL launcher` | `android.permission.INTERNET` | `Lcom/ahnali/runtime/UrlLauncherHelper;` | `openUrl(Landroid/app/Activity;Ljava/lang/String;)I` | `helper_call` |
| `Permissions` | `Permissions` | none | n/a | n/a | `permission_only` |
| `Maps` | `Maps` | `android.permission.ACCESS_FINE_LOCATION`, `android.permission.ACCESS_COARSE_LOCATION` | n/a | n/a | `permission_only` |
| `Location` | `Location` | `android.permission.ACCESS_FINE_LOCATION`, `android.permission.ACCESS_COARSE_LOCATION` | n/a | n/a | `permission_only` |

## Source of Truth in Code

- Registry and mapping model: `dsl/capabilities.py`
- ABI contract for generated helper bridge classes: `runtime_abi_v1.md`

## Conformance

- Mapping/runtime-binding tests: `tests/test_capabilities.py`
- ABI contract tests: `tests/test_runtime_abi_v1.py`
