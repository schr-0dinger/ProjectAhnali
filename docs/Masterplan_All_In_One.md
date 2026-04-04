# Ahnali Unified Masterplan

Last consolidated: 2026-02-16  
Code reality snapshot: 2026-03-10

Rebaseline (2026-03-10): v1 targets the static AOT compiler/toolchain plus implemented deterministic helper-call capability slices. Motion backlog (`8.6`), advanced/system/security/debug backlog (`8.7`–`8.10`), JNI/native bridging, embedded Python, and Play-delivered dynamic feature ambitions are deferred beyond v1.

---

## 1) What Ahnali Is

Ahnali is an ahead-of-time Android compiler. It takes a restricted Python-like DSL and emits Smali/Dalvik bytecode. No interpreter, no reflection, no runtime code generation.

**Is:** AOT compiler, deterministic pipeline, Smali/Dalvik output, static-first UI/state/navigation, capability-scoped Android integration.

**Is not:** Runtime scripting engine, dynamic UI tree runtime, reflection-driven plugin host.

---

## 2) Architecture

### Mode A: Static (default, identity)

Everything compiles ahead of time - UI, navigation, state wiring, event handlers. No runtime interpreter, no reflection-based dispatch. This is the only mode that ships in v1.

### Mode B: Hybrid (deferred research)

Optional, capability-scoped extension layer. UI remains static; dynamic behavior is bounded and explicit. Phase 1 (NDK + JNI) and Phase 2 (optional Python runtime plugin) are deferred beyond v1. See `docs/Ahnali_Dual_Mode_Architecture.md` for the research spec.

---

## 3) Code Reality Snapshot (2026-03-10)

Test suite: **648 passed, 3 skipped** (`PYTHONPATH=. pytest -q -rs`).

The toolchain has a one-command flow (`build_install_run(...)`). The following are implemented and tested:

- Navigation stack with system back bridge (`onSystemBack` + `onBackPressed` wrapper)
- Capability permission inference and manifest injection
- AAR manifest entry merge, direct AAR resolution, transitive AAR inference
- Library `R$*` class generation from merged symbols
- Full compiler pipeline: DSL → CFG → Dominance → Phi → SSA → verify → optimize → Dalvik → DCE → liveness → linear scan → spill → Smali
- Verification gates: CFG validation, SSA validation, typed call/return checks, try/catch structural validation, throw type validation, deterministic ordering checks

---

## 4) DSL Surface

### Core DSL

`app`, `activity`, `state`, `ui`, `on_click`, `Navigate`/`Back`/`Replace`, `request_permission`/`request_permissions`, `Theme`/`Style`/`presets`, `simple_activity` sugar.

### Handlers

Named function handler parsing with compile-time AST analysis. Supported: assignment, `if`, `while`, navigation, toast/dialog/log/exit/set_text.

### Expanded event handlers

`on_change`, `on_text_change`, `on_item_selected`, `on_menu_item_selected`, `on_focus_change` - all with named handlers and compile-time ID validation.

---

## 5) UI Model

Single-activity multi-screen model with stack semantics (`Navigate`/`Back`/`Replace`). Compile-time screen uniqueness checks and ID validation for click targets. Root scroll wrapper behavior.

**Containers:** Column, Row, Relative, Constraint, Container/Card. Grid is planned.

**Widget → Android mapping** (all implemented): Text→TextView, Button→Button, AppBar→Toolbar, FloatingActionButton→Button fallback, RaisedButton→Button, FlatButton→Button, IconButton→Button fallback, TextField→EditText, Checkbox→CheckBox, Radio→RadioButton, Switch→Switch, Slider→SeekBar, Dropdown→Spinner, PopupMenuButton→Button, Image→ImageView, ProgressBar→ProgressBar, RadioGroup→RadioGroup.

---

## 6) Styling and Theme

Layout sizing helpers (match/wrap/fill/numeric), padding/margin lowering, text color/background/size/radius. Theme channel merge order: `inline > style > theme > default`.

