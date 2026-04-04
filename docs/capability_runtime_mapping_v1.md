# Capability → Runtime Mapping v1

Frozen ABI. This is the contract between what you declare in the DSL and what helper class/method actually gets called at runtime.

## How it works

You declare a capability in your app config (`app_config(uses=[Caps.Networking])`). The compiler resolves it to a runtime helper class and the specific method signatures that class exposes. Every capability has a deterministic set of permissions attached to it.

Some capabilities are `helper_call` — they map to actual runtime helper classes with methods. Others are `permission_only` — they just inject the right manifest permissions and don't generate helper code.

## The mapping

### Capabilities with helper classes

**URLLauncher** → `UrlLauncherHelper`
- `openUrl(Activity, String) → int`
- Permissions: INTERNET

**Connectivity** → `ConnectivityHelper`
- `isConnected(Activity) → int`
- Permissions: ACCESS_NETWORK_STATE, INTERNET

**Storage** → `StorageHelper`
- Base: `putString`, `getString`, `remove`, `exists`, `clear`
- DataStore: `dataStorePutString`, `dataStoreGetString`, `dataStoreRemove`, `dataStoreExists`, `dataStoreClear`
- File: `fileWriteString`, `fileReadString`, `fileRemove`, `fileExists`, `fileClear`
- SQLite: `sqlitePutString`, `sqliteGetString`, `sqliteRemove`, `sqliteExists`, `sqliteClear`
- Room: `roomPutString`, `roomGetString`, `roomRemove`, `roomExists`, `roomClear`
- Encrypted: `encryptedPutString`, `encryptedGetString`, `encryptedRemove`, `encryptedExists`, `encryptedClear`
- Permissions: READ/WRITE_EXTERNAL_STORAGE

**Networking** → `HttpHelper`
- Sync: `httpGet`, `httpGetStatus`, `httpGetError`
- With timeout: `httpGetWithTimeout`, `httpGetStatusWithTimeout`, `httpGetErrorWithTimeout`
- Full request: `httpRequestWithTimeout`, `httpRequestStatusWithTimeout`, `httpRequestErrorWithTimeout`
- Retry: `httpGetRetry`
- JSON: `httpGetJsonField`, `httpGetJsonFieldError`
- Async: `nextAsyncToken`, `getCurrentAsyncToken`, `startAsync`, `startAsyncWithToken`, `cancelAsync`
- Async state: `getAsyncProgress`, `getAsyncError`, `getAsyncStatus`, `getAsyncBody`
- Async JSON: `getAsyncJsonField`, `getAsyncJsonFieldError`, `getAsyncJsonArrayLength`, `getAsyncJsonArrayLengthError`
- Permissions: INTERNET

**Location** → `LocationHelper`
- `isLocationEnabled(Activity) → int`
- Permissions: ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION

**Permissions** → `PermissionHelper`
- `isGranted(Activity, String) → int`
- No permissions needed (checks runtime grant state)

**Notifications** → `NotificationHelper`
- `createChannel(Activity, String, String) → int`
- `postNotification(Activity, String, String, String) → int`
- `postNotificationError(Activity, String, String, String) → int`
- Permissions: POST_NOTIFICATIONS

**Clipboard** → `ClipboardHelper`
- `setText(Activity, String) → int`
- `getText(Activity, String) → String`
- No permissions needed

**Sharing** → `ShareHelper`
- `shareText(Activity, String, String) → int`
- `shareFile(Activity, String, String, String) → int`
- `openUri(Activity, String) → int`
- Plus error variants for each
- No permissions needed

**WebView** → `WebHelper`
- `setPolicy(Activity, ...) → int`
- `loadUrl(Activity, String) → int`
- `addJsBridge(Activity, String) → int`
- `chooseFile(Activity, String) → int`
- `setCookie(Activity, String, String) → int`
- `getCookie(Activity, String, String) → String`
- Plus error variants for each
- Permissions: INTERNET

**DeepLinking** → `DeepLinkHelper`
- `getLaunchUri(Activity, String) → String`
- `getLaunchUriError(Activity) → int`
- No permissions needed

**WorkManager** → `WorkHelper`
- `enqueueWork(Activity, String, int) → int`
- `cancelWork(Activity, String) → int`
- `getWorkStatus(Activity, String) → int`
- Plus error variants
- No permissions needed

**AlarmManager** → `AlarmHelper`
- `scheduleAlarm(Activity, String, int) → int`
- `cancelAlarm(Activity, String) → int`
- `getAlarmStatus(Activity, String) → int`
- Plus error variants
- No permissions needed

**JobScheduler** → `JobHelper`
- `scheduleJob(Activity, int, int) → int`
- `cancelJob(Activity, int) → int`
- `getJobStatus(Activity, int) → int`
- Plus error variants
- No permissions needed

### Permission-only capabilities

These don't generate helper classes — they just inject manifest permissions:
- **Camera** → CAMERA
- **Microphone** → RECORD_AUDIO
- **Audio** → RECORD_AUDIO
- **Video** → CAMERA, RECORD_AUDIO
- **Sensors** → BODY_SENSORS
- **FilePicker** → READ_EXTERNAL_STORAGE
- **Maps** → ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION

## Where this lives in code

- Registry: `dsl/capabilities.py`
- ABI contract: `runtime_abi_v1.md` (now in `docs/`)
- Tests: `tests/test_capabilities.py`, `tests/test_runtime_abi_v1.py`
- Snapshot: `cfg/runtime_abi_snapshot_v1.json`

If you're adding a new capability, you need to update the registry, add the helper class, update the snapshot, and write tests. The CI gates will catch you if you miss any of those.
