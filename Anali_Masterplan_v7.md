# Anali Masterplan — v7 (Foundational Release Alignment)

Last updated: 2026-02-10

Anali is an ahead-of-time Android compiler that translates a restricted, Python-like DSL directly into Smali/Dalvik bytecode.

There is:
- no Python runtime
- no JVM execution layer
- no reflection
- no dynamic UI construction

v1 is not a prototype.
v1 is the long-term foundation.

---

## 1. Core Philosophy

Anali is built on three non-negotiable principles:

1. Ahead-of-time compilation only
2. Deterministic behavior
3. Explicit capabilities, not implicit magic

Anali intentionally rejects:
- runtime interpretation
- reflection
- dynamic widget trees
- plugin-driven execution models

Anali embraces:
- static analysis
- explicit structure
- compile-time validation
- Android-native execution

---

## 2. High-Level Architecture

User DSL (restricted Python-like syntax)
→ Anali Compiler (AST → CFG → SSA → Dalvik)
→ Runtime Support (static + modular)
→ Android Framework APIs

---

## 3. Compilation Model

### Compiled Ahead of Time
- Entire UI tree
- Navigation graph
- Event handlers
- State mutations
- Capability calls
- Runtime glue code

### Runtime Responsibilities
- View inflation
- Event dispatch
- Navigation transitions
- Capability invocation
- Android framework calls

No user code is interpreted at runtime.

---

## 4. Runtime Strategy

Anali uses a hybrid static + modular runtime model.

### 4.1 Core Runtime (Always Linked)

- Delivered inside base.apk
- Always present

Responsibilities:
- Screen stack manager
- Navigation controller
- State storage
- Event dispatcher
- UI binding glue
- Error mapping
- Common utilities (dp, sp, colors)

Properties:
- Small footprint
- No permissions
- No heavy Android APIs

This is Anali’s identity layer.

---

### 4.2 Capability-Scoped Runtime Modules

Included only if the DSL references them.

Examples:
- anali.runtime.audio
- anali.runtime.video
- anali.runtime.webview
- anali.runtime.sensors
- anali.runtime.storage
- anali.runtime.permissions
- anali.runtime.intent

Properties:
- Statically analyzable
- No reflection
- Tree-shaken by R8
- Permission-aware

These are compiled dependencies, not plugins.

---

### 4.3 Play-Delivered Dynamic Feature Modules

Used for heavy or rarely used features.

Examples:
- Video pipelines
- Maps SDK
- ML / vision
- Large native libraries

Properties:
- Ahead-of-time compiled
- Installed on demand via Play
- Loaded by system classloader
- No dynamic execution hacks

---

## 5. Capability Model

Capabilities are explicit feature accessors, not widgets.

Examples:
- Audio
- Video
- WebView
- Sensors
- Storage
- Permissions
- Networking
- Intent launching

Capabilities are:
- statically resolved
- permission-aware
- mapped directly to Android APIs

Implementation status (2026-02-10): capability/permission inference and manifest injection are not implemented yet.

Optional explicit declaration:

```python
app_config(
    uses=[Audio, Video, WebView]
)
```

---

## 6. UI Model

### Single Activity, Multi-Screen

- Exactly one Android Activity
- Multiple logical Screens
- Exactly one active screen at a time
- Stack-based navigation

Screens are not Android Activities.

---

### UI Tree Rules

- UI is defined top-down
- UI tree is static
- No conditional widget creation
- No runtime widget construction
- IDs are compile-time constants

---

## 7. Containers (v1)

Allowed:
- Column
- Row
- Relative
- Constraint
- Implicit ScrollRoot (root always scrollable)

Rejected in v1:
- Stack
- Grid
- RecyclerView
- Lazy lists

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
- maps to a known Android View
- has a fixed attribute schema
- is statically analyzable

---

## 9. Attribute System

### Common Attributes
- id
- width / height
- padding / margin
- visibility (visible | invisible | gone)
- enabled
- background
- radius
- style

### Layout-Specific
- weight (Row / Column only)
- percent (Row width / Column height only)
- alignment
- relative rules
- constraint rules

### Units
- dp(x)
- sp(x)
- px(x)
- percent(x)
- wrap
- match

Invalid combinations are compile-time errors.

---

## 10. Style System

