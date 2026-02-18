import re

import pytest

from dsl.app import (
    activity,
    app,
    button,
    clipboard_get,
    clipboard_set,
    check_connectivity,
    create_notification_channel,
    deep_link_error,
    deep_link_get,
    http_get,
    location_enabled,
    notify_error,
    notify_result,
    on_click,
    open_external_error,
    open_url,
    permission_granted,
    share_text,
    share_text_error,
    storage_put,
    text,
    ui,
    web_load,
    web_add_js_bridge,
    web_add_js_bridge_error,
    web_choose_file,
    web_choose_file_error,
    web_cookie_get,
    web_cookie_get_error,
    web_cookie_set,
    web_cookie_set_error,
    web_load_error,
    web_set_policy,
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


@on_click("btn_notification_channel")
def _handler_create_notification_channel():
    create_notification_channel("ahnali_diag", "Ahnali Diagnostics")


@on_click("btn_notify_result")
def _handler_notify_result():
    posted = notify_result("Diag", "Body", "ahnali_diag")
    status_label.text = posted


@on_click("btn_notify_error")
def _handler_notify_error():
    err = notify_error("Diag", "Body", "ahnali_diag")
    status_label.text = err


@on_click("btn_share_text")
def _handler_share_text():
    share_text("Diag share payload", "Ahnali share")


@on_click("btn_share_error")
def _handler_share_error():
    err = share_text_error("Diag share payload", "Ahnali share")
    status_label.text = err


@on_click("btn_open_external_error")
def _handler_open_external_error():
    err = open_external_error("https://example.com")
    status_label.text = err


@on_click("btn_deep_link_get")
def _handler_deep_link_get():
    value = deep_link_get("ahnali://fallback")
    status_label.text = value


@on_click("btn_deep_link_error")
def _handler_deep_link_error():
    err = deep_link_error()
    status_label.text = err


@on_click("btn_web_policy")
def _handler_web_policy():
    web_set_policy(1, 1, 0, 0)


@on_click("btn_web_load")
def _handler_web_load():
    web_load("https://example.com")


@on_click("btn_web_bridge")
def _handler_web_bridge():
    web_add_js_bridge("ahnali_bridge")


@on_click("btn_web_bridge_error")
def _handler_web_bridge_error():
    err = web_add_js_bridge_error("ahnali_bridge")
    status_label.text = err


@on_click("btn_web_choose_file")
def _handler_web_choose_file():
    web_choose_file("*/*")


@on_click("btn_web_choose_file_error")
def _handler_web_choose_file_error():
    err = web_choose_file_error("*/*")
    status_label.text = err


@on_click("btn_web_cookie_set")
def _handler_web_cookie_set():
    web_cookie_set("https://example.com", "ahnali=diag")


@on_click("btn_web_cookie_set_error")
def _handler_web_cookie_set_error():
    err = web_cookie_set_error("https://example.com", "ahnali=diag")
    status_label.text = err


@on_click("btn_web_cookie_get")
def _handler_web_cookie_get():
    value = web_cookie_get("https://example.com", "fallback-cookie")
    status_label.text = value


@on_click("btn_web_cookie_get_error")
def _handler_web_cookie_get_error():
    err = web_cookie_get_error("https://example.com")
    status_label.text = err


@on_click("btn_web_error")
def _handler_web_error():
    err = web_load_error("https://example.com")
    status_label.text = err


@on_click("btn_clipboard_set")
def _handler_clipboard_set():
    clipboard_set("diag clipboard value")


@on_click("btn_clipboard_get")
def _handler_clipboard_get():
    value = clipboard_get("diag fallback")
    status_label.text = value


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
        (
            "create_notification_channel",
            "Notifications",
            [button("Channel", id="btn_notification_channel")],
            _handler_create_notification_channel,
        ),
        (
            "notify_result",
            "Notifications",
            [text("status", id="status_label"), button("Post", id="btn_notify_result")],
            _handler_notify_result,
        ),
        (
            "notify_error",
            "Notifications",
            [text("status", id="status_label"), button("PostErr", id="btn_notify_error")],
            _handler_notify_error,
        ),
        (
            "share_text",
            "Sharing",
            [button("Share", id="btn_share_text")],
            _handler_share_text,
        ),
        (
            "share_text_error",
            "Sharing",
            [text("status", id="status_label"), button("ShareErr", id="btn_share_error")],
            _handler_share_error,
        ),
        (
            "open_external_error",
            "Sharing",
            [text("status", id="status_label"), button("OpenErr", id="btn_open_external_error")],
            _handler_open_external_error,
        ),
        (
            "deep_link_get",
            "DeepLinking",
            [text("status", id="status_label"), button("DeepGet", id="btn_deep_link_get")],
            _handler_deep_link_get,
        ),
        (
            "deep_link_error",
            "DeepLinking",
            [text("status", id="status_label"), button("DeepErr", id="btn_deep_link_error")],
            _handler_deep_link_error,
        ),
        (
            "web_set_policy",
            "WebView",
            [button("WebPolicy", id="btn_web_policy")],
            _handler_web_policy,
        ),
        (
            "web_load",
            "WebView",
            [button("WebLoad", id="btn_web_load")],
            _handler_web_load,
        ),
        (
            "web_add_js_bridge",
            "WebView",
            [button("WebBridge", id="btn_web_bridge")],
            _handler_web_bridge,
        ),
        (
            "web_add_js_bridge_error",
            "WebView",
            [text("status", id="status_label"), button("WebBridgeErr", id="btn_web_bridge_error")],
            _handler_web_bridge_error,
        ),
        (
            "web_choose_file",
            "WebView",
            [button("WebChooseFile", id="btn_web_choose_file")],
            _handler_web_choose_file,
        ),
        (
            "web_choose_file_error",
            "WebView",
            [text("status", id="status_label"), button("WebChooseErr", id="btn_web_choose_file_error")],
            _handler_web_choose_file_error,
        ),
        (
            "web_cookie_set",
            "WebView",
            [button("WebCookieSet", id="btn_web_cookie_set")],
            _handler_web_cookie_set,
        ),
        (
            "web_cookie_set_error",
            "WebView",
            [text("status", id="status_label"), button("WebCookieSetErr", id="btn_web_cookie_set_error")],
            _handler_web_cookie_set_error,
        ),
        (
            "web_cookie_get",
            "WebView",
            [text("status", id="status_label"), button("WebCookieGet", id="btn_web_cookie_get")],
            _handler_web_cookie_get,
        ),
        (
            "web_cookie_get_error",
            "WebView",
            [text("status", id="status_label"), button("WebCookieGetErr", id="btn_web_cookie_get_error")],
            _handler_web_cookie_get_error,
        ),
        (
            "web_load_error",
            "WebView",
            [text("status", id="status_label"), button("WebErr", id="btn_web_error")],
            _handler_web_error,
        ),
        (
            "clipboard_set",
            "Clipboard",
            [button("ClipSet", id="btn_clipboard_set")],
            _handler_clipboard_set,
        ),
        (
            "clipboard_get",
            "Clipboard",
            [text("status", id="status_label"), button("ClipGet", id="btn_clipboard_get")],
            _handler_clipboard_get,
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
