# Skills Map

This is the working skills map for contributors and coding agents operating in this repository.

## 1. Product-reality skill

Be able to distinguish:

- the current shipped model: restricted Python DSL plus verified AOT compiler
- the research direction: broader smart transpilation with selective runtime injection

Do not describe planned full-Python support as if it already exists.

## 2. Frontend/DSL skill

Know where the user-facing surface actually lives:

- `dsl/api.py`
- `dsl/widgets.py`
- `dsl/parser.py`
- `dsl/parser_dispatch.py`
- `dsl/lowering/`

This layer is where most feature work should start.

## 3. Compiler-backend skill

Understand the stable backend path:

- `alpha_pipeline.py`
- `cfg/`
- `ssa/`
- `passes/`
- `dalvik/`
- `emit/`

Treat this as the verified spine of the compiler. Change it deliberately and with tests.

## 4. Runtime/capability skill

Know how capability-linked runtime support is currently expressed:

- `dsl/capabilities.py`
- `dsl/runtime/`
- `emit/capability_helpers/`
- `emit/smali_runtime_helpers.py`

Today the project already performs bounded helper injection for declared capabilities. That is the most practical bridge toward any future runtime-selector work.

## 5. Toolchain skill

Be comfortable tracing APK generation through:

- `apk/toolchain.py`
- `apk/project.py`
- `apk/resources.py`

Understand what depends on Android SDK tools and what is testable without them.

## 6. Contracts-and-docs skill

Before calling a feature "done", check the enforcement layer:

- `tools/docs_consistency.py`
- `tools/v1_scope_matrix.py`
- `tools/runtime_abi_snapshot.py`
- `tools/reactive_surface_snapshot.py`
- `tools/python_library_policy.py`

This repo relies on contract docs and gates, not just implementation.

## 7. Strategy skill

For roadmap work, prefer this framing:

- feasible near-term: analyzer + selective lowering/runtime selection on top of the existing compiler
- deferred research: general Python semantics, broad Android API binding generation, heavy dynamic runtime features

## 8. Working norms

- Preserve static-default behavior.
- Keep reactive features explicit and opt-in.
- Avoid new dependencies unless policy and docs are updated together.
- Update docs whenever code reality changes.
- When strategy and code disagree, fix the docs or explicitly mark the gap.
