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
- Track C Wave 1 introduced initial helper-call bindings for URL launcher, connectivity checks, and storage put/get/remove/exists/clear.
- Track C Wave 2 adds networking fetch/response/retry/typed-JSON helper-call bindings (`http_get`, `http_get_status`, `http_get_error`, `http_get_retry`, `http_get_json_field`, `http_get_json_field_error`).
- Track C Wave 3/4 adds tokened async route dispatch (`http_get_route_async`) with deterministic cancellation/progress/error/status/body surfaces (`http_async_cancel`, `http_async_progress`, `http_async_error`, `http_async_status`, `http_async_body`), progress callback wiring, timeout/retry controls, request-option wiring (method/headers/body), hardened request-option transport semantics (header parsing/application + explicit POST body transport), typed async JSON adapters, and concurrent cancellation/race stress coverage.
- Track C Wave 6 adds location provider helper-call binding (`location_enabled`, `check_location`) with deterministic enabled/disabled surface.
- Track C Wave 7 adds permissions helper-call binding (`permission_granted`, `check_permission`) with deterministic granted/denied surface.
- Track C Wave 8 adds notifications/channels helper-call binding (`create_notification_channel`, `notify`, `notify_result`, `notify_error`) with deterministic delivery and error-code surface.
- Track C Wave 9 adds clipboard helper-call binding (`clipboard_set`, `clipboard_get`) with deterministic set/get fallback surface.
- Track C Wave 10 adds sharing/intents helper-call binding (`share_text`, `share_text_result`, `share_text_error`, `open_external`, `open_external_error`) with deterministic success/error surfaces.
- Track C Wave 11 adds WebView helper-call binding (`web_set_policy`, `web_load`, `web_load_result`, `web_load_error`) with deterministic policy/error surfaces.
- Track C Wave 12 adds Web JS bridge helper-call binding (`web_add_js_bridge`, `web_add_js_bridge_result`, `web_add_js_bridge_error`) with deterministic policy-constrained error surfaces.
- Track C Wave 13 adds Web file chooser/cookie helper-call bindings (`web_choose_file`, `web_choose_file_result`, `web_choose_file_error`, `web_cookie_set`, `web_cookie_set_result`, `web_cookie_set_error`, `web_cookie_get`, `web_cookie_get_error`) with deterministic chooser/cookie surfaces.
- Track C Wave 14 adds deep-link helper-call bindings (`deep_link_get`, `deep_link_error`) with deterministic launch-intent fallback/error surfaces.
- Track C Wave 15 adds WorkManager-style helper-call bindings (`work_enqueue`, `work_cancel`, `work_status`, `work_error`) with deterministic enqueue/cancel/status/error surfaces.
- Track C Wave 16 adds AlarmManager-style helper-call bindings (`alarm_schedule`, `alarm_cancel`, `alarm_status`, `alarm_error`) with deterministic schedule/cancel/status/error surfaces.
- Track C Wave 17 adds JobScheduler-style helper-call bindings (`job_schedule`, `job_cancel`, `job_status`, `job_error`) with deterministic API-level-guarded schedule/cancel/status/error surfaces.
- Program 5 extends `StorageHelper` with deterministic backend-specific surfaces for DataStore/file/SQLite/Room/encrypted storage.

## Mapping Table (v1)

