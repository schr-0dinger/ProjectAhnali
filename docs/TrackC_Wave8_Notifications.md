# Track C Wave 8: Notifications + Channels

Status: Completed on 2026-02-18

Adds notification delivery with deterministic error surfaces under `Caps.Notifications`.

## Capability + ABI

- Capability: `Caps.Notifications`
- Runtime helper: `Lcom/ahnali/runtime/NotificationHelper;`
- Helper methods:
  - `createChannel(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `postNotification(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I`
  - `postNotificationError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I`

Error codes from `postNotificationError`:
- `0`: success
- `1`: invalid args
- `2`: permission denied (`POST_NOTIFICATIONS`, SDK >= 33)
- `3`: channel/service failure
- `4`: runtime exception

## DSL surface

- Channel creation:
  - `create_notification_channel(channel_id, channel_name)`
  - `notification_channel(channel_id, channel_name)`
- Notification delivery:
  - `notify(title, body, channel_id="ahnali_default")`
  - `send_notification(title, body, channel_id="ahnali_default")`
- Deterministic result/error expressions:
  - `notify_result(title, body, channel_id="ahnali_default")`
  - `notify_error(title, body, channel_id="ahnali_default")`

## Conformance tests

- Capability/lowering/toolchain/parser: `tests/test_track_c_wave8_notifications.py`
- Visible deterministic fallback flow: `tests/test_track_c_wave8_visible_flow.py`
- ABI snapshot surface: `tests/test_runtime_abi_snapshot.py`, `cfg/runtime_abi_snapshot_v1.json`
- Mapping contract + docs drift: `tests/test_capability_mapping_contract.py`, `cfg/capability_mapping_snapshot_v1.json`

## Visible flow

The compiled app:
1. Creates a notification channel.
2. Attempts notification delivery through `notify_error(...)`.
3. Routes success to URL launch and success labels.
4. Routes failure to storage-backed deterministic fallback text.

References: `tests/test_track_c_wave8_visible_flow.py`, `docs/capability_runtime_mapping_v1.md`, `runtime_abi_v1.md`
