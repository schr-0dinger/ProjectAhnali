# Ahnali Runtime ABI v1 Contract

Status: Frozen for v1  
Effective date: 2026-02-16  
Scope: Generated helper/runtime bridge classes emitted by the current AOT toolchain.

This document defines the ABI contract for helper classes that connect generated app code to Android runtime callbacks.

## 1) Scope and Non-Scope

In scope:
- Wrapper Activity bridge (`MainActivity`-style generated class)
- Event listener helper classes (`Ahnali*Listener_*`)
- Static ListView adapter helper class (`AhnaliListAdapter_*`)
- `ProgramIR.support_classes` entry schema used by toolchain emission
- Frozen helper class/method signature snapshot (`cfg/runtime_abi_snapshot_v1.json`)
- Capability-to-runtime mapping contract for registered capabilities
- Track C Wave 1 capability helper ABI: URL launcher + connectivity + storage helpers
- Track C Wave 2 capability helper ABI: networking fetch/response/routing/retry/typed-JSON helpers
- Track C Wave 3/4 capability helper ABI: tokened async route dispatch + deterministic cancellation/progress/error/status/body helper methods + runnable support classes + timeout/retry controls + request-option and typed async JSON adapter helpers
- Track C Wave 6 capability helper ABI: location provider enabled surface
- Track C Wave 7 capability helper ABI: permissions granted surface
- Program 5 state helper ABI: deterministic DataStore/file/SQLite/Room/encrypted storage surfaces
- Optional wrapper lifecycle bridges: `onStart/onResume/onPause/onStop/onDestroy`

Out of scope:
- Future capability module helper APIs beyond URL launcher/connectivity/storage/networking/location/permissions fetch/response/routing/retry/typed-JSON/tokened-async/request-options helpers (network/storage/location/permissions wave expansion planned separately)
- Internal compiler IR structures that are not emitted into helper Smali classes

## 2) Descriptor and Naming Conventions

- Class and method signatures use Smali descriptors.
- Default helper package is `Lcom/ahnali/preview/`.
- Suffixes tied to widget ids are ABI-stable naming patterns.

Stable helper class descriptor patterns:
- Wrapper activity: `Lcom/ahnali/preview/MainActivity;` (default; configurable)
- Click listener: `Lcom/ahnali/preview/AhnaliClickListener_<target_id>;`
- Long-click listener: `Lcom/ahnali/preview/AhnaliLongClickListener_<target_id>;`
- Toggle/radio/switch change listener: `Lcom/ahnali/preview/AhnaliChangeListener_<target_id>;`
- Touch listener: `Lcom/ahnali/preview/AhnaliTouchListener_<target_id>;`
- Double-tap listener: `Lcom/ahnali/preview/AhnaliDoubleTapListener_<target_id>;`
- Swipe listener: `Lcom/ahnali/preview/AhnaliSwipeListener_<target_id>;`
- Scroll listener: `Lcom/ahnali/preview/AhnaliScrollListener_<target_id>;`
- Fling listener: `Lcom/ahnali/preview/AhnaliFlingListener_<target_id>;`
- Pinch listener: `Lcom/ahnali/preview/AhnaliPinchListener_<target_id>;`
- Zoom listener: `Lcom/ahnali/preview/AhnaliZoomListener_<target_id>;`
- Rotate gesture listener: `Lcom/ahnali/preview/AhnaliRotateGestureListener_<target_id>;`
- Scale gesture listener: `Lcom/ahnali/preview/AhnaliScaleGestureListener_<target_id>;`
- Drag listener: `Lcom/ahnali/preview/AhnaliDragListener_<target_id>;`
- Drop listener: `Lcom/ahnali/preview/AhnaliDropListener_<target_id>;`
- Text change listener: `Lcom/ahnali/preview/AhnaliTextChangeListener_<target_id>;`
- Item selected listener: `Lcom/ahnali/preview/AhnaliItemSelectedListener_<target_id>;`
- Focus change listener: `Lcom/ahnali/preview/AhnaliFocusChangeListener_<target_id>;`
- Popup menu item selected listener: `Lcom/ahnali/preview/AhnaliMenuItemListener_<target_id>;`
- Editor action listener: `Lcom/ahnali/preview/AhnaliEditorActionListener_<target_id>;`
- Key listener: `Lcom/ahnali/preview/AhnaliKeyListener_<target_id>;`
- Auto popup click listener: `Lcom/ahnali/preview/AhnaliClickListener_<popup_id>_popup;`
- Static list adapter: `Lcom/ahnali/preview/AhnaliListAdapter_<view_id>;`

