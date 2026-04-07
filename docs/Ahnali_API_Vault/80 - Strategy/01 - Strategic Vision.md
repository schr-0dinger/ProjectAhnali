---
tags: [ahnali, vision, strategy, roadmap]
---

# Ahnali Strategic Vision

> [!abstract] The Goal
> Make Ahnali dramatically more expressive over time through smart transpilation and selective runtime injection, without giving up the current compiler's static-default identity.

## The Core Insight

We should not try to "implement Python" in one leap. The viable path is to **translate an analyzable Python subset to native Android patterns** and inject runtime support only where the compiler can still preserve clear contracts.

```
Restricted / analyzable Python
    ↓
Feature Analyzer
    ↓
Selective Lowering + Runtime Selection
    ↓
Existing Verified Backend
    ↓
APK
```

## Reality Check

Today Ahnali is already very good at:

- restricted DSL authoring
- verified CFG/SSA/Dalvik/Smali compilation
- bounded helper injection for capabilities
- deterministic APK packaging

Today Ahnali is **not yet**:

- a full-program Python compiler
- a general Android API binding generator
- a dynamic runtime platform

That matters because the strategy is only credible if it extends the current architecture instead of pretending the current compiler does not exist.

## What This Means

| Feature | Approach | Runtime Cost |
|---|---|---|
| Variables, arithmetic | Direct Dalvik instructions | 0 bytes |
| `if/else`, `while`, `for` | Branches, loops | 0 bytes |
| `def` functions | Smali methods | 0 bytes |
| `class` definitions | Smali classes | 0 bytes |
| `list` | `ArrayList` wrapper | ~50 lines Smali |
| `dict` | `HashMap` wrapper | ~80 lines Smali |
| `getattr()` | Reflection helper | ~100 lines Smali |
| `async/await` | Coroutine runtime | ~400 lines Smali |
| Full feature set | Many modules | grows with supported subset |

Compare to embedding Python: the target remains far smaller and more deterministic, but exact runtime size depends on the supported subset and linked helpers.

## Strategic Implementation Principle

Preserve the verified backend. Most future work should happen in:

- source analysis
- frontend expansion
- lowering
- runtime/helper selection

Only change CFG/SSA/Dalvik/emission when the feature truly requires backend work.

## The Implementation Phases

### Phase 1: Foundation (Months 1-3)
**Goal**: Feature detection + smart runtime selection on top of the existing compiler spine

