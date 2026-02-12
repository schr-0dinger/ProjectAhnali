# Masterplan — Ultimate DSL Sugaring → Full Smali & API Coverage

**Scope:** This plan starts from the current state (Phase B complete: widgets + sugar helpers + signature mapping + click wiring + static state) and maps the path to a fully user‑friendly DSL, full smali opcode coverage (practical subset first, then complete), and broad Android API access.

**Guiding goals**
- Users never see smali, descriptors, or IR terms.
- DSL stays Pythonic and minimal.
- Every DSL feature has a runtime path (toolchain + device test).
- We grow bytecode coverage by production impact, not by completeness first.

**Plan reconciliation (2026-02-12)**
- ✅ Reviewed and reconciled: `Anali_Masterplan_v7.md`, `Anali_implement_immediate_plan.md`, `Masterplan_Ultimate.md`, `Anali_Dual_Mode_Architecture.md`.
- ✅ Canonical position: static AOT mode is default and identity; hybrid runtime is optional, capability-scoped, and non-structural by default.

---

## 0) Current Baseline (Done)
- ✅ One‑command build/install/run (`build_install_run`).
- ✅ DSL sugar: `simple_activity()`, `text_view`, `button`, `toast`, `linear_layout`, `add_view`, `on_click`.
- ✅ Click listener support class emitted by toolchain.
- ✅ Static fields + `x = x + 1` supported under the hood.
- ✅ String constants + basic calls + constructor support.
- ✅ Smoke tests (adb install/run + logcat check).

**Status Notes (2026-02-12, reality-checked)**
- ✅ Stack navigation exists and system back handling is wired (`onSystemBack` + wrapper `onBackPressed` bridge).
- ✅ Capability/permission inference and manifest permission injection are implemented.
- ✅ Direct AAR resolution is implemented.
- ✅ Library `R$*` class generation from merged symbols is implemented.
- Transitive AAR inference is not wired yet.
- ✅ Current test reality: `186 passed` (`PYTHONPATH=. pytest -q`).

---

## 0.1) Dual-Mode Architecture (Integrated)

### Mode A — Static Mode (Default, Canonical)
- ✅ Entire UI compiled at build time.
- ✅ Navigation graph and handlers compiled.
- ✅ State wiring compiled.
- ✅ No runtime interpreter or reflection.

### Mode B — Hybrid Mode (Optional Plugin Layer)
- Optional activation via app config/plugin boundary.
- Stage-gated and capability-scoped.
- UI remains static; hybrid logic can mutate state and trigger approved actions.
- Android API access remains via Anali capability wrappers.

### Hybrid Rollout Phases
- ✅ Phase 0 (static foundation): deterministic emission, navigation, capabilities, permissions/manifest wiring, AAR merge foundations.
- Phase 1: native execution layer (NDK + JNI bridge).
- Phase 2: optional Python runtime plugin on top of JNI bridge, with bounded mutation rules.

---

## 1) Ultimate DSL Sugaring (User-Facing)

### 1.1 Target Syntax (Pythonic, no internals)
```python
from dsl.app import app, activity, state, ui, text, button, on_click

app(
    activity("MainActivity",
        state(count=0),
        ui(
            text("Count: 0", id="label"),
            button("+", id="inc"),
            button("-", id="dec"),
        ),
        on_click("inc", [
            "count += 1",
            "label.text = f'Count: {count}'",
        ]),
        on_click("dec", [
            "count -= 1",
            "label.text = f'Count: {count}'",
        ]),
    )
)
```

### 1.2 Deliverables
- ✅ DSL builder objects with `.build()` → ProgramIR.
- ✅ Tiny expression parser for:
  - `x += 1`, `x -= 1`
  - `label.text = f'Count: {count}'`
- ✅ Auto‑wiring of:
  - static fields (state)
  - UI view registry (by `id`)
  - click handlers → auto‑generated methods

### 1.3 Implementation Steps
1. ✅ Add Pythonic sugar surface in `dsl/api.py` (re-exported by `dsl/app.py`) with:
   - `app(...)`, `activity(...)`, `state(...)`, `ui(...)`, `text(...)`, `button(...)`, `on_click(...)`
