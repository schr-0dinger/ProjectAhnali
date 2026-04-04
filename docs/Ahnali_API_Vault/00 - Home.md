---
tags: [ahnali, moc, index]
aliases: [Home, Ahnali Docs]
---

# Ahnali

> [!abstract] What is this?
> Ahnali is a Python-to-Android compiler. You write Python, it emits Smali, you get an APK. No Java, no Kotlin, no Gradle - straight from DSL to Dalvik bytecode.

---

## Start Here

| If you're... | Go to... |
|---|---|
| New to Ahnali | [[01 - Quick Start]] |
| Want to build your first app | [[02 - Your First App]] |
| Setting up the toolchain | [[03 - Project Setup]] |

## Core Concepts

Understanding how Ahnali works under the hood.

- [[20 - Core Concepts/01 - How Ahnali Works]] - The big picture
- [[20 - Core Concepts/02 - Compiler Pipeline]] - DSL → IR → CFG → SSA → Smali
- [[20 - Core Concepts/03 - Static vs Reactive Mode]] - Two modes, one compiler
- [[20 - Core Concepts/04 - Capabilities System]] - How platform access works
- [[20 - Core Concepts/05 - State Management]] - State backends and lifecycle
- [[20 - Core Concepts/06 - Design Philosophy]] - Why Ahnali is built this way

## API Reference

The complete DSL surface, organized by category.

### App Model
- [[30 - API Reference/01 - App Model]] - `app`, `activity`, `app_config`, `state`

### Values & Styling
- [[30 - API Reference/02 - Value Types and Units]] - `dp`, `sp`, colors, gradients
- [[30 - API Reference/03 - Shared Attributes]] - Layout, typography, tint, elevation, effects
- [[30 - API Reference/08 - Theme Style and Presets]] - `Theme`, `Style`, `ColorState`, `presets`

### Components
- [[30 - API Reference/04 - Structure Components]] - `Row`, `Column`, `Card`, `ScrollView`, `Screen`
- [[30 - API Reference/05 - Content and Display]] - `Text`, `Button`, `Image`, `AppBar`, `Divider`
- [[30 - API Reference/06 - Input and Selection]] - `TextField`, `Checkbox`, `Slider`, `Dropdown`, `ListView`
- [[30 - API Reference/07 - Feedback and Utility]] - `toast`, `snackbar`, `dialog`, `exit_app`

### Behavior
- [[30 - API Reference/09 - Events and Handlers]] - `on_click`, `on_change`, `on_text_change`, and more
- [[30 - API Reference/10 - Navigation and Screens]] - `Navigate`, `Back`, `Replace`, screen transitions
- [[30 - API Reference/11 - Animation DSL]] - `animate`, `fade_in`, `sequence`, `parallel`
- [[30 - API Reference/12 - Validation and Diagnostics]] - Compile-time checks and error messages

### Reference
- [[30 - API Reference/13 - Component Attribute Matrix]] - Every component and its attributes at a glance

## Capabilities

Platform services you can tap into from your handlers.

- [[40 - Capabilities/01 - Overview]] - How capabilities work
- [[40 - Capabilities/02 - Networking]] - HTTP sync, async, retry, JSON parsing
- [[40 - Capabilities/03 - Storage]] - SharedPreferences, DataStore, SQLite, Room, encrypted
- [[40 - Capabilities/04 - Permissions]] - Runtime permission requests and checks
- [[40 - Capabilities/05 - Notifications]] - Channels and notifications
- [[40 - Capabilities/06 - WebView]] - Web content, JS bridge, file chooser, cookies
- [[40 - Capabilities/07 - Sharing and Intents]] - Share text/files, open URIs
- [[40 - Capabilities/08 - Clipboard]] - Copy and paste
- [[40 - Capabilities/09 - Location]] - Location provider checks
- [[40 - Capabilities/10 - Deep Linking]] - Handle launch URIs
- [[40 - Capabilities/11 - Background Work]] - WorkManager, AlarmManager, JobScheduler
- [[40 - Capabilities/12 - Runtime ABI]] - Helper class contracts and signatures

## Tooling

- [[50 - Tooling/01 - Build and Package]] - From Smali to signed APK
- [[50 - Tooling/02 - Testing]] - Running the test suite
- [[50 - Tooling/03 - Benchmarking]] - APK size and cold-start gates
- [[50 - Tooling/04 - CI Gates]] - What CI checks and blocks
- [[50 - Tooling/05 - Python Library Policy]] - Dependency rules

## Architecture

- [[60 - Architecture/01 - Dual Mode Architecture]] - Static default, hybrid optional
- [[60 - Architecture/02 - Runtime Model]] - Core runtime and capability modules
- [[60 - Architecture/03 - Optimization Backlog]] - What we want to add eventually
- [[60 - Architecture/04 - Deferred Features]] - What's parked for post-v1

## Project

- [[70 - Project/01 - Current Status]] - Where things stand right now
- [[70 - Project/02 - Roadmap]] - What's next
- [[70 - Project/03 - Contributing]] - How to help

## Strategy

The long-term vision: making Ahnali as powerful as Kotlin through smart transpilation with on-demand runtime injection.

- [[80 - Strategy/01 - Strategic Vision]] - The goal, the approach, what we can replicate
- [[80 - Strategy/02 - Implementation Roadmap]] - Phase-by-phase plan from v1 to production

---

> [!info] About this vault
> This vault reflects the current repository implementation. If something here doesn't match the code, the code wins - file an issue or open a PR.
