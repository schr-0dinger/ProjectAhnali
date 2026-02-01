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

---

🔴 ANALI CONTEXT RESET BEACON 🔴

You are helping me build Anali, a Python DSL → Smali compiler.

Current phase: ALPHA (Semantic Core)

HARD CONSTRAINTS:

No Android UI, widgets, resources, or lifecycle sugar

No shortcuts from DSL to Smali

CFG must exist before SSA

SSA must exist before register allocation

Verification is mandatory and a hard gate

Emission must be dumb and purely textual

TASK EXPECTATION:

Stay strictly within compiler architecture

Prefer correctness over features

Do not propose hacks, shortcuts, or “temporary” fixes

Keep solutions phase-appropriate

If your answer violates these constraints, stop and correct course.

----

I — CFG VALIDATION PASS (PRE-SSA)

Purpose: prove that control flow is sane before adding SSA complexity
SSA must never run on an invalid CFG.

1️⃣ When CFG validation runs

After CFG construction

Before:

dominance computation

phi insertion

SSA renaming

any lowering

If CFG validation fails → hard stop.

2️⃣ CFG Validation Checklist (ALL mandatory)
Rule CFG-1 — Entry & Exit Integrity

Exactly one entry block

Exactly one exit block

Entry has no predecessors

Exit has no successors

Failure here = malformed function.

Rule CFG-2 — Reachability

Every block must be reachable from entry

Exit must be reachable from entry

Algorithm:

DFS from entry

Compare visited blocks vs cfg.blocks

Unreachable blocks = logic bug in builder.

Rule CFG-3 — Terminator Completeness

Every block must end with exactly one terminator

No statements allowed after a terminator

Allowed terminators (conceptual):

Branch

Jump

Return

Zero terminators or multiple terminators = invalid CFG.

Rule CFG-4 — Successor/Predecessor Symmetry

For every edge A → B:

B ∈ A.successors

A ∈ B.predecessors

Asymmetry means CFG corruption.

Rule CFG-5 — Structured Edge Legality

Branch must have exactly two successors

Jump must have exactly one successor

Return must have zero successors

Anything else is illegal.

Rule CFG-6 — Exit Reachability

All paths must eventually reach exit

No infinite fallthrough paths

Algorithm:

Reverse DFS from exit

Ensure all blocks can reach exit

This catches malformed loops.

3️⃣ CFG Validation Failure Policy

If any rule fails:

Raise a compiler error

Include:

block id

violated rule

short explanation

No recovery. No partial success.

4️⃣ Why CFG Validation Exists

Because SSA assumes:

correct predecessors

correct merges

correct dominance

Running SSA on a broken CFG produces silent miscompilation — the worst kind.

II — PHI INSERTION ALGORITHM (DETAILED)

Purpose: Insert Phi nodes only where values can diverge and reconverge.

This is where most amateur compilers break.

1️⃣ Inputs

Valid CFG

Set of variables assigned per block

Dominator tree

Dominance frontiers

2️⃣ Required Precomputation
A. Compute Dominators

For each block B, compute:

dom(B) — set of blocks dominating B

idom(B) — immediate dominator

B. Compute Dominance Frontier (DF)

Definition:

Block Y is in DF(X) if:

X dominates a predecessor of Y

X does not strictly dominate Y

Dominance frontier is where values merge.

3️⃣ Variable Definition Collection

For each variable v:

Compute def_blocks[v] = set of blocks where v is assigned

This must include:

assignments

loop-carried updates

variable initialization

4️⃣ Phi Insertion Algorithm (Per Variable)

This is the classic Cytron algorithm, adapted conservatively.

Algorithm
worklist = def_blocks[v]
has_phi = empty set

while worklist not empty:
    X = pop(worklist)

    for each Y in DF(X):
        if Y not in has_phi:
            insert phi for v in Y
            has_phi.add(Y)

            if Y not in def_blocks[v]:
                add Y to worklist

5️⃣ Properties of This Algorithm

Sound: never misses required Phi

Conservative: may insert extra Phi (acceptable in Alpha)

Deterministic

CFG-driven, not syntax-driven

6️⃣ Phi Node Placement Rules

A Phi node:

Appears at top of a block