2. ✅ Implement string‑expression compiler:
   - Simple tokenizer for `+=` and `f""` placeholders
   - Replace `f"Count: {count}"` → `"Count: " + valueOf(count)`
3. ✅ Translate sugar -> existing DSL helpers:
   - `state(count=0)` → static field + initialization
   - `text(...)` / `button(...)` → `text_view(...)` / `button(...)`
   - `on_click(...)` → `click_handler(...)` + `on_click(...)`
4. ✅ Tests:
   - Golden smali checks for UI + state + click
   - End‑to‑end install/run smoke

### 1.4 Exit Criteria
- User writes only sugar DSL.
- No internal symbols (`ctx`, `var`, `owner`) appear in user code.
- HelloWorld + Counter sample works on device.

---

## 2) UI Layout System (Minimal → Common)

### 2.1 Minimal Layout (Phase C)
- ✅ LinearLayout + addView (already done)
- ✅ Set padding, layout params, and container gravity/alignment wiring
- ✅ TextView style knobs:
  - `setTextSize`, `setTextColor`, `setTextAlignment`
- ✅ Button style knobs:
  - `setAllCaps`, `setEnabled`

### 2.2 Common Layouts
- ✅ RelativeLayout / ConstraintLayout
- ✅ Layout params builders

### 2.3 Deliverables
- `layout(...)` DSL wrappers:
  - ✅ `column(...)`, ✅ `row(...)`, `stack(...)` (pending)
  - ✅ `text(...)`, ✅ `button(...)`, ✅ `image(...)`
- ✅ Automatic view registry and parent/child wiring
- ✅ Tests for core layout primitives

---

## 3) Core Smali/DEX Coverage (Pragmatic Order)

### 3.1 Must-Have Ops (App usability)
- ✅ `invoke-interface`, `invoke-super`
- ✅ `sget`, `sput`, `iget`, `iput`
- ✅ `check-cast`, `instance-of`
- ✅ `new-array`, `aget`, `aput`
- ✅ `move-result-object`

### 3.1.a Bytecode Expansion Plan (Detailed)
**Step 1: Arrays**
- ✅ IR: `NewArray`, `ArrayGet`, `ArraySet` (+ element type)
- ✅ Dalvik: `new-array`, `filled-new-array` (optional), `aget/aget-object`, `aput/aput-object`
- ✅ Emit: choose op by elem descriptor (`I/Z/F/L...;`)
- ✅ Tests: golden smali + runtime sanity

**Step 2: Invoke Variants**
- ✅ `invoke-interface`, `invoke-super`, `invoke-virtual`, `invoke-static`, `invoke-direct`
- ✅ Validate args: receiver rules for instance invokes
- ✅ Support `move-result-object` / `move-result` mapping by return type

**Step 3: Exceptions**
- ✅ Explicit try/catch blocks (already supported)
- ✅ Validate range labels + handler descriptors
- ✅ Add tests for multiple handlers ordering and catchall

**Step 4: Primitive Conversions**
- ✅ IR: `Cast` / `Convert`
- ✅ Dalvik: `int-to-float`, `float-to-int`, `int-to-long`, `long-to-int`, etc.
- ✅ Verify type inference + type-verify gate

### 3.2 Medium Priority
- `switch` (packed/sparse)
- `monitor-enter/exit` (synchronization)
- ✅ `throw`, ✅ `try/catch`

### 3.3 Full Coverage (Completeness)
- Remaining opcodes from Dalvik/DEX table
- Verification against Smali reference suite

### 3.4 Exit Criteria
- 95% of practical apps compile
- All compiler instructions map to valid smali

---

## 4) API Coverage Roadmap

### 4.1 Immediate APIs (1–2 weeks)
- ✅ Logcat (`Log.d/i/w/e`)
- ✅ Toasts
- ✅ Dialogs
- SharedPreferences

### 4.2 UI APIs (2–4 weeks)
- ✅ TextView / EditText
- RecyclerView
- ✅ Button click listeners (named handlers; lambdas intentionally unsupported)
- ✅ View binding sugar

### 4.3 System APIs (4–8 weeks)
- Notifications
- Camera (CameraX)
- Location services
- File picker / storage APIs