**Wave A completed:**
- Phase 1 Typography v1: font_family, font_weight, font_style, letter_spacing, line_height, text_alignment, all_caps, max_lines, ellipsize - all lowered to TextView APIs
- Phase 2 Control Tinting v1: tint, thumb_tint, track_tint, progress_tint, button_tint - all lowered to corresponding widget tint APIs
- Phase 3 ColorStateList DSL: `ColorState(default, pressed, disabled, selected, focused)` with deterministic ordering, lowered to `ColorStateList`

See `docs/UI_Surface_Expansion_TODO.md` for the full phase-by-phase tracker (Phases 1–13, all complete).

---

## 7) Smali/DEX Coverage

All major opcode families implemented: invoke families (static/virtual/direct/interface/super), move-result variants, field ops (sget/sput/iget/iput + typed variants), arrays (new-array, filled-new-array, aget/aput typed variants), cast and type checks, exceptions (try/catch, multi-handler ordering, throw), wide constants, jumbo strings, move-exception, switch (packed/sparse) with payload emission, monitor-enter/monitor-exit.

---

## 8) Capabilities and Permissions

Capability registry (`Caps`, `Perms`, registry resolution). Explicit capability-based permission resolution and handler-based permission inference. Manifest permission rendering and merge of AAR manifest entries.

### Track C Capability Waves (all complete)

| Wave | Capability | Helper Class | Key Methods |
|------|-----------|-------------|-------------|
| 1 | URLLauncher, Connectivity, Storage | `UrlLauncherHelper`, `ConnectivityHelper`, `StorageHelper` | `openUrl`, `isConnected`, `putString`/`getString`/`remove`/`exists`/`clear` (+ DataStore/file/SQLite/Room/encrypted variants) |
| 2 | Networking | `HttpHelper` | `httpGet`, `httpGetStatus`, `httpGetError`, `httpGetRetry`, `httpGetJsonField`, `httpGetJsonFieldError` |
| 3 | Async route dispatch | `HttpHelper` + support classes | `http_get_route_async`, `http_async_cancel`/`progress`/`error`/`status`/`body` with token-scoped state |
| 4 | Multi-request async networking | `HttpHelper` | Token-indexed async state, request-option routing (`method`/`headers`/`body`), typed async JSON adapters |
| 5 | Visible integration flow | - | End-to-end: storage + async networking + connectivity with deterministic fallback |
| 6 | Location | `LocationHelper` | `isLocationEnabled` |
| 7 | Permissions | `PermissionHelper` | `isGranted` |
| 8 | Notifications | `NotificationHelper` | `createChannel`, `postNotification`, `postNotificationError` |
| 9 | Clipboard | `ClipboardHelper` | `setText`, `getText` |
| 10 | Sharing/Intents | `ShareHelper` | `shareText`, `openUri`, error surfaces |
| 11 | WebView | `WebHelper` | `setPolicy`, `loadUrl`, error surfaces |
| 12 | Web JS Bridge | `WebHelper` | `addJsBridge`, `addJsBridgeError` |
| 13 | Web File Chooser + Cookies | `WebHelper` | `chooseFile`, `setCookie`, `getCookie` + error surfaces |
| 14 | Deep Linking | `DeepLinkHelper` | `getLaunchUri`, `getLaunchUriError` |
| 15 | WorkManager | `WorkHelper` | `enqueueWork`, `cancelWork`, `getWorkStatus` + error surfaces |
| 16 | AlarmManager | `AlarmHelper` | `scheduleAlarm`, `cancelAlarm`, `getAlarmStatus` + error surfaces |
| 17 | JobScheduler | `JobHelper` | `scheduleJob`, `cancelJob`, `getJobStatus` + error surfaces (API-level guarded) |
| 18 | Sharing completion | `ShareHelper` | `shareFile`, `shareFileError` |

Full ABI signatures and return semantics are in `docs/runtime_abi_v1.md`. Capability-to-runtime mapping is in `docs/capability_runtime_mapping_v1.md`.

---

## 9) API Master Inventory

This is the growth envelope under Ahnali AOT deterministic constraints. Not everything ships in v1. Status: ✅ implemented, ⚠️ planned, ❌ not implemented.

