# Project Ahnali

Ahnali is a Python DSL -> IR -> CFG -> SSA -> Typed SSA -> Dalvik IR -> Smali compiler.
This repository contains the compiler pipeline, validation gates, and tests for a
phase-by-phase architecture-first build.

Ahnali is an ahead-of-time (AOT) compiler that translates a restricted, declarative, Python-like DSL into Dalvik bytecode. All UI structure, layout, navigation, and state wiring are statically compiled features, resolved entirely at compile time with no runtime interpretation. Alongside this, Ahnali ships a statically linked, capability-scoped support runtime: a small set of precompiled Smali helper classes that provide access to Android platform services (audio, sensors, storage, WebView, etc.). This runtime is not a framework engine but a link-time standard library, where only the capabilities referenced in user code are included in the final APK. As a result, Ahnali applications have deterministic behavior, minimal binary size, zero reflection, and native Android performance, while still exposing rich platform features through a strictly analyzable DSL.

Last updated: 2026-02-17

## Goals

- Correctness first. Every phase is verified and enforced.
- One-way lowering only. No back-mutation of earlier phases.
- Dumb emission. Smali emission only prints verified IR.
- Phase discipline. Each phase has a single responsibility.

## Repository Layout

- dsl/                Frontend DSL helpers (program/method/expr/stmt builders)
- ir/                 Frontend IR (expr, stmt, method, program, types)
- cfg/                Control flow graph (builder, dominance, frontier, validate)
- ssa/                SSA construction + verification
- dalvik/             Dalvik IR + blocks + methods
- passes/             Compiler passes (lowering, liveness, regalloc, DCE, SSA opts)
- emit/               Smali emission
- tests/              Unit and integration tests

## Current Pipeline (Authoritative)

DSL
-> CFG
-> Dominance
-> Phi insertion
-> SSA rename
-> SSA verify
-> Type inference
-> Type verify
-> SSA optimizations (Epsilon-2)
-> Dalvik lowering
-> Dead code elimination
-> CFG simplification (Epsilon-3)
-> Liveness
-> Linear scan allocation
-> Spilling
-> Smali emission

## Status Summary

Phases completed:
- Alpha: CFG + dominance + SSA + verification
- Beta: structured control flow (if/while)
- Gamma: relational branches (Compare)
- Delta: arithmetic SSA + lowering
- Omega-1: typed SSA inference + verification
- Omega-2: exception-capable CFG (structural)
- Zeta-0/1/2/3: regalloc, liveness, linear scan, spilling
- Epsilon-1: DCE
- Eta-2: typed calls and returns
- Eta-3: try/catch + throw + smali emission
- Epsilon-2: SSA constant/copy propagation + coalescing
- Epsilon-3: CFG simplification (redundant goto removal, block merging)

Active:
- UI/compiler expansion through Phase 13 complete (events, input, accessibility, effects, animations, themes, scroll controls, static list view, lint hardening)
- Packaging flow complete (`aapt2` + `zipalign` + `apksigner`)
- Inline event attribute sugar is available and wired to existing event lowering

Test status:
- Last suite run: `391 passed` (`PYTHONPATH=. pytest -q -rs`)

## DSL Surface (Current)

From dsl/app.py:

- program([...])
- method(name, params=[], param_types=[], return_type=None, body=[])
- assign(name, expr)
- call(name, args, return_type, arg_types, invoke_kind="static", owner="LTest;")
- call_stmt(name, args, return_type=None, arg_types=[], ...)
- ret(value=None)
- if_(cond, then, else_)
- while_(cond, body)
- binary(op, left, right)
- compare(op, left, right)
- try_catch(try_body, except_body=None, exception_type=None, handlers=None)
- throw(value)

## IR Surface (Current)

Expressions:
- Const(value)
- Var(name)
- BinaryOp(op, left, right)
- Compare(op, left, right)
- Call(func, args, return_type, arg_types, invoke_kind, owner)

Statements:
- Assign(name, expr)
- Return(value)
- CallStmt(Call(...))
- TryCatch(try_body, except_body, exception_type, handlers)
- Throw(value)

Methods / Program:
- MethodIR(name, params, body, return_type, param_types)
- ProgramIR(methods)

## Verification Gates

- CFG validation (structural correctness)
- SSA correctness (single def, dominance, phi legality)
- Typed SSA enforcement where required
- Call signature checks (arity and void/non-void rules)
- Return type checks (method signature vs return values)
- Try/catch structural validation (non-empty try, descriptor types, catchall ordering)
- Throw validation (must be OBJECT)

