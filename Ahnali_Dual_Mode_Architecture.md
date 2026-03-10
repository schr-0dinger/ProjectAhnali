# Ahnali Architecture Plan --- Dual Mode (Static + Hybrid)

Status: Experimental research appendix (post-v1)\
Phase Target: post-v1 research after static foundation freeze\
Scope: Android-only

------------------------------------------------------------------------

# 1. Core Philosophy

Ahnali is and will always be:

-   An ahead-of-time (AOT) Android compiler
-   Deterministic
-   Smali-emitting
-   Runtime-minimal
-   Static-first

Hybrid mode does not redefine Ahnali.

Hybrid mode is: - An optional plugin layer - Capability-scoped -
Strictly bounded - Never structural by default

------------------------------------------------------------------------

# 2. Two Operating Modes

Ahnali operates in two clearly defined modes.

## Mode A --- Static Mode (Default)

Canonical Ahnali behavior.

Characteristics:

-   Entire UI compiled at build time
-   Navigation compiled
-   State compiled
-   Event handlers compiled
-   No interpreter
-   No dynamic UI construction
-   No runtime code execution

Result:

-   Small APK
-   Deterministic behavior
-   Maximum performance
-   Full static analyzability
-   Zero reflection
-   No dynamic execution

------------------------------------------------------------------------

## Mode B --- Hybrid Mode (Optional Plugin)

Activated only when explicitly requested:

app_config(enable_module="python", python_lib=\["json", "socket"\])

Hybrid introduces:

-   Minimal Python execution environment
-   Controlled runtime logic execution
-   JNI-based execution boundary
-   Strictly bounded mutation capabilities

Hybrid mode never replaces static mode.

------------------------------------------------------------------------

# 3. Hybrid Mode Architecture

Stage 1 --- Native Execution Infrastructure

Before introducing Python runtime:

-   NDK-based native library integration
-   Shared object loading (.so)
-   Controlled JNI entrypoints
-   Capability-scoped native calls

Enables:

-   Native C/C++ logic
-   High-performance computation
-   Cryptographic primitives
-   Background logic
-   Future Python embedding

------------------------------------------------------------------------

Stage 2 --- Optional Python Runtime Plugin

Execution Flow:

Static UI (Smali) → Core Runtime (Smali) → JNI Bridge → libpython3.x.so
→ Restricted Python Execution

Core Rule:

UI is always static.

Python may: - Mutate state - Trigger navigation - Call approved
capabilities - Perform computation - Manage background logic

Python may NOT: - Create arbitrary new views (unless in bounded
region) - Destroy compiled views - Inject arbitrary classes - Access
Android APIs directly

All Android access passes through capability wrappers.

------------------------------------------------------------------------

# 4. Controlled Mutation Model

Level 1 --- Pure State Mutation

Python can: - Modify integers - Update text - Toggle visibility -
Trigger navigation

Structure remains static.

Level 2 --- Bounded Dynamic Regions (Optional)

Example:

Column(id="task_list", mutable=True)

Compiler generates:

-   Managed adapter region
-   Internal view factory
-   ID namespace isolation
-   Auto-generated dynamic IDs

Dynamic items: - Live inside sandbox - Cannot override static IDs -
Cannot modify parent structure

Structural mutation outside dynamic regions remains disallowed.

------------------------------------------------------------------------

# 5. JNI and Native Integration

Step 1 --- NDK Setup

-   Install Android NDK
-   Use NDK clang
-   Build shared libraries via CMake or direct clang

Step 2 --- Shared Object Integration

APK includes:

lib/armeabi-v7a/libahnali_native.so\
lib/arm64-v8a/libahnali_native.so

Loaded via:

System.loadLibrary("ahnali_native")

------------------------------------------------------------------------

# 6. Python Plugin Size Strategy

Estimated minimal CPython size: 5--10MB

Optimization strategy:

-   Remove unused modules
-   Strip debug symbols
-   Freeze required modules only
-   Capability-scoped inclusion

Hybrid APK increase is acceptable.

------------------------------------------------------------------------

# 7. Static vs Hybrid Responsibilities

Static Mode: - UI structure - Navigation graph - Event handlers - State
wiring - Capability resolution

Hybrid Mode: - Additional runtime logic - Optional dynamic state-driven
updates - Controlled computation layer - Python-backed background logic

------------------------------------------------------------------------

# 8. Implementation Phases

Phase 0 --- Static Stabilization - Deterministic emission - Stable
navigation - Capability registry - Manifest injection - Multidex support

Phase 1 --- Native Execution Layer - NDK integration - JNI bridge -
Capability-scoped native calls

Phase 2 --- Python Hybrid Plugin - Minimal CPython build - Controlled
bridge API - State mutation only - Optional bounded dynamic regions

------------------------------------------------------------------------

# Final Position

Ahnali is:

-   A static Android compiler at its core
-   With optional controlled dynamic logic
-   With optional embedded Python
-   With JNI-native support
-   Without surrendering structural determinism

Static is identity.\
Hybrid is power.\
Boundaries preserve integrity.
