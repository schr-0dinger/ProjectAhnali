# Track C Wave 15: WorkManager Deterministic Slice (Program 6-B)

Status: Complete  
Date: 2026-02-18

This wave adds a deterministic background-work helper surface for WorkManager-style
enqueue/cancel/status routing under capability guardrails.

## Contract

- Capability: `Caps.WorkManager`
- Runtime helper: `Lcom/ahnali/runtime/WorkHelper;`
- Helper methods:
  - `enqueueWork(Landroid/app/Activity;Ljava/lang/String;I)I`
  - `enqueueWorkError(Landroid/app/Activity;Ljava/lang/String;I)I`
  - `cancelWork(Landroid/app/Activity;Ljava/lang/String;)I`
  - `cancelWorkError(Landroid/app/Activity;Ljava/lang/String;)I`
  - `getWorkStatus(Landroid/app/Activity;Ljava/lang/String;)I`
  - `getWorkStatusError(Landroid/app/Activity;Ljava/lang/String;)I`

## DSL Surface

- `work_enqueue(name, delay_seconds=0)`
- `work_cancel(name)`
- `work_status(name)`
- `work_error(name)`

## Deterministic Error Contract

- `enqueueWorkError`: `0` success, `1` invalid args/context, `2` invalid delay, `3` exception.
- `cancelWorkError`: `0` success, `1` invalid args/context, `2` unknown work, `3` exception.
- `getWorkStatusError`: `0` status available, `1` invalid args/context, `2` unknown work, `3` exception.

## Conformance

- `tests/test_track_c_wave15_workmanager.py`
- Runtime mapping/ABI guards:
  - `tests/test_capabilities.py`
  - `tests/test_runtime_abi_v1.py`
  - `tests/test_runtime_abi_snapshot.py`
