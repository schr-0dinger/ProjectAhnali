# Anali Unified Masterplan (All-In-One)

Last consolidated: 2026-02-12  
Consolidation basis: code reality + tests in current repository

---

## 0) Source Merge Index

Merged into this single masterplan:
- ✅ `Masterplan_Ultimate.md`
- ✅ `Anali_Masterplan_v7.md`
- ✅ `Anali_implement_immediate_plan.md`
- ✅ `Anali_Dual_Mode_Architecture.md`
- ✅ `README.md`
- ✅ `docs/Widgets.md`
- ✅ `docs/UI_Surface_Expansion_TODO.md`

---

## 1) Canonical Product Definition

Anali is:
- ✅ Ahead-of-time (AOT) Android compiler
- ✅ Deterministic pipeline and emission
- ✅ Smali/Dalvik-native output
- ✅ Static-first UI, state, navigation, and handler wiring
- ✅ Capability-scoped Android integration

Anali is not:
- Runtime scripting engine
- Dynamic UI tree runtime
- Reflection-driven plugin host

---

## 2) Unified Architecture (Static + Hybrid)

### 2.1 Mode A: Static Mode (Default, Identity)

Implemented baseline:
- ✅ Static UI compilation
- ✅ Static navigation graph lowering
- ✅ Static handler lowering
- ✅ Static state wiring
- ✅ No runtime interpreter
- ✅ No reflection-based dispatch

### 2.2 Mode B: Hybrid Mode (Optional Extension)

Integrated architecture decision:
- Hybrid is optional and capability-scoped.
- Hybrid never replaces Static Mode.
- UI remains static; dynamic behavior is bounded and explicit.

Hybrid rollout status:
- ✅ Phase 0 static foundation is in place.
- Phase 1 native execution layer (NDK + JNI) is planned.
- Phase 2 optional Python runtime plugin is planned.

---

## 3) Code Reality Snapshot (As of 2026-02-12)

- ✅ Test suite reality: `203 passed` (`PYTHONPATH=. pytest -q`)
- ✅ One-command flow exists: `build_install_run(...)`
- ✅ Navigation stack exists
- ✅ System back bridge exists (`onSystemBack` + wrapper `onBackPressed`)
- ✅ Capability permission inference exists
- ✅ Manifest permission injection exists
- ✅ AAR manifest entry merge exists
- ✅ Library `R$*` class generation from merged symbols exists
- ✅ Direct AAR resolution exists
- ✅ Transitive AAR inference exists (manifest closure path + deterministic selection)

---

## 4) Compiler Pipeline and Verification

### 4.1 Pipeline

Implemented:
- ✅ DSL -> CFG -> Dominance -> Phi insertion -> SSA rename -> SSA verify
- ✅ Type inference + type verification
- ✅ SSA optimization (const/copy propagation + coalescing)
- ✅ Dalvik lowering
- ✅ DCE + CFG simplification
- ✅ Liveness + linear scan + spilling
- ✅ Smali emission

### 4.2 Verification and Safety Gates

Implemented:
- ✅ CFG validation
- ✅ SSA validation
- ✅ Typed call/return checks
- ✅ Try/catch structural validation
- ✅ Throw type validation
- ✅ Deterministic ordering checks (methods/fields/resources/class layout)

---

## 5) DSL Surface (Unified Status)

### 5.1 Core Pythonic App DSL

Implemented:
- ✅ `app`, `activity`, `state`, `ui`
- ✅ `on_click` handler DSL
- ✅ `Navigate`, `Back`, `Replace`
- ✅ `request_permission` / `request_permissions`
- ✅ `Theme`, `Style`, `presets`
- ✅ `simple_activity` sugar path

### 5.2 Handler Model

Implemented:
- ✅ Named function handler parsing
- ✅ Compile-time AST parse of handler statements
- ✅ Supported control flow in handlers: assignment, `if`, `while`, navigation, toast/dialog/log/exit/set_text

Expanded and implemented:
- ✅ `on_change`
- ✅ `on_text_change`
- ✅ `on_item_selected`
- ✅ `on_menu_item_selected`
- ✅ `on_focus_change`

---

## 6) UI Model and Runtime Mapping

### 6.1 UI Structure Model

Implemented:
- ✅ Single-activity multi-screen model
- ✅ Screen stack semantics (`Navigate`/`Back`/`Replace`)
- ✅ Compile-time screen uniqueness checks
- ✅ Compile-time id validation for click targets
- ✅ Root scroll wrapper behavior

### 6.2 Containers

Implemented:
- ✅ Column
- ✅ Row
- ✅ Relative
- ✅ Constraint
- ✅ Container/Card helpers

Not yet implemented as first-class static v1 surfaces:
- Grid (planned)
- Recycler/static list surface (planned)

### 6.3 Widget Runtime Classes (Code Reality)

Implemented mapping:
- ✅ Text -> `android.widget.TextView`
- ✅ Button -> `android.widget.Button`
- ✅ AppBar -> `android.widget.Toolbar`
- ✅ FloatingActionButton -> `android.widget.Button` fallback
- ✅ RaisedButton -> `android.widget.Button`
- ✅ FlatButton -> `android.widget.Button`
- ✅ IconButton -> `android.widget.Button` fallback
- ✅ TextField -> `android.widget.EditText`
- ✅ Checkbox -> `android.widget.CheckBox`
- ✅ Radio -> `android.widget.RadioButton`
- ✅ Switch -> `android.widget.Switch`
- ✅ Slider -> `android.widget.SeekBar`
- ✅ Dropdown -> `android.widget.Spinner`
- ✅ PopupMenuButton -> `android.widget.Button`
- ✅ Image -> `android.widget.ImageView`
- ✅ ProgressBar -> `android.widget.ProgressBar`
- ✅ RadioGroup -> `android.widget.RadioGroup`

---

## 7) Styling and Theme System

