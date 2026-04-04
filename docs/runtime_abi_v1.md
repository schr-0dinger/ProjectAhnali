# Ahnali Runtime ABI v1 Contract

ABI version: `1.0.0`

Code constant: `CAPABILITY_RUNTIME_ABI_VERSION = "1.0.0"` (in `dsl/capabilities.py`)

Status: Frozen for v1  
Effective date: 2026-02-16  
Scope: Generated helper/runtime bridge classes emitted by the AOT toolchain.

Related: `docs/capability_runtime_mapping_v1.md` - capability-to-runtime mapping

This document defines the ABI contract for helper classes that connect generated app code to Android runtime callbacks. The frozen signature snapshot lives at `cfg/runtime_abi_snapshot_v1.json`.

## 1) Scope

**In scope:** Wrapper activity bridge, event listener helper classes (`Ahnali*Listener_*`), static ListView adapter helper, `ProgramIR.support_classes` entry schema, frozen helper class/method signature snapshot, capability-to-runtime mapping contract, all Track C Wave 1–18 capability helper ABIs, Program 5 state helper ABI, optional lifecycle bridges, reactive surface guardrail snapshot.

**Out of scope:** Future capability modules beyond those listed, internal compiler IR not emitted into helper Smali, runtime UI diff/recomposition engines.

## 2) Naming Conventions

- Class and method signatures use Smali descriptors.
- Default helper package: `Lcom/ahnali/preview/`.
- Capability helper package: `Lcom/ahnali/runtime/`.
- Suffixes tied to widget IDs are ABI-stable naming patterns.

### Helper class patterns

| Kind | Descriptor Pattern |
|------|-------------------|
| Wrapper activity | `Lcom/ahnali/preview/MainActivity;` (default, configurable) |
| Click listener | `Lcom/ahnali/preview/AhnaliClickListener_<target_id>;` |
| Long-click listener | `Lcom/ahnali/preview/AhnaliLongClickListener_<target_id>;` |
| Change listener | `Lcom/ahnali/preview/AhnaliChangeListener_<target_id>;` |
| Touch listener | `Lcom/ahnali/preview/AhnaliTouchListener_<target_id>;` |
| Double-tap listener | `Lcom/ahnali/preview/AhnaliDoubleTapListener_<target_id>;` |
| Swipe listener | `Lcom/ahnali/preview/AhnaliSwipeListener_<target_id>;` |
| Scroll listener | `Lcom/ahnali/preview/AhnaliScrollListener_<target_id>;` |
| Fling listener | `Lcom/ahnali/preview/AhnaliFlingListener_<target_id>;` |
| Pinch listener | `Lcom/ahnali/preview/AhnaliPinchListener_<target_id>;` |
| Zoom listener | `Lcom/ahnali/preview/AhnaliZoomListener_<target_id>;` |
| Rotate gesture | `Lcom/ahnali/preview/AhnaliRotateGestureListener_<target_id>;` |
| Scale gesture | `Lcom/ahnali/preview/AhnaliScaleGestureListener_<target_id>;` |
| Drag listener | `Lcom/ahnali/preview/AhnaliDragListener_<target_id>;` |
| Drop listener | `Lcom/ahnali/preview/AhnaliDropListener_<target_id>;` |
| Text change | `Lcom/ahnali/preview/AhnaliTextChangeListener_<target_id>;` |
| Item selected | `Lcom/ahnali/preview/AhnaliItemSelectedListener_<target_id>;` |
| Focus change | `Lcom/ahnali/preview/AhnaliFocusChangeListener_<target_id>;` |
| Menu item selected | `Lcom/ahnali/preview/AhnaliMenuItemListener_<target_id>;` |
| Editor action | `Lcom/ahnali/preview/AhnaliEditorActionListener_<target_id>;` |
| Key listener | `Lcom/ahnali/preview/AhnaliKeyListener_<target_id>;` |
| Auto popup click | `Lcom/ahnali/preview/AhnaliClickListener_<popup_id>_popup;` |
| Static list adapter | `Lcom/ahnali/preview/AhnaliListAdapter_<view_id>;` |

## 3) Wrapper Activity ABI