## 3) Wrapper Activity ABI

Generated class (default descriptor `Lcom/ahnali/preview/MainActivity;`) must expose:

- `.method public constructor <init>()V`
- `.method protected onCreate(Landroid/os/Bundle;)V`

`onCreate` invocation contract:
- If target signature starts with `()`, wrapper calls: `invoke-static {}, <target_desc>->main()V`
- Otherwise wrapper passes activity instance: `invoke-static {p0}, <target_desc>->main(Landroid/app/Activity;)V`

Optional back bridge (enabled when `onSystemBack` exists and wrapper bridge is emitted):
- `.method public onBackPressed()V`
- Must call: `invoke-static {}, <target_desc>->onSystemBack()I`
- Return semantics: `1` means "handled" and suppresses `invoke-super ... onBackPressed()V`; `0` means "not handled" and wrapper must call `invoke-super ... onBackPressed()V`

Optional lifecycle bridges (emitted when target methods exist):
- `.method protected onStart()V` calling `invoke-static {}, <target_desc>->onStart()V`
- `.method protected onResume()V` calling `invoke-static {}, <target_desc>->onResume()V`
- `.method protected onPause()V` calling `invoke-static {}, <target_desc>->onPause()V`
- `.method protected onStop()V` calling `invoke-static {}, <target_desc>->onStop()V`
- `.method protected onDestroy()V` calling `invoke-static {}, <target_desc>->onDestroy()V`
- Current v1 ordering is deterministic: wrapper calls `invoke-super ...` first, then static lifecycle hook.

Target class ABI required by wrapper:
- `main()V` or `main(Landroid/app/Activity;)V` (selected by configured wrapper target signature)
- Optional `onSystemBack()I` when back bridge is enabled
- Optional lifecycle hook methods when lifecycle bridges are enabled:
  - `onStart()V`, `onResume()V`, `onPause()V`, `onStop()V`, `onDestroy()V`

## 4) Event Listener Helper ABI

All non-adapter listener helper classes must:
- Extend `Ljava/lang/Object;`
- Implement the matching Android listener interface
- Expose `.method public constructor <init>()V`
- Forward callback arguments to a static handler method on `target_desc`

Stable listener-kind mapping:

