# Project Anali

Anali is a Python DSL -> IR -> CFG -> SSA -> Typed SSA -> Dalvik IR -> Smali compiler.
This repository contains the compiler pipeline, validation gates, and tests for a
phase-by-phase architecture-first build.

Anali is an ahead-of-time (AOT) compiler that translates a restricted, declarative, Python-like DSL into Dalvik bytecode. All UI structure, layout, navigation, and state wiring are statically compiled features, resolved entirely at compile time with no runtime interpretation. Alongside this, Anali ships a statically linked, capability-scoped support runtime: a small set of precompiled Smali helper classes that provide access to Android platform services (audio, sensors, storage, WebView, etc.). This runtime is not a framework engine but a link-time standard library, where only the capabilities referenced in user code are included in the final APK. As a result, Anali applications have deterministic behavior, minimal binary size, zero reflection, and native Android performance, while still exposing rich platform features through a strictly analyzable DSL.

Last updated: 2026-02-06

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
- Zeta refinement wrap-up (exceptional-edge spill + determinism done)
- Omega toolchain prep

Test status:
- Last full run: `77` passing tests (`python -m pytest`)

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

1) Omega toolchain scaffolding (emit build dir + integrate smali/baksmali entrypoints)
2) APK packaging for a minimal class
3) Runtime smoke test harness

## Completion Roadmap (Detailed)

### Phase 1: Zeta Refinement (current)

Objectives:
- Prove allocator stability under stress and complex control flow.
- Validate spills across branches, invokes, and exception paths.

Work items:
- Add register-pressure stress tests with >16 live intervals.
- Add spill/reload tests around:
  - `DIf` branch joins
  - `DInvoke` argument and result paths
  - try/catch handler transitions
- Add deterministic-output tests:
  - same input program -> identical register assignment and normalized Smali.
  - multi-method programs compile deterministically per-method.

Exit criteria:
- No allocator regressions under stress.
- Spill correctness verified in branch/call/handler scenarios.
- Determinism tests stable across repeated runs.

### Phase 2: Omega Toolchain Integration

Objectives:
- Move from compiler output validation to executable artifact validation.

Work items:
- Build integration:
  - emit complete class/method files to a build directory.
  - integrate `smali`/`baksmali` invocation flow.
- Packaging:
  - generate a minimal APK from emitted Smali.
  - establish reproducible build commands and output paths.
- Runtime smoke:
  - install APK on emulator/device.
  - run minimal startup path and verify no verifier/runtime crashes.

Exit criteria:
- One-command compile-to-APK workflow.
- APK installs and launches for baseline test apps.
- Runtime smoke suite green.

### Phase 3: End-to-End DSL Validation

Objectives:
- Validate language surface against real build/runtime behavior.

Work items:
- Add end-to-end fixtures:
  - typed method calls/returns
  - nested branches and loops
  - try/catch with multi-handlers
  - throw/catch paths
- Golden checks:
  - expected Smali fragments for each fixture
  - expected runtime behavior for smoke scenarios

Exit criteria:
- DSL-to-APK flow validated for representative programs.
- No phase-local workaround required to pass runtime checks.

### Phase 4: Stabilization and Release Readiness

Objectives:
- Lock behavior and make future changes safe.

Work items:
- CI matrix for unit + integration + end-to-end tests.
- Regression dashboard for optimization and lowering changes.
- Developer docs:
  - architecture invariants
  - pass ordering constraints
  - adding a new IR feature checklist

Exit criteria:
- Stable CI on all critical paths.
- Regression turnaround is quick and actionable.
- Architecture and contribution path documented.

## How to Run Tests

- python -m pytest

## Example: Multi-Method Program

```python
from dsl.app import program, method, assign, call, const, ret
from ir.types import AnaliType

prog = program([
    method("foo", return_type=AnaliType.INT, body=[ret(const(1))]),
    method("main", return_type=None, body=[
        assign("y", call("foo", args=[], return_type=AnaliType.INT, arg_types=[]))
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