### 4.4 Deliverables
- ✅ Signature database for SDK methods
- Permission DSL:
  - ✅ `request_permission("CAMERA")` / `request_permissions(...)`
  - ✅ auto‑manifest updates
- Resource DSL:
  - ✅ string resources, icons, styles

### 4.5 Signature Database (Detailed Plan)
**Goal:** Map Pythonic calls → exact Android signatures automatically.

**Phase A: Minimal Curated Table**
- ✅ JSON signature DB in repo: `dsl/android/signatures_db.json`
- ✅ Curated/manual signature entries for core calls
- ✅ Loaded by DSL at import time

**Phase B: SDK Extraction**
- ✅ Parse `android.jar` / public stubs to generate signature index:
  - `class -> method -> [overloads]`
- ✅ Signature tooling for DB generation (`tools/build_signature_db.py`)

**Phase C: Overload Resolution**
- ✅ Use arg count + known/inferred types to pick overload
- ✅ Fail with user-facing errors for mismatches

**Phase D: Caching + Versioning**
- Cache by SDK version in build dir
- Allow `target_sdk` selection

---

## 5) Toolchain Polish (Production‑ready)

### 5.1 Build System
- Debug/release variants
- Deterministic APK output
- Versioning + reproducible builds

### 5.1.a Build Variants + Signing
- ✅ `debug` uses auto‑generated keystore
- `release` requires user keystore + alias + passwords
- Support v2/v3 signing (apksigner options)
- Store keystore config in `build.toml` or env vars

### 5.2 Resource Pipeline
- ✅ aapt2 resource staging
- ✅ icons, strings, themes
- layout XML (optional)

### 5.2.b Library R Class Handling (Foundational)
- ✅ Parse AAR `R.txt` + merged `R.txt` symbols from aapt2.
- ✅ Generate library `R$*` smali classes (attrs/styleables/etc.) into dex.
- ✅ Ensure resource IDs align with aapt2 output (stable IDs).
- Add tests with Material AAR to prevent `NoClassDefFoundError`.

### 5.2.a aapt2 Integration (Detailed)
- ✅ Generate `AndroidManifest.xml` from DSL + permissions
- Generate resource folders:
  - ✅ `res/drawable`, ✅ `res/values/strings.xml`
- ✅ Invoke `aapt2 compile` and `aapt2 link`
- ✅ Track `R.txt` equivalent mapping for resource IDs

### 5.3 Lint + Diagnostics
- ✅ Type/arity verification (expanded)
- ✅ Signature validation diagnostics
- Smali verifier checks pre‑APK

### 5.3.a Conversion/Lint Passes
- ✅ Primitive conversion correctness checks
- ✅ Illegal invoke types flagged early
- Array bounds warnings (optional)

### 5.4 CI + Regression
- ✅ Unit + integration + device smoke scaffolding/tests
- Golden smali snapshots in CI

---

## 6) Final Milestones

### Milestone A — “Friendly DSL”
- Users can author full apps in 10–20 lines
- No smali or descriptor exposure

### Milestone B — “Feature Usable”
- ~80% of common APIs and widgets supported
- Strong runtime stability on device

### Milestone C — “Production Ready”
- Release signing, variant builds, CI gating
- Full smali bytecode coverage
- Developer docs and examples

---

## 6.1) Dual-Mode Delivery Milestones

### Milestone D — “Native Hybrid Bridge”
- NDK integration and JNI boundary merged.
- Capability-scoped native entrypoints only.

### Milestone E — “Optional Python Plugin”
- Optional embedded Python runtime behind explicit config.
- State mutation + capability calls allowed; static UI invariants preserved.
- Bounded dynamic regions only where explicitly declared mutable.

---

## 7) UI Surface Expansion Program (Planned)

The full v1 UI expansion backlog is now tracked in:
- `docs/UI_Surface_Expansion_TODO.md`

This tracker is the source of truth for:
- Typography and advanced text controls
- Control tinting and stateful colors
- Expanded event surface
- Input and accessibility
- Visual effects and explicit animation DSL
- Theme channel expansion, scroll controls, static RecyclerView
- Compile-time lint/validation hardening

Execution follows wave ordering from the tracker to keep lowering deterministic and testable.

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

### 8.1 Structure APIs (UI Tree and Layout)

