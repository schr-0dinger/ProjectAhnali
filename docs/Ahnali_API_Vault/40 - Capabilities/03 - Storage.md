---
tags: [ahnali, capabilities, storage, persistence]
---

# Storage

> [!abstract] Six backends, one contract
> SharedPreferences, DataStore, File, SQLite, Room, and encrypted storage - all following the same put/get/exists/remove/clear pattern.

## The contract

Every backend follows the same pattern:

| Operation | Returns on success | Returns on failure |
|---|---|---|
| `*_put(key, value)` | `1` | `0` |
| `*_get(key, fallback)` | stored value | fallback argument |
| `*_exists(key)` | `1` | `0` |
| `*_remove(key)` | `1` | `0` |
| `*_clear()` | `1` | `0` |

## SharedPreferences (base storage)

```python
storage_put("username", "alice")
name = storage_get("username", "guest")
storage_exists("username")     # 1
storage_remove("username")
storage_clear()
```

Aliases: `set_storage`, `get_storage`, `load_storage`, `has_storage`, `exists_storage`, `delete_storage`, `clear_storage`.

## DataStore

```python
datastore_put("key", "value")
datastore_get("key", "default")
datastore_exists("key")
datastore_remove("key")
datastore_clear()
```

## File storage

```python
file_write("key", "value")
file_read("key", "default")
file_exists("key")
file_remove("key")
file_clear()
```

Internal file storage with deterministic key/value surface.

## SQLite

```python
sqlite_put("key", "value")
sqlite_get("key", "default")
sqlite_exists("key")
sqlite_remove("key")
sqlite_clear()
```

Static-safe surface - no raw SQL queries, just key/value operations.

## Room

```python
room_put("key", "value")
room_get("key", "default")
room_exists("key")
room_remove("key")
room_clear()
```

Same static-safe pattern as SQLite, backed by Room.

## Encrypted storage

```python
encrypted_storage_put("key", "value")
encrypted_storage_get("key", "default")
encrypted_storage_exists("key")
encrypted_storage_remove("key")
encrypted_storage_clear()
```

Aliases: `secure_storage_put`, `secure_storage_get`, etc.

## Capability

```python
app_config(uses=[Caps.Storage])
```

Injects `READ_EXTERNAL_STORAGE` and `WRITE_EXTERNAL_STORAGE` permissions and links `Lcom/ahnali/runtime/StorageHelper;` with all backend-specific methods.

## Storage introspection

```python
storage_exists("key")   # 1 if key exists, 0 otherwise
storage_clear()         # clears all keys, returns 1 on success
```

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- State management: [[20 - Core Concepts/05 - State Management]]
- Networking: [[40 - Capabilities/02 - Networking]]