## Eta-2 Details (Calls + Returns)

Implemented:
- Typed Call in IR
- Typed Call lowering to Dalvik DInvoke
- Smali invoke-* emission with signatures
- Return lowering to DReturn
- Return type verification
- DSL method signatures and call helpers
- Negative tests for invalid signatures
- Param binding into SSA

Constraints:
- Call must provide return_type for non-void
- arg_types length must match args
- void call cannot assign
- non-void call must assign
- param_types length must match params

## Eta-3 Details (try/catch + throw)

Implemented:
- TryCatch IR and DSL
- Exceptional edges in CFG builder
- .catch/.catchall Smali emission
- Throw IR and lowering to DThrow
- Validation for empty try blocks
- Validation for exception type descriptors
- Multi-handler ordering (catchall last)

Constraints:
- try_body must be non-empty
- exception_type must be Smali descriptor: L...;
- catchall must be last
- throw value must be OBJECT type

## Epsilon-2 Details (SSA optimizations)

Implemented:
- Constant propagation
- Copy propagation
- Optional constant folding (flagged)
- Coalescing across phi + non-phi moves
- Aggressive copy removal (rewrite + delete)

Flags:
- alpha_pipeline(..., ssa_opt={"enable_folding": True})

## Epsilon-3 Details (CFG simplification)

Implemented:
- Redundant goto elimination
- Empty block removal with single successor
- Block merging into single predecessor (safe)
- Dalvik branch/goto target retargeting during CFG rewrites
- Smali label emission filtering for unreferenced empty blocks
- Label-integrity regression tests (all branch/catch references resolve to defined labels)

Constraints:
- Do not simplify entry/exit blocks
- Do not simplify blocks in try regions
- Do not cross exceptional edges

## Immediate Plan (Next)

1) Track A complete: runtime ABI + capability mapping + frozen signature snapshot (`runtime_abi_v1.md`, `docs/capability_runtime_mapping_v1.md`, `cfg/runtime_abi_snapshot_v1.json`)
2) Track B enforcing: size benchmark strict on PR/push; cold-start benchmark strict on manual dispatch
3) Track C Wave 7 complete: permissions helper-call surface + visible deterministic flow (`tests/test_track_c_wave7_permissions.py`, `tests/test_track_c_wave7_visible_flow.py`)
4) Start Track C Wave 8 next capability slice (same end-to-end pattern: DSL + lowering + helper + tests + visible flow)
5) Start Track D first tranche: deterministic optimization passes with test/benchmark gates (see `docs/Ahnali_Optimization_Backlog.md`)

## Completion Roadmap (Current)

### Track A: Runtime Capability ABI

Status:
- ✅ Completed (2026-02-16)

Objectives:
- Lock stable runtime helper ABI for capability-scoped module linking.

Work items:
- ✅ Define runtime helper class/interface contracts and versioning rules (`runtime_abi_v1.md`).
- ✅ Add ABI compatibility tests (compile-time and runtime smoke for helper and mapping contracts).
- ✅ Document capability-to-runtime mapping in docs (`docs/capability_runtime_mapping_v1.md`).
- ✅ Freeze helper class/method ABI surface in generated snapshot (`cfg/runtime_abi_snapshot_v1.json`) with check tool (`tools/runtime_abi_snapshot.py`) and CI gate (`.github/workflows/ci.yml`).

Exit criteria:
- ✅ ABI contract frozen for v1.
- ✅ New capabilities can be added without breaking existing apps (guarded by ABI tests).
- ✅ ABI signature drift fails fast in CI via snapshot check.

### Track B: Benchmark Automation

Status:
- ✅ Completed (2026-02-16; size strict on PR/push, cold-start strict on manual dispatch)

Objectives:
- Make performance/size regressions visible and blocking.

Work items:
- ✅ Add deterministic APK size reporting in CI (`tools/benchmark_apk.py`, `.github/workflows/ci.yml` size gate).
- ✅ Add cold-start benchmark harness and threshold checks (`tools/benchmark_apk.py` + manual CI emulator gate).
- ✅ Track size regressions with committed baseline + threshold caps (`cfg/benchmark_baseline.json`, `cfg/benchmark_thresholds.json`).

Exit criteria:
- ✅ Benchmark gates are automated and enforced according to policy.
- ✅ Size gate is strict on PR/push; cold-start gate is strict on manual dispatch.

### Track C: Capability Expansion

