---
tags: [ahnali, project, roadmap]
---

# Roadmap

> [!abstract] What's next
> Close out v1, then build a staged smart-transpiler foundation on top of the compiler that already works.

> [!note] Naming clarity
> Milestones D and E are still useful labels, but they should be read as research/program names rather than promises of full-Python delivery on a fixed near-term schedule.

## Active tracks

### Program 6-B: Capability breadth closure
Waves 9-18 are done. The remaining work is housekeeping:
- Reconcile the scope matrix (`cfg/v1_scope_matrix.yaml`)
- Promote completed slices in the masterplan
- Mark retained backlog items as explicitly deferred
- Gate: `tools/v1_scope_matrix.py --check` passes, docs consistency passes

### Program 12-A: Docs freeze
Keep everything aligned:
- README, masterplan, ABI docs, capability mapping - all reconciled with code
- Gate: `tools/docs_consistency.py` passes

### Program 11-B + 12-B: Final release hardening
- Preserve green compiler/toolchain tests
- Benchmark gates stay green
- Runtime ABI and capability mapping consistency
- Final traceability report and release gates

### Phase 4 preparation: bounded advanced semantics
After the current v1 hardening work, the next credible compiler expansion is:
- build on the now-complete bounded Android binding layer instead of reopening that groundwork
- extend advanced semantics only where diagnostics and lowering stay explicit
- keep reusing runtime-plan reporting and selective helper emission when support code is actually needed
- preserve the current verified backend path as the stable spine

## Milestones

| Milestone | Status | What it means |
|---|---|---|
| A: Friendly DSL | ✅ Done | Pythonic app DSL usable without Smali internals |
| B: Feature-usable static foundation | ✅ Done | Navigation/state/event core, toolchain, styling |
| C: Production static core | ⚠️ In progress | Release hardening, CI gating, docs finalization |
| D: Smart transpiler foundation | ✅ Bounded core complete | Phase 1 and Phase 2 bounded slices are implemented and tested |
| E: Bounded Android binding expansion | ✅ Initial slice complete | Phase 3 Uri/Intent/activity bindings are implemented and tested without a backend rewrite |

## The New Direction

After v1 closes, the most credible next step is a **staged smart-transpiler foundation**:

1. **Analyze** a broader but still bounded Python subset
2. **Select** only the helper/runtime pieces that are actually required
3. **Lower** into the existing verified compiler backend
4. **Expand** the accepted surface only when the semantics stay statically checkable

This keeps the current product identity intact: no embedded Python interpreter, no unbounded runtime engine, and no wholesale backend rewrite.

> [!important] Feasibility boundary
> "Full Python" and "any Android app" should be treated as research goals, not near-term delivery promises. The codebase is currently strongest as a verified DSL compiler with an extensible backend, and the roadmap should build from that reality.

See [[80 - Strategy/01 - Strategic Vision]] for the full vision, [[80 - Strategy/02 - Implementation Roadmap]] for the phase-by-phase plan, and [[60 - Architecture/06 - Phase 3 Execution Plan]] for the bounded Android-binding execution path.

## Post-v1 (if/when)

The deferred list is long: JNI bridge, embedded Python, media pipelines, maps, Bluetooth, biometrics, canvas drawing, security hardening. Nothing is committed - these are research directions, not promises.

## Learn more

- Current status: [[70 - Project/01 - Current Status]]
- Contributing: [[70 - Project/03 - Contributing]]
- Strategic vision: [[80 - Strategy/01 - Strategic Vision]]
- Implementation roadmap: [[80 - Strategy/02 - Implementation Roadmap]]
- Deferred features: [[60 - Architecture/04 - Deferred Features]]
