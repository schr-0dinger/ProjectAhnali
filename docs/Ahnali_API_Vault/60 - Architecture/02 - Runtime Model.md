---
tags: [ahnali, architecture, runtime]
---

# Runtime Model

> [!abstract] Small core, modular capabilities
> The core runtime is always present and minimal. Capability modules are linked only when used.

> [!important] Current reality
> This is already a selective helper-linking model, which makes it the natural base for any future runtime-selector work. The next strategy should extend this model rather than replacing it with a large dynamic runtime.

> [!note] Phase 3 result
> The first bounded Android binding slice now follows this rule directly: Uri/Intent/activity bindings lower through typed direct calls, while the same runtime-plan and selective-linking path remains available if later Android bindings need helper support.

## Core runtime (always linked)

Delivered inside `base.apk`. Always present. Small - roughly 50-100 KB.

Responsibilities:
- Screen stack manager
- Navigation controller
- Event dispatcher
- State storage (int-only for compile-time state)
- View binding helpers
- Error mapping (Smali → DSL)
- Unit helpers (dp, sp, percent)
- Internal utilities

Properties:
- No permissions
- No heavy Android APIs
- No Play dependencies

This is Ahnali's identity layer.

## Capability modules (conditionally linked)

These aren't plugins - they're conditionally linked libraries. Included only if referenced by the DSL.

Examples:
- `Lcom/ahnali/runtime/HttpHelper;` - networking
- `Lcom/ahnali/runtime/StorageHelper;` - storage
- `Lcom/ahnali/runtime/NotificationHelper;` - notifications

Properties:
- Ahead-of-time compiled
- No reflection
- No dynamic dispatch
- Permission-aware
- Removed entirely if unused

## Helper class structure

Every helper class follows the same pattern:

```java
public class XxxHelper {
    public static int doSomething(Activity activity, ...) {
        try {
            // do the thing
            return 1;  // success
        } catch (Exception e) {
            return 0;  // failure
        }
    }
}
```

The compiler emits or links these classes during the packaging phase. They're Smali, not Java - but the structure is the same.

## Learn more

- Capabilities system: [[20 - Core Concepts/04 - Capabilities System]]
- Runtime ABI: [[40 - Capabilities/12 - Runtime ABI]]
- Dual mode architecture: [[60 - Architecture/01 - Dual Mode Architecture]]
- Pipeline evolution plan: [[60 - Architecture/05 - Pipeline Evolution Plan]]
