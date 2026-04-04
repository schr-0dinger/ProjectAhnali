# Program 5 - State and Lifecycle

This is closed. Here's what shipped and where you can verify it.

## What shipped

**Lifecycle hooks:** `on_start`, `on_resume`, `on_pause`, `on_stop`, `on_destroy`. When you define these, the compiler emits a wrapper bridge that calls `invoke-super` first, then your static handler. No surprises.

**State backends:** Six deterministic storage surfaces, all following the same contract:

| Backend | DSL prefix |
|---|---|
| SharedPreferences | `storage_*` |
| DataStore | `datastore_*` |
| File | `file_*` |
| SQLite | `sqlite_*` |
| Room | `room_*` |
| Encrypted | `encrypted_storage_*` / `secure_storage_*` |

Each one supports `put`, `get`, `exists`, `remove`, `clear`.

## The contract

- `*_put`, `*_remove`, `*_clear` return `1` on success, `0` on bad input or caught exception.
- `*_get` returns the stored value, or the fallback you passed in if the key is missing.
- `*_exists` returns `1` if the key is there, `0` otherwise.

Simple. Predictable. No magic.

## Where to check

Tests:
- `tests/test_program5_state_backends.py` - parser, lowering, and ABI for all backends
- `tests/test_program5_lifecycle.py` - lifecycle hook compilation and bridge emission
- `tests/test_runtime_abi_v1.py` - ABI signature checks
- `tests/test_runtime_abi_snapshot.py` - frozen signature stability

Docs:
- `README.md` - state backend and lifecycle contract sections
- `runtime_abi_v1.md` - ABI contract
- `docs/capability_runtime_mapping_v1.md` - the mapping baseline the toolchain uses

Program 5 is closed as long as those tests stay green and the docs stay in sync with the code.
