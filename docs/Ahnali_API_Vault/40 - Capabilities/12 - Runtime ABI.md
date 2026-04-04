---
tags: [ahnali, capabilities, abi, runtime, contract]
---

# Runtime ABI

> [!abstract] The frozen contract
> Every helper class, every method signature - locked for v1. CI checks for drift on every push.

## What the ABI covers

The ABI defines the exact class names and method signatures that the compiler emits for capability helpers. If you're writing tests that check compiled output, or if you're extending the capability system, this is your reference.

## Naming conventions

- Default helper package: `Lcom/ahnali/preview/`
- Event listener pattern: `Lcom/ahnali/preview/Ahnali<ListenerType>_<target_id>;`
- Suffixes tied to widget IDs are ABI-stable

## Stable listener class patterns

| Listener type | Class pattern |
|---|---|
| Click | `AhnaliClickListener_<id>` |
| Long click | `AhnaliLongClickListener_<id>` |
| Change (toggle/radio/switch) | `AhnaliChangeListener_<id>` |
| Touch | `AhnaliTouchListener_<id>` |
| Text change | `AhnaliTextChangeListener_<id>` |
| Item selected | `AhnaliItemSelectedListener_<id>` |
| Focus change | `AhnaliFocusChangeListener_<id>` |
| Menu item selected | `AhnaliMenuItemListener_<id>` |
| Swipe | `AhnaliSwipeListener_<id>` |
| Scroll | `AhnaliScrollListener_<id>` |
| Static list adapter | `AhnaliListAdapter_<id>` |

## Wrapper Activity ABI

The generated Activity (default: `Lcom/ahnali/preview/MainActivity;`) exposes:

- `constructor <init>()V`
- `onCreate(Landroid/os/Bundle;)V`
- Optional `onBackPressed()V` - calls `onSystemBack()I`, return `1` to suppress default, `0` to allow it
- Optional lifecycle bridges: `onStart()V`, `onResume()V`, `onPause()V`, `onStop()V`, `onDestroy()V`

Lifecycle ordering: `invoke-super` first, then static hook.

## Helper class signatures

### UrlLauncherHelper
- `openUrl(Activity, String) → int`

### ConnectivityHelper
- `isConnected(Activity) → int`

### StorageHelper
- `putString(Activity, String, String) → int`
- `getString(Activity, String, String) → String`
- `remove(Activity, String) → int`
- `exists(Activity, String) → int`
- `clear(Activity) → int`
- Plus DataStore, File, SQLite, Room, and encrypted variants

### HttpHelper
- `httpGet(Activity, String, String) → String`
- `httpGetStatus(Activity, String) → int`
- `httpGetError(Activity, String) → int`
- `httpGetRetry(Activity, String, int, int, String) → String`
- `httpGetJsonField(Activity, String, String, String) → String`
- `httpGetJsonFieldError(Activity, String, String) → int`
- Async: `nextAsyncToken() → int`, `startAsyncWithToken(int, Runnable) → int`, `cancelAsync(int) → int`, `getAsyncProgress(int) → int`, `getAsyncError(int) → int`, `getAsyncStatus(int) → int`, `getAsyncBody(int, String) → String`
- Plus timeout and request-option variants

### PermissionHelper
- `isGranted(Activity, String) → int`

### NotificationHelper
- `createChannel(Activity, String, String) → int`
- `postNotification(Activity, String, String, String) → int`
- `postNotificationError(Activity, String, String, String) → int`

### ClipboardHelper
- `setText(Activity, String) → int`
- `getText(Activity, String) → String`

### ShareHelper
- `shareText(Activity, String, String) → int`
- `shareFile(Activity, String, String, String) → int`
- `openUri(Activity, String) → int`
- Plus error variants

### WebHelper
- `setPolicy(Activity, ...) → int`
- `loadUrl(Activity, String) → int`
- `addJsBridge(Activity, String) → int`
- `chooseFile(Activity, String) → int`
- `setCookie(Activity, String, String) → int`
- `getCookie(Activity, String, String) → String`
- Plus error variants

### LocationHelper
- `isLocationEnabled(Activity) → int`

### DeepLinkHelper
- `getLaunchUri(Activity, String) → String`
- `getLaunchUriError(Activity) → int`

### WorkHelper
- `enqueueWork(Activity, String, int) → int`
- `cancelWork(Activity, String) → int`
- `getWorkStatus(Activity, String) → int`
- Plus error variants

### AlarmHelper
- `scheduleAlarm(Activity, String, int) → int`
- `cancelAlarm(Activity, String) → int`
- `getAlarmStatus(Activity, String) → int`
- Plus error variants

### JobHelper
- `scheduleJob(Activity, int, int) → int`
- `cancelJob(Activity, int) → int`
- `getJobStatus(Activity, int) → int`
- Plus error variants

## Versioning

ABI version: `1.0.0`. Frozen for v1. The snapshot file is `cfg/runtime_abi_snapshot_v1.json`.

## Conformance

- ABI tests: `tests/test_runtime_abi_v1.py`
- Snapshot drift check: `tests/test_runtime_abi_snapshot.py`
- CI gate: `.github/workflows/ci.yml` - fails on signature drift

## Learn more

- Capability mapping: [[../capability_runtime_mapping]]
- Capabilities overview: [[40 - Capabilities/01 - Overview]]
