---
tags: [ahnali, project, status, reality-check]
---

# Current Status

> [!abstract] Reality check as of 2026-04-07
> Ahnali is a working restricted-Python DSL compiler with a strong verified backend. The new smart-transpiler strategy is directionally plausible, but only as an incremental extension of the current architecture, not as a near-term pipeline replacement.

## What is verified right now

- `PYTHONPATH=. pytest -q` passes locally: **691 passed**
- `tools/docs_consistency.py` passes
- `tools/v1_scope_matrix.py --check` passes
- `tools/python_library_policy.py --policy cfg/python_library_policy.json` passes
- GitHub Actions CI already enforces runtime ABI, reactive-surface snapshot, scope matrix, docs consistency, library policy, tests, and benchmark gates

## What the codebase actually is

Ahnali today is:

- a **restricted, declarative Python DSL**, not general Python support
- a **verified mid/back-end compiler**: `DSL -> IR -> CFG -> SSA -> types -> Dalvik -> Smali`
- a **capability-linked runtime/toolchain** that injects bounded helper classes and packages APKs without Gradle

Important reality checks from the code:

- Handler parsing is based on Python AST inspection of bounded DSL handlers in [`dsl/parser.py`](../../../dsl/parser.py), not a full-program Python compiler.
- The stable execution spine is [`alpha_pipeline.py`](../../../alpha_pipeline.py), which already has clear validation gates and a complete backend path.
- Runtime support is already selectively linked for capabilities via the existing toolchain/runtime helper path, especially in [`apk/toolchain.py`](../../../apk/toolchain.py) and [`emit/smali_runtime_helpers.py`](../../../emit/smali_runtime_helpers.py).
- Phase 1 is now complete for the bounded repo scope: [`dsl/analyzer/__init__.py`](../../../dsl/analyzer/__init__.py), [`dsl/runtime/modules/__init__.py`](../../../dsl/runtime/modules/__init__.py), the runtime-plan CLI (`tools/feature_runtime_plan.py`), emitted `runtime_plan.json` build artifacts, helper emission for selected modules, and one bounded semantic reflection path (`getattr(widget, "text")`) all work without changing the verified backend path.
- Phase 2 is now complete for the bounded repo-real scope: list, dict, set, and tuple literals, plus `len(collection_symbol)` on supported local collection literals, lower through [`dsl/lowering/context.py`](../../../dsl/lowering/context.py) into `ListWrapperRuntime` / `DictWrapperRuntime` / `SetWrapperRuntime` / `TupleWrapperRuntime`, and the selected helpers are emitted through the existing runtime-module packaging path. Bounded type-conversion support covers `str(...)`, `int(...)`, `float(...)`, `type(...)`, and `isinstance(...)` for explicitly supported constants, locals, and nested supported calls. Phase 2.3 now also includes bounded string method lowering for `.strip()`, `.replace(...)`, `.lower()`, `.upper()`, helper-backed `.split(...)`, and separator `.join(...)` over supported list/tuple flows, including direct `label.text = ...` and f-string interpolation.
- Phase 3 is now complete for the bounded repo scope: [`dsl/android/bindings.py`](../../../dsl/android/bindings.py) provides an inspectable binding registry, the frontend accepts explicit `android_uri_parse(...)`, `android_intent_view(...)`, `android_intent_chooser(...)`, and `android_start_activity(...)` flows, [`dsl/lowering/context.py`](../../../dsl/lowering/context.py) lowers them directly into `Uri.parse`, `Intent` construction, `Intent.createChooser`, and `Activity.startActivity`, and runtime-plan metadata now records `android.bindings.uri`, `android.bindings.intent`, and `android.bindings.activity`.

## Phase summary

- **Phase 1**: Complete for the bounded scope in-repo.
- **Phase 2**: Complete for the bounded scope in-repo.
- **Phase 3**: Complete for the initial bounded Android-binding scope in-repo.

## Phase 3 bounded delivery

What Phase 3 now includes:

- binding metadata and diagnostics for a narrow set of Android classes/methods
- explicit frontend exposure of Android calls that map cleanly to the current IR and helper model
- runtime-plan/runtime-module visibility for those direct Android binding slices
- a bounded end-to-end launch flow covering Uri parsing, Intent construction, chooser wrapping, and `startActivity(...)`

What Phase 3 should **not** mean right now:

- `from android.widget import TextView` working as a general user-facing API surface
- generated bindings for "all Android APIs"
- broad Play Services or AndroidX coverage promised in one step
- backend rewrites just to make frontend syntax easier

## Strategic assessment

The new strategy is **feasible only if we treat it as a staged frontend expansion**.

What looks feasible:

- add a feature-analysis layer ahead of lowering
- expand the accepted Python subset gradually
- reuse the existing capability/helper injection model as the basis for a future runtime-selector system
- continue compiling through the existing verified CFG/SSA/Dalvik/Smali backend

What does **not** look near-term feasible without major risk:

- replacing the current DSL compiler with a full-Python compiler in one step
- promising "any Android app" support
- promising 95% Python syntax support on the current roadmap horizon
- moving core semantics into a heavy dynamic runtime without undermining the project identity

## Recommended project posture

For the current release train:

1. Finish v1 hardening and docs/scope closure.
2. Keep the current compiler backend frozen except for correctness and targeted improvements.
3. Treat Phase 1 and Phase 2 as closed for the bounded scopes already implemented.
4. Treat Phase 3 as closed for its initial bounded Android-binding slice.
5. Treat Phase 4 advanced semantics and broader Android coverage as research-style expansion milestones, not blanket delivery promises.

## Practical feasibility summary

The safest migration path is:

`restricted DSL -> broader analyzable subset -> feature analyzer -> selective runtime/helper selection -> existing verified backend`

The unsafe migration path is:

`general Python parser -> dynamic semantics -> backend rewrites -> unclear validation story`

## Learn more

- Roadmap: [[70 - Project/02 - Roadmap]]
- Contributing: [[70 - Project/03 - Contributing]]
- Strategic vision: [[80 - Strategy/01 - Strategic Vision]]
- Compiler pipeline: [[20 - Core Concepts/02 - Compiler Pipeline]]
