# Project Anali

Anali is a Python DSL -> IR -> CFG -> SSA -> Typed SSA -> Dalvik IR -> Smali compiler.
This repository contains the compiler pipeline, validation gates, and tests for a
phase-by-phase architecture-first build.

Last updated: 2026-02-05

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
- passes/             Compiler passes (lowering, liveness, regalloc, DCE)
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
-> Dalvik lowering
-> Dead code elimination
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
- Eta-3: try/catch surface + exceptional edges + smali emission

Active:
- Eta polish (remaining UX and tests)

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
- try_catch(try_body, except_body, exception_type=None)
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
- TryCatch(try_body, except_body, exception_type)
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

## Eta-2 Details (Calls + Returns)

Implemented:
- Typed Call in IR
- Typed Call lowering to Dalvik DInvoke
- Smali invoke-* emission with signatures
- Return lowering to DReturn
- Return type verification
- DSL method signatures and call helpers
- Negative tests for invalid signatures

Constraints:
- Call must provide return_type for non-void
- arg_types length must match args
- void call cannot assign
- non-void call must assign

## Eta-3 Details (try/catch + throw)

Implemented:
- TryCatch IR and DSL
- Exceptional edges in CFG builder
- .catch/.catchall Smali emission
- Throw IR and lowering to DThrow
- Validation for empty try blocks
- Validation for exception type descriptors

Constraints:
- try_body must be non-empty
- exception_type must be Smali descriptor: L...;
- throw value must be OBJECT type

## How to Run Tests

- python -m pytest

## Example: Multi-Method Program

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

## Next Work (Detailed)

Eta polish:
- Typed parameter binding smoke tests for multiple params
- Method signature validation for param descriptors in Smali
- Negative tests for invalid descriptors

Epsilon-2 optimizations:
- Constant propagation on SSA
- Copy propagation on SSA
- SSA coalescing
- Dominance-safe DCE ordering

Zeta refinements:
- Register pressure stress tests
- Spill correctness across calls and branches
- Deterministic regalloc across multiple methods

Omega endgame:
- Smali -> APK build integration
- APK install + runtime smoke tests
- Full DSL program end-to-end tests

## Philosophy Summary

- Correctness over features
- No direct DSL -> Smali shortcuts
- Verification is mandatory and blocking
- Emission is dumb by design