### 7.1 Core Styling

Implemented:
- ✅ Layout sizing helpers (`match`, `wrap`, `fill`, numeric)
- ✅ Padding/margin lowering
- ✅ Text color/background/text size/radius
- ✅ Theme channel merge order (`inline > style > theme > default`)

### 7.2 UI Expansion Wave A (from TODO tracker)

Phase 1 Typography v1 (core implemented):
- ✅ `font_family`
- ✅ `font_weight`
- ✅ `font_style`
- ✅ `letter_spacing`
- ✅ `line_height`
- ✅ `text_alignment`
- ✅ `all_caps`
- ✅ `max_lines`
- ✅ `ellipsize`
- ✅ Lowering to corresponding TextView APIs
- Coverage hardening for all secondary text surfaces remains ongoing.

Phase 2 Control Tinting v1 (core implemented):
- ✅ `tint`
- ✅ `thumb_tint`
- ✅ `track_tint`
- ✅ `progress_tint`
- ✅ `button_tint`
- ✅ Lowering for slider/progress/switch/compound/button tint APIs

Phase 3 ColorStateList DSL (core implemented):
- ✅ `ColorState(default, pressed, disabled, selected, focused)`
- ✅ Deterministic state ordering
- ✅ Lowering to `ColorStateList`
- ✅ ColorState support in text color + tint/background channels

---

## 8) Smali/DEX Coverage Status

Implemented opcode families and features:
- ✅ Invoke families: static/virtual/direct/interface/super
- ✅ `move-result`, `move-result-object`, `move-result-wide`
- ✅ Field ops: `sget/sput` + typed variants
- ✅ Field ops: `iget/iput` + typed variants
- ✅ Arrays: `new-array`, `filled-new-array`, `aget/aput` typed variants
- ✅ Cast and type checks: `check-cast`, `instance-of`, primitive conversions
- ✅ Exceptions: `try/catch`, multi-handler ordering, `throw`
- ✅ Wide constants + jumbo strings + move-exception

Recently completed high-priority coverage:
- ✅ `switch` (packed/sparse) with payload emission
- ✅ monitor-enter/monitor-exit synchronization ops

---

## 9) Capabilities, Permissions, and Manifest

Implemented:
- ✅ Capability registry (`Caps`, `Perms`, registry resolution)
- ✅ Explicit capability-based permission resolution (`app_config(uses=[...])`)
- ✅ Handler-based permission inference (`request_permissions(...)`)
- ✅ Manifest permission rendering
- ✅ Merge of permission/provider/service/receiver entries from AAR manifests

Pending:
- ⚠️ Expanded capability module runtime ABI surface

---

## 10) Dependency and Plugin Model

Implemented:
- ✅ Plugin registry and loading (`core`, optional plugins)
- ✅ Dependency collection for required AAR artifacts
- ✅ ConstraintLayout dependency wiring
- ✅ Optional Material plugin dependency collection

Tooling implemented:
- ✅ AAR resolve hooks via `libs/aar_resolved.json`
- ✅ AAR classes merge path via d8
- ✅ Resource merge + symbol extraction path

Completed:
- ✅ Transitive AAR inference (manifest-resolved closure path)

---

## 11) Toolchain and Packaging

Implemented:
- ✅ Smali assemble integration
- ✅ Baksmali disassemble integration
- ✅ Build dir emission from frontend ProgramIR
- ✅ Wrapper activity emission
- ✅ Click listener support class emission
- ✅ Multi-event support class emission (`click`, `change`, `text_change`, `item_selected`, `focus_change`, `menu_item_selected`)
- ✅ APK packaging via `aapt2` + `apksigner`
- ✅ Debug keystore auto-generation
- ✅ Release signing mode with explicit keystore workflow
- ✅ Reproducibility hash check support for unsigned archive content
- ✅ Resource writing (strings/colors/dimens/styles)
- ✅ Stable id path support for resources

Integration and smoke:
- ✅ Toolchain diagnostics checks
- ✅ Integration tests for packaging and manifest wiring
- ✅ Device smoke scaffolding in tests

Pending:
- ⚠️ Size/perf benchmark automation

---

## 8) Anali API Master Inventory (Exhaustive Surface Envelope)

This inventory reorganizes the full practical native Android Java surface into Anali architectural layers:
- Structure
- Style
- Interaction
- State
- Capability
- Motion

This is the complete growth envelope under Anali AOT deterministic constraints.  
It is not a promise that all items ship in v1.

Status legend:
- ✅ Implemented in code reality
- ⚠️ Needed/planned implementation target
- ❌ Not implemented yet

### 8.1 Structure APIs (UI Tree and Layout)

Core structural primitives:
- ✅ Screen
- ✅ Activity (single-activity model)
- ✅ Column (LinearLayout vertical)
- ✅ Row (LinearLayout horizontal)
- ✅ Container
- ✅ Card
- ✅ View
- ✅ Relative
- ✅ Constraint
- ⚠️ ScrollView
- ⚠️ HorizontalScrollView
- ❌ FrameLayout
- ⚠️ ListView
- ❌ GridView
- ⚠️ RecyclerView (static adapter model)
- ❌ ViewPager (static page model)
- ❌ TabLayout
- ⚠️ NavigationBar
- ⚠️ NavigationRail
- ⚠️ DrawerLayout
- ❌ BottomNavigationView
- ✅ Toolbar
- ✅ AppBar
- ❌ CoordinatorLayout
- ❌ NestedScrollView
- ❌ Fragment container (if later supported)

Structural modifiers:
- ✅ width/height
- ✅ match/wrap/fill
- ⚠️ percent
- ✅ weight
- ✅ margin
- ✅ padding
- ✅ gravity
- ❌ layout_gravity
- ✅ constraints
- ✅ relative rules
- ✅ alignment
- ✅ orientation
- ⚠️ z-index (elevation layering)

