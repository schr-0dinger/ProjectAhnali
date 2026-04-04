---
tags: [ahnali, capabilities, background, workmanager, alarm, jobscheduler]
---

# Background Work

> [!abstract] Three scheduling primitives
> WorkManager for deferrable work, AlarmManager for time-based triggers, JobScheduler for condition-based jobs. All deterministic.

## WorkManager

For deferrable, guaranteed background work:

```python
work_enqueue("my_work_tag", priority=0)
work_cancel("my_work_tag")
status = work_status("my_work_tag")
error = work_error("my_work_tag")
```

Error variants:
```python
work_enqueue("my_work_tag", priority=0)
work_enqueue_error("my_work_tag", priority=0)
work_cancel("my_work_tag")
work_cancel_error("my_work_tag")
work_status("my_work_tag")
work_status_error("my_work_tag")
```

## AlarmManager

For exact-time triggers:

```python
alarm_schedule("my_alarm", timestamp_ms=0)
alarm_cancel("my_alarm")
status = alarm_status("my_alarm")
error = alarm_error("my_alarm")
```

Error variants:
```python
alarm_schedule("my_alarm", timestamp_ms=0)
alarm_schedule_error("my_alarm", timestamp_ms=0)
alarm_cancel("my_alarm")
alarm_cancel_error("my_alarm")
alarm_status("my_alarm")
alarm_status_error("my_alarm")
```

## JobScheduler

For condition-based jobs (API level guarded):

```python
job_schedule(job_id=0, network_type=0)
job_cancel(job_id=0)
status = job_status(job_id=0)
error = job_error(job_id=0)
```

Error variants:
```python
job_schedule(job_id=0, network_type=0)
job_schedule_error(job_id=0, network_type=0)
job_cancel(job_id=0)
job_cancel_error(job_id=0)
job_status(job_id=0)
job_status_error(job_id=0)
```

> [!warning] API level guard
> JobScheduler has API-level requirements. The compiler emits a guard check — if the device's API level is too low, the helper returns an error code deterministically.

## Capabilities

```python
app_config(uses=[Caps.WorkManager])
app_config(uses=[Caps.AlarmManager])
app_config(uses=[Caps.JobScheduler])
```

None of these require manifest permissions.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Networking async: [[40 - Capabilities/02 - Networking]]
