# Capability → Runtime Mapping v1

> ABI version: `1.0.0`

Frozen ABI. This is the contract between what you declare in the DSL and what helper class/method actually gets called at runtime.

## The mapping

| Capability | Mode | Helper Class | Primary Method | Permissions |
|---|---|---|---|---|
| `AlarmManager` | helper_call | `Lcom/ahnali/runtime/AlarmHelper;` | `scheduleAlarm(...)` | — |
| `Audio` | permission_only | n/a | n/a | android.permission.RECORD_AUDIO |
| `Camera` | permission_only | n/a | n/a | android.permission.CAMERA |
| `Clipboard` | helper_call | `Lcom/ahnali/runtime/ClipboardHelper;` | `setText(...)` | — |
| `Connectivity` | helper_call | `Lcom/ahnali/runtime/ConnectivityHelper;` | `isConnected(...)` | android.permission.ACCESS_NETWORK_STATE, android.permission.INTERNET |
| `DeepLinking` | helper_call | `Lcom/ahnali/runtime/DeepLinkHelper;` | `getLaunchUri(...)` | — |
| `FilePicker` | permission_only | n/a | n/a | android.permission.READ_EXTERNAL_STORAGE |
| `JobScheduler` | helper_call | `Lcom/ahnali/runtime/JobHelper;` | `scheduleJob(...)` | — |
| `Location` | helper_call | `Lcom/ahnali/runtime/LocationHelper;` | `isLocationEnabled(...)` | android.permission.ACCESS_FINE_LOCATION, android.permission.ACCESS_COARSE_LOCATION |
| `Maps` | permission_only | n/a | n/a | android.permission.ACCESS_FINE_LOCATION, android.permission.ACCESS_COARSE_LOCATION |
| `Microphone` | permission_only | n/a | n/a | android.permission.RECORD_AUDIO |
| `Networking` | helper_call | `Lcom/ahnali/runtime/HttpHelper;` | `httpGet(...)` | android.permission.INTERNET |
| `Notifications` | helper_call | `Lcom/ahnali/runtime/NotificationHelper;` | `postNotification(...)` | android.permission.POST_NOTIFICATIONS |
| `Permissions` | helper_call | `Lcom/ahnali/runtime/PermissionHelper;` | `isGranted(...)` | — |
| `Sensors` | permission_only | n/a | n/a | android.permission.BODY_SENSORS |
| `Sharing` | helper_call | `Lcom/ahnali/runtime/ShareHelper;` | `shareText(...)` | — |
| `Storage` | helper_call | `Lcom/ahnali/runtime/StorageHelper;` | `putString(...)` | android.permission.READ_EXTERNAL_STORAGE, android.permission.WRITE_EXTERNAL_STORAGE |
| `URLLauncher` | helper_call | `Lcom/ahnali/runtime/UrlLauncherHelper;` | `openUrl(...)` | android.permission.INTERNET |
| `Video` | permission_only | n/a | n/a | android.permission.CAMERA, android.permission.RECORD_AUDIO |
| `WebView` | helper_call | `Lcom/ahnali/runtime/WebHelper;` | `loadUrl(...)` | android.permission.INTERNET |
| `WorkManager` | helper_call | `Lcom/ahnali/runtime/WorkHelper;` | `enqueueWork(...)` | — |

## How it works

You declare a capability in your app config (`app_config(uses=[Caps.Networking])`). The compiler resolves it to a runtime helper class and the specific method signatures that class exposes. Every capability has a deterministic set of permissions attached to it.

Some capabilities are `helper_call` — they map to actual runtime helper classes with methods. Others are `permission_only` — they just inject the right manifest permissions and don't generate helper code.

## Where this lives in code

- Registry: `dsl/capabilities.py`
- ABI contract: `docs/runtime_abi_v1.md`
- Tests: `tests/test_capabilities.py`, `tests/test_runtime_abi_v1.py`
- Snapshot: `cfg/capability_mapping_snapshot_v1.json`

If you're adding a new capability, you need to update the registry, add the helper class, update the snapshot, and write tests. The CI gates will catch you if you miss any of those.