One Phi per variable per block

One incoming per predecessor

Incoming values are filled later during renaming.

7️⃣ Forbidden Phi Behavior

❌ Phi in block with one predecessor
❌ Phi without matching predecessor edges
❌ Phi created during renaming
❌ Phi created during lowering

Phi insertion is a separate, explicit pass.

8️⃣ Why Phi Insertion Is Separate from Renaming

Because:

Placement is structural

Renaming is semantic

Mixing them causes hidden bugs

III — SSA-AWARE VERIFICATION RULES

Purpose: Prove SSA is correct, complete, and unambiguous
This is the last semantic checkpoint before lowering.

1️⃣ Verification Order

SSA verification runs after renaming, before lowering.

If SSA verification fails → stop compilation.

2️⃣ SSA Verification Rules
SSA-1 — Single Definition Rule

Each SSAValue:

Must be defined exactly once

Either by:

assignment

Phi target

Duplicate definitions = fatal error.

SSA-2 — Dominance Rule

Every use of an SSAValue must be dominated by its definition.

Algorithm:

For each use, check:

def_block ∈ dom(use_block)

Violation = use-before-definition.

SSA-3 — Phi Predecessor Matching

For every Phi node in block B:

Incoming keys must match B.predecessors exactly

No missing edges

No extra edges

Mismatch = CFG/SSA inconsistency.

SSA-4 — Phi Placement Legality

Phi nodes may exist only in blocks with ≥2 predecessors

Phi nodes must appear before all statements

Violation = illegal SSA form.

SSA-5 — Variable Version Monotonicity

For each variable name:

Versions must be strictly increasing

No reuse of (name, version) pairs

This ensures determinism and sanity.

SSA-6 — No Non-SSA Variables Remain

After SSA:

No raw variable names allowed

All references must be SSAValue

Any remaining variable name = incomplete renaming.

3️⃣ SSA Failure Policy

On failure:

Identify:

variable name

version

block id

violated rule

Abort compilation

No lowering allowed after SSA failure.

4️⃣ Why SSA Verification Is Separate from CFG Verification

Because:

CFG verifies where control can go

SSA verifies which value is used

They answer different questions.

Conflating them is a design error.

FINAL SYNTHESIS (KEEP THIS MENTALLY)

CFG validation ensures structural truth

Phi insertion ensures merge correctness

SSA verification ensures semantic truth

Only after all three pass do you have:

a program that can be safely lowered to Dalvik

---

I — DOMINANCE COMPUTATION ALGORITHM

Dominance is the backbone of SSA.
If dominance is wrong, SSA cannot be correct.

We use the classic iterative dominance algorithm (simple, correct, Alpha-appropriate).

1️⃣ Definitions (frozen)

Block A dominates block B
⇢ Every path from entry to B passes through A

Immediate Dominator (idom)
⇢ The closest strict dominator of a block

Dominator Tree
⇢ Tree formed by idom relationships

2️⃣ Inputs & Outputs
Input

Valid CFG (already validated)

Output

dom[B] → set of dominators of block B

idom[B] → immediate dominator

Dominator tree

3️⃣ Dominator Set Computation (Iterative)
Initialization
For entry block E:
    dom[E] = {E}

For all other blocks B:
    dom[B] = all blocks

Iteration (until fixed point)
repeat:
    changed = false

    for each block B ≠ entry:
        new_dom = {B} ∪ intersection(dom[P] for each predecessor P of B)

        if new_dom ≠ dom[B]:
            dom[B] = new_dom
            changed = true
until not changed

4️⃣ Immediate Dominator Computation

For block B ≠ entry:

idom[B] is the unique block D such that:

D ∈ dom[B]

D ≠ B

D does not dominate any other strict dominator of B

Algorithmically:

idom[B] = the dominator of B (excluding B) with the largest dom-set

5️⃣ Dominator Tree Construction

For each block B ≠ entry:

Add edge idom[B] → B

This tree defines SSA renaming traversal order.

6️⃣ Dominance Invariants (Must Hold)

Entry dominates all blocks

Each block has exactly one immediate dominator (except entry)

Dominator tree is acyclic

Dominator tree includes all blocks

If any fail → CFG is invalid or dominance algorithm is wrong.