### 8.2 Style APIs (Visual and Appearance)

Typography:
- ✅ text_color
- ✅ text_size
- ✅ font_family
- ✅ font_weight
- ✅ font_style
- ✅ letter_spacing
- ✅ line_height
- ✅ text_alignment
- ✅ max_lines
- ✅ ellipsize
- ✅ all_caps
- ❌ hint_color
- ❌ highlight_color
- ⚠️ text_shadow

Color and background:
- ✅ background_color
- ✅ gradient background
- ❌ radial gradient
- ❌ sweep gradient
- ✅ border_width
- ✅ border_color
- ✅ border_radius
- ✅ per-corner radius
- ✅ ripple_color
- ✅ opacity
- ⚠️ elevation
- ✅ clip_to_outline
- ✅ clip_children

Stateful styling:
- ✅ ColorState (default/pressed/disabled/selected/focused)
- ✅ background tint
- ❌ text tint
- ✅ progress tint
- ✅ thumb tint
- ✅ track tint
- ✅ button tint

Image styling:
- ❌ scaleType
- ❌ crop
- ❌ centerInside
- ❌ adjustViewBounds
- ❌ tint
- ❌ image alpha
- ❌ image matrix transform

Progress styling:
- ✅ indeterminate tint
- ✅ progress tint
- ❌ secondary progress tint

Switch/Checkbox/Radio styling:
- ✅ button tint
- ✅ thumb tint
- ✅ track tint

### 8.3 Interaction APIs (Event Surface)

Click and touch:
- ✅ on_click
- ❌ on_long_click
- ❌ on_double_tap
- ❌ on_touch
- ❌ on_swipe
- ❌ on_drag
- ❌ on_drop
- ❌ on_scroll
- ❌ on_fling

Input events:
- ✅ on_text_change
- ❌ on_editor_action
- ✅ on_focus_change
- ❌ on_key
- ✅ on_change (Switch/Checkbox/Radio/Slider/RadioGroup)
- ⚠️ on_slider_change (no dedicated alias; use `on_change`)
- ✅ on_item_selected
- ✅ on_menu_item_selected

Navigation:
- ✅ Navigate
- ✅ Back
- ✅ Replace
- ❌ PopToRoot
- ❌ ClearStack

Gesture detection:
- ❌ pinch
- ❌ zoom
- ❌ rotate gesture
- ❌ drag
- ❌ scale gesture detector

### 8.4 State APIs (Deterministic App Data)

Global state:
- ✅ state()
- ✅ static fields
- ✅ integer fields
- ✅ boolean fields
- ✅ numeric operations
- ✅ comparisons
- ✅ branching

Persistence:
- ⚠️ SharedPreferences
- ❌ DataStore
- ❌ file storage (internal/external)
- ❌ SQLite
- ❌ Room (if statically supported)
- ❌ encrypted storage

Lifecycle state:
- ❌ on_start
- ❌ on_resume
- ❌ on_pause
- ❌ on_stop
- ❌ on_destroy

### 8.5 Capability APIs (Platform Services)

Permissions:
- ✅ request_permission
- ✅ request_permissions
- ❌ check_permission
- ⚠️ runtime permission handling

Audio:
- ❌ MediaPlayer
- ❌ ExoPlayer
- ❌ SoundPool
- ❌ AudioManager
- ❌ audio focus
- ❌ audio recording
- ❌ microphone access

Video:
- ❌ VideoView
- ❌ MediaPlayer video
- ❌ CameraX
- ❌ MediaRecorder
- ❌ video playback controls

Camera:
- ❌ CameraX preview
- ❌ image capture
- ❌ video capture
- ❌ flash control
- ❌ focus control

Sensors:
- ❌ accelerometer
- ❌ gyroscope
- ❌ magnetometer
- ❌ light sensor
- ❌ proximity sensor
- ❌ step counter

Location:
- ❌ FusedLocationProvider
- ❌ GPS
- ❌ geofencing

Networking:
- ❌ HTTP requests
- ❌ OkHttp
- ❌ Retrofit
- ❌ WebSockets
- ❌ ConnectivityManager
- ❌ DownloadManager

Web:
- ❌ WebView
- ❌ WebSettings
- ❌ JS bridge
- ❌ file chooser
- ❌ cookie manager

Notifications:
- ❌ NotificationManager
- ❌ channels
- ❌ push notifications
- ❌ foreground service notification

Background work:
- ❌ WorkManager
- ❌ AlarmManager
- ❌ JobScheduler
- ❌ foreground services
- ❌ BroadcastReceiver

Storage:
- ❌ internal storage
- ❌ external storage
- ❌ MediaStore
- ❌ file picker
- ❌ SAF (Storage Access Framework)

Sharing and intents:
- ❌ open URL
- ❌ share text
- ❌ share file
- ❌ open external app
- ❌ deep linking
- ❌ custom URI schemes

Clipboard:
- ❌ copy
- ❌ paste
- ❌ clear

Biometrics:
- ❌ fingerprint
- ❌ face authentication

Maps:
- ❌ Google Maps SDK
- ❌ map markers
- ❌ camera movement
- ❌ map gestures

Bluetooth:
- ❌ classic Bluetooth
- ❌ BLE
- ❌ device scanning

NFC:
- ❌ NFC read/write

System UI:
- ❌ status bar control
- ❌ immersive mode
- ❌ orientation lock
- ❌ screen brightness
- ❌ WakeLock

### 8.6 Motion APIs (Animation and Effects)

Explicit animations:
- ⚠️ animate
- ⚠️ fade_in
- ⚠️ fade_out
- ⚠️ rotate
- ⚠️ scale
- ⚠️ translate
- ⚠️ animate_elevation
- ⚠️ alpha animation

Animator composition:
- ⚠️ sequence
- ⚠️ parallel
- ⚠️ repeat
- ⚠️ reverse
- ⚠️ interpolators

