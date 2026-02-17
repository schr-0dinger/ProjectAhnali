import re

import pytest

from dsl.app import (
    activity,
    app,
    button,
    check_connectivity,
    http_get,
    location_enabled,
    on_click,
    open_url,
    permission_granted,
    storage_put,
    text,
    ui,
)


@on_click("btn_open_url")
def _handler_open_url():
    open_url("https://example.com")


@on_click("btn_connectivity")
def _handler_connectivity():
    check_connectivity()


@on_click("btn_storage")
def _handler_storage():
    storage_put("k", "v")


@on_click("btn_http")
def _handler_http_get():
    value = http_get("https://example.com", "fallback")
    status_label.text = value


@on_click("btn_location")
def _handler_location_enabled():
    enabled = location_enabled()
    status_label.text = enabled


@on_click("btn_permission")
def _handler_permission_granted():
    granted = permission_granted("android.permission.CAMERA")
    status_label.text = granted


@pytest.mark.parametrize(
    "api_name,cap_name,ui_items,handler",
    [
        ("open_url", "URLLauncher", [button("Open", id="btn_open_url")], _handler_open_url),
        (
            "check_connectivity",
            "Connectivity",
            [button("Check", id="btn_connectivity")],
            _handler_connectivity,
        ),
        ("storage_put", "Storage", [button("Store", id="btn_storage")], _handler_storage),
        (
            "http_get",
            "Networking",
            [text("status", id="status_label"), button("Fetch", id="btn_http")],
            _handler_http_get,
        ),
        (
            "location_enabled",
            "Location",
            [text("status", id="status_label"), button("Locate", id="btn_location")],
            _handler_location_enabled,
        ),
        (
            "permission_granted",
            "Permissions",
            [text("status", id="status_label"), button("Perm", id="btn_permission")],
            _handler_permission_granted,
        ),
    ],
)
def test_capability_diagnostics_use_standard_error_format(api_name, cap_name, ui_items, handler):
    prog = app(
        activity(
            "MainActivity",
            ui(*ui_items),
            handler,
        )
    )

    expected = (
        rf"\[CapabilityError\] {re.escape(api_name)} requires Caps\.{re.escape(cap_name)}\. "
        rf"Fix: add app_config\(uses=\[Caps\.{re.escape(cap_name)}\]\) to activity\(\.\.\.\)\."
    )

    with pytest.raises(RuntimeError, match=expected):
        prog.build()