7️⃣ Why Iterative Dominance Is Enough for Alpha

CFGs are small

Simplicity > performance

Correctness is obvious

Easy to debug

Omega can upgrade to Lengauer–Tarjan later. Alpha must be boring.

II — SSA LOWERING CONTRACTS

(SSA → Dalvik IR)

This is where most compilers cheat.
We will not.

Lowering must not change semantics.
Lowering must not “fix” SSA.
Lowering must not introduce ambiguity.

1️⃣ What SSA Lowering Is Allowed to Assume

Lowering may assume:

SSA is fully verified

Every value is defined once

All Phi nodes are legal

CFG structure is correct

Dominance holds

If lowering depends on anything else, the design is wrong.

2️⃣ What SSA Lowering Must Produce

For each CFG block:

A linear Dalvik instruction list

Explicit labels

Explicit jumps

No Phi nodes

Phi nodes must be eliminated, not translated.

3️⃣ Phi Elimination Contract (Critical)

Phi nodes are eliminated by edge moves, not inline logic.

Rule

For Phi node in block B:

x = phi(P1: v1, P2: v2, ...)


For each predecessor Pi:

Insert before the terminator of Pi:

move x <- vi

Invariants

Moves happen on incoming edges

Phi targets are real SSA values

No move occurs after terminator

No move occurs in successor block

This preserves SSA semantics exactly.

4️⃣ Ordering Rules for Phi Moves

If multiple Phi nodes exist:

Moves must be ordered to avoid clobbering

Temporary values may be introduced (allowed)

Alpha rule:

Use parallel-move resolution (even naive is fine)

5️⃣ Lowering of SSA Statements
Assignment
x2 = x1 + 1


⇢

add-int x2, x1, 1

Conditionals

SSA values used directly

No recomputation

No hidden temporaries

6️⃣ Forbidden SSA Lowering Behavior

❌ Evaluating expressions twice
❌ Rewriting CFG
❌ Removing blocks
❌ Introducing new control flow
❌ Allocating registers

Lowering is semantic projection, not transformation.

7️⃣ Lowering Invariants (Post-Lowering)

No Phi nodes remain

Every Dalvik value corresponds to one SSAValue

CFG structure unchanged

Instruction order preserves dominance semantics

If any invariant breaks → lowering is invalid.

III — ALPHA GOLDEN TEST CASES

(CFG + SSA, fully explicit)

These are non-negotiable.
Your implementation must reproduce these exactly.

🧪 TEST 1 — Straight Line
Source DSL
x = 1
x = x + 1

CFG
B0 (entry)
  |
  v
B1 (exit)

SSA
B0:
  x0 = 1
  x1 = x0 + 1


No Phi.
Dominance trivial.

🧪 TEST 2 — If / Else Merge
Source DSL
x = 0
if cond:
    x = 1
else:
    x = 2
y = x

CFG
        B0
        |
       cond
      /    \
    B1      B2
      \    /
        B3

SSA
B0:
  x0 = 0

B1:
  x1 = 1

B2:
  x2 = 2

B3:
  x3 = phi(B1: x1, B2: x2)
  y0 = x3


Phi mandatory.
Any implementation without this Phi is wrong.

🧪 TEST 3 — While Loop (Loop-Carried Variable)
Source DSL
x = 0
while x < 3:
    x = x + 1

CFG
        B0
        |
        v
       B1 (cond)
      /    \
    B2      B3 (exit)
     |
     └──────┘

SSA
B0:
  x0 = 0

B1:
  x1 = phi(B0: x0, B2: x2)
  if x1 < 3 goto B2 else B3

B2:
  x2 = x1 + 1
  goto B1


This test forces correct Phi insertion + dominance.

🧪 TEST 4 — Nested If in Loop (Alpha Stress Test)
Source DSL
x = 0
while x < 5:
    if cond:
        x = x + 1
    else:
        x = x + 2

SSA (key part)
B1:
  x1 = phi(B0: x0, B4: x4)

B2:
  x2 = x1 + 1

B3:
  x3 = x1 + 2

B4:
  x4 = phi(B2: x2, B3: x3)
  goto B1


This catches:

incorrect Phi placement

dominance errors

broken renaming stacks