### 9.1 Structure (UI Tree and Layout)

Screen, Activity (single-activity), Column, Row, Container, Card, View, Relative, Constraint, ScrollView, HorizontalScrollView, FrameLayout, ListView (static adapter), GridView (static adapter), RecyclerView (static model), ViewPager (static pages), TabLayout, NavigationBar, NavigationRail, DrawerLayout, BottomNavigationView, Toolbar, AppBar, CoordinatorLayout, NestedScrollView, Fragment container (static host path).

Modifiers: width/height, match/wrap/fill, percent, weight, margin, padding, gravity, layout_gravity, constraints, relative rules, alignment, orientation, z-index.

### 9.2 Style (Visual and Appearance)

Typography: text_color, text_size, font_family, font_weight, font_style, letter_spacing, line_height, text_alignment, max_lines, ellipsize, all_caps, hint_color, highlight_color, text_shadow.

Color/background: background_color, gradient (linear/radial/sweep), border_width/color/radius (per-corner), ripple_color, opacity, elevation, clip_to_outline, clip_children.

Stateful styling: ColorState (default/pressed/disabled/selected/focused), background/text/progress/thumb/track/button tint.

Image: scaleType, crop, centerInside, adjustViewBounds, tint, alpha, matrix transform.

### 9.3 Interaction (Event Surface)

Click/touch: on_click, on_long_click, on_double_tap, on_touch, on_swipe, on_drag, on_drop, on_scroll, on_fling.

Input: on_text_change, on_editor_action, on_focus_change, on_key, on_change (Switch/Checkbox/Radio/Slider/RadioGroup), on_slider_change, on_item_selected, on_menu_item_selected.

Navigation: Navigate, Back, Replace, PopToRoot, ClearStack.

Gestures: pinch, zoom, rotate, drag, scale gesture detector.

### 9.4 State (Deterministic App Data)

Global state: `state()`, static fields (integer/boolean), numeric operations, comparisons, branching.

Persistence: SharedPreferences, DataStore, file storage (internal/external), SQLite, Room (if statically supported), encrypted storage.

Lifecycle: on_start, on_resume, on_pause, on_stop, on_destroy.

### 9.5 Capability (Platform Services)

✅ Implemented: permissions (request/check/runtime handling), HTTP requests (deterministic helper surface: sync/route/retry/async), ConnectivityManager, WebView (+ WebSettings, JS bridge, file chooser, cookie manager), NotificationManager + channels, WorkManager, AlarmManager, JobScheduler, URL launching, share text/file, open external app, deep linking, custom URI schemes, clipboard (copy/paste).

❌ Deferred: audio/video/camera/sensors (accelerometer, gyroscope, etc.), FusedLocationProvider/GPS/geofencing, OkHttp/Retrofit/WebSockets/DownloadManager, push notifications, foreground services/BroadcastReceiver, MediaStore/file picker/SAF, biometrics, maps, Bluetooth, NFC, system UI control (status bar, immersive mode, etc.).

### 9.6 Motion (Animation and Effects)

⚠️ Planned: animate, fade_in/out, rotate, scale, translate, animate_elevation, alpha animation, sequence/parallel/repeat/reverse, interpolators, ViewPropertyAnimator (duration/delay/interpolator), ObjectAnimator (property/multi-property), AnimatorSet, screen enter/exit/back navigation animations, fade/slide transitions, transform matrix.

✅ Implemented: blur (API 31+ with compile-time min-sdk guard), elevation shadow, text shadow, ripple, opacity, gradient.

❌ Not implemented: withEndAction/withStartAction, scene/layout/explode/shared element transitions.

### 9.7–9.10 Deferred Categories

**Advanced Graphics (8.7):** Canvas draw ops, Paint, hardware acceleration - all ❌.

**System/App Control (8.8):** exit_app ✅, restart_app/clear_cache/clear_data ❌. Build config (package, version, min_sdk, target_sdk, debuggable, keystore) ✅.

**Security/Privacy (8.9):** secure flag, block screenshots, encryption, secure preferences, network security config - all ❌.