| Kind | Interface | Required callback methods | Target static method signature |
|---|---|---|---|
| `click` | `Landroid/view/View$OnClickListener;` | `onClick(Landroid/view/View;)V` | `<target_method>(Landroid/view/View;)V` |
| `long_click` | `Landroid/view/View$OnLongClickListener;` | `onLongClick(Landroid/view/View;)Z` | `<target_method>(Landroid/view/View;)V` and listener returns constant `true` |
| `touch` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `double_tap` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `swipe` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `scroll` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `fling` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `pinch` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `zoom` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `rotate_gesture` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `scale_gesture_detector` | `Landroid/view/View$OnTouchListener;` | `onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/MotionEvent;)V` and listener returns constant `true` |
| `drag` | `Landroid/view/View$OnDragListener;` | `onDrag(Landroid/view/View;Landroid/view/DragEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/DragEvent;)V` and listener returns constant `true` |
| `drop` | `Landroid/view/View$OnDragListener;` | `onDrag(Landroid/view/View;Landroid/view/DragEvent;)Z` | `<target_method>(Landroid/view/View;Landroid/view/DragEvent;)V` and listener returns constant `true` |
| `change` | `Landroid/widget/CompoundButton$OnCheckedChangeListener;` | `onCheckedChanged(Landroid/widget/CompoundButton;Z)V` | `<target_method>(Landroid/widget/CompoundButton;Z)V` |
| `slider_change` | `Landroid/widget/SeekBar$OnSeekBarChangeListener;` | `onProgressChanged(Landroid/widget/SeekBar;IZ)V`, `onStartTrackingTouch(Landroid/widget/SeekBar;)V`, `onStopTrackingTouch(Landroid/widget/SeekBar;)V` | `<target_method>(Landroid/widget/SeekBar;IZ)V` |
| `radiogroup_change` | `Landroid/widget/RadioGroup$OnCheckedChangeListener;` | `onCheckedChanged(Landroid/widget/RadioGroup;I)V` | `<target_method>(Landroid/widget/RadioGroup;I)V` |
| `text_change` | `Landroid/text/TextWatcher;` | `beforeTextChanged(Ljava/lang/CharSequence;III)V`, `onTextChanged(Ljava/lang/CharSequence;III)V`, `afterTextChanged(Landroid/text/Editable;)V` | `<target_method>(Landroid/text/Editable;)V` |
| `item_selected` | `Landroid/widget/AdapterView$OnItemSelectedListener;` | `onItemSelected(Landroid/widget/AdapterView;Landroid/view/View;IJ)V`, `onNothingSelected(Landroid/widget/AdapterView;)V` | `<target_method>(Landroid/widget/AdapterView;Landroid/view/View;IJ)V` |
| `focus_change` | `Landroid/view/View$OnFocusChangeListener;` | `onFocusChange(Landroid/view/View;Z)V` | `<target_method>(Landroid/view/View;Z)V` |
| `menu_item_selected` | `Landroid/widget/PopupMenu$OnMenuItemClickListener;` | `onMenuItemClick(Landroid/view/MenuItem;)Z` | `<target_method>(Landroid/view/MenuItem;)V` and listener returns constant `true` |
| `editor_action` | `Landroid/widget/TextView$OnEditorActionListener;` | `onEditorAction(Landroid/widget/TextView;ILandroid/view/KeyEvent;)Z` | `<target_method>(Landroid/widget/TextView;ILandroid/view/KeyEvent;)V` and listener returns constant `true` |
| `key` | `Landroid/view/View$OnKeyListener;` | `onKey(Landroid/view/View;ILandroid/view/KeyEvent;)Z` | `<target_method>(Landroid/view/View;ILandroid/view/KeyEvent;)V` and listener returns constant `true` |

Handler owner contract:
- In pythonic DSL lowering, target handler owner is typically `LTestHandlers;`.
- Handler method names are deterministic: `onClick_<id>`, `onChange_<id>`, `onTextChange_<id>`, `onItemSelected_<id>`, `onFocusChange_<id>`, `onMenuItemSelected_<id>`

## 5) Static List Adapter Helper ABI

`list_adapter` kind emits a class that:
- Extends `Landroid/widget/BaseAdapter;`
- Declares fields: `mInflater:Landroid/view/LayoutInflater;`, `mItems:[Ljava/lang/String;`

Required methods:
- `.method public constructor <init>(Landroid/content/Context;[Ljava/lang/String;)V`
- `.method public getCount()I`
- `.method public getItem(I)Ljava/lang/Object;`
- `.method public getItemId(I)J`
- `.method public getView(ILandroid/view/View;Landroid/view/ViewGroup;)Landroid/view/View;`

Behavior contract:
- Uses deterministic holder pattern via `View.setTag/getTag`
- Binds `String` item values to `android.R.id.text1` (`0x1020014`) `TextView`
- Uses deterministic item layout resource id passed through support-class metadata

## 6) `support_classes` Entry ABI

Canonical v1 entry shape:
- `(class_desc, target_method, target_desc, kind)`

Where:
- `class_desc`: emitted helper class descriptor
- `target_method`: static method name on `target_desc`  
  For `list_adapter`, this is the decimal/string form of layout resource id.
- `target_desc`: class descriptor containing static callback method
- `kind`: one of `click`, `long_click`, `touch`, `double_tap`, `swipe`, `scroll`, `fling`, `pinch`, `zoom`, `rotate_gesture`, `scale_gesture_detector`, `drag`, `drop`, `editor_action`, `key`, `change`, `slider_change`, `radiogroup_change`, `text_change`, `item_selected`, `focus_change`, `menu_item_selected`, `list_adapter`, `ui_runnable_click`, `http_route_async_worker`

Compatibility note:
- Toolchain currently accepts legacy tuple lengths (2/3 entries), but 4-entry form is the stable ABI form for v1.

## 7) Versioning Rules

Versioning model: `MAJOR.MINOR.PATCH`.

