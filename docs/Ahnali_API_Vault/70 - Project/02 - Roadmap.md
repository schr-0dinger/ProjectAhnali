---
tags: [ahnali, project, roadmap]
---

# Roadmap

> [!abstract] What's next
> Close out v1, then build the smart transpiler that competes with Kotlin.

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

## Milestones

| Milestone | Status | What it means |
|---|---|---|
| A: Friendly DSL | ✅ Done | Pythonic app DSL usable without Smali internals |
| B: Feature-usable static foundation | ✅ Done | Navigation/state/event core, toolchain, styling |
| C: Production static core | ⚠️ In progress | Release hardening, CI gating, docs finalization |
| D: Smart transpiler foundation | 🔄 Planned | Feature detection + on-demand runtime injection |
| E: Full Python support | 🔄 Planned | 95% Python syntax → native Android patterns |

## The New Direction

After v1 closes, we shift from a restricted DSL to a **smart transpiler with on-demand runtime injection**:

1. **Analyze** Python code to detect used features
2. **Select** only the runtime modules that are actually needed
3. **Translate** Python to native Android patterns (not a Python interpreter)
4. **Emit** Smali with minimal runtime overhead (5KB-35KB vs 10-15MB)

This is how we compete with Kotlin: full Python syntax, native Android performance, zero configuration.

See [[80 - Strategy/01 - Strategic Vision]] for the full vision and [[80 - Strategy/02 - Implementation Roadmap]] for the phase-by-phase plan.

## Post-v1 (if/when)

The deferred list is long: JNI bridge, embedded Python, media pipelines, maps, Bluetooth, biometrics, canvas drawing, security hardening. Nothing is committed - these are research directions, not promises.

## Learn more

- Current status: [[70 - Project/01 - Current Status]]
- Contributing: [[70 - Project/03 - Contributing]]
- Strategic vision: [[80 - Strategy/01 - Strategic Vision]]
- Implementation roadmap: [[80 - Strategy/02 - Implementation Roadmap]]
- Deferred features: [[60 - Architecture/04 - Deferred Features]]