Status:
- ⚠️ In progress (Wave 1 closed on 2026-02-17; Wave 2 completed on 2026-02-17 with networking response/routing/retry/typed-JSON and visible integration flow; Wave 3 completed tokened async route/cancellation/progress/payload/timeout-retry + visible flow on 2026-02-17; Wave 4 request-option transport hardening + race stress coverage completed on 2026-02-17; Wave 5 visible integration flow completed on 2026-02-17; Wave 6 location helper-call capability + visible integration flow completed on 2026-02-17; Wave 7 permissions helper-call capability + visible integration flow completed on 2026-02-17)

Objectives:
- Enable practical app logic beyond static UI/state.

Work items:
- ✅ Add initial helper-call capability primitives:
  - `URLLauncher` → `Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl(...)I`
  - `Connectivity` → `Lcom/ahnali/runtime/ConnectivityHelper;->isConnected(...)I`
  - `Storage` → `Lcom/ahnali/runtime/StorageHelper;->putString(...)I` + `getString(...)Ljava/lang/String;` + `remove(...)I` + `exists(...)I` + `clear(...)I`
- ✅ Start Wave 2 networking primitive:
  - `Networking` → `Lcom/ahnali/runtime/HttpHelper;->httpGet(...)Ljava/lang/String;` via `http_get(...)`
- ✅ Add networking response surface:
  - `http_get_status(...)` → `httpGetStatus(...)I`
  - `http_get_error(...)` → `httpGetError(...)I`
  - `http_get_route(url, "success_btn", "failure_btn", fallback)` for success/failure handler wiring
- ✅ Add deterministic retry/backoff primitive:
  - `http_get_retry(url, retries, backoff_ms, fallback)` → `httpGetRetry(...)Ljava/lang/String;`
- ✅ Add typed JSON field networking helpers:
  - `http_get_json_field(url, key, fallback)` → `httpGetJsonField(...)Ljava/lang/String;`
  - `http_get_json_field_error(url, key)` → `httpGetJsonFieldError(...)I`
- ✅ Start Wave 3 async route primitive:
  - `http_get_route_async(url, "success_btn", "failure_btn", fallback, progress_target_id, retries, timeout_ms)` → tokened background route worker + UI-thread callback dispatch
- ✅ Add Wave 3 tokened async primitives:
  - `http_async_cancel(token)` → token-scoped cancellation request
  - `http_async_progress(token)` → token-scoped deterministic progress surface (`0..100`)
  - `http_async_error(token)` → token-scoped deterministic async error surface
  - `http_async_status(token)` → token-scoped completion status surface
  - `http_async_body(token, fallback)` → token-scoped completion body surface
- ✅ Add Wave 3 async progress callback wiring:
  - optional `progress_target_id` in `http_get_route_async(...)` posts UI-thread progress callbacks
- ✅ Add Wave 3 async completion payload routing:
  - success/failure handlers can read deterministic token-scoped `status/body/error`
- ✅ Add Wave 3 timeout/retry controls in async worker:
  - optional `retries` + `timeout_ms` arguments in `http_get_route_async(...)`
- ✅ Add Wave 4 multi-request token runtime state:
  - token-indexed async stores for cancellation/progress/error/status/body in `HttpHelper`
- ✅ Add Wave 4 request-option wiring for async route:
  - optional `method` + `headers` + `body` arguments in `http_get_route_async(...)`
  - worker routes through `httpRequest*WithTimeout(...)` helper ABI
- ✅ Add Wave 4 typed async JSON adapters:
  - `http_async_json_field(token, key, fallback)`
  - `http_async_json_field_error(token, key)`
  - `http_async_json_array_length(token, fallback)`
- ✅ Harden Wave 4 request-option transport semantics:
  - deterministic method normalization (`GET` default; `GET`/`POST` accepted; others invalid)
  - newline-delimited header parsing/application (`Key: Value`; malformed lines ignored)
  - explicit POST UTF-8 body transport path (`setDoOutput`, fixed-length streaming, output-stream write)
