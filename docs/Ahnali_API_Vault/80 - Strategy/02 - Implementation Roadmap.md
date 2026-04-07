---
tags: [ahnali, roadmap, phases, implementation]
---

# Implementation Roadmap

> [!abstract] From DSL to Full Python
> The path from a restricted DSL compiler to a broader smart-transpiler foundation must be incremental, contract-driven, and backend-preserving.

## Current State (v1)

What we have today:
- ✅ DSL → IR → CFG → SSA → Dalvik → Smali pipeline
- ✅ 30+ widget types with full styling
- ✅ 18 capability waves (networking, storage, permissions, etc.)
- ✅ For loops, try/except, function definitions
- ✅ Bounded helper/runtime injection for declared capabilities
- ✅ Phase 1 bounded feature analyzer/runtime-selector layer
- ✅ Runtime-module helper emission and build-report scaffolding
- ✅ One bounded analyzer-selected semantic reflection path: `getattr(widget, "text")`
- ✅ Runtime-plan CLI tool and emitted `runtime_plan.json` build artifacts
- ✅ 691 passing tests
- ✅ Bounded Phase 2 collection/type/string-method slices complete for the intended repo scope
- ✅ Bounded Phase 3 Android binding slice complete for the intended repo scope

What we do **not** have today:

- ❌ General full-program Python compilation
- ❌ Broad dynamic Python object-model support
- ❌ A basis for promising "any Android app" coverage yet

## Phase 1: Feature Detection + Smart Runtime (Months 1-3)

**Goal**: Analyze a bounded Python subset to detect used features, then reuse the existing compiler backend and helper-linking model.

**Status**: Complete for the bounded scope currently implemented in this repository.

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
- `dsl/analyzer/__init__.py` - Feature analysis entry point
- `dsl/analyzer/collector.py` - AST visitor that collects feature usage
- `dsl/analyzer/profile.py` - FeatureUsageProfile dataclass
- `dsl/analyzer/runtime_selector.py` - Selects runtime modules from profile

**Implemented now:**
- `analyze_features(...)` for source/AST/callable analysis
- `analyze_frontend_ir(...)` for current `ProgramIR` metadata
- merged profile support across `ProgramIR` and preserved handler callables
- runtime-module selection scaffold wired into `app(...).build()`
- `ProgramIR.feature_usage_profile`, `ProgramIR.selected_runtime_modules`, and `ProgramIR.runtime_module_names`
- bounded reflection lowering for `getattr(widget_symbol, "text")`
- `tools/feature_runtime_plan.py` for direct source inspection
- emitted `runtime_plan.json` build artifacts from `emit_build_dir_from_program(...)`

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

**Implemented now:**
- `dsl/runtime/modules/__init__.py` provides the initial registry/spec layer
- selection now also drives helper-class emission scaffolding for selected modules during build packaging
- one non-capability Python runtime feature is now semantically wired through lowering and helper emission: `getattr(widget_symbol, "text")`
- broader non-capability Python runtime features are still scaffolds, not yet fully lowered semantics

### 1.3 Smart Runtime Injection
```python
# In build_program():
profile = analyze_features(source_code)
modules = select_runtime_modules(profile)
runtime_smali = generate_runtime_smali(modules)
# Only include the Smali that's actually needed
```

**Implemented now:**
- selected modules are attached to `ProgramIR`
- selected module helpers are emitted into the build dir when they declare helper methods/signatures
- `runtime_plan.json` records the chosen modules and merged feature profile

### 1.4 Direct Android API Calls
```python
# No wrapper needed - direct Smali emission
from android.widget import TextView
text_view = TextView(context)
text_view.setText("Hello")
```

**Deliverable**: Can accept a broader analyzable subset and selectively include helper/runtime support while still lowering through the existing verified backend.

**Phase completion note**: This deliverable is complete for the bounded scope the current codebase can honestly support. Broader Python semantics now belong to Phase 2+ work, not more Phase 1 scaffolding.

## Phase 2: Collections & Types (Months 4-6)

**Goal**: Expand collection and type support where semantics stay statically checkable.

**Status**: Complete for the bounded repo scope currently implemented.

### 2.1 Collection Wrappers
- `list` → `ArrayList` wrapper (~50 lines Smali)
- `dict` → `HashMap` wrapper (~80 lines)
- `set` → `HashSet` wrapper (~40 lines)
- `tuple` → Immutable array wrapper (~20 lines)

**Implemented now:**
- list literals lower into `ListWrapperRuntime.create(...)` plus typed append helpers
- dict literals lower into `DictWrapperRuntime.create(...)` plus typed put helpers
- set literals lower into `SetWrapperRuntime.create(...)` plus typed add helpers
- tuple literals lower into `TupleWrapperRuntime.create(...)` plus typed indexed writes
- `len(collection_symbol)` lowers into `size(...)` for supported local list/dict/set/tuple literals
- selected list/dict/set/tuple wrapper helpers are emitted into the build dir through the runtime-module packaging path
- supported scope is intentionally narrow: local list/set/tuple literals with constant string/int elements, and local dict literals with constant string keys plus constant string/int values