ViewPropertyAnimator:
- ⚠️ duration
- ⚠️ delay
- ⚠️ interpolator
- ❌ withEndAction
- ❌ withStartAction

ObjectAnimator:
- ⚠️ property animation
- ⚠️ multi-property animation
- ⚠️ AnimatorSet

Transition APIs:
- ❌ scene transition
- ❌ layout transition
- ⚠️ fade transition
- ⚠️ slide transition
- ❌ explode transition
- ❌ shared element transition

Navigation transitions:
- ⚠️ screen enter animation
- ⚠️ screen exit animation
- ⚠️ back navigation animation

Visual effects:
- ✅ blur (API 31+) with compile-time min-sdk guard (`min_sdk < 31` => warn + skip lowering)
- ✅ elevation shadow
- ✅ text shadow
- ✅ ripple
- ✅ opacity
- ✅ gradient
- ⚠️ transform matrix

### 8.7 Advanced Graphics (Optional Future)

Canvas:
- ❌ drawRect
- ❌ drawCircle
- ❌ drawPath
- ❌ drawBitmap
- ❌ drawText

Paint:
- ❌ stroke width
- ❌ stroke color
- ❌ style
- ❌ shader

Hardware acceleration:
- ❌ layer type control

### 8.8 System and App Control

App control:
- ✅ exit_app
- ❌ restart_app
- ❌ clear_cache
- ❌ clear_data

Build config:
- ✅ package
- ✅ version
- ✅ min_sdk
- ✅ target_sdk
- ✅ debuggable
- ✅ keystore

### 8.9 Security and Privacy

- ❌ secure flag
- ❌ block screenshots
- ❌ encryption
- ❌ secure preferences
- ❌ network security config

### 8.10 Testing and Debug

- ✅ log
- ❌ debug overlay
- ❌ performance metrics
- ❌ trace sections

---

## 13) UI Surface Expansion Tracker (Merged Status)

Global constraints:
- ✅ Named handlers and static registration model held
- ✅ Compile-time id validation held
- ✅ Deterministic lowering held

Phase status:
- ✅ Phase 1 Typography v1 (core)
- ✅ Phase 2 Control Tinting v1 (core)
- ✅ Phase 3 ColorStateList DSL (core)
- ✅ Phase 4 Event surface expansion
- ✅ Phase 5 Input configuration expansion
- ✅ Phase 6 Accessibility expansion
- ✅ Phase 7 Elevation and shadow
- ⚠️ Phase 8 Visual effects pack
- ⚠️ Phase 9 Explicit animation DSL
- ⚠️ Phase 10 Theme channel expansion
- ⚠️ Phase 11 Scroll controls as explicit DSL widgets
- ⚠️ Phase 12 Recycler/static list deterministic adapter layer
- ⚠️ Phase 13 Validation/lint hardening expansion

---

## 14) Locked Non-Goals (Unified)

- No reactive hooks/runtime diffing
- No runtime-generated widget trees
- No reflection-based execution model
- No core identity shift away from static AOT

---

## 15) Consolidated Milestones

### Milestone A: Friendly DSL
- ✅ Pythonic app DSL usable without smali internals

### Milestone B: Feature-Usable Static Foundation
- ✅ Navigation/state/event core in place
- ✅ Toolchain compile/package/install path in place
- ✅ Wave A styling foundation complete

### Milestone C: Production Static Core
- ⚠️ Release hardening, CI gating polish, broader API coverage, docs finalization

### Milestone D: Native Hybrid Bridge
- ⚠️ NDK/JNI capability-scoped bridge

### Milestone E: Optional Python Plugin
- ⚠️ Embedded Python plugin over JNI, bounded by static UI invariants

---

## 16) Immediate Unified Execution Plan

1. ✅ Finalize transitive AAR inference and error diagnostics.
2. ✅ Execute Phase 4 core event surface expansion (`on_change`, text/item/menu/focus listeners).
3. ✅ Execute Phase 5 input configuration fields + lowering.
4. ✅ Complete Phase 6 accessibility surface (`important_for_accessibility`, alias coverage, tests).
5. ✅ Execute Phase 7 elevation/shadow surface (`setElevation`, text shadow, pressed-elevation state animator).
6. ⚠️ Begin Hybrid Phase 1 (NDK/JNI skeleton, capability-scoped entrypoints).
7. ⚠️ Continue API modularization (`dsl/api.py` split into domain modules) while preserving compatibility.

---

## 17) Source of Truth Policy

This file is now the canonical all-in-one masterplan.  
When updating roadmap/status:
- Add `✅` only when implementation is confirmed by code/tests.
- Keep pending items unmarked.
- Update test reality snapshot with exact command/result.


---

## Appendix A) Verbatim Import — Anali_Dual_Mode_Architecture.md

# Anali Architecture Plan --- Dual Mode (Static + Hybrid)

Status: Architectural Definition\
Phase Target: v1 Static Foundation → Stage 2 Hybrid Extension\
Scope: Android-only

------------------------------------------------------------------------

# 1. Core Philosophy

Anali is and will always be:

-   An ahead-of-time (AOT) Android compiler
-   Deterministic
-   Smali-emitting
-   Runtime-minimal
-   Static-first

Hybrid mode does not redefine Anali.

Hybrid mode is: - An optional plugin layer - Capability-scoped -
Strictly bounded - Never structural by default

------------------------------------------------------------------------

# 2. Two Operating Modes

Anali operates in two clearly defined modes.

## Mode A --- Static Mode (Default)

Canonical Anali behavior.

Characteristics:

-   Entire UI compiled at build time
-   Navigation compiled
-   State compiled
-   Event handlers compiled
-   No interpreter
-   No dynamic UI construction
-   No runtime code execution

Result:

-   Small APK
-   Deterministic behavior
-   Maximum performance
-   Full static analyzability
-   Zero reflection
-   No dynamic execution

