---
tags: [ahnali, architecture, deferred, roadmap]
---

# Deferred Features

> [!abstract] What's parked for post-v1
> These aren't forgotten. They're just not happening until the static compiler is frozen and we've got breathing room.

## Deferred beyond v1

### Motion backlog
Animation primitives exist (Phase 9 is done), but the broader motion backlog - advanced animation composition, transition APIs, shared element transitions - is deferred.

### Advanced/system/security/debug
- Canvas drawing (drawRect, drawCircle, drawPath, drawBitmap)
- Paint control (stroke, shader)
- Hardware acceleration / layer type control
- Secure flag, block screenshots, encryption
- Network security config
- Debug overlay, performance metrics, trace sections
- Status bar control, immersive mode, orientation lock

### Media
- MediaPlayer / ExoPlayer
- CameraX (preview, capture, video)
- AudioManager (focus, recording, microphone)
- Sensors (accelerometer, gyroscope, magnetometer, light, proximity)

### Connectivity
- Bluetooth (classic + BLE)
- NFC
- WebSockets
- DownloadManager

### Maps
- Google Maps SDK
- Map markers, camera movement, map gestures

### Biometrics
- Fingerprint
- Face authentication

### JNI / Native bridge (Milestone D)
NDK integration, JNI bridge, capability-scoped native calls. This is the prerequisite for the hybrid mode.

### Embedded Python (Milestone E)
Optional bounded Python plugin over JNI. Minimal CPython build, controlled bridge API, state mutation only.

> [!note] Why defer all this?
> Each of these areas needs the same treatment the implemented capabilities got: deterministic contracts, helper classes, tests, visible flows, ABI snapshots, docs. Doing them right takes time. Doing them fast would break the model. So they wait.

## Learn more

- Current status: [[70 - Project/01 - Current Status]]
- Roadmap: [[70 - Project/02 - Roadmap]]
- Dual mode architecture: [[60 - Architecture/01 - Dual Mode Architecture]]
