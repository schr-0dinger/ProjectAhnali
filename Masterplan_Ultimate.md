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

---

## 5) Toolchain Polish (Production‑ready)

### 5.1 Build System
- Debug/release variants
- Deterministic APK output
- Versioning + reproducible builds

### 5.2 Resource Pipeline
- aapt2 resource staging
- icons, strings, themes
- layout XML (optional)

### 5.3 Lint + Diagnostics
- Type/arity verification (expanded)
- Signature validation warnings
- Smali verifier checks pre‑APK

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
1. Implement **Pythonic DSL layer** (`app(...)`, `activity(...)`, `state(...)`, `ui(...)`, `on_click(...)`).
2. Add **expression mini‑parser** for `+=` and `f""`.
3. Add **golden tests** + adb smoke for counter example.

--- 

**Note:** This plan is meant to evolve. As soon as the Pythonic DSL is in place, every subsequent feature should be added through that layer (not via internal helper APIs).
