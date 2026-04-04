---
tags: [ahnali, philosophy, design]
---

# Design Philosophy

> [!abstract] Why Ahnali is built the way it is
> Four principles drive every decision: correctness, one-way lowering, dumb emission, and phase discipline.

## Correctness over features

If a phase can't validate its output, the pipeline stops. No "good enough" passes. No "we'll fix it later." Every transformation has verification gates, and those gates are blocking.

This means the compiler is slower to grow — each new feature needs tests, validation, and integration work. But it also means when something compiles, you can trust it.

## One-way lowering only

Nothing goes backwards. DSL becomes IR, IR becomes CFG, CFG becomes SSA, SSA becomes Dalvik, Dalvik becomes Smali. No phase mutates the output of a later phase. No back-patching.

This constraint makes the compiler easier to reason about. If there's a bug in the Smali output, you can trace it back through exactly one path.

## Dumb emission

The Smali emitter doesn't make decisions. It doesn't try to optimize, or guess, or be clever. It prints what the verified IR tells it to print.

If the Smali is wrong, an earlier phase should've caught it. The emitter is just a printer.

## Phase discipline

Each phase has a single responsibility. CFG construction doesn't do type inference. SSA optimization doesn't do register allocation. The boundaries are strict.

This makes the codebase bigger than a monolithic compiler would be. It also makes it possible to understand, test, and modify individual phases without breaking everything else.

## Static by default

Everything is resolved at compile time. UI structure, navigation, state, event handlers, capability calls — all compiled in. The resulting APK has no interpreter, no runtime UI tree builder, no dynamic dispatch.

Reactive mode exists, but you have to explicitly ask for it. And even then, the UI tree is static — only the data flow changes.

## No shortcuts

Nothing goes straight from DSL to Smali. Every transformation earns its place in the pipeline. If you can't describe what a phase does in one sentence, it probably shouldn't exist.

## What this means for you

**Good:** When your app compiles, it works the way the compiler says it will. No runtime surprises. Small APKs. Native performance.

**Trade-off:** The DSL is restricted. You can't do everything you could in Kotlin. Some things that are easy in Kotlin require more explicit code in Ahnali. This is intentional — the restriction is what makes static analysis possible.

## Learn more

- How the pipeline enforces these principles: [[20 - Core Concepts/02 - Compiler Pipeline]]
- Static vs reactive: [[20 - Core Concepts/03 - Static vs Reactive Mode]]
- What's deferred and why: [[70 - Project/02 - Roadmap]]