`MAJOR` bump required for any breaking ABI change, including:
- Renaming/removing helper class descriptor patterns
- Changing method descriptors (argument or return types)
- Changing callback interface implementations
- Changing `onSystemBack()I` semantic meaning
- Removing accepted `kind` values

`MINOR` bump for additive, backward-compatible changes:
- New helper kind with new class pattern
- New optional helper class that does not modify existing signatures
- New optional methods that do not alter existing callback contracts

`PATCH` bump for non-ABI changes:
- Internal implementation refactors
- Performance changes with unchanged descriptors/signatures/semantics
- Documentation clarifications

Deprecation policy:
- Any planned removal/rename must be announced in docs first and preserved for at least one `MINOR` cycle before a `MAJOR` removal.

## 8) Capability Mapping Companion Contract

- Companion mapping document: `docs/capability_runtime_mapping_v1.md`
- Code source of truth: `dsl/capabilities.py`
- ABI version constant: `CAPABILITY_RUNTIME_ABI_VERSION = "1.0.0"`
- Capability modes are `permission_only` or `helper_call`.
- Track C Wave 1 helper-call binding:
  - Capability: `URLLauncher`
  - Helper class: `Lcom/ahnali/runtime/UrlLauncherHelper;`
  - Helper method/sig: `openUrl(Landroid/app/Activity;Ljava/lang/String;)I`
  - Return semantics: `1` on successful dispatch to `Activity.startActivity`, `0` on null input or caught exception.
- Track C Wave 1 helper-call binding:
  - Capability: `Connectivity`
  - Helper class: `Lcom/ahnali/runtime/ConnectivityHelper;`
  - Helper method/sig: `isConnected(Landroid/app/Activity;)I`
  - Return semantics: `1` when active network is connected, `0` for null context, no active network, or caught exception.
- Track C Wave 1 helper-call binding:
  - Capability: `Storage`
  - Helper class: `Lcom/ahnali/runtime/StorageHelper;`
  - Helper methods/sigs:
    - `putString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
    - `getString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `remove(Landroid/app/Activity;Ljava/lang/String;)I`
    - `exists(Landroid/app/Activity;Ljava/lang/String;)I`
    - `clear(Landroid/app/Activity;)I`
    - `dataStorePutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
    - `dataStoreGetString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `dataStoreRemove(Landroid/app/Activity;Ljava/lang/String;)I`
    - `dataStoreExists(Landroid/app/Activity;Ljava/lang/String;)I`
    - `dataStoreClear(Landroid/app/Activity;)I`
    - `fileWriteString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
    - `fileReadString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `fileRemove(Landroid/app/Activity;Ljava/lang/String;)I`
    - `fileExists(Landroid/app/Activity;Ljava/lang/String;)I`
    - `fileClear(Landroid/app/Activity;)I`
    - `sqlitePutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
    - `sqliteGetString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `sqliteRemove(Landroid/app/Activity;Ljava/lang/String;)I`
    - `sqliteExists(Landroid/app/Activity;Ljava/lang/String;)I`
    - `sqliteClear(Landroid/app/Activity;)I`
    - `roomPutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
    - `roomGetString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `roomRemove(Landroid/app/Activity;Ljava/lang/String;)I`
    - `roomExists(Landroid/app/Activity;Ljava/lang/String;)I`
    - `roomClear(Landroid/app/Activity;)I`
    - `encryptedPutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
    - `encryptedGetString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `encryptedRemove(Landroid/app/Activity;Ljava/lang/String;)I`
    - `encryptedExists(Landroid/app/Activity;Ljava/lang/String;)I`
    - `encryptedClear(Landroid/app/Activity;)I`
  - Return semantics:
    - `putString`: `1` on successful `SharedPreferences` write; `0` on null context/key or caught exception.
    - `getString`: stored value when present; fallback argument on null context/key, missing value, or caught exception.
    - `remove`: `1` on successful `SharedPreferences` remove/apply; `0` on null context/key or caught exception.
    - `exists`: `1` when key exists in `SharedPreferences`; `0` on missing key, null context/key, or caught exception.
    - `clear`: `1` on successful `SharedPreferences` clear/apply; `0` on null context or caught exception.
    - Program 5 backend variants (`dataStore*`, `file*`, `sqlite*`, `room*`, `encrypted*`) keep the same deterministic success/fallback semantics, scoped to backend-specific namespaces.