------------------------------------------------------------------------

## Mode B --- Hybrid Mode (Optional Plugin)

Activated only when explicitly requested:

app_config(enable_module="python", python_lib=\["json", "socket"\])

Hybrid introduces:

-   Minimal Python execution environment
-   Controlled runtime logic execution
-   JNI-based execution boundary
-   Strictly bounded mutation capabilities

Hybrid mode never replaces static mode.

------------------------------------------------------------------------

# 3. Hybrid Mode Architecture

Stage 1 --- Native Execution Infrastructure

Before introducing Python runtime:

-   NDK-based native library integration
-   Shared object loading (.so)
-   Controlled JNI entrypoints
-   Capability-scoped native calls

Enables:

-   Native C/C++ logic
-   High-performance computation
-   Cryptographic primitives
-   Background logic
-   Future Python embedding

------------------------------------------------------------------------

Stage 2 --- Optional Python Runtime Plugin

Execution Flow:

Static UI (Smali) → Core Runtime (Smali) → JNI Bridge → libpython3.x.so
→ Restricted Python Execution

Core Rule:

UI is always static.

Python may: - Mutate state - Trigger navigation - Call approved
capabilities - Perform computation - Manage background logic

Python may NOT: - Create arbitrary new views (unless in bounded
region) - Destroy compiled views - Inject arbitrary classes - Access
Android APIs directly

All Android access passes through capability wrappers.

------------------------------------------------------------------------

# 4. Controlled Mutation Model

Level 1 --- Pure State Mutation

Python can: - Modify integers - Update text - Toggle visibility -
Trigger navigation

Structure remains static.

Level 2 --- Bounded Dynamic Regions (Optional)

Example:

Column(id="task_list", mutable=True)

Compiler generates:

-   Managed adapter region
-   Internal view factory
-   ID namespace isolation
-   Auto-generated dynamic IDs

Dynamic items: - Live inside sandbox - Cannot override static IDs -
Cannot modify parent structure

Structural mutation outside dynamic regions remains disallowed.

------------------------------------------------------------------------

# 5. JNI and Native Integration

Step 1 --- NDK Setup

-   Install Android NDK
-   Use NDK clang
-   Build shared libraries via CMake or direct clang

Step 2 --- Shared Object Integration

APK includes:

lib/armeabi-v7a/libanali_native.so\
lib/arm64-v8a/libanali_native.so

Loaded via:

System.loadLibrary("anali_native")

------------------------------------------------------------------------

# 6. Python Plugin Size Strategy

Estimated minimal CPython size: 5--10MB

Optimization strategy:

-   Remove unused modules
-   Strip debug symbols
-   Freeze required modules only
-   Capability-scoped inclusion

Hybrid APK increase is acceptable.

------------------------------------------------------------------------

# 7. Static vs Hybrid Responsibilities

Static Mode: - UI structure - Navigation graph - Event handlers - State
wiring - Capability resolution

Hybrid Mode: - Additional runtime logic - Optional dynamic state-driven
updates - Controlled computation layer - Python-backed background logic

------------------------------------------------------------------------

# 8. Implementation Phases

Phase 0 --- Static Stabilization - Deterministic emission - Stable
navigation - Capability registry - Manifest injection - Multidex support

Phase 1 --- Native Execution Layer - NDK integration - JNI bridge -
Capability-scoped native calls

Phase 2 --- Python Hybrid Plugin - Minimal CPython build - Controlled
bridge API - State mutation only - Optional bounded dynamic regions

------------------------------------------------------------------------

# Final Position

Anali is:

-   A static Android compiler at its core
-   With optional controlled dynamic logic
-   With optional embedded Python
-   With JNI-native support
-   Without surrendering structural determinism

Static is identity.\
Hybrid is power.\
Boundaries preserve integrity.


---

## Appendix B) Verbatim Import — docs/UI_Surface_Expansion_TODO.md

# Anali UI Surface Expansion TODO (v1)

Last updated: 2026-02-11

Goal:
- Expand UI depth and polish while preserving:
- Ahead-of-time compilation
- Deterministic smali emission
- No reactive runtime
- No implicit property diffing
- No dynamic widget trees

All animations and effects must be explicit and imperative.

## Global Constraints (Apply to Every Phase)

- [ ] Keep handlers named and statically registered (no lambdas/dynamic callbacks).
- [ ] Keep compile-time ID validation for all widget/event references.
- [ ] Keep deterministic lowering only (no runtime behavior inference).
- [ ] Add compile-time lint for unsupported widget/style combinations.
- [ ] Add focused lowering tests and at least one integration smoke test per phase.

## Phase 1: Typography v1

### DSL and Style Surface (`dsl/widgets.py`)
- [ ] Add `font_family` to `Style`.
- [ ] Add `font_weight` to `Style`.
- [ ] Add `font_style` to `Style`.
- [ ] Add `letter_spacing` to `Style`.
- [ ] Add `line_height` to `Style`.
- [ ] Add `text_alignment` to `Style`.
- [ ] Add `all_caps` to `Style`.
- [ ] Add `max_lines` to `Style`.
- [ ] Add `ellipsize` to `Style`.

### Lowering (`dsl/lowering/attr_registry.py`, `dsl/lowering/context.py`)
- [ ] Lower `font_*` to `setTypeface`.
- [ ] Lower `letter_spacing` to `setLetterSpacing`.
- [ ] Lower `line_height` to `setLineSpacing`.
- [ ] Lower `text_alignment` to `setTextAlignment`.
- [ ] Lower `all_caps` to `setAllCaps`.
- [ ] Lower `max_lines` to `setMaxLines`.
- [ ] Lower `ellipsize` to `setEllipsize`.

### Coverage
- [ ] Text
- [ ] Button family
- [ ] Radio / Checkbox / Switch
- [ ] Dropdown text surface
- [ ] Popup menu item text surface