| Canonical Capability | Accepted Aliases | Permissions | Runtime Helper Class | Runtime Helper Method/Sig | Mode |
|---|---|---|---|---|---|
| `Camera` | `Camera` | `android.permission.CAMERA` | n/a | n/a | `permission_only` |
| `Microphone` | `Microphone` | `android.permission.RECORD_AUDIO` | n/a | n/a | `permission_only` |
| `Audio` | `Audio` | `android.permission.RECORD_AUDIO` | n/a | n/a | `permission_only` |
| `Video` | `Video` | `android.permission.CAMERA`, `android.permission.RECORD_AUDIO` | n/a | n/a | `permission_only` |
| `WebView` | `WebView`, `Web` | `android.permission.INTERNET` | `Lcom/ahnali/runtime/WebHelper;` | `setPolicy(Landroid/app/Activity;IIII)I`, `loadUrl(Landroid/app/Activity;Ljava/lang/String;)I`, `loadUrlError(Landroid/app/Activity;Ljava/lang/String;)I`, `addJsBridge(Landroid/app/Activity;Ljava/lang/String;)I`, `addJsBridgeError(Landroid/app/Activity;Ljava/lang/String;)I`, `chooseFile(Landroid/app/Activity;Ljava/lang/String;)I`, `chooseFileError(Landroid/app/Activity;Ljava/lang/String;)I`, `setCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`, `setCookieError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`, `getCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`, `getCookieError(Landroid/app/Activity;Ljava/lang/String;)I` | `helper_call` |
| `Sensors` | `Sensors` | `android.permission.BODY_SENSORS` | n/a | n/a | `permission_only` |
| `Storage` | `Storage` | `android.permission.READ_EXTERNAL_STORAGE`, `android.permission.WRITE_EXTERNAL_STORAGE` | `Lcom/ahnali/runtime/StorageHelper;` | `putString(...)`, `getString(...)`, `remove(...)`, `exists(...)`, `clear(...)`, `dataStorePutString(...)`, `dataStoreGetString(...)`, `dataStoreRemove(...)`, `dataStoreExists(...)`, `dataStoreClear(...)`, `fileWriteString(...)`, `fileReadString(...)`, `fileRemove(...)`, `fileExists(...)`, `fileClear(...)`, `sqlitePutString(...)`, `sqliteGetString(...)`, `sqliteRemove(...)`, `sqliteExists(...)`, `sqliteClear(...)`, `roomPutString(...)`, `roomGetString(...)`, `roomRemove(...)`, `roomExists(...)`, `roomClear(...)`, `encryptedPutString(...)`, `encryptedGetString(...)`, `encryptedRemove(...)`, `encryptedExists(...)`, `encryptedClear(...)` | `helper_call` |
| `FilePicker` | `FilePicker`, `File Picker` | `android.permission.READ_EXTERNAL_STORAGE` | n/a | n/a | `permission_only` |
| `Clipboard` | `Clipboard` | none | `Lcom/ahnali/runtime/ClipboardHelper;` | `setText(Landroid/app/Activity;Ljava/lang/String;)I`, `getText(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;` | `helper_call` |
| `Connectivity` | `Connectivity` | `android.permission.ACCESS_NETWORK_STATE`, `android.permission.INTERNET` | `Lcom/ahnali/runtime/ConnectivityHelper;` | `isConnected(Landroid/app/Activity;)I` | `helper_call` |
| `Networking` | `Networking`, `Network` | `android.permission.INTERNET` | `Lcom/ahnali/runtime/HttpHelper;` | `httpGet(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`, `httpGetStatus(Landroid/app/Activity;Ljava/lang/String;)I`, `httpGetError(Landroid/app/Activity;Ljava/lang/String;)I`, `httpGetWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;`, `httpGetStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;I)I`, `httpGetErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;I)I`, `httpRequestWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;`, `httpRequestStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I`, `httpRequestErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I`, `httpGetRetry(Landroid/app/Activity;Ljava/lang/String;IILjava/lang/String;)Ljava/lang/String;`, `httpGetJsonField(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`, `httpGetJsonFieldError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`, `nextAsyncToken()I`, `getCurrentAsyncToken()I`, `startAsync(Ljava/lang/Runnable;)I`, `startAsyncWithToken(ILjava/lang/Runnable;)I`, `cancelAsync(I)I`, `getAsyncProgress(I)I`, `getAsyncError(I)I`, `getAsyncStatus(I)I`, `getAsyncBody(ILjava/lang/String;)Ljava/lang/String;`, `getAsyncJsonField(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;`, `getAsyncJsonFieldError(ILjava/lang/String;)I`, `getAsyncJsonArrayLength(II)I`, `getAsyncJsonArrayLengthError(I)I` | `helper_call` |
| `Notifications` | `Notifications`, `Notification` | `android.permission.POST_NOTIFICATIONS` | `Lcom/ahnali/runtime/NotificationHelper;` | `createChannel(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`, `postNotification(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I`, `postNotificationError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I` | `helper_call` |
| `URLLauncher` | `URLLauncher`, `URL launcher` | `android.permission.INTERNET` | `Lcom/ahnali/runtime/UrlLauncherHelper;` | `openUrl(Landroid/app/Activity;Ljava/lang/String;)I` | `helper_call` |
| `Permissions` | `Permissions` | none | `Lcom/ahnali/runtime/PermissionHelper;` | `isGranted(Landroid/app/Activity;Ljava/lang/String;)I` | `helper_call` |
| `Sharing` | `Sharing`, `Intents`, `Share` | none | `Lcom/ahnali/runtime/ShareHelper;` | `shareText(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`, `shareTextError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`, `openUri(Landroid/app/Activity;Ljava/lang/String;)I`, `openUriError(Landroid/app/Activity;Ljava/lang/String;)I` | `helper_call` |
| `DeepLinking` | `DeepLinking`, `DeepLink`, `Deep Links` | none | `Lcom/ahnali/runtime/DeepLinkHelper;` | `getLaunchUri(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;`, `getLaunchUriError(Landroid/app/Activity;)I` | `helper_call` |
| `WorkManager` | `WorkManager`, `Work`, `BackgroundWork` | none | `Lcom/ahnali/runtime/WorkHelper;` | `enqueueWork(Landroid/app/Activity;Ljava/lang/String;I)I`, `enqueueWorkError(Landroid/app/Activity;Ljava/lang/String;I)I`, `cancelWork(Landroid/app/Activity;Ljava/lang/String;)I`, `cancelWorkError(Landroid/app/Activity;Ljava/lang/String;)I`, `getWorkStatus(Landroid/app/Activity;Ljava/lang/String;)I`, `getWorkStatusError(Landroid/app/Activity;Ljava/lang/String;)I` | `helper_call` |
| `AlarmManager` | `AlarmManager`, `Alarms`, `Alarm` | none | `Lcom/ahnali/runtime/AlarmHelper;` | `scheduleAlarm(Landroid/app/Activity;Ljava/lang/String;I)I`, `scheduleAlarmError(Landroid/app/Activity;Ljava/lang/String;I)I`, `cancelAlarm(Landroid/app/Activity;Ljava/lang/String;)I`, `cancelAlarmError(Landroid/app/Activity;Ljava/lang/String;)I`, `getAlarmStatus(Landroid/app/Activity;Ljava/lang/String;)I`, `getAlarmStatusError(Landroid/app/Activity;Ljava/lang/String;)I` | `helper_call` |
| `JobScheduler` | `JobScheduler`, `Jobs`, `Job` | none | `Lcom/ahnali/runtime/JobHelper;` | `scheduleJob(Landroid/app/Activity;II)I`, `scheduleJobError(Landroid/app/Activity;II)I`, `cancelJob(Landroid/app/Activity;I)I`, `cancelJobError(Landroid/app/Activity;I)I`, `getJobStatus(Landroid/app/Activity;I)I`, `getJobStatusError(Landroid/app/Activity;I)I` | `helper_call` |
| `Maps` | `Maps` | `android.permission.ACCESS_FINE_LOCATION`, `android.permission.ACCESS_COARSE_LOCATION` | n/a | n/a | `permission_only` |
| `Location` | `Location` | `android.permission.ACCESS_FINE_LOCATION`, `android.permission.ACCESS_COARSE_LOCATION` | `Lcom/ahnali/runtime/LocationHelper;` | `isLocationEnabled(Landroid/app/Activity;)I` | `helper_call` |

