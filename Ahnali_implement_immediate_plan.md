# Ahnali Implementation — Immediate Masterplan (Corrected & Locked)

Last updated: 2026-02-10

This document is a **corrected, implementation-ready refinement** of the Ahnali v7 masterplan.
It resolves contradictions, tightens scope, and aligns the plan with the **non-negotiable decision**:

> **Ahnali will not ship until it supports a statically linked core runtime,
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

## 1. What Ahnali *Is* (Reconfirmed)

Ahnali is:

- An **ahead-of-time compiler**
- Targeting **Android/Dalvik directly**
- Using a **restricted, Python-like DSL**
- Producing **fully native Android apps**
- With **no interpreter, no reflection, no runtime code execution**

Ahnali is **not**:
- A scripting engine
- A Python runtime
- A reactive framework
- A plugin host

---

## 2. Final Architecture (Locked)

```
User DSL
  ↓
Ahnali Compiler
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

This runtime defines **Ahnali identity**.

---

### 4.2 Capability-Scoped Runtime Modules (Static, Optional)

These are **not plugins**.
They are **conditionally linked libraries**.

Included **only if referenced by DSL**.

Examples:
- `ahnali.runtime.audio`
- `ahnali.runtime.video`
- `ahnali.runtime.webview`
- `ahnali.runtime.sensors`
- `ahnali.runtime.storage`
- `ahnali.runtime.permissions`
- `ahnali.runtime.network`
- `ahnali.runtime.intent`

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

Ahnali orchestrates usage — Android delivers code.

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

## 14. What Ahnali Will *Never* Do

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

If Ahnali ships with **this architecture**, it will be taken seriously.