**Testing/Debug (8.10):** log ✅, debug overlay/performance metrics/trace sections ❌.

---

## 9) API Master Inventory

This is the growth envelope under Ahnali AOT deterministic constraints. Not everything ships in v1. Status: ✅ implemented, ⚠️ planned, ❌ not implemented.

### 9.1 Structure (UI Tree and Layout)

Screen, Activity (single-activity), Column, Row, Container, Card, View, Relative, Constraint, ScrollView, HorizontalScrollView, FrameLayout, ListView (static adapter), GridView (static adapter), RecyclerView (static model), ViewPager (static pages), TabLayout, NavigationBar, NavigationRail, DrawerLayout, BottomNavigationView, Toolbar, AppBar, CoordinatorLayout, NestedScrollView, Fragment container (static host path).

Modifiers: width/height, match/wrap/fill, percent, weight, margin, padding, gravity, layout_gravity, constraints, relative rules, alignment, orientation, z-index.

### 9.2 Style (Visual and Appearance)

Typography: text_color, text_size, font_family, font_weight, font_style, letter_spacing, line_height, text_alignment, max_lines, ellipsize, all_caps, hint_color, highlight_color, text_shadow.

Color/background: background_color, gradient (linear/radial/sweep), border_width/color/radius (per-corner), ripple_color, opacity, elevation, clip_to_outline, clip_children.

Stateful styling: ColorState (default/pressed/disabled/selected/focused), background/text/progress/thumb/track/button tint.

Image: scaleType, crop, centerInside, adjustViewBounds, tint, alpha, matrix transform.

### 9.3 Interaction (Event Surface)

Click/touch: on_click, on_long_click, on_double_tap, on_touch, on_swipe, on_drag, on_drop, on_scroll, on_fling.

Input: on_text_change, on_editor_action, on_focus_change, on_key, on_change (Switch/Checkbox/Radio/Slider/RadioGroup), on_slider_change, on_item_selected, on_menu_item_selected.

Navigation: Navigate, Back, Replace, PopToRoot, ClearStack.

Gestures: pinch, zoom, rotate, drag, scale gesture detector.

### 9.4 State (Deterministic App Data)

Global state: `state()`, static fields (integer/boolean), numeric operations, comparisons, branching.

Persistence: SharedPreferences, DataStore, file storage (internal/external), SQLite, Room (if statically supported), encrypted storage.

Lifecycle: on_start, on_resume, on_pause, on_stop, on_destroy.

### 9.5 Capability (Platform Services)

- ✅ permissions (request/check/runtime handling)
- ✅ HTTP requests (deterministic helper surface: sync/route/retry/async)
- ✅ ConnectivityManager
- ✅ WebView (+ WebSettings, JS bridge, file chooser, cookie manager)
- ✅ NotificationManager + channels
- ✅ WorkManager
- ✅ AlarmManager
- ✅ JobScheduler
- ✅ URL launching
- ✅ share text/file
- ✅ open external app
- ✅ deep linking
- ✅ custom URI schemes
- ✅ clipboard (copy/paste)
- ❌ audio/video/camera/sensors (accelerometer, gyroscope, etc.)
- ❌ FusedLocationProvider/GPS/geofencing
- ❌ OkHttp/Retrofit/WebSockets/DownloadManager
- ❌ push notifications
- ❌ foreground services/BroadcastReceiver
- ❌ MediaStore/file picker/SAF
- ❌ biometrics
- ❌ maps
- ❌ Bluetooth
- ❌ NFC
- ❌ system UI control (status bar, immersive mode, etc.)

### 9.6 Motion (Animation and Effects)

- ⚠️ animate, fade_in/out, rotate, scale, translate, animate_elevation
- ⚠️ alpha animation
- ⚠️ sequence/parallel/repeat/reverse
- ⚠️ interpolators
- ⚠️ ViewPropertyAnimator (duration/delay/interpolator)
- ⚠️ ObjectAnimator (property/multi-property)
- ⚠️ AnimatorSet
- ⚠️ screen enter/exit/back navigation animations
- ⚠️ fade/slide transitions
- ⚠️ transform matrix
- ✅ blur (API 31+ with compile-time min-sdk guard)
- ✅ elevation shadow
- ✅ text shadow
- ✅ ripple
- ✅ opacity
- ✅ gradient
- ❌ withEndAction/withStartAction
- ❌ scene/layout/explode/shared element transitions