Generated class (default `Lcom/ahnali/preview/MainActivity;`) must expose:

- `.method public constructor <init>()V`
- `.method protected onCreate(Landroid/os/Bundle;)V`

**onCreate contract:** If target signature starts with `()`, wrapper calls `invoke-static {}, <target_desc>->main()V`. Otherwise passes activity instance: `invoke-static {p0}, <target_desc>->main(Landroid/app/Activity;)V`.

**Optional back bridge** (when `onSystemBack` exists):
- `.method public onBackPressed()V` calls `invoke-static {}, <target_desc>->onSystemBack()I`
- Return `1` = handled (suppresses super), `0` = not handled (calls super)

**Optional lifecycle bridges** (emitted when target methods exist):
- `onStart()V`, `onResume()V`, `onPause()V`, `onStop()V`, `onDestroy()V` - each calls `invoke-super` first, then the static lifecycle hook on `target_desc`.

**Target class must provide:** `main()V` or `main(Landroid/app/Activity;)V`, optional `onSystemBack()I`, optional lifecycle hooks.

## 4) Event Listener Helper ABI

All non-adapter listener helpers:
- Extend `Ljava/lang/Object;`
- Implement the matching Android listener interface
- Expose `.method public constructor <init>()V`
- Forward callback arguments to a static handler method on `target_desc`

### Listener kind mapping

| Kind | Interface | Callback method(s) | Target static signature |
|------|-----------|-------------------|------------------------|
| `click` | `View$OnClickListener` | `onClick(View)V` | `<target>(View)V` |
| `long_click` | `View$OnLongClickListener` | `onLongClick(View)Z` | `<target>(View)V` (returns `true`) |
| `touch` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `double_tap` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `swipe` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `scroll` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `fling` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `pinch` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `zoom` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `rotate_gesture` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `scale_gesture_detector` | `View$OnTouchListener` | `onTouch(View;MotionEvent)Z` | `<target>(View;MotionEvent)V` (returns `true`) |
| `drag` | `View$OnDragListener` | `onDrag(View;DragEvent)Z` | `<target>(View;DragEvent)V` (returns `true`) |
| `drop` | `View$OnDragListener` | `onDrag(View;DragEvent)Z` | `<target>(View;DragEvent)V` (returns `true`) |
| `change` | `CompoundButton$OnCheckedChangeListener` | `onCheckedChanged(CompoundButton;Z)V` | `<target>(CompoundButton;Z)V` |
| `slider_change` | `SeekBar$OnSeekBarChangeListener` | `onProgressChanged(SeekBar;IZ)V`, `onStartTrackingTouch`, `onStopTrackingTouch` | `<target>(SeekBar;IZ)V` |
| `radiogroup_change` | `RadioGroup$OnCheckedChangeListener` | `onCheckedChanged(RadioGroup;I)V` | `<target>(RadioGroup;I)V` |
| `text_change` | `TextWatcher` | `beforeTextChanged`, `onTextChanged`, `afterTextChanged(Editable)V` | `<target>(Editable)V` |
| `item_selected` | `AdapterView$OnItemSelectedListener` | `onItemSelected(AdapterView;View;IJ)V`, `onNothingSelected` | `<target>(AdapterView;View;IJ)V` |
| `focus_change` | `View$OnFocusChangeListener` | `onFocusChange(View;Z)V` | `<target>(View;Z)V` |
| `menu_item_selected` | `PopupMenu$OnMenuItemClickListener` | `onMenuItemClick(MenuItem)Z` | `<target>(MenuItem)V` (returns `true`) |
| `editor_action` | `TextView$OnEditorActionListener` | `onEditorAction(TextView;I;KeyEvent)Z` | `<target>(TextView;I;KeyEvent)V` (returns `true`) |
| `key` | `View$OnKeyListener` | `onKey(View;I;KeyEvent)Z` | `<target>(View;I;KeyEvent)V` (returns `true`) |

Handler method names are deterministic: `onClick_<id>`, `onChange_<id>`, `onTextChange_<id>`, `onItemSelected_<id>`, `onFocusChange_<id>`, `onMenuItemSelected_<id>`.

## 5) Static List Adapter ABI

