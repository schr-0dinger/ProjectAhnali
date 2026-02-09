# Masterplan — Ultimate DSL Sugaring → Full Smali & API Coverage

**Scope:** This plan starts from the current state (Phase B complete: widgets + sugar helpers + signature mapping + click wiring + static state) and maps the path to a fully user‑friendly DSL, full smali opcode coverage (practical subset first, then complete), and broad Android API access.

**Guiding goals**
- Users never see smali, descriptors, or IR terms.
- DSL stays Pythonic and minimal.
- Every DSL feature has a runtime path (toolchain + device test).
- We grow bytecode coverage by production impact, not by completeness first.

---

## 0) Current Baseline (Done)
- One‑command build/install/run (`build_install_run`).
- DSL sugar: `simple_activity()`, `text_view`, `button`, `toast`, `linear_layout`, `add_view`, `on_click`.
- Click listener support class emitted by toolchain.
- Static fields + `x = x + 1` supported under the hood.
- String constants + basic calls + constructor support.
- Smoke tests (adb install/run + logcat check).

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
- DSL builder objects with `.build()` → ProgramIR.
- Tiny expression parser for:
  - `x += 1`, `x -= 1`
  - `label.text = f'Count: {count}'`
- Auto‑wiring of:
  - static fields (state)
  - UI view registry (by `id`)
  - click handlers → auto‑generated methods

### 1.3 Implementation Steps
1. Add `dsl/sugar.py` with:
   - `app(...)`, `activity(...)`, `state(...)`, `ui(...)`, `text(...)`, `button(...)`, `on_click(...)`
2. Implement string‑expression compiler:
   - Simple tokenizer for `+=` and `f""` placeholders
   - Replace `f"Count: {count}"` → `"Count: " + valueOf(count)`
3. Translate sugar -> existing DSL helpers:
   - `state(count=0)` → static field + initialization
   - `text(...)` / `button(...)` → `text_view(...)` / `button(...)`
   - `on_click(...)` → `click_handler(...)` + `on_click(...)`
4. Tests:
   - Golden smali checks for UI + state + click
   - End‑to‑end install/run smoke

### 1.4 Exit Criteria
- User writes only sugar DSL.
- No internal symbols (`ctx`, `var`, `owner`) appear in user code.
- HelloWorld + Counter sample works on device.

---

## 2) UI Layout System (Minimal → Common)

### 2.1 Minimal Layout (Phase C)
- LinearLayout + addView (already done)
- Set padding, gravity, layout params
- TextView style knobs:
  - `setTextSize`, `setTextColor`, `setGravity`
- Button style knobs:
  - `setAllCaps`, `setEnabled`

### 2.2 Common Layouts
- RelativeLayout / ConstraintLayout
- Layout params builders

### 2.3 Deliverables
- `layout(...)` DSL wrappers:
  - `column(...)`, `row(...)`, `stack(...)`
  - `text(...)`, `button(...)`, `image(...)`
- Automatic view registry and parent/child wiring
- Tests for each layout primitive

---

## 3) Core Smali/DEX Coverage (Pragmatic Order)

### 3.1 Must-Have Ops (App usability)
- `invoke-interface`, `invoke-super`
- `iget`, `iput`, `sget`, `sput` (done: sget/sput)
- `const-class`, `check-cast`, `instance-of`
- `new-array`, `aget`, `aput`
- `move-object`, `move-result-object`

### 3.1.a Bytecode Expansion Plan (Detailed)
**Step 1: Arrays**
- IR: `NewArray`, `ArrayGet`, `ArraySet` (+ element type)
- Dalvik: `new-array`, `filled-new-array` (optional), `aget/aget-object`, `aput/aput-object`
- Emit: choose op by elem descriptor (`I/Z/F/L...;`)
- Tests: golden smali + runtime sanity

**Step 2: Invoke Variants**
- `invoke-interface`, `invoke-super`, `invoke-virtual`, `invoke-static`, `invoke-direct`
- Validate args: receiver rules for instance invokes
- Support `move-result-object` / `move-result` mapping by return type