### 9.7 Advanced Graphics

- ❌ Canvas draw ops
- ❌ Paint
- ❌ hardware acceleration

### 9.8 System/App Control

- ✅ exit_app
- ❌ restart_app
- ❌ clear_cache
- ❌ clear_data

### 9.9 Security/Privacy

- ❌ secure flag
- ❌ block screenshots
- ❌ encryption
- ❌ secure preferences
- ❌ network security config

### 9.10 Testing/Debug

- ✅ log
- ❌ debug overlay
- ❌ performance metrics
- ❌ trace sections

---

## 10) Dependency and Plugin Model

Plugin registry with core and optional plugins. Dependency collection for required AAR artifacts. ConstraintLayout dependency wiring. Optional Material plugin dependency collection.

## 11) Toolchain and Packaging

aapt2 resource compilation, d8 dex conversion, zipalign, apksigner. AAR dependency resolution and manifest merge. Benchmark harness (APK size + cold-start). CI gates for ABI drift, capability mapping, docs consistency, scope matrix, library policy.

## 12) Optimization Backlog

Resource shrinking, image optimization (WebP/AVIF), dependency analysis, dead code elimination hardening, constant folding, branch pruning, function inlining, native layer optimization, security checks, build-time enhancements. See `docs/Ahnali_Optimization_Backlog.md`.

## 13) Locked Non-Goals

No reactive runtime in static mode. No implicit diff/recomposition. No dynamic widget construction. No runtime UI tree builder. No reflection-based dispatch. No embedded Python interpreter. No Gradle. No Java/Kotlin source generation.

AAR resolve hooks via `libs/aar_resolved.json`, AAR classes merge path via d8, resource merge + symbol extraction. Transitive AAR inference (manifest-resolved closure path) complete.

---

## 11) Toolchain and Packaging

Smali/baksmali integration, build dir emission from frontend ProgramIR, wrapper activity emission, multi-event support class emission (click, change, text_change, item_selected, focus_change, menu_item_selected). APK packaging via `aapt2` + `zipalign` + `apksigner`. Debug keystore auto-generation, release signing mode. Reproducibility hash check support. Resource writing (strings/colors/dimens/styles) with stable ID path support.

**CI and benchmarking:** Toolchain diagnostics checks, integration tests for packaging/manifest wiring, device smoke scaffolding. Deterministic benchmark harness (`tools/benchmark_apk.py`). CI size benchmark gate on push/PR, manual CI cold-start benchmark gate. Committed size baseline + strict threshold caps (`cfg/benchmark_baseline.json`, `cfg/benchmark_thresholds.json`). CI smali jar launcher fallback for jars without `Main-Class` manifest. v1 scope matrix gate (`cfg/v1_scope_matrix.yaml`). Capability mapping contract drift gate. Docs consistency gate across plan/README/ABI/mapping references.

Policy: Cold-start PR-gate rollout is intentionally deferred; manual gate is enforced for now.

---

## 12) Optimization Backlog

Tracked in `docs/Ahnali_Optimization_Backlog.md`. Areas: asset optimization, resource optimization, code-level optimization, dependency optimization, manifest optimization, native layer optimization, performance static analysis, security optimization, build-time enhancements, app architecture optimization, packaging optimization, developer experience enhancements.

Rule: Each item must preserve deterministic AOT behavior and be guarded by validation/tests before default enablement.

---

## 13) Locked Non-Goals

- Static-first deterministic AOT remains the default identity.
- Reactive features are allowed only as explicit opt-in (`mode="reactive"`); static mode behavior is unchanged.
- No implicit runtime UI tree diff/recomposition engine in static mode.
- No runtime-generated widget trees, no reflection-based execution.

