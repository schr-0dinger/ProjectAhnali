---
tags: [ahnali, architecture, phase3, android, bindings]
---

# Phase 3 Execution Plan

> [!abstract] What Phase 3 should actually mean in this repo
> Phase 3 should begin as a bounded Android binding layer built on top of the existing analyzer, runtime-selector, lowering, and packaging path. It should not begin as arbitrary Android imports or universal binding generation.

> [!success] Current status
> The initial bounded Phase 3 slice is now complete in code: `android_uri_parse(...)`, `android_intent_view(...)`, `android_intent_chooser(...)`, and `android_start_activity(...)` are implemented through [`dsl/android/bindings.py`](../../../dsl/android/bindings.py) and [`dsl/lowering/context.py`](../../../dsl/lowering/context.py), and runtime-plan metadata records the selected Android binding modules.

## Starting point

The codebase already has:

- a verified backend (`IR -> CFG -> SSA -> Dalvik -> Smali`)
- selective helper emission during packaging
- runtime-module selection and emitted `runtime_plan.json`
- broad platform behavior already proven through DSL capabilities and helper classes

That means Phase 3 should focus on **how users express Android surfaces**, not on replacing the backend or inventing a new runtime model.

## Phase 3 goal

Deliver a first bounded Android binding layer that:

- has explicit signatures
- produces clear diagnostics
- lowers through the existing backend
- reuses helper emission only when direct lowering is not enough

## Non-goals

Phase 3 should not promise:

- arbitrary `from android... import ...` support
- generated bindings for the full Android SDK
- broad AndroidX or Play Services coverage in one step
- dynamic reflection-driven Android calls from user code

## Workstreams

### 1. Binding registry

Create structured binding metadata for a narrow set of Android classes and methods:

- owner class
- allowed constructors/methods
- fixed argument and return types
- whether the call lowers directly or requires helper support
- required artifacts, if any

The registry should be inspectable and testable, not implicit in lowering code.

### 2. Frontend syntax

Add only the minimum syntax needed for those bindings:

- explicit class/value construction
- explicit static or instance calls with fixed signatures
- diagnostics when a class or member is outside the supported set

Avoid broad import semantics until there is a stable binding story.

### 3. Lowering

For each supported binding:

- lower directly to existing IR where possible
- use helper-backed lowering only when the Android surface is awkward or repetitive
- keep all calls typed and validation-heavy

### 4. Packaging and reporting

Phase 3 additions should show up in the same places as other selective runtime work:

- runtime module selection
- emitted helper classes when needed
- build metadata / `runtime_plan.json`
- artifact requirements in the build dir

## Implemented first slice

The safest first slices were Android surfaces the repo already modeled internally, and that is what now shipped:

- `android.net.Uri` parsing through `android_uri_parse(...)`
- `android.content.Intent` construction for launch flows through `android_intent_view(...)`
- chooser wrapping through `android_intent_chooser(...)`
- explicit launch via `android_start_activity(...)`

These are better starting points than jumping straight to generic widgets, Play Services, or broad AndroidX binding generation.

## Exit criteria

Phase 3 should count as genuinely started only when all of the following are true:

- at least one Android binding slice is available to user code
- unsupported members fail with explicit diagnostics
- helper-backed bindings can be emitted and reported through the existing packaging path when needed
- tests cover parser, lowering, emission, packaging, and docs updates

## Learn more

- Current status: [[70 - Project/01 - Current Status]]
- Roadmap: [[70 - Project/02 - Roadmap]]
- Strategic vision: [[80 - Strategy/01 - Strategic Vision]]
- Implementation roadmap: [[80 - Strategy/02 - Implementation Roadmap]]
- Pipeline evolution plan: [[60 - Architecture/05 - Pipeline Evolution Plan]]
