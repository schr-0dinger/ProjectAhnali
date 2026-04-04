---
tags: [ahnali, compiler, pipeline, ssa]
---

# Compiler Pipeline

> [!abstract] Overview
> DSL → IR → CFG → Dominance → Phi → SSA → Types → Optimize → Dalvik → Regalloc → Smali. Each step validates before the next one runs.

## The full pipeline

```
Python DSL
    ↓
Frontend IR (expr, stmt, method, program)
    ↓
CFG construction (basic blocks, edges)
    ↓
Dominance analysis
    ↓
Phi insertion
    ↓
SSA renaming
    ↓
SSA verification
    ↓
Type inference
    ↓
Type verification
    ↓
SSA optimization (const/copy propagation, coalescing)
    ↓
Dalvik lowering
    ↓
Dead code elimination
    ↓
CFG simplification (redundant goto removal, block merging)
    ↓
Liveness analysis
    ↓
Linear scan register allocation
    ↓
Spilling (when registers run out)
    ↓
Smali emission
```

## What each phase does

### Frontend IR

Your DSL constructs (`text`, `button`, `on_click`, `state`, etc.) get converted into a structured intermediate representation. This is where Python objects become compiler data.

### CFG construction

The IR gets broken into basic blocks — straight-line code segments with single entry and exit points. Branches (if/while) create edges between blocks.

### Dominance analysis

For each block, we figure out which other blocks dominate it (must execute before it). This is needed for SSA construction.

### Phi insertion

At join points in the control flow (where two paths merge), we insert phi functions to track which version of a variable we're using.

### SSA renaming

Every variable gets renamed so that each one is assigned exactly once. This is the core of Static Single Assignment form.

### SSA verification

We check that the SSA form is legal: single def, dominance properties hold, phi functions are well-formed. If this fails, something's wrong with an earlier phase.

### Type inference

Every expression and variable gets a type: INT, FLOAT, STRING, OBJECT, BOOLEAN, etc. This is needed for correct Dalvik instruction selection.

### Type verification

Types are checked against method signatures, call arguments, and return values. Mismatches are caught here.

### SSA optimization

Three passes:
- **Constant propagation** — replace variables with known constant values
- **Copy propagation** — replace `x = y` with direct use of `y`
- **Coalescing** — merge redundant copies across phi and non-phi moves

These can be enabled with `alpha_pipeline(..., ssa_opt={"enable_folding": True})`.

### Dalvik lowering

The typed SSA IR becomes Dalvik instructions. This is where `BinaryOp(ADD, x, y)` becomes `add-int`.

### Dead code elimination

Remove instructions whose results are never used.

### CFG simplification

- Remove redundant gotos
- Merge empty blocks with their single successor
- Retarget all branch and catch references

> [!warning] Safety constraints
> Entry/exit blocks are never simplified. Blocks in try regions are never simplified. Exceptional edges are never crossed.

### Liveness analysis

For each program point, figure out which variables are live (will be used before being reassigned). This drives register allocation.

### Register allocation

Linear scan allocation assigns Dalvik virtual registers to live ranges. When there aren't enough registers, spilling moves values to stack slots.

### Smali emission

The final step: verified, register-allocated Dalvik IR becomes Smali text. The emitter doesn't make decisions — it prints what the IR says.

## Verification gates

Every phase has validation:

| Gate | What it checks |
|---|---|
| CFG validation | Structural correctness, valid edges |
| SSA validation | Single def, dominance, phi legality |
| Type verification | Method signatures, call arity, return types |
| Try/catch validation | Non-empty try, descriptor types, catchall ordering |
| Throw validation | Must be OBJECT type |

If any gate fails, the pipeline stops. No exceptions.

## What's implemented

All phases from DSL through Smali emission are complete and tested. The pipeline handles:

- Control flow (if/while)
- Arithmetic and comparisons
- Typed calls and returns
- Exception handling (try/catch/throw)
- Register allocation with spilling
- Switch (packed/sparse)
- Monitor enter/exit

## Learn more

- How Ahnali fits together: [[20 - Core Concepts/01 - How Ahnali Works]]
- The ABI contract: [[40 - Capabilities/12 - Runtime ABI]]
- Build and packaging: [[50 - Tooling/01 - Build and Package]]
