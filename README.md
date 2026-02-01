anali/
├── dsl/                # user-facing API (tiny)
│   └── app.py
│
├── ir/                 # frontend IR (VERY small)
│   ├── expr.py
│   ├── stmt.py
│   └── types.py
│
├── cfg/                # control flow graph (core)
│   ├── block.py
│   ├── graph.py
│   └── builder.py
│
├── dalvik/             # Dalvik-aware IR
│   ├── instr.py
│   ├── value.py
│   └── block.py
│
├── passes/
│   ├── lower_to_cfg.py
│   ├── ssa.py
│   ├── regalloc.py
│   └── verify.py
│
├── emit/
│   └── smali.py
│
└── tests/
    └── golden/

-----------------------------------

🧬 ANALI DEVELOPMENT CONSTITUTION

(Alpha → Omega)

    PART I — CORE PHILOSOPHY (IMMUTABLE)
    Rule 1 — Anali is a compiler, not a code generator

    Every output must be derivable from intermediate representations.

    No direct DSL → Smali shortcuts.

    No “just emit this line”.

    If something bypasses IR → reject the change.

    Rule 2 — Correctness beats features, always

    A smaller correct compiler > a large buggy one.

    Any feature that weakens verification is illegal.

    “Works in practice” is not a success metric.

    Rule 3 — Every phase has a single responsibility

    If a file needs to “know” two phases → architecture violation.

    If a bug fix touches 3+ phases → design flaw, not patch material.

    Rule 4 — Verification is law, not tooling

    Verification failure must halt compilation

    No --force, no bypass flags

    No “best effort” emission

    Rule 5 — Smali emission must be dumb

    Emission ≠ decision making

    Emission ≠ validation

    Emission ≠ optimization

    If emission contains logic → upstream is broken.

    PART II — PHASE MODEL (ALPHA → OMEGA)

    Each phase unlocks the next.
    You do not partially skip phases.

🟡 ALPHA — Semantic Core

    “Can this compiler be trusted at all?”

    Allowed features

    Single activity

    Scalars only (int, boolean, string)

    assign, if, while

    Framework calls as opaque calls (no callbacks)

    Forbidden

    ❌ UI widgets
    ❌ Resources
    ❌ Event listeners
    ❌ Exceptions
    ❌ Objects
    ❌ Arrays

    Mandatory invariants

    Structured DSL → Frontend IR

    CFG built for all methods

    SSA is correct

    Register allocation is deterministic

    Verification is exhaustive

    Exit criteria

    ✔ While-loops compile correctly
    ✔ If/else merges verified
    ✔ No use-after-free possible
    ✔ .locals always correct

    If Alpha fails, nothing else matters.

🟢 BETA — Dalvik Reality

    “Can this generate real bytecode safely?”

    New features

    Objects (new-instance, fields)

    Method calls (virtual, direct, static)

    Basic Android lifecycle (onCreate, onClick)

    Simple layouts as objects (no XML yet)

    New invariants

    Object lifetimes tracked

    this always pinned

    Constructor rules enforced

    Method sealing mandatory

    New verification rules

    Constructor must call super.<init> first

    Object used only after initialization

    No leaked temporaries across calls

    Forbidden

    ❌ XML resources
    ❌ Reflection
    ❌ Threads
    ❌ Exceptions

    Exit criteria

    ✔ Generated APK installs
    ✔ Lifecycle works
    ✔ No verifier false positives
    ✔ Smali passes baksmali → smali roundtrip

🔵 GAMMA — Android Semantics

    “Does this understand Android, not just Dalvik?”

    New features

    Android framework API modeling

    Type-aware calls (View, Context, Activity)

    Event callbacks

    Resource IDs (still no XML)

    Architectural rule

    Android APIs are modeled, not hardcoded

    You must introduce:

    API descriptors

    Signature tables

    Type constraints

    New verification

    Method signature correctness

    Context validity

    Lifecycle legality

    Example:

    No UI access off main thread

    No view usage before setContentView

    Exit criteria

    ✔ Multiple activities
    ✔ Event callbacks verified
    ✔ Framework misuse rejected at compile-time

🟣 DELTA — Resources & UI

    “Can this build a real app?”

    New features

    XML layout generation

    Resource compilation model

    ID linking

    View binding

    Critical rule

    Resources are compiled, not copied

    No raw XML dumping.
    Resources must be:

    modeled

    validated

    linked

    New invariants

    Every ID resolves

    No unused resources

    Layout inflation verified

    Exit criteria

    ✔ UI renders correctly
    ✔ IDs stable across builds
    ✔ No runtime layout crashes

🟠 EPSILON — Optimization & Scale

    “Can this handle real programs?”

    New features

    Dead code elimination

    Register reuse optimization

    CFG simplification

    Inlining (limited)

    Optimization rule

    Optimization must preserve verification invariants

    No peephole hacks

    No post-allocation rewrites

    No “trust me” transforms

Exit criteria

✔ Smaller Smali output
✔ No semantic regressions
✔ Verified optimized builds

🔴 ZETA — Full Android Surface

“Can this replace writing Java/Kotlin?”

New features

Threads

Services

Broadcast receivers

Intents

Permissions

Exceptions (finally)

Hard constraint

Every new Android feature requires:

IR representation

CFG semantics

Verification rules

Dalvik lowering rules

If any are missing → feature rejected.

⚫ OMEGA — Complete Native Integration

“Anali is a first-class Android compiler.”

Capabilities

Full Android API surface

Complete resource system

Deterministic builds

Static verification of Android misuse

Optimized Smali output

Toolchain-grade reliability

Omega invariants

No runtime surprises

Compile-time rejection of illegal Android code

Smali output indistinguishable from hand-written expert code

PART III — DEVELOPMENT RULES (ABSOLUTE)
Rule A — No feature without IR

If you can’t model it in IR, you don’t understand it.

Rule B — No IR without CFG

If control flow matters, CFG must exist first.

Rule C — No CFG without verification

CFG bugs propagate catastrophically.

Rule D — No verification exceptions

If a rule is annoying → fix the design, not the rule.

Rule E — No large commits

One phase

One concept

One invariant

Rule F — No “temporary” hacks

Temporary hacks become permanent debt.

PART IV — FAILURE MODES (WHAT TO WATCH FOR)

🚨 DSL growing faster than backend
🚨 Emission logic increasing
🚨 Verification rules being relaxed
🚨 “We’ll fix it later” comments
🚨 Features before CFG changes

Any of these = stop development