- ✅ Add Wave 4 concurrent cancellation/race stress coverage for tokened async surfaces.
- ✅ Close Wave 1 with visible app flow compile coverage (`tests/test_track_c_wave1_visible_flow.py`)
- ✅ Document visible Wave 1 app flow (`docs/TrackC_Wave1_Visible_Flow.md`)
- ✅ Add Wave 2 visible capability integration flow (`tests/test_track_c_wave2_visible_flow.py`)
- ✅ Document visible Wave 2 app flow (`docs/TrackC_Wave2_Visible_Flow.md`)
- ✅ Document Wave 3 async route contract (`docs/TrackC_Wave3_Async_Route.md`)
- ✅ Add Wave 3 visible tokened async capability flow (`tests/test_track_c_wave3_visible_flow.py`)
- ✅ Document Wave 3 visible tokened flow (`docs/TrackC_Wave3_Visible_Flow.md`)
- ✅ Document Wave 4 async concurrency/request-options contract (`docs/TrackC_Wave4_Async_Concurrency.md`)
- ✅ Add Wave 5 visible integration flow combining networking + storage + connectivity with deterministic fallback UI routing (`tests/test_track_c_wave5_visible_flow.py`)
- ✅ Document Wave 5 visible flow (`docs/TrackC_Wave5_Visible_Flow.md`)
- ✅ Add Wave 6 location capability helper-call primitive:
  - `Location` → `Lcom/ahnali/runtime/LocationHelper;->isLocationEnabled(...)I`
  - DSL surfaces: `location_enabled()`, `is_location_enabled()`, `check_location()`
- ✅ Add Wave 6 visible integration flow combining location + networking + storage with deterministic fallback routing (`tests/test_track_c_wave6_visible_flow.py`)
- ✅ Document Wave 6 location contract + flow (`docs/TrackC_Wave6_Location.md`)
- ✅ Add Wave 7 permissions capability helper-call primitive:
  - `Permissions` → `Lcom/ahnali/runtime/PermissionHelper;->isGranted(...)I`
  - DSL surfaces: `permission_granted()`, `has_permission()`, `check_permission()`, `permission_check()`
- ✅ Add Wave 7 visible integration flow combining permissions + storage + URL launcher with deterministic fallback routing (`tests/test_track_c_wave7_visible_flow.py`)
- ✅ Document Wave 7 permissions contract + flow (`docs/TrackC_Wave7_Permissions.md`)
- ✅ Add capability-scoped storage introspection primitives (`storage_exists`, `storage_clear`).
- Continue adding capability-scoped primitives beyond networking/storage/location/permissions.

Exit criteria:
- At least one end-to-end app flow using capabilities compiles, installs, and runs with deterministic output.
- ✅ Wave 2 networking response/retry conformance is enforced by `tests/test_track_c_wave2_http_get.py`.
- ✅ Wave 2 visible capability integration flow conformance is enforced by `tests/test_track_c_wave2_visible_flow.py`.
- ✅ Wave 3 async route dispatch conformance is enforced by `tests/test_track_c_wave3_async_route.py`.
- ✅ Wave 3 visible tokened async flow conformance is enforced by `tests/test_track_c_wave3_visible_flow.py`.
- ✅ Wave 4 async concurrency/request-options/typed-adapter/transport/race conformance is enforced by `tests/test_track_c_wave4_async_networking.py`.
- ✅ Wave 4 device integration conformance is enforced by `tests/test_http_helper_device_integration.py` (requires `adb` device in `device` state).
- ✅ Wave 5 visible deterministic fallback flow conformance is enforced by `tests/test_track_c_wave5_visible_flow.py`.
- ✅ Wave 6 location capability conformance is enforced by `tests/test_track_c_wave6_location.py`.
- ✅ Wave 6 visible deterministic fallback flow conformance is enforced by `tests/test_track_c_wave6_visible_flow.py`.
- ✅ Wave 7 permissions capability conformance is enforced by `tests/test_track_c_wave7_permissions.py`.
- ✅ Wave 7 visible deterministic fallback flow conformance is enforced by `tests/test_track_c_wave7_visible_flow.py`.

Capability diagnostics (standard format):
- `[CapabilityError] <api_name> requires Caps.<Capability>. Fix: add app_config(uses=[Caps.<Capability>]) to activity(...).`

How to fix examples:
- URL launcher:
```python
app(
    activity(
        "MainActivity",
        app_config(uses=[Caps.URLLauncher]),
        ...
    )
)
```
- Connectivity:
```python
app(
    activity(
        "MainActivity",
        app_config(uses=[Caps.Connectivity]),
        ...
    )
)
```
- Storage:
```python
app(
    activity(
        "MainActivity",
        app_config(uses=[Caps.Storage]),
        ...
    )
)
```
- Networking (`http_get`):
```python
app(
    activity(
        "MainActivity",
        app_config(uses=[Caps.Networking]),
        ...
    )
)
```
- Permissions (`check_permission` / `permission_granted`):
```python
app(
    activity(
        "MainActivity",
        app_config(uses=[Caps.Permissions]),
        ...
    )
)
```

Networking response contract:
- `http_get(...)` returns response body, else fallback string.
- `http_get_status(...)` returns HTTP status, else `-1`.
- `http_get_error(...)` returns deterministic error code:
  - `0` success
  - `1` invalid input
  - `2` transport/runtime exception
  - `3` non-200 status
  - `4` empty body
