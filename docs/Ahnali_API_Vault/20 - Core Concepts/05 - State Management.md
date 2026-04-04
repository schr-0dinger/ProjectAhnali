---
tags: [ahnali, state, lifecycle, storage]
---

# State Management

> [!abstract] Three layers of state
> Compile-time state fields, lifecycle hooks, and persistent storage backends. All deterministic, all resolved at compile time.

## Compile-time state

The simplest form of state:

```python
app(
    activity("Main",
        state(count=0, step=1),
        ui(text("0", id="label")),
        on_click("btn", [
            count = count + 1,
            label.text = f"Count: {count}",
        ]),
    ),
)
```

`state(count=0)` declares a static integer field on the generated class. The handler reads and writes it directly. No runtime state engine - just a field on a class.

> [!note] Current limitation
> State values must be integer literals at compile time. No strings, no objects, no computed initial values. This is intentional - keeping it simple keeps it analyzable.

## Lifecycle hooks

Five lifecycle hooks map directly to Android Activity lifecycle methods:

```python
app(
    activity("Main",
        on_start([log("Activity started")]),
        on_resume([log("Activity resumed")]),
        on_pause([log("Activity paused")]),
        on_stop([log("Activity stopped")]),
        on_destroy([log("Activity destroyed")]),
        ui(text("Hello", id="label")),
    ),
)
```

The compiler emits a wrapper Activity class that overrides each lifecycle method, calls `invoke-super` first, then your static handler. If you don't define a hook, nothing is emitted.

## Persistent storage

Six backends, all following the same contract:

| Backend | DSL prefix | What it is |
|---|---|---|
| SharedPreferences | `storage_*` | Simple key-value |
| DataStore | `datastore_*` | Jetpack DataStore |
| File | `file_*` | Internal file storage |
| SQLite | `sqlite_*` | Raw SQLite |
| Room | `room_*` | Jetpack Room |
| Encrypted | `encrypted_storage_*` / `secure_storage_*` | Encrypted storage |

### The contract

Every backend follows the same pattern:

- `*_put(key, value)` → `1` on success, `0` on failure
- `*_get(key, fallback)` → stored value, or fallback if missing
- `*_exists(key)` → `1` if key exists, `0` otherwise
- `*_remove(key)` → `1` on success, `0` on failure
- `*_clear()` → `1` on success, `0` on failure

```python
storage_put("username", "alice")
name = storage_get("username", "guest")  # "alice"
storage_exists("username")               # 1
storage_remove("username")
storage_get("username", "guest")         # "guest" (fallback)
```

## State in handlers

State mutations inside handlers are compiled into field operations. The compiler tracks reads and writes through SSA, so it knows exactly what each handler does to what state.

```python
@on_click("save")
def save():
    storage_put("count", count)  # persist compile-time state to storage
    toast("Saved")
```

## Learn more

- Capabilities system: [[20 - Core Concepts/04 - Capabilities System]]
- Storage capability: [[40 - Capabilities/03 - Storage]]
- Events and handlers: [[30 - API Reference/09 - Events and Handlers]]