### StorageHelper Program 5 Signatures

- Base storage:
  - `putString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `getString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
  - `remove(Landroid/app/Activity;Ljava/lang/String;)I`
  - `exists(Landroid/app/Activity;Ljava/lang/String;)I`
  - `clear(Landroid/app/Activity;)I`
- DataStore:
  - `dataStorePutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `dataStoreGetString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
  - `dataStoreRemove(Landroid/app/Activity;Ljava/lang/String;)I`
  - `dataStoreExists(Landroid/app/Activity;Ljava/lang/String;)I`
  - `dataStoreClear(Landroid/app/Activity;)I`
- File:
  - `fileWriteString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `fileReadString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
  - `fileRemove(Landroid/app/Activity;Ljava/lang/String;)I`
  - `fileExists(Landroid/app/Activity;Ljava/lang/String;)I`
  - `fileClear(Landroid/app/Activity;)I`
- SQLite:
  - `sqlitePutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `sqliteGetString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
  - `sqliteRemove(Landroid/app/Activity;Ljava/lang/String;)I`
  - `sqliteExists(Landroid/app/Activity;Ljava/lang/String;)I`
  - `sqliteClear(Landroid/app/Activity;)I`
- Room:
  - `roomPutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `roomGetString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
  - `roomRemove(Landroid/app/Activity;Ljava/lang/String;)I`
  - `roomExists(Landroid/app/Activity;Ljava/lang/String;)I`
  - `roomClear(Landroid/app/Activity;)I`
- Encrypted:
  - `encryptedPutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `encryptedGetString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
  - `encryptedRemove(Landroid/app/Activity;Ljava/lang/String;)I`
  - `encryptedExists(Landroid/app/Activity;Ljava/lang/String;)I`
  - `encryptedClear(Landroid/app/Activity;)I`

## Source of Truth in Code

- Registry and mapping model: `dsl/capabilities.py`
- ABI contract for generated helper bridge classes: `runtime_abi_v1.md`

## Conformance

- Mapping/runtime-binding tests: `tests/test_capabilities.py`
- ABI contract tests: `tests/test_runtime_abi_v1.py`
