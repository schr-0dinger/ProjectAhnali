# Program 5 Closure (State + Lifecycle)

Status: Closed (code/tests/docs evidence)

This document closes Program 5 by linking shipped behavior to deterministic contracts and conformance tests.

## Scope Closed

1. Lifecycle hooks
- `on_start`, `on_resume`, `on_pause`, `on_stop`, `on_destroy`
- Wrapper lifecycle bridges emit deterministic forwarding when hooks are present.

2. Deterministic state backends
- SharedPreferences helper surface (`storage_put/get/remove/exists/clear`)
- DataStore helper surface (`datastore_*`)
- File helper surface (`file_*`)
- SQLite helper surface (`sqlite_*`)
- Room helper surface (`room_*`)
- Encrypted helper surface (`encrypted_storage_*`, aliases `secure_storage_*`)

## Deterministic Contract Summary

1. `*_put/remove/clear`
- Return `1` on success.
- Return `0` on invalid input or caught exception.

2. `*_get`
- Return stored value when present.
- Return fallback argument when missing/error.

3. `*_exists`
- Return `1` when key exists.
- Return `0` otherwise.

4. Lifecycle bridge ordering
- Wrapper calls `invoke-super` first, then static lifecycle hook.

## Evidence (Tests)

1. `tests/test_program5_state_backends.py`
- Verifies parser/lowering + helper-call ABI for all deterministic backends.

2. `tests/test_program5_lifecycle.py`
- Verifies lifecycle hook compilation and wrapper lifecycle bridge emission.

3. `tests/test_runtime_abi_v1.py`
- Verifies lifecycle bridge ABI signatures and helper contract expectations.

4. `tests/test_runtime_abi_snapshot.py`
- Verifies frozen helper signature surface remains stable.

## Evidence (Docs/Contracts)

1. `README.md`
- Program 5 state backend and lifecycle contract sections.

2. `runtime_abi_v1.md`
- Lifecycle bridge ABI and helper contract references.

3. `docs/capability_runtime_mapping_v1.md`
- Capability/helper mapping baseline used by toolchain binding checks.

## Closure Gate

Program 5 is considered closed when:
- tests above remain green,
- ABI snapshot checks remain green,
- docs listed above stay aligned with code reality.
