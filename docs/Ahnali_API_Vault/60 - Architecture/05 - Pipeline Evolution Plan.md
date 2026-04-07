---
tags: [ahnali, architecture, pipeline, strategy, migration]
---

# Pipeline Evolution Plan

> [!abstract] How to grow Ahnali without breaking its strongest asset
> The verified CFG/SSA/Dalvik/Smali backend is the most mature part of the project. The right migration path is to evolve the frontend and runtime-selection layers around it, not replace the backend first.

## The current spine

Today the dependable path is:

`restricted DSL -> frontend IR -> CFG -> SSA -> typed lowering -> Dalvik -> Smali -> APK`

That path already has:

- validation gates
- broad test coverage
- clear phase boundaries
- packaging/toolchain integration

## The migration rule

Default assumption:

**new strategy work belongs before IR unless proven otherwise**

That means most future work should land in:

- source analysis
- parser/frontend expansion
- lowering normalization
- capability/helper selection
- packaging-time helper/runtime assembly

Not in:

- CFG shape changes
- SSA rewrites for source-language convenience
- emitter shortcuts that bypass validated IR

## Feasible staged plan

### Stage 1: Feature analysis

Add an analysis layer that answers:

- what source features are used?
- what helper/runtime support is required?
- what parts of the existing lowering path can already handle the result?

This should produce structured data, not hidden heuristics.

### Stage 2: Bounded source expansion

Grow beyond the current DSL in explicit slices:

- more analyzable expressions
- more collection sugar
- more bounded handler/function forms
- limited Android API binding surfaces where typing and lowering remain clear

Each slice should have:

- parser rules
- lowering rules
- diagnostics
- tests

### Stage 3: Runtime/helper selection

Generalize the current capability-helper model so the build step selects only the support classes required by the analyzed feature set.

This should reuse the existing runtime/helper model before inventing a separate runtime platform.

### Stage 4: Backend extension only when necessary

Only touch CFG/SSA/Dalvik/emission when the new source feature cannot be represented cleanly with the current IR and passes.

When backend changes are necessary:

- preserve one-way lowering
- add validation where the new representation introduces risk
- add focused regression tests first

## Phase 3 implication

The next architecture-valid expansion after the current bounded Phase 2 work is **bounded Android binding metadata plus lowering**, not a parser jump to arbitrary Android imports.

That has now been proven in the initial bounded slice:

- a binding registry landed before broad syntax
- the first user-facing Android surfaces are Uri/Intent/activity flows already proven internally by the current helper/capability/toolchain path
- runtime selection and build metadata now record those bindings without needing a backend rewrite
- "all Android APIs" remains a long-term ceiling, not an implementation claim

## What to avoid

Avoid these migration traps:

- "replace the parser with general Python and figure it out later"
- "move semantics into runtime code because it is faster to ship"
- "patch the emitter to support a source feature directly"
- "promise full Python coverage before the object model and diagnostics exist"

Each of these trades away the current reliability advantage.

## Success criteria

The strategy is succeeding if:

- the accepted source subset grows
- helper/runtime selection becomes more precise
- docs and contracts stay truthful
- the existing backend remains the stable compilation spine
- tests continue to guard every expansion step

## Learn more

- Compiler pipeline: [[20 - Core Concepts/02 - Compiler Pipeline]]
- Runtime model: [[60 - Architecture/02 - Runtime Model]]
- Current status: [[70 - Project/01 - Current Status]]
- Strategic vision: [[80 - Strategy/01 - Strategic Vision]]
