# Track C Wave 16: AlarmManager Deterministic Slice (Program 6-B)

Status: Complete
Date: 2026-02-18

Adds deterministic AlarmManager-style scheduling APIs with strict parser validation and explicit status/error surfaces.

## Contract

- Capability: `Caps.AlarmManager`
- Runtime helper: `Lcom/ahnali/runtime/AlarmHelper;`
- Helper methods:
  - `scheduleAlarm(Landroid/app/Activity;Ljava/lang/String;I)I`
  - `scheduleAlarmError(Landroid/app/Activity;Ljava/lang/String;I)I`
  - `cancelAlarm(Landroid/app/Activity;Ljava/lang/String;)I`
  - `cancelAlarmError(Landroid/app/Activity;Ljava/lang/String;)I`
  - `getAlarmStatus(Landroid/app/Activity;Ljava/lang/String;)I`
  - `getAlarmStatusError(Landroid/app/Activity;Ljava/lang/String;)I`

## DSL Surface

- `alarm_schedule(name, trigger_seconds=0)`
- `alarm_cancel(name)`
- `alarm_status(name)`
- `alarm_error(name)`

## Error contract

- `scheduleAlarmError`: `0` success, `1` invalid args/context, `2` invalid trigger, `3` exception.
- `cancelAlarmError`: `0` success, `1` invalid args/context, `2` unknown alarm, `3` exception.
- `getAlarmStatusError`: `0` status available, `1` invalid args/context, `2` unknown alarm, `3` exception.

## Conformance

- `tests/test_track_c_wave16_alarmmanager.py`
- Runtime mapping/ABI guards: `tests/test_capabilities.py`, `tests/test_runtime_abi_v1.py`, `tests/test_runtime_abi_snapshot.py`