## Phase 2: Control Tinting v1

### DSL and Style Surface (`dsl/widgets.py`)
- [ ] Add `tint`.
- [ ] Add `thumb_tint`.
- [ ] Add `track_tint`.
- [ ] Add `progress_tint`.
- [ ] Add `button_tint`.

### Lowering (`dsl/lowering/context.py`)
- [ ] Slider: `setThumbTintList`.
- [ ] Slider: `setProgressTintList`.
- [ ] Slider: `setProgressBackgroundTintList`.
- [ ] ProgressBar: `setProgressTintList`.
- [ ] ProgressBar: `setIndeterminateTintList`.
- [ ] Switch: `setThumbTintList`.
- [ ] Switch: `setTrackTintList`.
- [ ] Checkbox/Radio: `setButtonTintList`.
- [ ] Button: `setBackgroundTintList`.

## Phase 3: ColorStateList DSL

### DSL (`dsl/widgets.py` or `dsl/colors.py`)
- [ ] Add `ColorState(default=..., pressed=..., disabled=..., selected=..., focused=...)`.
- [ ] Validate allowed keys: `default`, `pressed`, `disabled`, `selected`, `focused`.
- [ ] Deterministic state ordering for emitted arrays.

### Lowering (`dsl/lowering/context.py`)
- [ ] Convert `ColorState` to `ColorStateList`.
- [ ] Support `ColorState` in `text_color`.
- [ ] Support `ColorState` in `background`/tint channels.
- [ ] Support `ColorState` in progress/tint fields.

## Phase 4: Event Surface Expansion

### DSL API (`dsl/app.py`, `dsl/widgets.py`)
- [x] Add `on_change`.
- [x] Add `on_text_change`.
- [x] Add `on_item_selected`.
- [x] Add `on_menu_item_selected`.
- [x] Add `on_focus_change`.

### Lowering (`dsl/lowering/context.py`, support listener classes)
- [x] Slider -> `OnSeekBarChangeListener`.
- [x] Switch/Checkbox -> `OnCheckedChangeListener`.
- [x] RadioGroup -> `OnCheckedChangeListener`.
- [x] TextField -> `TextWatcher`.
- [x] Dropdown -> `OnItemSelectedListener`.
- [x] PopupMenu -> `OnMenuItemClickListener`.

### Constraints
- [x] Named handlers only.
- [x] Compile-time ID validation.
- [x] No dynamic registration at runtime.

## Phase 5: Input Configuration

### DSL (`dsl/widgets.py`)
- [x] Add TextField fields: `input_type`, `ime_options`, `max_length`, `single_line`, `password`, `auto_capitalize`, `numeric_only`.

### Lowering (`dsl/lowering/context.py`)
- [x] `setInputType`.
- [x] `setImeOptions`.
- [x] `setFilters`.
- [x] `setSingleLine`.
- [x] `setTransformationMethod`.

## Phase 6: Accessibility

### DSL (`dsl/widgets.py`)
- [x] Add `content_description`.
- [x] Add `important_for_accessibility`.
- [x] Add `accessibility_label` alias.

### Lowering (`dsl/lowering/context.py`)
- [x] `setContentDescription`.
- [x] `setImportantForAccessibility`.

## Phase 7: Elevation and Shadow

### DSL (`dsl/widgets.py`)
- [x] Add `elevation`.
- [x] Add `pressed_elevation`.
- [x] Add `text_shadow_color`.
- [x] Add `text_shadow_radius`.
- [x] Add `text_shadow_dx`.
- [x] Add `text_shadow_dy`.

### Lowering (`dsl/lowering/context.py`)
- [x] `setElevation`.
- [x] Text-only `setShadowLayer`.
- [x] Optional pressed elevation animation path (explicit only).

### Coverage
- [x] Card
- [x] Button
- [x] Container
- [x] AppBar
- [x] Text

## Phase 8: Visual Effects Pack v1

### 8.1 Opacity
- [x] Add `opacity`.
- [x] Lower to `setAlpha`.

### 8.2 Border
- [x] Add `border_width`.
- [x] Add `border_color`.
- [x] Add `border_radius` (allow per-corner model).
- [x] Lower via `GradientDrawable` stroke.

### 8.3 Gradient Background
- [x] Add `Gradient(start, end, direction)`.
- [x] Lower to `GradientDrawable` gradients.

### 8.4 Ripple
- [x] Add `ripple_color`.
- [x] Lower to `RippleDrawable`.

### 8.5 Clip and Outline
- [x] Add `clip_to_outline`.
- [x] Add `clip_children`.
- [x] Lower to `setClipToOutline` / `setClipChildren`.

### 8.6 Blur (API 31+)
- [x] Add `blur_radius`.
- [x] Lower to `RenderEffect.createBlurEffect`.
- [x] Warn at compile time when `min_sdk < 31`. (Add if-else : if min_sdk>30, add blur-radius, else, nothing)

### 8.7 Static Transforms
- [ ] Add `rotation`.
- [ ] Add `scale_x`.
- [ ] Add `scale_y`.
- [ ] Add `translation_x`.
- [ ] Add `translation_y`.
- [ ] Lower to corresponding view setters.

## Phase 9: Explicit Animation DSL (Imperative Only)

### DSL (`dsl/app.py` or `dsl/animation.py`)
- [ ] Add `animate(id, ...)`.
- [ ] Add helpers: `fade_in`, `fade_out`, `rotate`, `scale`, `translate`, `animate_elevation`.
- [ ] Add composition helpers: `sequence(...)`, `parallel(...)`.

### Supported Properties
- [ ] `rotate`
- [ ] `scale`
- [ ] `scale_x`
- [ ] `scale_y`
- [ ] `translate_x`
- [ ] `translate_y`
- [ ] `alpha`
- [ ] `elevation`

### Common Params
- [ ] `duration`
- [ ] `delay`
- [ ] `interpolator`