Extends `Landroid/widget/BaseAdapter;` with fields `mInflater:Landroid/view/LayoutInflater;` and `mItems:[Ljava/lang/String;`.

Required methods:
- `constructor <init>(Context;[String)V`
- `getCount()I`, `getItem(I)Object`, `getItemId(I)J`
- `getView(I;View;ViewGroup)View`

Uses deterministic holder pattern via `View.setTag/getTag`. Binds `String` items to `android.R.id.text1` (`0x1020014`) `TextView`.

## 6) `support_classes` Entry ABI

Canonical v1 entry shape: `(class_desc, target_method, target_desc, kind)`

- `class_desc`: emitted helper class descriptor
- `target_method`: static method name on `target_desc` (for `list_adapter`, the decimal/string form of layout resource id)
- `target_desc`: class descriptor containing static callback method
- `kind`: one of `click`, `long_click`, `touch`, `double_tap`, `swipe`, `scroll`, `fling`, `pinch`, `zoom`, `rotate_gesture`, `scale_gesture_detector`, `drag`, `drop`, `editor_action`, `key`, `change`, `slider_change`, `radiogroup_change`, `text_change`, `item_selected`, `focus_change`, `menu_item_selected`, `list_adapter`, `ui_runnable_click`, `http_route_async_worker`

Legacy 2/3-entry tuples are accepted for backward compatibility, but 4-entry form is the stable ABI.

## 7) Versioning

Model: `MAJOR.MINOR.PATCH`.

**MAJOR** (breaking): renaming/removing helper class patterns, changing method descriptors, changing callback interface implementations, changing `onSystemBack()I` semantics, removing accepted `kind` values.

**MINOR** (additive): new helper kind with new class pattern, new optional helper class that doesn't modify existing signatures, new optional methods.

**PATCH** (non-ABI): internal refactors, performance changes, documentation clarifications.

Deprecation: any planned removal/rename must be announced in docs first and preserved for at least one MINOR cycle before MAJOR removal.

## 8) Capability Helper ABI Reference

All capability helpers follow the pattern: methods take `Landroid/app/Activity;` as the first argument and return `I` (status code) or `Ljava/lang/String;` (value with fallback). Return semantics are deterministic - `1` typically means success, `0` means failure, with specific error codes documented per helper.

### 8.1 Wave 1: URLLauncher, Connectivity, Storage

| Helper | Method | Signature |
|--------|--------|-----------|
| `UrlLauncherHelper` | `openUrl` | `(Activity;String)I` |
| `ConnectivityHelper` | `isConnected` | `(Activity)I` |
| `StorageHelper` | `putString` | `(Activity;String;String)I` |
| `StorageHelper` | `getString` | `(Activity;String;String)String` |
| `StorageHelper` | `remove` | `(Activity;String)I` |
| `StorageHelper` | `exists` | `(Activity;String)I` |
| `StorageHelper` | `clear` | `(Activity)I` |

Storage also provides `dataStore*`, `file*`, `sqlite*`, `room*`, `encrypted*` backend variants with the same signature shapes, scoped to backend-specific namespaces.

### 8.2 Wave 2: Networking (HttpHelper)

| Method | Signature |
|--------|-----------|
| `httpGet` | `(Activity;String;String)String` |
| `httpGetStatus` | `(Activity;String)I` |
| `httpGetError` | `(Activity;String)I` |
| `httpGetWithTimeout` | `(Activity;String;String;I)String` |
| `httpGetStatusWithTimeout` | `(Activity;String;I)I` |
| `httpGetErrorWithTimeout` | `(Activity;String;I)I` |
| `httpRequestWithTimeout` | `(Activity;String;String;String;String;I)String` |
| `httpRequestStatusWithTimeout` | `(Activity;String;String;String;I)I` |
| `httpRequestErrorWithTimeout` | `(Activity;String;String;String;I)I` |
| `httpGetRetry` | `(Activity;String;II;String)String` |
| `httpGetJsonField` | `(Activity;String;String;String)String` |
| `httpGetJsonFieldError` | `(Activity;String;String)I` |

