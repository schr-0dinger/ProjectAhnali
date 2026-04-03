# Ahnali

[![Version](https://img.shields.io/badge/version-alpha-red.svg)](https://github.com/schr-0dinger/ProjectAhnali)
[![Version](https://img.shields.io/badge/status-WIP-yellow.svg)](https://github.com/schr-0dinger/ProjectAhnali)
![GitHub License](https://img.shields.io/github/license/:schr-0dinger/:ProjectAhnali)
[![Platform](https://img.shields.io/badge/platform-Android-brightgreen.svg)](https://developer.android.com)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)

Ahnali is a **Python DSL → IR → CFG → SSA → Typed SSA → Dalvik IR → Smali** compiler for Android.

It is an **ahead-of-time (AOT) compiler** that translates a restricted, declarative Python-like DSL into **Dalvik bytecode**, producing fully native Android apps with:

- zero runtime interpretation  
- zero reflection  
- deterministic behavior  
- analyzable capability boundaries  

---

## ⚡ Core Idea

Ahnali is **not a framework**.

It is a **compiler toolchain** that emits:

- Static UI structure
- Static navigation
- Static state wiring
- Deterministic helper-call bridges to Android APIs

There is **no runtime engine**, no virtual DOM, no interpreter.

---

## 🧠 Architecture Overview

DSL → IR → CFG → SSA → Typed SSA → Optimizations → Dalvik IR → Register Allocation → Smali

All transformations are:

- **one-way**
- **verified**
- **deterministic**

---

## 🎯 v1 Scope (Authoritative)

The current release track is strictly:

> **Static AOT compiler + deterministic helper-call capability slices**

Included:

- Compiler pipeline (DSL → Smali)
- Static UI + navigation + state
- Capability helpers:
  - Storage
  - Networking
  - Permissions
  - Notifications
  - WebView
  - Sharing
  - Background work

Not included (deferred):

- JNI / native bridge  
- Embedded Python runtime  
- Dynamic feature systems  
- Hybrid execution model  

---

## 🧱 Repository Structure

dsl/  
ir/  
cfg/  
ssa/  
dalvik/  
passes/  
emit/  
tests/  

---

## 🔬 Pipeline (Authoritative)

DSL → CFG → Dominance → Phi insertion → SSA rename → SSA verify → Type inference → Type verify → SSA optimizations → Dalvik lowering → Dead code elimination → CFG simplification → Liveness → Linear scan register allocation → Spilling → Smali emission

---

## ✅ Status

### Completed

- CFG + SSA + verification
- Typed SSA
- Exception-capable CFG
- Register allocation (linear scan)
- Dead code elimination
- CFG simplification
- Try/catch + throw → Smali
- Packaging pipeline (`aapt2`, `zipalign`, `apksigner`)

### Tests

648 passed, 3 skipped

---

## 🧩 Capability Model

Capabilities are:

- explicit
- compile-time resolved
- permission-aware
- mapped to helper calls

Example:

app_config(uses=[Caps.Networking, Caps.Storage])

---

## 🧪 Running Tests

python -m pytest

---

## 📊 Benchmarking

Size-only:

PYTHONPATH=. python tools/benchmark_apk.py --threshold-file cfg/benchmark_thresholds.json --baseline-file cfg/benchmark_baseline.json --skip-cold-start

---

## ⏸ Deferred Beyond V1

- Motion system
- Advanced/system/security/debug
- JNI / native bridge
- Embedded Python runtime

---

## 🧠 Design Principles

- Correctness over features
- Static over dynamic
- Explicit over implicit
- Verification over convenience
- Compilation over interpretation

---

## 🚫 What Ahnali Is Not

- Not React / Flutter / Compose  
- Not a Python runtime  
- Not a UI framework  
- Not a plugin system  

---

## 🧭 Philosophy

Ahnali treats Android as a compile target, not a runtime environment.

> The DSL is not executed. It is resolved, verified, and erased into native code.
