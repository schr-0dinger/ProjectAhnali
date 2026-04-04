---
tags: [ahnali, architecture, optimization, backlog]
---

# Optimization Backlog

> [!abstract] Things we want to add eventually
> None of this is enabled by default. Every optimization needs a flag, tests, and a good reason.

## High priority

- **Unused resource detection** - find and flag resources that nothing references
- **Unused permission detection** - catch permissions declared but never used
- **APK size diff reporting** - show what changed between builds
- **Dead code elimination hardening** - remove unused functions and state variables

## Medium priority

- **Image optimization** - PNG → WebP, strip metadata, auto-generate density buckets
- **Resource deduplication** - merge duplicate layouts, deduplicate repeated strings
- **Dependency analysis** - detect unused classes, flag conflicting versions, suggest lighter alternatives
- **Manifest optimization** - remove redundant features, warn about exported components

## Lower priority

- **Asset optimization** - video re-encoding, audio format conversion
- **Code-level optimization** - constant folding, branch pruning, function inlining
- **Native layer optimization** - strip debug symbols, enable LTO
- **Performance static analysis** - detect blocking network calls on main thread, flag expensive operations in UI callbacks
- **Security checks** - detect hardcoded secrets, warn about insecure HTTP, flag weak crypto
- **Build-time enhancements** - deterministic build hashing, reproducible artifacts, version stamping
- **Developer experience** - lint for anti-patterns, auto-format DSL, visual UI tree map

## The rule

Every optimization must:
1. Be deterministic
2. Be behind an explicit flag until behavior is stable
3. Have tests
4. Not regress build reproducibility or runtime correctness

## Learn more

- Design philosophy: [[20 - Core Concepts/06 - Design Philosophy]]
- Deferred features: [[60 - Architecture/04 - Deferred Features]]