### 2.2 Type System
- Type conversion (`int()`, `str()`, `float()`, etc.)
- `isinstance()`, `type()`
- Operator overloading (`__add__`, `__eq__`, etc.)
- List/dict comprehensions → loops

**Implemented now:**
- `str(...)` lowers for supported int/float expressions, supported `len(...)` results, `isinstance(...)` results, `type(...)` results, and supported string/int/float symbols/constants
- `int(...)` lowers for supported int/float/string values plus supported `len(...)`, `str(...)`, `float(...)`, and `isinstance(...)` results
- `float(...)` lowers for supported int/float/string values plus supported `len(...)`, `str(...)`, `int(...)`, and `isinstance(...)` results
- `type(...)` lowers to bounded type-name strings for supported constants, collection literals, supported locals, and supported nested builtin calls
- `isinstance(...)` lowers for supported values and supported type specs including bounded tuples of builtin type names
- direct `label.text = str(...)` and `label.text = type(...)` are supported through the existing verified lowering path
- supported scope is intentionally narrow: no generic object model, no operator overloading, and no comprehension lowering yet

### 2.3 String Methods
- `split()`, `join()`, `replace()`, `strip()`, etc.
- `format()`, f-strings
- String comparison, slicing

**Implemented now:**
- bounded method-call parsing supports `string_expr.strip()`, `string_expr.replace(old, new)`, `string_expr.lower()`, `string_expr.upper()`, `string_expr.split(sep)`, and `separator.join(items)`
- supported receivers are intentionally narrow: string constants, string locals, and supported string-producing calls like `str(...)`, `type(...)`, `getattr(...)`, and nested bounded string methods
- `split(...)` lowers through `StringMethodsRuntime.split(...)` into `ArrayList` so supported `len(...)` flows work on the result
- `join(...)` lowers through `StringMethodsRuntime.joinList(...)` / `joinTuple(...)` for supported local list/tuple symbols and nested supported `split(...)` results
- direct `label.text = string_expr.method(...)` is supported through the existing verified lowering path
- bounded string methods are also supported inside f-strings
- Phase 2.3 is complete for the bounded repo scope; unsupported for now are generic `format(...)`, slicing, richer string comparison helpers, locale-aware variants, and general Python string object semantics

**Deliverable**: Useful collection/type expansion with explicit limits and tests.

## Phase 3: Bounded Android Bindings (Months 7-9)

**Goal**: Expand practical Android coverage through explicit, typed binding slices that preserve the current analyzer/lowering/runtime-selection contract.

**Status**: Complete for the bounded repo scope currently implemented.

### 3.1 Binding Metadata + Diagnostics
- introduce binding metadata for a narrow set of constructors, methods, and fields
- validate arity/types before IR lowering
- keep signatures explicit instead of offering dynamic member lookup

**Implemented now:**
- [`dsl/android/bindings.py`](../../../dsl/android/bindings.py) provides an inspectable binding registry for `android_uri_parse`, `android_intent_view`, `android_intent_chooser`, and `android_start_activity`
- analyzer/runtime-plan metadata tracks these through `uri_binding`, `intent_binding`, and `activity_binding` flags
- runtime-module selection now records `android.bindings.uri`, `android.bindings.intent`, and `android.bindings.activity`

### 3.2 Frontend Exposure of Proven Android Flows
- expose Android value/object construction only for surfaces Ahnali already models internally or can lower directly
- first slices should reuse known patterns such as URI parsing, Intent construction, launch/share/deep-link flows, and small value objects
- when a binding needs support code, route it through the same runtime-module/helper-emission path used by capabilities and Phase 1/2 features

**Implemented now:**
- explicit frontend syntax accepts `android_uri_parse(string_expr)`
- explicit frontend syntax accepts `android_intent_view(uri_expr)` and `android_intent_chooser(intent_expr, title_expr)`
- explicit frontend syntax accepts `android_start_activity(intent_expr)` as a statement form
- nested binding expressions are supported for the bounded Uri/Intent launch flow

### 3.3 Packaging + Artifact Alignment
- make AndroidX or support-library requirements explicit in build metadata
- prefer surfaces already backed by the toolchain or current capability/helper path
- defer broad library generation until artifact/linking rules are stable

**Implemented now:**
- Phase 3 bindings reuse the existing runtime-plan/build-report path even though the initial slice lowers directly and does not need helper emission
- build metadata now surfaces the chosen Android binding modules alongside Phase 1/2 runtime modules

### 3.4 Exit Criteria
- at least one bounded Android binding slice lowered end to end
- diagnostics for unsupported classes/methods are explicit and test-covered
- runtime-plan/build-dir outputs reflect any helper-backed bindings
- no backend architecture rewrite required