**Static Mode Invariants:** `app_config(mode="static")` is default. Existing static programs remain backward compatible. Reactive APIs fail at compile time in static mode with deterministic diagnostics. Compile-time analyzability and deterministic lowering remain mandatory.

**Reactive Mode Constraints:** Explicit opt-in via `app_config(mode="reactive")`. Reactive updates are explicit (`observable`, `set_observable`, `derived`, `listen`, `bind_text`). No hidden observer graph. ABI drift guarded by snapshot checks.

**Python Dependency Policy:** Only minimal, purpose-justified external libraries allowed (`rich` for diagnostics, `httpx` for HTTP, optional `tenacity` for retry, optional `pydantic` for validation). Required stdlib: `dataclasses`, `asyncio`. All external libraries must stay behind explicit wrapper contracts. CI enforces policy via `cfg/python_library_policy.json`.

---

## 14) Milestones

| Milestone | Status | Description |
|-----------|--------|-------------|
| A: Friendly DSL | ✅ | Pythonic app DSL usable without Smali internals |
| B: Feature-Usable Static Foundation | ✅ | Navigation/state/event core, toolchain compile/package/install path, Wave A styling |
| C: Production Static Core | ⚠️ | Release hardening, CI gating polish, broader API coverage, docs finalization |
| D: Native Hybrid Bridge | ⚠️ | NDK/JNI capability-scoped bridge (deferred) |
| E: Optional Python Plugin | ⚠️ | Embedded Python plugin over JNI (deferred) |

---

## 15) Execution Plan

Authoritative active-v1 execution order after the static-core rebaseline:

1. ✅ **Program 5 closure pass:** state/lifecycle traceability locked to tests/docs (`docs/Program5_Closure.md`, `tests/test_program5_closure.py`).
2. ✅ **Program 11-A gate hardening:** contract/CI guardrails strict and blocking (`tools/v1_scope_matrix.py`, `tools/capability_mapping_contract.py`, `tools/docs_consistency.py`).
3. ✅ **Program 6-A capability core:** runtime-permission + notifications/channels slices shipped under ABI/test/doc pattern.
4. ⚠️ **Program 6-B closure/freeze:** Waves 9–18 complete (clipboard, sharing/intents, WebView, JS bridge, file chooser/cookies, deep-linking, WorkManager/AlarmManager/JobScheduler). Remaining retained `8.5` inventory frozen through explicit `deferred`/`blocked` scope-matrix status.
5. ⚠️ **Program 12-A docs/API reference freeze:** keep masterplan/README/ABI/capability docs continuously reconciled with code and `cfg/v1_scope_matrix.yaml`.
6. ⚠️ **Program 11-B + 12-B final static-v1 release hardening:** preserve compiler/toolchain green status, benchmark gates, runtime ABI/capability mapping consistency, and final traceability report/release gates.

Guardrail-first reactive unlock remains active throughout: static-default mode unchanged, reactive surfaces remain explicit opt-in, no implicit runtime diff/recomposition in static mode.

---

## 16) Immediate Unified Execution Plan

1. ✅ **Program 5** - State and lifecycle hooks (closed).
2. ✅ **Program 11-A** - Docs/API reference freeze (closed).
3. ✅ **Program 6-A** - Capability depth (closed).
4. ⚠️ **Program 6-B** - Capability breadth closure/freeze (in progress).
5. ⚠️ **Program 12-A** - Docs consistency gate (in progress).
6. ⚠️ **Program 11-B + 12-B** - Final static-v1 release hardening (in progress).

---

## 17) Deferred Beyond V1

1. ⚠️ **Program 7** - Motion backlog (`8.6`): deferred until static compiler/toolchain is frozen.
2. ⚠️ **Program 8** - Advanced/system/security/debug backlog (`8.7`–`8.10`): deferred beyond current release train.
3. ⚠️ **Program 9 / Milestone D** - Deterministic NDK/JNI bridge: deferred to post-v1 research/prototyping.
4. ⚠️ **Program 10 / Milestone E** - Optional bounded Python plugin: deferred to post-v1 research/prototyping.
