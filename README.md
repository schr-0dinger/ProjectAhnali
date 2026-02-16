# Project Ahnali

Ahnali is a Python DSL -> IR -> CFG -> SSA -> Typed SSA -> Dalvik IR -> Smali compiler.
This repository contains the compiler pipeline, validation gates, and tests for a
phase-by-phase architecture-first build.

Ahnali is an ahead-of-time (AOT) compiler that translates a restricted, declarative, Python-like DSL into Dalvik bytecode. All UI structure, layout, navigation, and state wiring are statically compiled features, resolved entirely at compile time with no runtime interpretation. Alongside this, Ahnali ships a statically linked, capability-scoped support runtime: a small set of precompiled Smali helper classes that provide access to Android platform services (audio, sensors, storage, WebView, etc.). This runtime is not a framework engine but a link-time standard library, where only the capabilities referenced in user code are included in the final APK. As a result, Ahnali applications have deterministic behavior, minimal binary size, zero reflection, and native Android performance, while still exposing rich platform features through a strictly analyzable DSL.

Last updated: 2026-02-16

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
- Last suite run: `264 passed, 1 skipped` (`PYTHONPATH=. pytest -q -rs`; skipped test requires an `adb` device in `device` state)

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

1) Track A complete: runtime ABI + capability mapping frozen (`runtime_abi_v1.md`, `docs/capability_runtime_mapping_v1.md`)
2) Size/perf benchmark automation (APK size + cold start)
3) First capability wave for real app logic (network/storage primitives)
4) Ongoing integration smoke expansion for each new capability area
5) Optimization backlog execution (see `docs/Ahnali_Optimization_Backlog.md`)

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

Exit criteria:
- ✅ ABI contract frozen for v1.
- ✅ New capabilities can be added without breaking existing apps (guarded by ABI tests).

### Track B: Benchmark Automation

Objectives:
- Make performance/size regressions visible and blocking.

Work items:
- Add deterministic APK size reporting in CI.
- Add cold-start benchmark harness and threshold checks.
- Track regressions per commit in artifacts/logs.

Exit criteria:
- Benchmark gates are automated and reliable.
- Regressions are caught before merge.

### Track C: Capability Expansion

Objectives:
- Enable practical app logic beyond static UI/state.

Work items:
- Add capability-scoped networking primitives.
- Add capability-scoped storage primitives.
- Add permission/capability diagnostics for new surfaces.

Exit criteria:
- At least one end-to-end app flow using capabilities compiles, installs, and runs with deterministic output.

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