Error codes: `0` = success, `1` = invalid input, `2` = transport exception, `3` = non-200 HTTP status, `4` = empty body.

JSON field error codes extend the above: `5` = malformed JSON, `6` = missing key.

### 8.3 Waves 3–4: Async Networking (HttpHelper)

| Method | Signature |
|--------|-----------|
| `nextAsyncToken` | `()I` |
| `getCurrentAsyncToken` | `()I` |
| `startAsync` | `(Runnable)I` |
| `startAsyncWithToken` | `(I;Runnable)I` |
| `cancelAsync` | `()I` and `(I)I` |
| `getAsyncProgress` | `()I` and `(I)I` |
| `getAsyncError` | `()I` and `(I)I` |
| `getAsyncStatus` | `(I)I` |
| `getAsyncBody` | `(I;String)String` |
| `getAsyncJsonField` | `(I;String;String)String` |
| `getAsyncJsonFieldError` | `(I;String)I` |
| `getAsyncJsonArrayLength` | `(II)I` |
| `getAsyncJsonArrayLengthError` | `(I)I` |

Async error codes: `0` = success, `1` = invalid input, `2` = transport exception, `3` = non-200, `4` = empty body, `7` = cancelled, `8` = stale/unknown token.

Support classes: `ui_runnable_click` (Runnable proxy for click handlers), `http_route_async_worker` (background worker with timeout-aware request/status/error, token-scoped cancellation, UI-thread callbacks).

### 8.4 Wave 6: Location

| Helper | Method | Signature |
|--------|--------|-----------|
| `LocationHelper` | `isLocationEnabled` | `(Activity)I` |

Returns `1` when GPS or network provider is enabled, `0` otherwise.

### 8.5 Wave 7: Permissions

| Helper | Method | Signature |
|--------|--------|-----------|
| `PermissionHelper` | `isGranted` | `(Activity;String)I` |

Returns `1` if granted, `0` if denied/null/exception.

### 8.6 Wave 8: Notifications

| Helper | Method | Signature |
|--------|--------|-----------|
| `NotificationHelper` | `createChannel` | `(Activity;String;String)I` |
| `NotificationHelper` | `postNotification` | `(Activity;String;String;String)I` |
| `NotificationHelper` | `postNotificationError` | `(Activity;String;String;String)I` |

`createChannel`: `0` success, `1` invalid args, `3` channel/service failure, `4` exception.  
`postNotification`: `1` success, `0` failure.  
`postNotificationError`: `0` success, `1` invalid args, `2` permission denied (SDK ≥ 33), `3` channel failure, `4` exception.

### 8.7 Wave 9: Clipboard

| Helper | Method | Signature |
|--------|--------|-----------|
| `ClipboardHelper` | `setText` | `(Activity;String)I` |
| `ClipboardHelper` | `getText` | `(Activity;String)String` |

`setText`: `1` success, `0` failure. `getText`: clipboard text when present, fallback argument otherwise.

### 8.8 Wave 10: Sharing/Intents

| Helper | Method | Signature |
|--------|--------|-----------|
| `ShareHelper` | `shareText` | `(Activity;String;String)I` |
| `ShareHelper` | `shareTextError` | `(Activity;String;String)I` |
| `ShareHelper` | `openUri` | `(Activity;String)I` |
| `ShareHelper` | `openUriError` | `(Activity;String)I` |

Error codes: `0` success, `1` invalid args, `3` no handler/activity not found, `4` exception.

### 8.9 Wave 11: WebView

| Helper | Method | Signature |
|--------|--------|-----------|
| `WebHelper` | `setPolicy` | `(Activity;IIII)I` |
| `WebHelper` | `loadUrl` | `(Activity;String)I` |
| `WebHelper` | `loadUrlError` | `(Activity;String)I` |

`loadUrlError`: `0` success, `1` invalid args, `2` cleartext blocked, `3` missing WebSettings, `4` exception.

### 8.10 Wave 12: Web JS Bridge

| Helper | Method | Signature |
|--------|--------|-----------|
| `WebHelper` | `addJsBridge` | `(Activity;String)I` |
| `WebHelper` | `addJsBridgeError` | `(Activity;String)I` |

