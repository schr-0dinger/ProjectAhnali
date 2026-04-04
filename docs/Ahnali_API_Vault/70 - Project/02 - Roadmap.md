---
tags: [ahnali, project, roadmap]
---

# Roadmap

> [!abstract] What's next
> Close out the v1 release tracks, then decide what comes after.

## Active tracks

### Program 6-B: Capability breadth closure
Waves 9-18 are done. The remaining work is housekeeping:
- Reconcile the scope matrix (`cfg/v1_scope_matrix.yaml`)
- Promote completed slices in the masterplan
- Mark retained backlog items as explicitly deferred
- Gate: `tools/v1_scope_matrix.py --check` passes, docs consistency passes

### Program 12-A: Docs freeze
Keep everything aligned:
- README, masterplan, ABI docs, capability mapping — all reconciled with code
- Gate: `tools/docs_consistency.py` passes

### Program 11-B + 12-B: Final release hardening
- Preserve green compiler/toolchain tests
- Benchmark gates stay green
- Runtime ABI and capability mapping consistency
- Final traceability report and release gates

## Milestones

| Milestone | Status | What it means |
|---|---|---|
| A: Friendly DSL | ✅ Done | Pythonic app DSL usable without Smali internals |
| B: Feature-usable static foundation | ✅ Done | Navigation/state/event core, toolchain, styling |
| C: Production static core | ⚠️ In progress | Release hardening, CI gating, docs finalization |
| D: Native hybrid bridge | Deferred | NDK/JNI capability-scoped bridge |
| E: Optional Python plugin | Deferred | Embedded Python over JNI, bounded by static UI invariants |

## Post-v1 (if/when)

The deferred list is long: JNI bridge, embedded Python, media pipelines, maps, Bluetooth, biometrics, canvas drawing, security hardening. Nothing is committed — these are research directions, not promises.

## Learn more

- Current status: [[70 - Project/01 - Current Status]]
- Contributing: [[70 - Project/03 - Contributing]]
- Deferred features: [[60 - Architecture/04 - Deferred Features]]
