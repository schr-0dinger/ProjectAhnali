# Track C Wave 17: JobScheduler Deterministic Slice (Program 6-B)

Status: Complete
Date: 2026-02-18

Completes Program 6-B background-work tranche C with JobScheduler-style APIs, explicit API-level guard behavior, and a visible deterministic fallback flow.

## Contract

- Capability: `Caps.JobScheduler`
- Runtime helper: `Lcom/ahnali/runtime/JobHelper;`
- Helper methods:
  - `scheduleJob(Landroid/app/Activity;II)I`
  - `scheduleJobError(Landroid/app/Activity;II)I`
  - `cancelJob(Landroid/app/Activity;I)I`
  - `cancelJobError(Landroid/app/Activity;I)I`
  - `getJobStatus(Landroid/app/Activity;I)I`
  - `getJobStatusError(Landroid/app/Activity;I)I`

## DSL Surface

- `job_schedule(job_id, delay_seconds=0)`
- `job_cancel(job_id)`
- `job_status(job_id)`
- `job_error(job_id)`

## Error contract

- API guard: `SDK_INT < 21` returns unsupported code from error methods.
- `scheduleJobError`: `0` success, `1` invalid args/context, `2` unsupported API, `3` invalid delay, `4` exception.
- `cancelJobError`: `0` success, `1` invalid args/context, `2` unsupported API, `3` missing job, `4` exception.
- `getJobStatusError`: `0` status available, `1` invalid args/context, `2` unsupported API, `3` missing job, `4` exception.

## Visible flow

`tests/test_track_c_wave17_visible_flow.py` composes:
- Work enqueue
- Alarm schedule
- Job schedule/status
- URL-launch deterministic fallback branch

## Conformance

- `tests/test_track_c_wave17_jobscheduler.py`
- `tests/test_track_c_wave17_visible_flow.py`
- Runtime mapping/ABI guards: `tests/test_capabilities.py`, `tests/test_runtime_abi_v1.py`, `tests/test_runtime_abi_snapshot.py`