`addJsBridgeError`: `0` success, `1` invalid args, `2` JS blocked by policy, `3` missing WebSettings, `4` exception, `5` bridge name policy violation (must start with `ahnali_`).

### 8.11 Wave 13: Web File Chooser + Cookies

| Helper | Method | Signature |
|--------|--------|-----------|
| `WebHelper` | `chooseFile` | `(Activity;String)I` |
| `WebHelper` | `chooseFileError` | `(Activity;String)I` |
| `WebHelper` | `setCookie` | `(Activity;String;String)I` |
| `WebHelper` | `setCookieError` | `(Activity;String;String)I` |
| `WebHelper` | `getCookie` | `(Activity;String;String)String` |
| `WebHelper` | `getCookieError` | `(Activity;String)I` |

### 8.12 Wave 14: Deep Linking

| Helper | Method | Signature |
|--------|--------|-----------|
| `DeepLinkHelper` | `getLaunchUri` | `(Activity)String` |
| `DeepLinkHelper` | `getLaunchUriError` | `(Activity)I` |

### 8.13 Wave 15: WorkManager

| Helper | Method | Signature |
|--------|--------|-----------|
| `WorkHelper` | `enqueueWork` | `(Activity;String;I)I` |
| `WorkHelper` | `enqueueWorkError` | `(Activity;String;I)I` |
| `WorkHelper` | `cancelWork` | `(Activity;String)I` |
| `WorkHelper` | `cancelWorkError` | `(Activity;String)I` |
| `WorkHelper` | `getWorkStatus` | `(Activity;String)I` |
| `WorkHelper` | `getWorkStatusError` | `(Activity;String)I` |

### 8.14 Wave 16: AlarmManager

| Helper | Method | Signature |
|--------|--------|-----------|
| `AlarmHelper` | `scheduleAlarm` | `(Activity;String;I)I` |
| `AlarmHelper` | `scheduleAlarmError` | `(Activity;String;I)I` |
| `AlarmHelper` | `cancelAlarm` | `(Activity;String)I` |
| `AlarmHelper` | `cancelAlarmError` | `(Activity;String)I` |
| `AlarmHelper` | `getAlarmStatus` | `(Activity;String)I` |
| `AlarmHelper` | `getAlarmStatusError` | `(Activity;String)I` |

### 8.15 Wave 17: JobScheduler

| Helper | Method | Signature |
|--------|--------|-----------|
| `JobHelper` | `scheduleJob` | `(Activity;II)I` |
| `JobHelper` | `scheduleJobError` | `(Activity;II)I` |
| `JobHelper` | `cancelJob` | `(Activity;I)I` |
| `JobHelper` | `cancelJobError` | `(Activity;I)I` |
| `JobHelper` | `getJobStatus` | `(Activity;I)I` |
| `JobHelper` | `getJobStatusError` | `(Activity;I)I` |

API-level guard: SDK < 21 returns explicit unsupported code from `*Error` methods.

### 8.16 Wave 18: Sharing Completion

| Helper | Method | Signature |
|--------|--------|-----------|
| `ShareHelper` | `shareFile` | `(Activity;String;String;String)I` |
| `ShareHelper` | `shareFileError` | `(Activity;String;String;String)I` |

## 9) Conformance References

**Tests:** `tests/test_runtime_abi_v1.py`, `tests/test_runtime_abi_snapshot.py`, `tests/test_capabilities.py`, `tests/test_track_c_wave{2..18}_*.py`, `tests/test_program5_*.py`, `tests/test_support_click_listener.py`, `tests/test_event_surface_listeners.py`, `tests/test_navigation_stack.py`, `tests/test_omega_toolchain_scaffold.py`, `tests/test_list_view_static.py`, `tests/test_http_helper_device_integration.py`.

**ABI drift guard:** `tools/runtime_abi_snapshot.py` generates/checks against `cfg/runtime_abi_snapshot_v1.json`. CI gate in `.github/workflows/ci.yml` step `Check runtime ABI snapshot`.

**Reactive guardrail:** `tools/reactive_surface_snapshot.py` checks against `cfg/reactive_surface_snapshot_v1.json`. CI gate `Check reactive surface snapshot`.