Components:
- Style(...) reusable objects
- Theme(...) global defaults
- Presets for beginners

Precedence:
1. Inline attributes
2. Explicit style=
3. Theme defaults
4. Widget defaults

No cascading magic.

---

## 11. State Model (v1)

Properties:
- Global state only
- Int-only
- Booleans are 0/1
- No strings, lists, dicts
- No dynamic keys

Allowed operations:
- assignment
- arithmetic
- comparison
- boolean logic

Navigation does not reset state unless explicitly changed.

---

## 12. Event Handling Model

Supported:
- on_click only

Handler rules:
- Named functions only
- No lambdas
- No arbitrary function calls
- No widget creation
- No imports

Allowed statements:
- assignment
- if / while
- Navigate / Back / Replace
- toast
- log
- exit_app
- set_text

Handlers are imperative islands.

---

## 13. Navigation DSL

Semantics:
- Navigate("Screen") → push
- Back() → pop
- Replace("Screen") → replace top

Initial screen = first declared Screen.

System back pops stack or exits app.

No parameters in v1.

Implementation status (2026-02-10): stack navigation exists, but system back handling is not wired.

---

## 14. Forbidden Patterns

Hard compile-time errors:
- Widgets inside handlers
- Conditional UI trees
- Loops generating widgets
- Arbitrary Python calls
- Reflection / eval
- Dynamic IDs
- Runtime widget lookup
- UI outside Screen(...)

---

## 15. Debugging Model

- Smali line mapping back to DSL
- Deterministic codegen
- Stable block ordering
- Explicit diagnostics

Goal: Smali errors trace back to DSL.

---

## 16. What Anali Is / Is Not

Anali is:
- A compiler
- Android-native
- Deterministic
- Capability-driven
- Ahead-of-time

Anali is not:
- React
- Flutter
- Compose
- A Python runtime
- A scripting environment

---

## Final Position

Anali will ship only when:
- Core runtime is statically linked
- Capabilities are modular and scoped
- Heavy features are Play-deliverable
- DSL is strict, readable, and analyzable
- Generated apps behave like native Android apps

---

## Capability Map (Feasibility)

### Can Implement Now (or very small additions)
- Basic widgets/layouts: AppBar, Button, Checkbox, Column, Row, Container, Card, Divider, Text, TextField, Image, Icon, IconButton, FloatingActionButton, Slider, Switch, Radio, RadioGroup, ProgressBar, Stack (as Relative), View.
- Simple menus: PopupMenuButton, ContextMenu (via Android PopupMenu), AlertDialog (already).
- Simple layout helpers: SafeArea (via padding from status bar), Placeholder.
- Simple pickers: DatePicker, TimePicker.
- Basic scroll: ListView, GridView (adapter-backed).
- Events: tap/click, basic keyboard events, scroll events.

### Can Implement With Reasonable Work (needs DSL + runtime support)
- Navigation: NavigationBar, NavigationDrawer, NavigationRail, Tabs, Page, Pagelet, MultiView (needs fragment/activity or view-stack manager).
- Input UX: AutoComplete, SearchBar, SelectionArea, TextSelectionChangeEvent.
- Complex widgets: ExpansionTile, ExpansionPanel(List), Chip, Badge, Banner, BottomSheet, BottomAppBar.
- Drag/Drop: DragTarget, Draggable, ReorderableListView, ReorderableDragHandle, Dismissible.
- Data components: DataTable, DataTable2, Charts (needs adapter + canvas).
- Media: Video, Audio, AudioRecorder (Android media APIs + permissions).
- Web: WebView (Android WebView + config).
- Markdown (render to TextView with spans or WebView).
- Lottie, Rive (AARs + asset pipelines).
- Map (AAR + API keys + manifest wiring).
- AnimatedSwitcher, Shimmer, ShaderMask, InteractiveViewer (animation/graphics work).
- Canvas (custom View + draw pipeline).
- Screenshot (requires view capture + storage permissions).

### Not Currently Feasible / Out of Scope Without Major Platform Work
- Desktop/window APIs: WindowDragArea, WindowEvent, WindowResizeEdge.
- Multi-platform abstractions: FletApp, FletTestApp, PagePlatform, WebRenderer, WebBrowserName, BrowserConfiguration, BrowserContextMenu.
- iOS/macOS specific: IosUtsname, KeychainAccessibility, Cupertino* enums.
- “Services” that require OS-level background services or cross-platform plugin layer without a runtime: Wakelock, SemanticsService, ShakeDetector (possible but big runtime scope).
- React-style hooks: use_state, use_effect, use_memo, etc. (requires a reactive runtime not currently in Anali).

