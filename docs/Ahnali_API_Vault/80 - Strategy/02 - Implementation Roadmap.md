---
tags: [ahnali, roadmap, phases, implementation]
---

# Implementation Roadmap

> [!abstract] From DSL to Full Python
> The path from a restricted DSL to a smart transpiler that competes with Kotlin.

## Current State (v1)

What we have today:
- ✅ DSL → IR → CFG → SSA → Dalvik → Smali pipeline
- ✅ 30+ widget types with full styling
- ✅ 18 capability waves (networking, storage, permissions, etc.)
- ✅ For loops, try/except, function definitions
- ✅ Smart runtime injection (only what's used)
- ✅ 653 passing tests

## Phase 1: Feature Detection + Smart Runtime (Months 1-3)

**Goal**: Analyze Python code to detect used features, generate only needed runtime modules.

### 1.1 AST Feature Analyzer
```python
# Input: Python source code
# Output: FeatureUsageProfile

from dsl.analyzer import analyze_features

profile = analyze_features("""
def handler():
    items = [1, 2, 3]
    mapping = {"a": 1}
    for item in items:
        if item > 1:
            print(item)
""")

# profile = {
#     "collections": {"list": True, "dict": True},
#     "control_flow": {"for": True, "if": True},
#     "functions": {"def": True},
#     "builtins": {"print": True},
#     "classes": False,
#     "async": False,
#     "getattr": False,
# }
```

**Files to create:**
- `dsl/analyzer/__init__.py` — Feature analysis entry point
- `dsl/analyzer/collector.py` — AST visitor that collects feature usage
- `dsl/analyzer/profile.py` — FeatureUsageProfile dataclass
- `dsl/analyzer/runtime_selector.py` — Selects runtime modules from profile

### 1.2 Runtime Module System
```
dsl/runtime/modules/
├── __init__.py          # Runtime module registry
├── list_wrapper.py      # list → ArrayList wrapper spec
├── dict_wrapper.py      # dict → HashMap wrapper spec
├── set_wrapper.py       # set → HashSet wrapper spec
├── reflection.py        # getattr/setattr helpers
├── async_runtime.py     # coroutine runtime
├── iterator.py          # iterator protocol
└── ...
```

Each module defines:
- What features it provides
- What Smali code it generates
- What other modules it depends on

### 1.3 Smart Runtime Injection
```python
# In build_program():
profile = analyze_features(source_code)
modules = select_runtime_modules(profile)
runtime_smali = generate_runtime_smali(modules)
# Only include the Smali that's actually needed
```

### 1.4 Direct Android API Calls
```python
# No wrapper needed — direct Smali emission
from android.widget import TextView
text_view = TextView(context)
text_view.setText("Hello")
```

**Deliverable**: Can compile Python classes with Android API calls to Smali, with only the runtime modules that are actually used.

## Phase 2: Collections & Types (Months 4-6)

**Goal**: Full Python type system support with minimal runtime.

### 2.1 Collection Wrappers
- `list` → `ArrayList` wrapper (~50 lines Smali)
- `dict` → `HashMap` wrapper (~80 lines)
- `set` → `HashSet` wrapper (~40 lines)
- `tuple` → Immutable array wrapper (~20 lines)

### 2.2 Type System
- Type conversion (`int()`, `str()`, `float()`, etc.)
- `isinstance()`, `type()`
- Operator overloading (`__add__`, `__eq__`, etc.)
- List/dict comprehensions → loops

### 2.3 String Methods
- `split()`, `join()`, `replace()`, `strip()`, etc.
- `format()`, f-strings
- String comparison, slicing

**Deliverable**: Full Python collection support with minimal runtime (~200 lines Smali for full collection support).

## Phase 3: Android SDK Coverage (Months 7-9)

**Goal**: Complete Android API bindings.

### 3.1 Direct Smali Emission
- All Android APIs emit directly to Smali
- No wrapper classes needed
- Type-safe bindings generated from Android SDK

### 3.2 AndroidX & Jetpack
- Room → SQLite wrappers + DAO pattern
- ViewModel → State management pattern
- LiveData → Observable pattern
- Navigation → Screen stack + transitions
- WorkManager → `JobScheduler` + `AlarmManager`

### 3.3 Play Services
- Maps → Google Maps SDK bindings
- Location → FusedLocationProvider
- Ads → AdMob bindings

**Deliverable**: Can build any Android app using Python.

## Phase 4: Advanced Features (Months 10-12)

**Goal**: 95% Python syntax support.

### 4.1 Async/Await
- `async def` → coroutine state machine
- `await` → yield/resume pattern
- `asyncio` → coroutine runtime (~400 lines Smali)

### 4.2 Advanced OOP
- Multiple inheritance → interface pattern
- Descriptors → attribute resolution chain
- Metaclasses → class creation hooks
- `__getattribute__` → full attribute dispatch

### 4.3 Advanced Python
- Generators → state machine generation
- Decorators → function wrapping
- Context managers → try/finally pattern
- `*args`/`**kwargs` → varargs handling

**Deliverable**: 95% Python syntax support.

## Phase 5: Ecosystem (Months 13-18)

**Goal**: Production-ready toolchain.

### 5.1 Third-Party Bindings
- Retrofit/OkHttp → Direct `HttpURLConnection` + JSON parsing
- Gson/Moshi → JSON parsing via Android APIs
- Glide/Coil → Image loading via `BitmapFactory`
- Dagger/Hilt → Manual DI (no compile-time codegen)
- RxJava → Async/await + streams

### 5.2 Tooling
- Build system (no Gradle)
- IDE support (language server, code completion)
- Testing framework (pytest → Smali tests)
- Debugging support (source maps, breakpoints)
- Package manager (Ahnali packages)

**Deliverable**: Production-ready Python-to-Android compiler.

## Migration Path

### Current Codebase → New Architecture

The current codebase provides the foundation:
- ✅ Compiler pipeline (DSL → IR → CFG → SSA → Dalvik → Smali)
- ✅ Widget rendering system
- ✅ Capability system
- ✅ Build toolchain

What needs to change:
1. **Parser** — From DSL-only to full Python AST
2. **Lowering** — From widget-specific to feature-based
3. **Runtime** — From fixed to on-demand
4. **Emitter** — From widget Smali to general Smali

The migration is incremental:
1. Keep the current DSL as a subset
2. Add feature detection on top
3. Add runtime module selection
4. Add direct Android API support
5. Gradually expand Python syntax support