- AST feature analyzer (detects used language features)
- Runtime module selector (only includes what's needed)
- Basic Python → Smali translation (variables, control flow, functions)
- Class generation (Python classes → Smali classes)
- Method generation (Python functions → Smali methods)
- Direct Android API calls (no wrapper needed)

**Deliverable**: Can analyze a broader bounded subset and route it through the current backend with selective helper inclusion

**Status**: Complete for the bounded scope currently implemented in-repo: analyzer, runtime selector, emitted runtime plan/reporting, helper-class emission for selected modules, and one semantic reflection slice.

### Phase 2: Collections & Types (Months 4-6)
**Goal**: Add high-value collection and type features without weakening analyzability

- `list` → `ArrayList` wrapper
- `dict` → `HashMap` wrapper
- `set` → `HashSet` wrapper
- `tuple` → Immutable array wrapper
- String methods (split, join, replace, etc.)
- Type conversion (`int()`, `str()`, `float()`, etc.)
- Operator overloading (`__add__`, `__eq__`, etc.)
- List/dict comprehensions → loops

**Deliverable**: A materially broader subset with explicit contracts and tests

**Status**: Complete for the bounded repo scope currently implemented.

### Phase 3: Android SDK Coverage (Months 7-9)
**Goal**: Expand practical platform coverage through bounded, typed Android bindings that preserve explicit lowering contracts

- binding metadata for a narrow set of Android classes, constructors, fields, and methods
- explicit frontend syntax for those bindings, with fixed signatures and diagnostics
- helper-backed Android bindings only where direct lowering is not enough
- AndroidX/artifact wiring only for surfaces that already have toolchain precedent or clear packaging rules
- no generic "import any Android class" promise

**Implemented bounded slice**:

- `android.net.Uri`-style parsing via `android_uri_parse(...)`
- `android.content.Intent`-style construction via `android_intent_view(...)`
- chooser wrapping via `android_intent_chooser(...)`
- activity launch via `android_start_activity(...)`
- runtime-plan/reporting alignment through `android.bindings.uri`, `android.bindings.intent`, and `android.bindings.activity`

**Deliverable**: Broader Android integration without pretending the project already has universal SDK binding generation

**Status**: Complete for the initial bounded repo scope currently implemented.

### Phase 4: Advanced Features (Months 10-12)
**Goal**: Add carefully bounded advanced features where semantics stay testable and deterministic

- `async/await` → coroutine runtime
- Decorators → function wrapping
- Context managers → try/finally pattern
- Generators → state machine generation
- `getattr`/`setattr` → reflection helpers
- `isinstance`/`type` → type checking
- `*args`/`**kwargs` → varargs handling
- Multiple inheritance → interface pattern

**Deliverable**: More expressive bounded support, not an unconditional "95% Python" claim

### Phase 5: Ecosystem (Months 13-18)
**Goal**: Production-ready tooling around the compiler that actually exists

- Third-party library bindings (Retrofit, Gson, Room, etc.)
- Build system (no Gradle, but packaging + signing)
- IDE support (language server, code completion)
- Testing framework (pytest → Smali tests)
- Debugging support (source maps, breakpoints)
- Documentation generator
- Package manager (Ahnali packages)

**Deliverable**: Production-ready compiler/toolchain with a credible path to a broader analyzable subset

## What We Can Replicate

### ✅ Direct Translation (Zero Runtime)
- Variables, arithmetic, comparisons
- `if/else`, `while`, `for`
- `def` functions, `class` definitions
- `try/except/finally`, `raise`
- `return`, `break`, `continue`
- All Android APIs (direct Smali calls)
- Static state

### ✅ Minimal Runtime (Small Wrappers)
- `list`, `dict`, `set`, `tuple`
- String methods
- List/dict comprehensions
- `enumerate()`, `zip()`
- `*args`, `**kwargs`
- `lambda` → anonymous classes
- `@property` → getter/setter
- `super()` → parent method resolution
- `__init__`, `__str__`, `__repr__`
- `__getitem__`, `__setitem__`
- `with` statement → try/finally
- `assert` → conditional throw

### ✅ Moderate Runtime (Feature Modules)
- `getattr()`, `setattr()`, `hasattr()`, `delattr()`
- Decorators → function wrapping
- Multiple inheritance → interface pattern
- Class methods, static methods
- `__call__` objects → callable interface
- `__iter__`, `__next__` → iterator protocol
- `yield` (simple) → generator state machine
- `async/await` (simple) → coroutine runtime
- `import` (static) → module loader
- `__eq__`, `__ne__`, `__lt__`, etc. → comparison operators
- `__add__`, `__sub__`, etc. → operator overloading

### ⚠️ Heavy Runtime (Complex)
- `eval()` (limited) → expression evaluator
- `exec()` (limited) → statement executor
- Metaclasses → class creation hooks
- Descriptors → attribute resolution chain
- `__getattribute__` → full attribute dispatch
- Complex generators → full state machine
- Complex async/await → full coroutine runtime
- Dynamic imports → runtime module loading
- `globals()`, `locals()` → scope management

### ❌ Impossible (Without Full Interpreter)
- `eval()` with dynamic code
- `exec()` with dynamic code
- Runtime class creation (`type(name, bases, dict)`)
- Monkey patching
- `__dict__` access on arbitrary objects
- `import` with dynamic names
- `__import__` hooks
- `sys.modules` manipulation
- `inspect` module

## Libraries We Can Replicate

### Android SDK — bounded coverage path
The backend can emit Smali for any API *once lowering exists*, but the user-facing compiler does not yet expose arbitrary Android bindings. The realistic path is bounded typed coverage, not blanket SDK promises:
- `android.view`, `android.widget`, `android.app`
- `android.content`, `android.os`, `android.graphics`
- `android.media`, `android.hardware`, `android.location`
- All AndroidX libraries
- All Google Play Services

### Java Standard Library — bounded practical coverage
Anything that is explicitly lowered and tested can work well. The roadmap should treat this as a per-slice expansion story rather than a 100% claim:
- `java.lang` (String, Object, Math, etc.)
- `java.util` (ArrayList, HashMap, Date, etc.)
- `java.io` (File, InputStream, OutputStream, etc.)
- `java.net` (URL, HttpURLConnection, etc.)
- `java.time` (LocalDate, Instant, etc.)

### Kotlin Standard Library - High Coverage

| Kotlin Feature | Ahnali Implementation |
|---|---|
| `List<T>`, `Map<K,V>`, `Set<T>` | Python list/dict/set → Android wrappers |
| `Sequence<T>` | Python generators |
| `coroutines` | Python async/await → coroutine runtime |
| `extension functions` | Decorators + method injection |
| `data classes` | `@dataclass` → Smali class generation |
| `sealed classes` | Enum + pattern matching |
| `let`, `run`, `apply`, `also` | Context manager patterns |
| `?.` safe call | Optional type checking |
| `?:` elvis operator | Default value patterns |
| `!!` non-null assertion | Runtime null checks |
| `lazy` | Lazy initialization pattern |
| `companion object` | Static methods |

### Popular Android Libraries - High Coverage

| Library | Ahnali Implementation |
|---|---|
| Retrofit/OkHttp | Direct `HttpURLConnection` + JSON parsing |
| Gson/Moshi | JSON parsing via Android APIs |
| Room | SQLite wrappers + DAO pattern |
| Glide/Coil | Image loading via `BitmapFactory` |
| ViewModel | State management pattern |
| LiveData | Observable pattern |
| Navigation | Screen stack + transitions |
| WorkManager | `JobScheduler` + `AlarmManager` |
| Dagger/Hilt | Manual DI (no compile-time codegen) |
| RxJava | Async/await + streams |

## Competitive Advantages

| Dimension | Kotlin/Java | Ahnali |
|---|---|---|
| Syntax verbosity | Medium | Low (Python) |
| Build complexity | High (Gradle, XML, manifests) | Zero (single Python file) |
| Compile time | 30s-5min | 1-5s |
| APK size | 2-10 MB (Kotlin stdlib + runtime) | 50KB-2 MB (on-demand runtime) |
| Learning curve | Steep (types, nullability, coroutines) | Gentle (Python) |
| Error messages | Opaque (JVM stack traces) | Clear (compile-time checks) |

## The Path to Victory

1. **Start with simple apps** - Forms, dashboards, settings screens
2. **Prove the performance** - Smaller APKs, faster compilation
3. **Build the ecosystem** - Package manager, third-party bindings
4. **Win the niche** - Internal tools, prototypes, educational apps
5. **Expand gradually** - More complex apps, more library support

## Current Status

The foundation is being built. The current codebase has:
- ✅ DSL → IR → CFG → SSA → Dalvik → Smali pipeline
- ✅ 30+ widget types with full styling
- ✅ 18 capability waves (networking, storage, permissions, etc.)
- ✅ For loops, try/except, function definitions
- ✅ Smart runtime injection (only what's used)
- ✅ 691 passing tests

Phase 2 has now delivered a bounded collections-and-types slice: list/dict/set/tuple literals, `len(collection_symbol)` for supported locals, bounded `str(...)`, `int(...)`, `float(...)`, `type(...)`, and `isinstance(...)` lowering, and a bounded string-method slice covering `.strip()`, `.replace(...)`, `.lower()`, `.upper()`, helper-backed `.split(...)`, and separator `.join(...)` on supported flows, all without changing the verified backend contract.

Phase 3 has now delivered the first bounded Android binding slice too: an inspectable binding registry plus explicit `android_uri_parse(...)`, `android_intent_view(...)`, `android_intent_chooser(...)`, and `android_start_activity(...)` flows that lower directly through the verified backend and surface in runtime-plan metadata.