### Lowering
- [ ] `ViewPropertyAnimator`.
- [ ] `ObjectAnimator`.
- [ ] `AnimatorSet`.

### Navigation Transitions
- [ ] Add `Screen(..., transition=...)`.
- [ ] Support `fade`, `slide_left`, `slide_right`, `slide_up`, `slide_down`.
- [ ] Lower to predefined animator methods.

### Forbidden (must stay forbidden)
- [ ] No state-bound implicit animations.
- [ ] No diff-based recomposition.
- [ ] No reactive animation runtime.

## Phase 10: Theme Expansion

### Theme Channels (`dsl/widgets.py`)
- [ ] Add `input`.
- [ ] Add `selector`.
- [ ] Add `progress`.
- [ ] Add `icon`.
- [ ] Add `container`.
- [ ] Add `appbar`.

### Resolution Order
- [ ] Enforce `inline attrs > style= > Theme channel > widget defaults`.
- [ ] Add lint/tests for deterministic precedence.

## Phase 11: Scroll Controls

### DSL and Validation
- [ ] Add `ScrollView`.
- [ ] Add `HorizontalScrollView`.
- [ ] Enforce single direct child at compile time.

### Lowering
- [ ] Emit corresponding widget constructors and layout wiring.

## Phase 12: RecyclerView (Static v1)

### DSL
- [ ] Add `ListView(items=[...], item_layout=...)` static-only shape.

### Lowering
- [ ] Deterministic adapter class generation.
- [ ] Stable view holder + bind logic.
- [ ] Compile-time-only dataset (no runtime diffing).

## Phase 13: Validation and Linting

### Compile-time Checks
- [ ] Style field incompatible with widget.
- [ ] Invalid state keys.
- [ ] Unsupported event binding target.
- [ ] Duplicate IDs.
- [ ] Animation target ID not found.
- [ ] Blur below API 31.
- [ ] Invalid gradient config.

### Diagnostics
- [ ] Error messages with widget id and field name.
- [ ] Warnings for degraded fallback behavior.

## Non-Goals (Locked)

- [ ] No reactive hooks.
- [ ] No CSS-style cascade engine.
- [ ] No dynamic theme switching in v1.
- [ ] No shader DSL in v1.
- [ ] No runtime layout diffing/recomposition.

## Execution Order (Recommended)

- [ ] Wave A: Phases 1, 2, 3 (style primitives + state colors).
- [ ] Wave B: Phases 4, 5, 6 (events + input + accessibility).
- [ ] Wave C: Phases 7, 8 (visual polish primitives).
- [ ] Wave D: Phase 9 (explicit animation layer).
- [ ] Wave E: Phases 10, 11, 12, 13 (theme expansion + containers + validation hardening).


---

## Appendix C) Verbatim Import — Anali_implement_immediate_plan.md

# Anali Implementation — Immediate Masterplan (Corrected & Locked)

Last updated: 2026-02-10

This document is a **corrected, implementation-ready refinement** of the Anali v7 masterplan.
It resolves contradictions, tightens scope, and aligns the plan with the **non-negotiable decision**:

> **Anali will not ship until it supports a statically linked core runtime,
> capability-scoped optional modules, and Play-delivered dynamic features.**

This is not aspirational. This is the execution plan.

---

## 0. Status of This Document

- ✅ Validated against current compiler architecture (AST → CFG → SSA → Dalvik)
- ✅ Consistent with Android platform constraints
- ✅ Realistic in terms of APK size, Play policy, and tooling
- ✅ Safe for long-term evolution (v2, v3 without breaking v1)

This replaces earlier ambiguous drafts.

---

## 1. What Anali *Is* (Reconfirmed)

Anali is:

- An **ahead-of-time compiler**
- Targeting **Android/Dalvik directly**
- Using a **restricted, Python-like DSL**
- Producing **fully native Android apps**
- With **no interpreter, no reflection, no runtime code execution**

Anali is **not**:
- A scripting engine
- A Python runtime
- A reactive framework
- A plugin host

---

## 2. Final Architecture (Locked)

```
User DSL
  ↓
Anali Compiler
  - AST validation
  - CFG / SSA construction
  - Static capability resolution
  - Deterministic Smali emission
  ↓
Core Runtime (always linked)
  +
Capability Modules (statically linked if used)
  +
Play Dynamic Features (installed on demand)
  ↓
Android Framework APIs
```

Everything above the Android framework is **fully deterministic**.

---

## 3. Compilation vs Runtime (Correct Separation)

### Compile Time (100% deterministic)

Compiled into Smali:
- UI tree (screens, widgets, layouts)
- Navigation graph
- Event handlers
- State layout
- Capability call sites
- Runtime glue selection
- Permission requirements

### Runtime (NO user code execution)

Runtime does **only**:
- Inflate precompiled views
- Dispatch events
- Manage screen stack
- Store state
- Call Android APIs
- Call capability modules

No user logic is interpreted at runtime.

---

## 4. Runtime Model (Corrected)

### 4.1 Core Runtime (Mandatory, Static)

Always packaged in **base.apk**.

Responsibilities:
- Screen stack manager
- Navigation controller
- Event dispatcher
- State storage (int-only)
- View binding helpers
- Error mapping (Smali → DSL)
- Unit helpers (dp/sp/percent)
- Internal utilities

Properties:
- Small (~50–100 KB)
- No permissions
- No heavy APIs
- No Play dependencies

This runtime defines **Anali identity**.

---

### 4.2 Capability-Scoped Runtime Modules (Static, Optional)

These are **not plugins**.
They are **conditionally linked libraries**.

Included **only if referenced by DSL**.

Examples:
- `anali.runtime.audio`
- `anali.runtime.video`
- `anali.runtime.webview`
- `anali.runtime.sensors`
- `anali.runtime.storage`
- `anali.runtime.permissions`
- `anali.runtime.network`
- `anali.runtime.intent`