Core structural primitives:
- Screen
- Activity (single-activity model)
- Column (LinearLayout vertical)
- Row (LinearLayout horizontal)
- Container
- Card
- View
- Relative
- Constraint
- ScrollView
- HorizontalScrollView
- FrameLayout
- ListView
- GridView
- RecyclerView (static adapter model)
- ViewPager (static page model)
- TabLayout
- NavigationBar
- NavigationRail
- DrawerLayout
- BottomNavigationView
- Toolbar
- AppBar
- CoordinatorLayout
- NestedScrollView
- Fragment container (if later supported)

Structural modifiers:
- width/height
- match/wrap/fill
- percent
- weight
- margin
- padding
- gravity
- layout_gravity
- constraints
- relative rules
- alignment
- orientation
- z-index (elevation layering)

### 8.2 Style APIs (Visual and Appearance)

Typography:
- text_color
- text_size
- font_family
- font_weight
- font_style
- letter_spacing
- line_height
- text_alignment
- max_lines
- ellipsize
- all_caps
- hint_color
- highlight_color
- text_shadow

Color and background:
- background_color
- gradient background
- radial gradient
- sweep gradient
- border_width
- border_color
- border_radius
- per-corner radius
- ripple_color
- opacity
- elevation
- clip_to_outline
- clip_children

Stateful styling:
- ColorState (default/pressed/disabled/selected/focused)
- background tint
- text tint
- progress tint
- thumb tint
- track tint
- button tint

Image styling:
- scaleType
- crop
- centerInside
- adjustViewBounds
- tint
- image alpha
- image matrix transform

Progress styling:
- indeterminate tint
- progress tint
- secondary progress tint

Switch/Checkbox/Radio styling:
- button tint
- thumb tint
- track tint

### 8.3 Interaction APIs (Event Surface)

Click and touch:
- on_click
- on_long_click
- on_double_tap
- on_touch
- on_swipe
- on_drag
- on_drop
- on_scroll
- on_fling

Input events:
- on_text_change
- on_editor_action
- on_focus_change
- on_key
- on_change (Switch/Checkbox/Radio/Slider/RadioGroup)
- on_slider_change (optional alias; `on_change` is canonical)
- on_item_selected
- on_menu_item_selected

Navigation:
- Navigate
- Back
- Replace
- PopToRoot
- ClearStack

Gesture detection:
- pinch
- zoom
- rotate gesture
- drag
- scale gesture detector

### 8.4 State APIs (Deterministic App Data)

Global state:
- state()
- static fields
- integer fields
- boolean fields
- numeric operations
- comparisons
- branching

Persistence:
- SharedPreferences
- DataStore
- file storage (internal/external)
- SQLite
- Room (if statically supported)
- encrypted storage

Lifecycle state:
- on_start
- on_resume
- on_pause
- on_stop
- on_destroy

### 8.5 Capability APIs (Platform Services)

Permissions:
- request_permission
- request_permissions
- check_permission
- runtime permission handling

Audio:
- MediaPlayer
- ExoPlayer
- SoundPool
- AudioManager
- audio focus
- audio recording
- microphone access

Video:
- VideoView
- MediaPlayer video
- CameraX
- MediaRecorder
- video playback controls

Camera:
- CameraX preview
- image capture
- video capture
- flash control
- focus control

Sensors:
- accelerometer
- gyroscope
- magnetometer
- light sensor
- proximity sensor
- step counter

Location:
- FusedLocationProvider
- GPS
- geofencing

Networking:
- HTTP requests
- OkHttp
- Retrofit
- WebSockets
- ConnectivityManager
- DownloadManager

Web:
- WebView
- WebSettings
- JS bridge
- file chooser
- cookie manager

Notifications:
- NotificationManager
- channels
- push notifications
- foreground service notification

Background work:
- WorkManager
- AlarmManager
- JobScheduler
- foreground services
- BroadcastReceiver

Storage:
- internal storage
- external storage
- MediaStore
- file picker
- SAF (Storage Access Framework)

Sharing and intents:
- open URL
- share text
- share file
- open external app
- deep linking
- custom URI schemes

Clipboard:
- copy
- paste
- clear

Biometrics:
- fingerprint
- face authentication

Maps:
- Google Maps SDK
- map markers
- camera movement
- map gestures