**Exit result**:
- achieved for the initial bounded slice via Uri parsing, Intent construction, chooser wrapping, and `startActivity(...)`
- helper-backed Android bindings remain available as a later extension path, but the initial slice did not require new helper classes

**Deliverable**: A credible first Android-binding layer on top of the existing verified backend, not a blanket SDK generator.

## Phase 4: Advanced Features (Months 10-12)

**Goal**: Add bounded advanced features that preserve deterministic lowering and diagnostics.

**Status**: Complete for bounded scope - async/await/yield tracked by analyzer, runtime modules selected, bounded lowering with clear diagnostics.

### 4.1 Async/Await
- `async def` → coroutine state machine
- `await` → yield/resume pattern
- `asyncio` → coroutine runtime (~400 lines Smali)

**Implemented now:**
- `_StmtAsyncFunctionDef` AST node for async function definitions
- `_ExprAwait` AST node for await expressions  
- `_ExprYield` and `_ExprYieldFrom` AST nodes for generators
- `_StmtAsyncFor` and `_StmtAsyncWith` AST nodes
- Feature analyzer detects `async_def`, `await`, `yield`, `yield_from` in source
- Runtime module `python.async.async_runtime` selected when async features used
- Runtime module `python.generators.iterator_runtime` selected when yield used
- Clear diagnostic errors when async features encountered at lowering: "await expressions are not yet supported in this bounded scope"
- 695 passing tests (691 baseline + 4 new Phase 4 tests)

### 4.2 Advanced OOP
- Multiple inheritance → interface pattern
- Descriptors → attribute resolution chain
- Metaclasses → class creation hooks
- `__getattribute__` → full attribute dispatch

**Status**: Not yet implemented - tracked as future work.

### 4.3 Advanced Python
- Generators → state machine generation
- Decorators → function wrapping
- Context managers → try/finally pattern
- `*args`/`**kwargs` → varargs handling

**Status**: Bounded support via feature detection - analyzer tracks these features for runtime module selection, full lowering is future work.

**Deliverable**: More expressive support with clearer feasibility than a blanket syntax-percentage target.

## Phase 5: Ecosystem (Months 13-18)

**Goal**: Production-ready tooling around the existing compiler plus any new analysis/runtime-selection layers that prove out.

**Status**: Complete - CLI, package manager, VS Code extension implemented.

### 5.1 CLI Commands
- `ahnali build <source>` - Compile Python source to APK
- `ahnali run <source>` - Build, install, and run on device
- `ahnali analyze <source>` - Feature analysis and runtime selection
- `ahnali init <name>` - Scaffold new project
- `ahnali install <package>` - Install from HTTP registry
- `ahnali list` - List installed packages
- `ahnali publish <dir>` - Publish package to registry

**Implemented now:**
- CLI at `cli/` with click-based commands
- All commands functional with proper error handling
- 695 passing tests

### 5.2 Package Manager
- HTTP registry support for package discovery
- Local package installation (`~/.ahnali/packages/`)
- Package publishing workflow with ZIP creation

**Implemented now:**
- Install from JSON-based registry
- Local package storage and listing
- Publish command for creating distributable packages

### 5.3 IDE Support
- VS Code extension for syntax highlighting
- TextMate grammar for Ahnali DSL keywords

**Implemented now:**
- Extension at `editor/vscode/`
- Syntax highlighting for DSL keywords, Python builtins, strings, comments, numbers
- Keywords: app, activity, ui, text, button, image, on_click, state, navigation, etc.

### 5.4 Third-Party Bindings (Deferred)
- Retrofit/OkHttp → Direct `HttpURLConnection` + JSON parsing
- Gson/Moshi → JSON parsing via Android APIs
- Glide/Coil → Image loading via `BitmapFactory`
- Dagger/Hilt → Manual DI (no compile-time codegen)
- RxJava → Async/await + streams

**Status**: Not yet implemented - tracked as future work.

**Deliverable**: Production-ready compiler/toolchain with a staged migration path.

## Migration Path

### Current Codebase → New Architecture

The current codebase provides the foundation:
- ✅ Compiler pipeline (DSL → IR → CFG → SSA → Dalvik → Smali)
- ✅ Widget rendering system
- ✅ Capability system
- ✅ Build toolchain

What needs to change:
1. **Analyzer** - Add feature analysis ahead of lowering
2. **Frontend** - Expand beyond the current DSL in bounded slices
3. **Runtime selection** - Generalize the existing helper-linking model
4. **Lowering** - Broaden source forms while preserving the backend contract

The migration is incremental:
1. Keep the current DSL as a subset
2. Add feature detection on top
3. Add runtime module selection
4. Reuse the current backend as the compilation spine
5. Gradually expand Python syntax support only where contracts remain clear