- Track C Wave 6 helper-call binding:
  - Capability: `Location`
  - Helper class: `Lcom/ahnali/runtime/LocationHelper;`
  - Helper method/sig:
    - `isLocationEnabled(Landroid/app/Activity;)I`
  - Return semantics:
    - `1`: when either `gps` or `network` location provider is enabled
    - `0`: null context, unavailable manager, disabled providers, or caught exception
- Track C Wave 7 helper-call binding:
  - Capability: `Permissions`
  - Helper class: `Lcom/ahnali/runtime/PermissionHelper;`
  - Helper method/sig:
    - `isGranted(Landroid/app/Activity;Ljava/lang/String;)I`
  - Return semantics:
    - `1`: permission is granted
    - `0`: null context, null permission, denied permission, or caught exception
- Track C Wave 2/3 helper-call binding:
  - Capability: `Networking`
  - Helper class: `Lcom/ahnali/runtime/HttpHelper;`
  - Helper methods/sigs:
    - `httpGet(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `httpGetStatus(Landroid/app/Activity;Ljava/lang/String;)I`
    - `httpGetError(Landroid/app/Activity;Ljava/lang/String;)I`
    - `httpGetWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;`
    - `httpGetStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;I)I`
    - `httpGetErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;I)I`
    - `httpRequestWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;`
    - `httpRequestStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I`
    - `httpRequestErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I`
    - `httpGetRetry(Landroid/app/Activity;Ljava/lang/String;IILjava/lang/String;)Ljava/lang/String;`
    - `httpGetJsonField(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `httpGetJsonFieldError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
    - `nextAsyncToken()I`
    - `getCurrentAsyncToken()I`
    - `startAsync(Ljava/lang/Runnable;)I`
    - `startAsyncWithToken(ILjava/lang/Runnable;)I`
    - `cancelAsync()I` and `cancelAsync(I)I`
    - `getAsyncProgress()I` and `getAsyncProgress(I)I`
    - `getAsyncError()I` and `getAsyncError(I)I`
    - `getAsyncStatus(I)I`
    - `getAsyncBody(ILjava/lang/String;)Ljava/lang/String;`
    - `getAsyncJsonField(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
    - `getAsyncJsonFieldError(ILjava/lang/String;)I`
    - `getAsyncJsonArrayLength(II)I`
    - `getAsyncJsonArrayLengthError(I)I`
  - Return semantics:
    - `httpGet`: response body string on HTTP 200 with readable body; fallback argument on null URL, non-200 response, empty body, or caught exception.
    - `httpGetStatus`: HTTP status code when available; `-1` on null URL or caught exception.
    - `httpGetError`: deterministic error code:
      - `0`: success (HTTP 200 with readable non-empty body)
      - `1`: invalid input (null URL)
      - `2`: transport/runtime exception
      - `3`: non-200 HTTP status
      - `4`: empty body
    - `httpGetJsonField`: extracts a deterministic string field value from JSON response body.
      - Returns extracted value when `httpGetJsonFieldError(...) == 0`
      - Returns fallback argument for any non-zero error code
      - Non-string JSON values are stringified via `Object.toString()`
    - `httpGetJsonFieldError`: deterministic JSON extraction error code:
      - `0`: success (HTTP success + parseable JSON + key present and non-null)
      - `1`: invalid input (null URL or null key)
      - `2`: transport/runtime exception
      - `3`: non-200 HTTP status
      - `4`: empty body
      - `5`: malformed JSON payload
      - `6`: missing key (or key value is JSON null)
    - `httpGetRetry`: retries deterministic fetch attempts and returns response body on first success, else fallback.
      - Success condition: `httpGetError(...) == 0`
      - Retry policy: total attempts = `max(0, retries) + 1`
      - Backoff policy: fixed sleep `max(0, backoff_ms)` between failed attempts (no jitter)
    - `httpRequest*WithTimeout`:
      - Request options accept method/header/body surfaces for async route worker ABI.
      - Method semantics:
        - null/empty method defaults to `GET`
        - supported deterministic method set is `GET`/`POST` (case-insensitive)
        - any other method returns deterministic invalid-input surfaces (`fallback` for body call, `-1` for status, `1` for error)
      - Header semantics:
        - newline-delimited header entries are parsed as `Key: Value`
        - malformed/empty entries are ignored deterministically
        - parsed entries are applied via `HttpURLConnection.setRequestProperty(...)`
      - Body semantics:
        - body is explicitly transported only for `POST`
        - body bytes are encoded UTF-8 and written through `HttpURLConnection` output stream with fixed-length streaming mode
        - non-POST methods do not emit request body bytes
    - `nextAsyncToken`: allocates and returns a positive token, resets token-scoped async state.
    - `startAsync`: allocates a token and starts a background thread for a provided `Runnable`.
      - Returns token (`>0`) when dispatch succeeds
      - Returns `0` for null runnable or caught exception during dispatch
    - `startAsyncWithToken`: starts background thread for provided token/runnable pair.
      - Returns same token on success
      - Returns `0` for invalid token, null runnable, or caught exception
    - `cancelAsync(I)`: token-scoped cancellation request.
      - Returns `1` when token exists and cancellation is recorded; else `0`.
    - `getAsyncProgress(I)`: token-scoped deterministic progress (`0..100`); returns `0` on unknown token.
    - `getAsyncError(I)`: token-scoped deterministic async error code:
      - `0`: success
      - `1`: invalid input
      - `2`: transport/runtime exception
      - `3`: non-200 HTTP status
      - `4`: empty body
      - `7`: cancelled
      - `8`: stale/unknown token
    - `getAsyncStatus(I)`: token-scoped HTTP status surface; returns `-1` on unknown token.
    - `getAsyncBody(I, fallback)`: token-scoped response-body surface; returns fallback when body missing or unknown token.
    - `getAsyncJsonFieldError(I, key)`: token-scoped deterministic JSON field extraction error surface:
      - pass-through of async/networking error codes (`0,1,2,3,4,7,8`)
      - `5`: malformed JSON payload
      - `6`: missing key (or key value is JSON null)
    - `getAsyncJsonField(I, key, fallback)`: token-scoped JSON field string extraction; returns fallback on any non-zero `getAsyncJsonFieldError`.
    - `getAsyncJsonArrayLengthError(I)`: token-scoped deterministic JSON array parse error surface (`0,2,4,5` plus pass-through async codes).
    - `getAsyncJsonArrayLength(I, fallback)`: token-scoped JSON array length extraction; returns fallback on parse/fetch errors.
  - Async route support classes:
    - `ui_runnable_click`: Runnable proxy that captures `View` and invokes static click handler on `target_desc`.
    - `http_route_async_worker`: Runnable worker that evaluates timeout-aware request/status/error in background with deterministic retry, checks token-scoped cancellation, stores token-scoped completion payload (`status/body/error`), and posts success/failure/progress runnable callbacks via `Activity.runOnUiThread(...)`.

## 9) Conformance References

Current behavior is enforced by tests including:
- `tests/test_runtime_abi_v1.py`
- `tests/test_runtime_abi_snapshot.py`
- `tests/test_capabilities.py`
- `tests/test_track_c_wave2_http_get.py`
- `tests/test_track_c_wave2_visible_flow.py`
- `tests/test_track_c_wave3_async_route.py`
- `tests/test_track_c_wave3_visible_flow.py`
- `tests/test_track_c_wave4_async_networking.py`
- `tests/test_http_helper_device_integration.py`
- `tests/test_track_c_wave6_location.py`
- `tests/test_track_c_wave6_visible_flow.py`
- `tests/test_track_c_wave7_permissions.py`
- `tests/test_track_c_wave7_visible_flow.py`
- `tests/test_program5_state_backends.py`
- `tests/test_program5_lifecycle.py`
- `tests/test_support_click_listener.py`
- `tests/test_event_surface_listeners.py`
- `tests/test_navigation_stack.py`
- `tests/test_omega_toolchain_scaffold.py`
- `tests/test_list_view_static.py`

ABI drift guard tooling:
- Snapshot generator/check: `tools/runtime_abi_snapshot.py`
- Frozen snapshot: `cfg/runtime_abi_snapshot_v1.json`
- CI gate: `.github/workflows/ci.yml` step `Check runtime ABI snapshot`
