---
tags: [ahnali, capabilities, notifications]
---

# Notifications

> [!abstract] Channels and notifications
> Create notification channels and post notifications with deterministic delivery and error reporting.

## Creating channels

```python
create_notification_channel("my_channel", "My Channel")
notification_channel("my_channel", "My Channel")  # alias
```

Maps to `NotificationHelper.createChannel(Activity, String, String) → int`.

## Posting notifications

```python
notify("Title", "Body", channel_id="my_channel")
send_notification("Title", "Body", channel_id="my_channel")  # alias
```

Maps to `NotificationHelper.postNotification(Activity, String, String, String) → int`.

## Result and error surfaces

```python
result = notify_result(title, body, channel_id="my_channel")
error = notify_error(title, body, channel_id="my_channel")
```

## Capability

```python
app_config(uses=[Caps.Notifications])
```

Injects `POST_NOTIFICATIONS` permission and links `Lcom/ahnali/runtime/NotificationHelper;`.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Sharing and intents: [[40 - Capabilities/07 - Sharing and Intents]]