Properties:
- Ahead-of-time compiled
- No reflection
- No dynamic dispatch
- Permission-aware
- Removed entirely if unused
- R8 tree-shakable

These modules provide **capabilities**, not widgets.

---

### 4.3 Play Feature Dynamic Modules (Heavy, Optional)

Used for **large or policy-sensitive features**.

Examples:
- Video pipelines
- Maps SDK
- ML / vision
- Large native (.so) libraries

Properties:
- Compiled ahead-of-time
- Delivered via Play Feature Delivery
- Installed on demand
- Loaded via system classloader
- No custom loaders, no hacks

Anali orchestrates usage — Android delivers code.

---

## 5. Capability Model (Final)

Capabilities are **compile-time features**, not runtime discovery.

Examples:
- Audio
- Video
- WebView
- Sensors
- Storage
- Clipboard
- Connectivity
- Permissions
- URL launching

Capabilities:
- Are resolved at compile time
- Generate direct Android API calls
- Control permission wiring
- Pull in the correct runtime module

Implementation status (2026-02-10): capability/permission inference and manifest injection are not implemented yet.

Optional explicit declaration:

```python
app_config(
    uses=[Audio, Video, WebView]
)
```

If omitted, compiler infers usage.

---

## 6. UI Model (Locked)

### Single Activity, Multi-Screen

- Exactly **one Android Activity**
- Multiple logical **Screens**
- Exactly **one active Screen**
- Stack-based navigation

Screens are **not Activities**.
They are view subtrees managed by runtime.

---

### UI Tree Rules

- UI declared top-down
- Tree is fully static
- No conditional widget creation
- No runtime widget creation
- All IDs known at compile time

---

## 7. Containers (v1 Only)

Allowed:
- Column
- Row
- Relative
- Constraint
- Implicit ScrollRoot (root always scrollable)

Explicitly rejected:
- RecyclerView
- Lazy lists
- Stack (Relative replaces it)
- Grid (later phase)

---

## 8. Widgets (v1)

Leaf widgets only:

- Text
- Button
- TextField
- Image
- Checkbox
- Switch
- Slider
- Dropdown
- IconButton
- FloatingActionButton
- AppBar (non-Material)

Each widget:
- Maps to a known Android View
- Has a fixed attribute schema
- Is statically analyzable

---

## 9. State Model (Corrected)

- Global state only (v1)
- Int-only
- Boolean = 0 / 1
- No strings, lists, dicts
- No dynamic keys

Allowed:
- assignment
- arithmetic
- comparison
- boolean logic

Navigation does NOT reset state automatically.

---

## 10. Event Handling

Supported:
- `on_click` only

Rules:
- Named functions only
- No lambdas
- No imports
- No arbitrary calls
- No widget creation

Allowed statements:
- assignment
- if / while
- Navigate / Back / Replace
- toast
- log
- exit_app
- set_text

Handlers are **imperative islands**.

---

## 11. Navigation (Final)

- `Navigate("Screen")` → push
- `Back()` → pop
- `Replace("Screen")` → replace top

Initial screen = first declared.

System back pops stack or exits.

No parameters in v1.

Implementation status (2026-02-10): stack navigation exists, but system back handling is not wired.

---

## 12. Debugging & Tooling

- Stable Smali emission
- Deterministic block numbering
- Smali → DSL line mapping
- Clear compile-time diagnostics

Goal:
> **Smali crashes always map back to DSL lines**

Dependency status (2026-02-10): direct AAR resolution is implemented; transitive AAR inference is not wired.

---

## 13. Capability Feasibility (Clarified)

### Fully Achievable via Capability Modules

- Audio / Video
- WebView
- Sensors
- Storage / SharedPreferences
- Clipboard
- Connectivity
- URL launcher
- Permissions
- File picker
- Maps
- Markdown (Text spans or WebView)

These **do not require** a scripting runtime.

---

### Not Included in Core Runtime (By Design)

- Audio/video decoding
- Maps SDK
- ML
- Web rendering engines
- Native libraries

These belong in:
- Capability modules
- Or Play Feature modules

This keeps base APK small.

---

## 14. What Anali Will *Never* Do

- Runtime Python execution
- Reflection-based dispatch
- Dynamic widget trees
- Reactive hooks (`use_state`, etc.)
- Plugin-defined execution models

Hybrid runtimes (Python/JS/etc.) may exist **only as optional plugins**,
never as core behavior.

---

## 15. Immediate Implementation Checklist

### Compiler
- ✅ Finalize Screen-only UI enforcement
- ✅ Lock attribute validation rules
- Capability resolution graph
- Permission inference
- ✅ Deterministic ordering everywhere

### Runtime
- Core runtime stabilization
- Capability module ABI
- ✅ Navigation engine
- ✅ State storage

### Toolchain
- ✅ Smali ↔ baksmali roundtrip tests
- APK size tracking
- Cold start benchmarks

---

## 16. UI Expansion Tracker (Locked for Execution)

The full UI v1 expansion backlog is now tracked in:
- `docs/UI_Surface_Expansion_TODO.md`

Execution order is locked by waves:
- Wave A: Typography, tinting, ColorState DSL (Phases 1–3)
- Wave B: Event surface, input configuration, accessibility (Phases 4–6)
- Wave C: Elevation/shadow + visual effects pack (Phases 7–8)
- Wave D: Explicit animation DSL + navigation transitions (Phase 9)
- Wave E: Theme expansion, scroll controls, static RecyclerView, lint hardening (Phases 10–13)

All work under this tracker must preserve:
- deterministic lowering
- ahead-of-time compilation
- no reactive runtime
- no implicit diffing/dynamic UI construction

---

## Final Lock

This plan is:
- Technically sound
- Android-policy compliant
- Competitive
- Honest about tradeoffs

If Anali ships with **this architecture**, it will be taken seriously.