**Step 3: Exceptions**
- Explicit try/catch blocks (already supported)
- Validate range labels + handler descriptors
- Add tests for multiple handlers ordering and catchall

**Step 4: Primitive Conversions**
- IR: `Cast` / `Convert`
- Dalvik: `int-to-float`, `float-to-int`, `int-to-long`, `long-to-int`, etc.
- Verify type inference + type-verify gate

### 3.2 Medium Priority
- `switch` (packed/sparse)
- `monitor-enter/exit` (synchronization)
- `throw` (done), `try/catch` (done)

### 3.3 Full Coverage (Completeness)
- Remaining opcodes from Dalvik/DEX table
- Verification against Smali reference suite

### 3.4 Exit Criteria
- 95% of practical apps compile
- All compiler instructions map to valid smali

---

## 4) API Coverage Roadmap

### 4.1 Immediate APIs (1–2 weeks)
- Logcat (`Log.d/i/w/e`)
- Toasts (done)
- Dialogs
- SharedPreferences

### 4.2 UI APIs (2–4 weeks)
- TextView / EditText / RecyclerView
- Button click listeners with lambdas
- View binding sugar

### 4.3 System APIs (4–8 weeks)
- Notifications
- Camera (CameraX)
- Location services
- File picker / storage APIs

### 4.4 Deliverables
- Signature database for SDK methods
- Permission DSL:
  - `permission("CAMERA")`
  - auto‑manifest updates
- Resource DSL:
  - string resources, icons, styles

### 4.5 Signature Database (Detailed Plan)
**Goal:** Map Pythonic calls → exact Android signatures automatically.

**Phase A: Minimal Curated Table**
- YAML/JSON in repo: `signatures/android_core.json`
- Hand‑curated entries for UI + core services
- Loaded by DSL at import time

**Phase B: SDK Extraction**
- Parse `android.jar` / public stubs to generate signature index:
  - `class -> method -> [overloads]`
- Generate a compact JSON for fast lookup

**Phase C: Overload Resolution**
- Use arg count + known types to pick overload
- If ambiguous, require explicit annotation
- Emit user‑friendly error with suggested signatures

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
- `debug` uses auto‑generated keystore
- `release` requires user keystore + alias + passwords
- Support v2/v3 signing (apksigner options)
- Store keystore config in `build.toml` or env vars

### 5.2 Resource Pipeline
- aapt2 resource staging
- icons, strings, themes
- layout XML (optional)

### 5.2.b Library R Class Handling (Foundational)
- Parse AAR `R.txt` + merged `R.txt` symbols from aapt2.
- Generate library `R$*` smali classes (attrs/styleables/etc.) into dex.
- Ensure resource IDs align with aapt2 output (stable IDs).
- Add tests with Material AAR to prevent `NoClassDefFoundError`.

### 5.2.a aapt2 Integration (Detailed)
- Generate `AndroidManifest.xml` from DSL + permissions
- Generate resource folders:
  - `res/layout`, `res/drawable`, `res/values/strings.xml`
- Invoke `aapt2 compile` and `aapt2 link`
- Track `R.txt` equivalent mapping for resource IDs

### 5.3 Lint + Diagnostics
- Type/arity verification (expanded)
- Signature validation warnings
- Smali verifier checks pre‑APK

### 5.3.a Conversion/Lint Passes
- Primitive conversion correctness checks
- Illegal invoke types flagged early
- Array bounds warnings (optional)

### 5.4 CI + Regression
- Unit + integration + device smoke tests
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

## What’s Next (Immediate Work)
1. Implement **Library R class handling** (merged symbols → library `R$*` smali).
2. Validate **AAR class/resource merge** on device (Material smoke test).
3. Draft **Navigation API** and wire minimal multi‑screen prototype.

--- 

**Note:** This plan is meant to evolve. As soon as the Pythonic DSL is in place, every subsequent feature should be added through that layer (not via internal helper APIs).