- `http_get_retry(...)` performs deterministic retries:
  - attempts = `max(0, retries) + 1`
  - backoff = fixed `max(0, backoff_ms)` milliseconds between failed attempts
  - success condition = `http_get_error(...) == 0`
  - returns response body on first success, otherwise fallback
- `http_get_json_field(...)` returns extracted JSON field string, else fallback string.
- `http_get_json_field_error(...)` returns deterministic extraction error code:
  - `0` success
  - `1` invalid input
  - `2` transport/runtime exception
  - `3` non-200 status
  - `4` empty body
  - `5` malformed payload
  - `6` missing key (or null value)
- `http_get_route_async(url, "success_btn", "failure_btn", fallback, progress_target_id="", retries=0, timeout_ms=8000, method="GET", headers="", body="")` dispatches tokened network route checks in a background thread and posts success/failure/progress handlers to the UI thread.
  - request option transport semantics:
    - `method`: null/empty defaults to `GET`; `GET`/`POST` are accepted (case-insensitive); others map to deterministic invalid-input surfaces.
    - `headers`: newline-delimited `Key: Value` entries are parsed and applied via request properties; malformed lines are ignored deterministically.
    - `body`: only applied for `POST`, encoded as UTF-8 bytes and written through output stream.
- `http_async_cancel(token)` requests token-scoped cancellation for async networking work.
- `http_async_progress(token)` returns token-scoped deterministic progress (`0..100`).
- `http_async_error(token)` returns token-scoped deterministic async error code:
  - `0` success
  - `1` invalid input
  - `2` transport/runtime exception
  - `3` non-200 status
  - `4` empty body
  - `7` cancelled
  - `8` stale/unknown token
- `http_async_status(token)` returns token-scoped completion status (`-1` on stale/unknown token).
- `http_async_body(token, fallback)` returns token-scoped completion body, else deterministic fallback.
- `http_async_json_field(token, key, fallback)` returns token-scoped JSON field string, else deterministic fallback.
- `http_async_json_field_error(token, key)` returns deterministic token-scoped JSON field extraction error code (`0,1,2,3,4,5,6,7,8`).
- `http_async_json_array_length(token, fallback)` returns token-scoped JSON array length, else deterministic fallback.

Storage introspection contract:
- `storage_exists("key")` returns `1` when key exists, else `0`.
- `storage_clear()` clears all app storage keys for this helper namespace and returns `1` on success, else `0`.

Known limits (current networking surface):
- Retry policy is fixed-backoff without jitter.

### Track D: Optimization and Build Intelligence

Objectives:
- Add static optimization/lint/security/performance intelligence without violating deterministic AOT constraints.

Work items:
- Execute optimization backlog tracks (assets, resources, code-level, dependencies, manifest, native, perf static analysis, security, packaging, DX).
- Prioritize high-impact/low-risk items first (unused resource/permission detection, size diff reporting, build benchmarking).
- Keep each optimization behind explicit flags until behavior is stable.

Exit criteria:
- Optimization passes are deterministic, test-covered, and measurable via CI reports.
- No regressions in build reproducibility or runtime correctness.

## How to Run Tests

- python -m pytest

## Benchmark Harness

- Local usage and CI details: `docs/Benchmarking.md`
- Size-only gate (no adb device):
  - `PYTHONPATH=. python tools/benchmark_apk.py --threshold-file cfg/benchmark_thresholds.json --baseline-file cfg/benchmark_baseline.json --report-file build/benchmark/size_report.json --api 34 --skip-cold-start`
- Cold-start gate (adb device/emulator required):
  - `PYTHONPATH=. python tools/benchmark_apk.py --threshold-file cfg/benchmark_thresholds.json --baseline-file cfg/benchmark_baseline.json --report-file build/benchmark/cold_start_report.json --api 34 --require-cold-start --cold-start-iterations 3`

## Example: Multi-Method Program

```python
from dsl.app import program, method, assign, call, const, ret
from ir.types import AhnaliType

prog = program([
    method("foo", return_type=AhnaliType.INT, body=[ret(const(1))]),
    method("main", return_type=None, body=[
        assign("y", call("foo", args=[], return_type=AhnaliType.INT, arg_types=[]))
    ])
])

result = alpha_pipeline(prog)
print(result["smali_class"])
```

## Philosophy Summary

- Correctness over features
- No direct DSL -> Smali shortcuts
- Verification is mandatory and blocking
- Emission is dumb by design
