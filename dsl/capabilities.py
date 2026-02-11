from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

ANDROID_PERMISSION_PREFIX = "android.permission."


@dataclass(frozen=True)
class Capability:
    name: str
    permissions: tuple[str, ...]


def normalize_permission(value: str) -> str:
    raw = str(value).strip()
    if not raw:
        return raw
    if raw.startswith(ANDROID_PERMISSION_PREFIX):
        return raw
    if raw.isupper() or raw.replace("_", "").isupper():
        return ANDROID_PERMISSION_PREFIX + raw
    return raw


class CapabilityRegistry:
    def __init__(self):
        self._caps: dict[str, Capability] = {}

    def register(self, name: str, permissions: Iterable[str] | None = None):
        key = str(name).strip()
        if not key:
            raise RuntimeError("Capability name must be non-empty")
        perms = tuple(
            normalize_permission(p) for p in (permissions or []) if str(p).strip()
        )
        cap = Capability(name=key, permissions=perms)
        self._caps[key] = cap
        self._caps[key.lower()] = cap

    def resolve_permissions(self, uses: Iterable[str] | None) -> list[str]:
        out: list[str] = []
        if not uses:
            return out
        for raw in uses:
            if raw is None:
                continue
            item = str(raw).strip()
            if not item:
                continue
            if item.startswith(ANDROID_PERMISSION_PREFIX):
                out.append(item)
                continue
            if item.isupper() or item.replace("_", "").isupper():
                out.append(normalize_permission(item))
                continue
            cap = self._caps.get(item) or self._caps.get(item.lower())
            if cap is None:
                raise RuntimeError(f"Unknown capability '{item}'")
            out.extend(cap.permissions)
        # preserve order, drop duplicates
        seen = set()
        ordered = []
        for perm in out:
            if perm in seen:
                continue
            seen.add(perm)
            ordered.append(perm)
        return ordered


DEFAULT_CAPABILITY_REGISTRY = CapabilityRegistry()

# Conservative, initial map. Expand as capabilities ship.
DEFAULT_CAPABILITY_REGISTRY.register("Camera", ["android.permission.CAMERA"])
DEFAULT_CAPABILITY_REGISTRY.register("Microphone", ["android.permission.RECORD_AUDIO"])
DEFAULT_CAPABILITY_REGISTRY.register("Audio", ["android.permission.RECORD_AUDIO"])
DEFAULT_CAPABILITY_REGISTRY.register(
    "Video",
    ["android.permission.CAMERA", "android.permission.RECORD_AUDIO"],
)
DEFAULT_CAPABILITY_REGISTRY.register("WebView", ["android.permission.INTERNET"])
DEFAULT_CAPABILITY_REGISTRY.register(
    "Sensors",
    ["android.permission.BODY_SENSORS"],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "Storage",
    ["android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE"],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "FilePicker",
    ["android.permission.READ_EXTERNAL_STORAGE"],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "File Picker",
    ["android.permission.READ_EXTERNAL_STORAGE"],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "Connectivity",
    ["android.permission.ACCESS_NETWORK_STATE", "android.permission.INTERNET"],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "URL launcher",
    ["android.permission.INTERNET"],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "URLLauncher",
    ["android.permission.INTERNET"],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "Permissions",
    [],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "Maps",
    ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"],
)
DEFAULT_CAPABILITY_REGISTRY.register(
    "Location",
    ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"],
)


class _Caps:
    Camera = "Camera"
    Microphone = "Microphone"
    Audio = "Audio"
    Video = "Video"
    WebView = "WebView"
    Sensors = "Sensors"
    Storage = "Storage"
    FilePicker = "FilePicker"
    Connectivity = "Connectivity"
    URLLauncher = "URLLauncher"
    Permissions = "Permissions"
    Maps = "Maps"
    Location = "Location"


class _Perms:
    CAMERA = "android.permission.CAMERA"
    RECORD_AUDIO = "android.permission.RECORD_AUDIO"
    INTERNET = "android.permission.INTERNET"
    ACCESS_NETWORK_STATE = "android.permission.ACCESS_NETWORK_STATE"
    ACCESS_WIFI_STATE = "android.permission.ACCESS_WIFI_STATE"
    ACCESS_FINE_LOCATION = "android.permission.ACCESS_FINE_LOCATION"
    ACCESS_COARSE_LOCATION = "android.permission.ACCESS_COARSE_LOCATION"
    READ_EXTERNAL_STORAGE = "android.permission.READ_EXTERNAL_STORAGE"
    WRITE_EXTERNAL_STORAGE = "android.permission.WRITE_EXTERNAL_STORAGE"
    READ_MEDIA_IMAGES = "android.permission.READ_MEDIA_IMAGES"
    READ_MEDIA_VIDEO = "android.permission.READ_MEDIA_VIDEO"
    READ_MEDIA_AUDIO = "android.permission.READ_MEDIA_AUDIO"
    BODY_SENSORS = "android.permission.BODY_SENSORS"
    POST_NOTIFICATIONS = "android.permission.POST_NOTIFICATIONS"
    BLUETOOTH = "android.permission.BLUETOOTH"
    BLUETOOTH_CONNECT = "android.permission.BLUETOOTH_CONNECT"
    BLUETOOTH_SCAN = "android.permission.BLUETOOTH_SCAN"
    BLUETOOTH_ADVERTISE = "android.permission.BLUETOOTH_ADVERTISE"
    VIBRATE = "android.permission.VIBRATE"
    WAKE_LOCK = "android.permission.WAKE_LOCK"
    FOREGROUND_SERVICE = "android.permission.FOREGROUND_SERVICE"
    RECEIVE_BOOT_COMPLETED = "android.permission.RECEIVE_BOOT_COMPLETED"
    WRITE_SETTINGS = "android.permission.WRITE_SETTINGS"
    READ_PHONE_STATE = "android.permission.READ_PHONE_STATE"
    CALL_PHONE = "android.permission.CALL_PHONE"
    SEND_SMS = "android.permission.SEND_SMS"


Caps = _Caps()
Perms = _Perms()


def infer_permissions_from_handlers(click_specs) -> list[str]:
    from dsl.ast import _StmtIf, _StmtWhile, _StmtRequestPermissions

    out: list[str] = []

    def walk(stmts):
        for stmt in stmts or []:
            if isinstance(stmt, _StmtRequestPermissions):
                out.extend(normalize_permission(p) for p in stmt.permissions)
            elif isinstance(stmt, _StmtIf):
                walk(stmt.then)
                walk(stmt.else_)
            elif isinstance(stmt, _StmtWhile):
                walk(stmt.body)

    for spec in click_specs or []:
        walk(getattr(spec, "stmts", None) or [])
    # de-dup preserve order
    seen = set()
    ordered = []
    for perm in out:
        if perm in seen:
            continue
        seen.add(perm)
        ordered.append(perm)
    return ordered


def infer_permissions_from_ui(ui_items) -> list[str]:
    # Currently no UI widgets imply runtime permissions.
    return []
