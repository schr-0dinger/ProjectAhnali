---
tags: [ahnali, core, overview]
---

# How Ahnali Works

> [!abstract] The short version
> You write Python that describes UI, state, navigation, and platform calls. Ahnali compiles it to Smali, packages it into an APK, and installs it on your device. Nothing is interpreted at runtime.

## The mental model

Think of Ahnali as a compiler, not a framework. You're not importing a library and calling its functions - you're writing a description of your app in a restricted Python dialect, and the compiler turns that description into native Android bytecode.

```
Your Python DSL
    ↓
Ahnali Compiler
    ↓
Smali (Dalvik bytecode)
    ↓
APK (aapt2 + zipalign + apksigner)
    ↓
Your Android device
```

## What makes this different

Most Python-to-Android tools embed a Python runtime in your APK and interpret your code on the device. Ahnali doesn't do that. Your Python code is consumed entirely at compile time. The resulting APK contains zero Python - just Smali that talks directly to the Android framework.

This means:
- **Small APKs** - no embedded interpreter
- **Native performance** - it's just Dalvik bytecode
- **Full static analysis** - the compiler can validate everything before you ship
- **No runtime surprises** - if it compiles, it behaves the way the compiler says it will

## Two modes

**Static mode** (default): Everything is resolved at compile time. UI structure, navigation graph, state wiring, event handlers - all compiled in. This is Ahnali's identity.

**Reactive mode** (opt-in): You can opt into reactive bindings (`observable`, `bind_text`, `set_observable`) for cases where you need UI to respond to state changes. But this is explicit - you have to ask for it, and it doesn't change how static apps behave.

> [!note] Reactive doesn't mean dynamic
> Even in reactive mode, the UI tree is static. What changes is how data flows to widgets. There's no runtime diffing engine or dynamic widget construction.

## Capabilities

Want to make an HTTP request? Show a notification? Read from storage? You declare what you need in `app_config(uses=[Caps.Networking, Caps.Storage])` and the compiler links the right helper classes and injects the right manifest permissions.

If you don't declare a capability, you can't use it. The compiler catches this at compile time with a clear error message.

## The pipeline

Under the hood, your code goes through:

1. **DSL parsing** - your Python constructs become an IR
2. **CFG construction** - control flow graph with basic blocks
3. **SSA construction** - dominance, phi insertion, renaming
4. **Type inference** - everything gets typed
5. **SSA optimization** - constant propagation, copy propagation, coalescing
6. **Dalvik lowering** - IR becomes Dalvik instructions
7. **Register allocation** - liveness analysis, linear scan, spilling
8. **Smali emission** - verified IR becomes Smali text

Each phase validates its output. If something's wrong, the pipeline stops. No phase skips ahead.

## What you get

- 30+ widget types with full styling
- Navigation stack with transitions
- Six state backends (SharedPreferences, DataStore, SQLite, Room, encrypted, file)
- 18 capability waves (networking, storage, permissions, notifications, WebView, sharing, clipboard, deep linking, background work, location)
- Explicit animations and transitions
- Full APK packaging with signing

## Learn more

- The pipeline in detail: [[20 - Core Concepts/02 - Compiler Pipeline]]
- Static vs reactive: [[20 - Core Concepts/03 - Static vs Reactive Mode]]
- How capabilities work: [[20 - Core Concepts/04 - Capabilities System]]
- Why it's built this way: [[20 - Core Concepts/06 - Design Philosophy]]
