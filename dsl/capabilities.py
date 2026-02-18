from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

ANDROID_PERMISSION_PREFIX = "android.permission."


@dataclass(frozen=True)
class Capability:
    name: str
    permissions: tuple[str, ...]


@dataclass(frozen=True)
class CapabilityRuntimeBinding:
    capability: str
    permissions: tuple[str, ...]
    helper_class_desc: str | None = None
    helper_method: str | None = None
    helper_sig: str | None = None
    mode: str = "permission_only"

    def __post_init__(self):
        if self.mode not in {"permission_only", "helper_call"}:
            raise RuntimeError(
                f"Unsupported capability runtime mode '{self.mode}' for '{self.capability}'"
            )
        if self.mode == "helper_call":
            if not (self.helper_class_desc and self.helper_method and self.helper_sig):
                raise RuntimeError(
                    f"helper_call mode requires helper_class_desc/helper_method/helper_sig for '{self.capability}'"
                )
        if self.helper_class_desc is not None:
            if not (
                self.helper_class_desc.startswith("L")
                and self.helper_class_desc.endswith(";")
            ):
                raise RuntimeError(
                    f"Invalid helper class descriptor '{self.helper_class_desc}' for '{self.capability}'"
                )
        if self.helper_sig is not None:
            if "(" not in self.helper_sig or ")" not in self.helper_sig:
                raise RuntimeError(
                    f"Invalid helper signature '{self.helper_sig}' for '{self.capability}'"
                )


CAPABILITY_RUNTIME_ABI_VERSION = "1.0.0"


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
DEFAULT_CAPABILITY_RUNTIME_BINDINGS: dict[str, CapabilityRuntimeBinding] = {}
_CAPABILITY_BINDING_ALIASES: dict[str, str] = {}


def _remember_capability_alias(alias: str, canonical: str):
    key = str(alias).strip()
    if not key:
        return
    _CAPABILITY_BINDING_ALIASES[key] = canonical
    _CAPABILITY_BINDING_ALIASES[key.lower()] = canonical


def register_default_capability(
    name: str,
    permissions: Iterable[str] | None = None,
    *,
    aliases: Iterable[str] | None = None,
    helper_class_desc: str | None = None,
    helper_method: str | None = None,
    helper_sig: str | None = None,
):
    canonical = str(name).strip()
    if not canonical:
        raise RuntimeError("Capability name must be non-empty")
    normalized_perms = tuple(
        normalize_permission(p) for p in (permissions or []) if str(p).strip()
    )
    DEFAULT_CAPABILITY_REGISTRY.register(canonical, normalized_perms)
    binding = CapabilityRuntimeBinding(
        capability=canonical,
        permissions=normalized_perms,
        helper_class_desc=helper_class_desc,
        helper_method=helper_method,
        helper_sig=helper_sig,
        mode="helper_call" if helper_class_desc else "permission_only",
    )
    DEFAULT_CAPABILITY_RUNTIME_BINDINGS[canonical] = binding
    _remember_capability_alias(canonical, canonical)
    for alias in aliases or []:
        DEFAULT_CAPABILITY_REGISTRY.register(alias, normalized_perms)
        _remember_capability_alias(str(alias), canonical)


def default_capability_runtime_mapping() -> dict[str, CapabilityRuntimeBinding]:
    return dict(DEFAULT_CAPABILITY_RUNTIME_BINDINGS)


def resolve_runtime_bindings(uses: Iterable[str] | None) -> list[CapabilityRuntimeBinding]:
    out: list[CapabilityRuntimeBinding] = []
    seen: set[str] = set()
    if not uses:
        return out
    for raw in uses:
        if raw is None:
            continue
        item = str(raw).strip()
        if not item:
            continue
        if item.startswith(ANDROID_PERMISSION_PREFIX):
            continue
        if item.isupper() or item.replace("_", "").isupper():
            continue
        canonical = _CAPABILITY_BINDING_ALIASES.get(item) or _CAPABILITY_BINDING_ALIASES.get(
            item.lower()
        )
        if canonical is None:
            raise RuntimeError(f"Unknown capability '{item}'")
        if canonical in seen:
            continue
        seen.add(canonical)
        out.append(DEFAULT_CAPABILITY_RUNTIME_BINDINGS[canonical])
    return out

# Conservative, initial map. Expand as capabilities ship.
register_default_capability("Camera", ["android.permission.CAMERA"])
register_default_capability("Microphone", ["android.permission.RECORD_AUDIO"])
register_default_capability("Audio", ["android.permission.RECORD_AUDIO"])
register_default_capability(
    "Video",
    ["android.permission.CAMERA", "android.permission.RECORD_AUDIO"],
)
register_default_capability("WebView", ["android.permission.INTERNET"])
register_default_capability(
    "Sensors",
    ["android.permission.BODY_SENSORS"],
)
register_default_capability(
    "Storage",
    ["android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE"],
    helper_class_desc="Lcom/ahnali/runtime/StorageHelper;",
    helper_method="putString",
    helper_sig="(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
)
register_default_capability(
    "FilePicker",
    ["android.permission.READ_EXTERNAL_STORAGE"],
    aliases=["File Picker"],
)
register_default_capability(
    "Connectivity",
    ["android.permission.ACCESS_NETWORK_STATE", "android.permission.INTERNET"],
    helper_class_desc="Lcom/ahnali/runtime/ConnectivityHelper;",
    helper_method="isConnected",
    helper_sig="(Landroid/app/Activity;)I",
)
register_default_capability(
    "Networking",
    ["android.permission.INTERNET"],
    aliases=["Network"],
    helper_class_desc="Lcom/ahnali/runtime/HttpHelper;",
    helper_method="httpGet",
    helper_sig="(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
)
register_default_capability(
    "URLLauncher",
    ["android.permission.INTERNET"],
    aliases=["URL launcher"],
    helper_class_desc="Lcom/ahnali/runtime/UrlLauncherHelper;",
    helper_method="openUrl",
    helper_sig="(Landroid/app/Activity;Ljava/lang/String;)I",
)
register_default_capability(
    "Permissions",
    [],
    helper_class_desc="Lcom/ahnali/runtime/PermissionHelper;",
    helper_method="isGranted",
    helper_sig="(Landroid/app/Activity;Ljava/lang/String;)I",
)
register_default_capability(
    "Notifications",
    ["android.permission.POST_NOTIFICATIONS"],
    aliases=["Notification"],
    helper_class_desc="Lcom/ahnali/runtime/NotificationHelper;",
    helper_method="postNotification",
    helper_sig="(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I",
)
register_default_capability(
    "Clipboard",
    [],
    helper_class_desc="Lcom/ahnali/runtime/ClipboardHelper;",
    helper_method="setText",
    helper_sig="(Landroid/app/Activity;Ljava/lang/String;)I",
)
register_default_capability(
    "Maps",
    ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"],
)
register_default_capability(
    "Location",
    ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"],
    helper_class_desc="Lcom/ahnali/runtime/LocationHelper;",
    helper_method="isLocationEnabled",
    helper_sig="(Landroid/app/Activity;)I",
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
    Networking = "Networking"
    URLLauncher = "URLLauncher"
    Permissions = "Permissions"
    Notifications = "Notifications"
    Clipboard = "Clipboard"
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