### Classes / Enums
- Most style/geometry/value classes (Padding, Margin, Border, Color, Size, Gradient, TextStyle, Theme, etc.) are implementable.
- Platform/renderer enums (WebRenderer, PagePlatform, Cupertino enums) are out of scope unless those platforms are targeted.
- Many events are feasible once underlying widget exists; those tied to unsupported widgets or multi-platform are not.

---

## Execution Plan (Phased)

### Phase 0: Baseline Stabilization (Immediate)
1. ✅ Enforce DSL structural rules (Screen-only layouts, unique ids, single root per Screen).
2. ✅ Extend static validation:
   - ✅ Reject mixed Screen/non-Screen UI.
   - ✅ Lint global state usage in multi-screen apps.
   - ✅ Confirm all referenced ids exist at compile time.
3. ✅ Hard-fail on invalid smali emission:
   - ✅ Register bounds, branch targets, try/catch structure.
4. ✅ Maintain deterministic emission:
   - ✅ Sorted methods/fields, stable resource ordering, stable class layout.

### Phase 1: Core Runtime + Capability Registry (v1)
1. Core runtime always linked:
   - Screen stack manager, navigation controller, event dispatcher, state storage.
2. Capability registry:
   - Compile-time resolution of required modules.
   - Link-time inclusion of only referenced runtime modules.
3. Capability manifest:
   - Explicit `uses=[...]` optional declaration.
   - Permission-aware mapping to Android APIs.
4. Zero reflection, no dynamic dispatch.

### Phase 2: Navigation + View-Stack Engine
1. Define navigation semantics:
   - Navigate / Back / Replace.
   - Stack-based screen transitions.
2. Add Navigation UI:
   - NavigationBar, NavigationRail, Tabs, Drawer.
3. Runtime module:
   - Stack transitions, screen visibility, optional animations.
4. Tests:
   - Multi-screen navigation correctness.
   - Rebuild determinism: compile twice, identical smali output.

### Phase 3: Input + Form UX
1. AutoComplete/SearchBar/SelectionArea:
   - Adapter-based text suggestion.
   - Text selection events.
2. Text field enhancements:
   - Input validation, formatting, input filters.
3. Minimal accessibility hooks.

### Phase 4: Data + Lists
1. Adapter framework:
   - ListView, GridView, DataTable.
2. Reorderable/Dismissible:
   - Drag/drop + swipe.
3. Declarative data binding:
   - Compile-time binding between state and adapters.

### Phase 5: Media + Web
1. Audio/Video player wrappers.
2. WebView embedding + config DSL.
3. Screenshot capture helpers.

### Phase 6: Graphics + Animation
1. Canvas + drawing primitives.
2. AnimatedSwitcher/Shimmer/ShaderMask/InteractiveViewer.
3. Lottie/Rive integration (AAR + asset pipeline).

### Phase 7: Maps + Sensors
1. Map integration with key management.
2. Sensor services (accelerometer, gyroscope, etc.).
3. Permission model for sensitive capabilities.

---

## Toolchain & Testing Plan
1. ✅ Toolchain diagnostics:
   - ✅ Validate smali/baksmali availability.
   - ✅ Validate aapt2, zipalign, apksigner.
2. ✅ Pipeline tests:
   - ✅ End-to-end compile → smali → baksmali → smali roundtrip.
   - UI smoke apps (navigation, forms, lists).
3. Benchmarks:
   - APK size.
   - Cold start time.
   - Memory footprint.

Dependency status (2026-02-10): direct AAR resolution is implemented; transitive AAR inference is not wired.

---

## Release Milestones
1. Alpha: deterministic compile, core runtime, navigation.
2. Beta: media + web + adapters, stable capabilities.
3. v1.0: capability registry, maps/sensors, benchmarks, docs.

---

## Open Risks / Decisions
- Runtime versioning: how to preserve compatibility across DSL upgrades.
- Permissions & security boundaries for capability modules.
- Play feature module policy and lifecycle.
- Build pipeline stability across Android SDK versions.
