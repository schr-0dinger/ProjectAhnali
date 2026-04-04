---
tags: [ahnali, architecture, dual-mode, hybrid]
---

# Dual Mode Architecture

> [!abstract] Static is identity. Hybrid is optional research.
> Ahnali's core is static AOT compilation. A hybrid mode with JNI and embedded Python is planned for post-v1 but will never replace static mode.

## Mode A: Static (default)

This is Ahnali. Everything is compiled at build time:
- UI structure
- Navigation graph
- Event handlers
- State wiring
- Capability calls

Result: small APK, deterministic behavior, native performance, full static analyzability, zero reflection.

## Mode B: Hybrid (deferred research)

Optional, capability-scoped, strictly bounded. The idea:

```
Static UI (Smali) → Core Runtime (Smali) → JNI Bridge → libpython3.x.so → Restricted Python
```

Core rule: **UI is always static.** Python may mutate state, trigger navigation, call approved capabilities, and perform computation — but it cannot create arbitrary views or destroy compiled structures.

## Hybrid rollout phases

**Phase 0** (done): Static foundation — deterministic emission, navigation, capabilities, permissions, manifest wiring.

**Phase 1** (deferred): Native execution layer — NDK integration, JNI bridge, capability-scoped native calls.

**Phase 2** (deferred): Optional Python runtime plugin — minimal CPython build, controlled bridge API, state mutation only, optional bounded dynamic regions.

> [!important] Hybrid never replaces static
> Static mode is the default identity. Hybrid is an optional plugin layer. Even if hybrid ships, static apps behave exactly the same way.

## Controlled mutation model

If hybrid ever ships, mutation would be bounded:

**Level 1 — Pure state mutation**: Python can modify integers, update text, toggle visibility, trigger navigation. Structure remains static.

**Level 2 — Bounded dynamic regions** (optional): Marked regions like `Column(id="task_list", mutable=True)` get a managed adapter. Items live inside a sandbox, can't override static IDs, can't modify parent structure.

## Learn more

- Static vs reactive: [[20 - Core Concepts/03 - Static vs Reactive Mode]]
- Deferred features: [[60 - Architecture/04 - Deferred Features]]
- Runtime model: [[60 - Architecture/02 - Runtime Model]]