Bluetooth:
- classic Bluetooth
- BLE
- device scanning

NFC:
- NFC read/write

System UI:
- status bar control
- immersive mode
- orientation lock
- screen brightness
- WakeLock

### 8.6 Motion APIs (Animation and Effects)

Explicit animations:
- animate
- fade_in
- fade_out
- rotate
- scale
- translate
- animate_elevation
- alpha animation

Animator composition:
- sequence
- parallel
- repeat
- reverse
- interpolators

ViewPropertyAnimator:
- duration
- delay
- interpolator
- withEndAction
- withStartAction

ObjectAnimator:
- property animation
- multi-property animation
- AnimatorSet

Transition APIs:
- scene transition
- layout transition
- fade transition
- slide transition
- explode transition
- shared element transition

Navigation transitions:
- screen enter animation
- screen exit animation
- back navigation animation

Visual effects:
- blur (API 31+) - TODO: Add a flag for API version check and fallback for older versions.
- elevation shadow
- text shadow
- ripple
- opacity
- gradient
- transform matrix

### 8.7 Advanced Graphics (Optional Future)

Canvas:
- drawRect
- drawCircle
- drawPath
- drawBitmap
- drawText

Paint:
- stroke width
- stroke color
- style
- shader

Hardware acceleration:
- layer type control

### 8.8 System and App Control

App control:
- exit_app
- restart_app
- clear_cache
- clear_data

Build config:
- package
- version
- min_sdk
- target_sdk
- debuggable
- keystore

### 8.9 Security and Privacy

- secure flag
- block screenshots
- encryption
- secure preferences
- network security config

### 8.10 Testing and Debug

- log
- debug overlay
- performance metrics
- trace sections

Conclusion:
- This inventory covers nearly everything achievable in standard native Android Java, reorganized into Anali layers.
- Not all items belong in v1.
- Architecturally, this is the full surface Anali can grow into without violating AOT deterministic principles.

### 8.11 API Surface Modularization Plan (`dsl/api.py` Simplification)

Target package split:

```text
dsl/
  structure.py
  style.py
  interaction.py
  state.py
  capability.py
  motion.py
```

Rules:
- Widgets remain in `dsl/widgets.py` and widget classes/functions stay separate from domain facades.
- `dsl/api.py` becomes a thin compatibility layer that only re-exports public APIs from the six domain modules.
- No business logic should remain in `dsl/api.py` after migration.

User mental model (official):
- Structure = layout
- Style = appearance
- Interaction = events
- State = data
- Capability = platform access
- Motion = animation

Migration steps:
1. Create `dsl/structure.py` and move layout/screen/navigation structure-facing exports.
2. Create `dsl/style.py` and move theme/style/color-state/fill-wrap-size-facing exports.
3. Create `dsl/interaction.py` and move event declarations/handler decorators and interaction helpers.
4. Create `dsl/state.py` and move state declarations and deterministic state operations.
5. Create `dsl/capability.py` and move capability/permission surface exports.
6. Create `dsl/motion.py` and move animation/transition APIs.
7. Reduce `dsl/api.py` to grouped re-exports only.
8. Add API-equivalence tests to ensure old import paths continue to work.
9. Update docs/examples to prefer domain imports while keeping `dsl.app`/`dsl.api` compatibility.

Acceptance criteria:
- `dsl/api.py` contains no lowering logic, no compilation logic, no helper implementation logic.
- All public APIs remain import-compatible for existing projects.
- New docs teach the six-module mental model first.

---

## What’s Next (Immediate Work)
1. ✅ Implement **Library R class handling** (merged symbols → library `R$*` smali).
2. Validate **AAR class/resource merge** on device (Material smoke test).
3. ✅ Draft **Navigation API** and wire minimal multi‑screen prototype.
4. ✅ Start UI expansion **Wave A** from `docs/UI_Surface_Expansion_TODO.md` (Phases 1–3).
5. Start API modularization of `dsl/api.py` into the six domain modules above.
6. Start Dual Mode **Phase 1**: NDK + JNI native execution layer (hybrid foundation).

--- 

**Note:** This plan is meant to evolve. As soon as the Pythonic DSL is in place, every subsequent feature should be added through that layer (not via internal helper APIs).
