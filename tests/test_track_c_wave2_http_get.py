import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from emit.smali_runtime_helpers import emit_capability_helper_smali
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    http_get,
    http_get_error,
    http_get_json_field,
    http_get_json_field_error,
    http_get_retry,
    http_get_route,
    http_get_status,
    on_click,
    text,
    ui,
)


@on_click("fetch_btn")
def _fetch_btn_handler():
    body = http_get("https://example.com", "offline")
    label.text = body


@on_click("fetch_stmt_btn")
def _fetch_stmt_btn_handler():
    http_get("https://example.com", "offline")


@on_click("retry_btn")
def _retry_btn_handler():
    body = http_get_retry("https://example.com", 2, 150, "offline")
    label.text = body


@on_click("retry_stmt_btn")
def _retry_stmt_btn_handler():
    http_get_retry("https://example.com", 1, 0, "offline")


@on_click("json_btn")
def _json_btn_handler():
    value = http_get_json_field("https://example.com/data.json", "title", "offline")
    label.text = value


@on_click("json_stmt_btn")
def _json_stmt_btn_handler():
    http_get_json_field("https://example.com/data.json", "title", "offline")


@on_click("json_err_btn")
def _json_err_btn_handler():
    code = http_get_json_field_error("https://example.com/data.json", "title")
    if code == 0:
        label.text = "JSON OK"
    else:
        label.text = "JSON error"


@on_click("probe_btn")
def _probe_btn_handler():
    status = http_get_status("https://example.com")
    err = http_get_error("https://example.com")
    if status == 200:
        label.text = "Network OK"
    else:
        label.text = "Network error"


@on_click("success_btn")
def _success_btn_handler():
    label.text = "Routed success"


@on_click("failure_btn")
def _failure_btn_handler():
    label.text = "Routed failure"


@on_click("dispatch_btn")
def _dispatch_btn_handler():
    http_get_route("https://example.com", "success_btn", "failure_btn", "offline")


def test_track_c_wave2_http_get_lowers_to_runtime_helper_call_and_symbol_set_text():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("Init", id="label"),
                button("Fetch", id="fetch_btn"),
            ),
            _fetch_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGet("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_track_c_wave2_http_get_status_and_error_lower_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("Init", id="label"),
                button("Probe", id="probe_btn"),
            ),
            _probe_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetStatus("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_track_c_wave2_http_get_route_wires_success_and_failure_handlers():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("Init", id="label"),
                button("Dispatch", id="dispatch_btn"),
                button("Success", id="success_btn"),
                button("Failure", id="failure_btn"),
            ),
            _dispatch_btn_handler,
            _success_btn_handler,
            _failure_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetStatus("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGet("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert "LTestHandlers;->onClick_success_btn(Landroid/view/View;)V" in merged
    assert "LTestHandlers;->onClick_failure_btn(Landroid/view/View;)V" in merged


def test_track_c_wave2_http_get_statement_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(button("Fetch", id="fetch_stmt_btn")),
            _fetch_stmt_btn_handler,
        )
    ).build()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGet("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged


def test_track_c_wave2_http_get_retry_lowers_to_runtime_helper_call_and_symbol_set_text():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("Init", id="label"),
                button("Retry", id="retry_btn"),
            ),
            _retry_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetRetry("
        "Landroid/app/Activity;Ljava/lang/String;IILjava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_track_c_wave2_http_get_retry_statement_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(button("Retry", id="retry_stmt_btn")),
            _retry_stmt_btn_handler,
        )
    ).build()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetRetry("
        "Landroid/app/Activity;Ljava/lang/String;IILjava/lang/String;)Ljava/lang/String;"
    ) in merged


def test_track_c_wave2_http_get_json_field_lowers_to_runtime_helper_call_and_symbol_set_text():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("Init", id="label"),
                button("JSON", id="json_btn"),
            ),
            _json_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetJsonField("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_track_c_wave2_http_get_json_field_error_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("Init", id="label"),
                button("JSON Err", id="json_err_btn"),
            ),
            _json_err_btn_handler,
        )
    ).build()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetJsonFieldError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave2_http_get_json_field_statement_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(button("JSON", id="json_stmt_btn")),
            _json_stmt_btn_handler,
        )
    ).build()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetJsonField("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged


def test_track_c_wave2_http_get_requires_networking_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Fetch", id="fetch_stmt_btn")),
            _fetch_stmt_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Networking capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] http_get requires Caps.Networking." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Networking]) to activity(...)." in str(exc)


def test_track_c_wave2_http_get_retry_requires_networking_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Retry", id="retry_stmt_btn")),
            _retry_stmt_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Networking capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] http_get_retry requires Caps.Networking." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Networking]) to activity(...)." in str(exc)


def test_track_c_wave2_http_get_json_field_requires_networking_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("JSON", id="json_stmt_btn")),
            _json_stmt_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Networking capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] http_get_json_field requires Caps.Networking." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Networking]) to activity(...)." in str(exc)


def test_track_c_wave2_http_get_json_field_error_requires_networking_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("JSON Err", id="json_err_btn"),
            ),
            _json_err_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Networking capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] http_get_json_field_error requires Caps.Networking." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Networking]) to activity(...)." in str(exc)


def test_track_c_wave2_toolchain_emits_http_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(button("Fetch", id="fetch_stmt_btn")),
            _fetch_stmt_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "HttpHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert (
        ".method public static httpGet("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in helper_smali
    assert (
        ".method public static httpGetStatus("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in helper_smali
    assert (
        ".method public static httpGetError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in helper_smali
    assert (
        ".method public static httpGetRetry("
        "Landroid/app/Activity;Ljava/lang/String;IILjava/lang/String;)Ljava/lang/String;"
    ) in helper_smali
    assert (
        ".method public static httpGetJsonFieldError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in helper_smali
    assert (
        ".method public static httpGetJsonField("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in helper_smali
    assert "Ljava/net/URL;->openConnection()Ljava/net/URLConnection;" in helper_smali
    assert "Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V" in helper_smali
    assert "Lcom/ahnali/runtime/HttpHelper;->httpGetError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert "Lcom/ahnali/runtime/HttpHelper;->httpGet(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in helper_smali
    assert "Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V" in helper_smali
    assert "Lorg/json/JSONObject;->has(Ljava/lang/String;)Z" in helper_smali
    assert "Lorg/json/JSONObject;->isNull(Ljava/lang/String;)Z" in helper_smali
    assert "Lorg/json/JSONObject;->opt(Ljava/lang/String;)Ljava/lang/Object;" in helper_smali
    assert "Ljava/lang/Thread;->sleep(J)V" in helper_smali
    assert "return-object p2" in helper_smali
    assert "const/4 v0, -0x1" in helper_smali
    assert "const/4 v0, 0x0" in helper_smali
    assert "const/4 v0, 0x3" in helper_smali
    assert "const/4 v0, 0x4" in helper_smali
    assert "const/4 v0, 0x5" in helper_smali
    assert "const/4 v0, 0x6" in helper_smali
    assert "return-object p4" in helper_smali


def test_track_c_wave2_http_get_json_field_error_maps_malformed_payload_code():
    helper_smali = emit_capability_helper_smali(
        class_desc="Lcom/ahnali/runtime/HttpHelper;",
        helper_method="httpGet",
        helper_sig="(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
    )
    assert ":ahnali_http_json_error_malformed" in helper_smali
    assert "const/4 v0, 0x5" in helper_smali


def test_track_c_wave2_http_get_json_field_error_maps_missing_key_code():
    helper_smali = emit_capability_helper_smali(
        class_desc="Lcom/ahnali/runtime/HttpHelper;",
        helper_method="httpGet",
        helper_sig="(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
    )
    assert ":ahnali_http_json_error_missing_key" in helper_smali
    assert "const/4 v0, 0x6" in helper_smali


def _build_with_bad_handler(btn_id: str, handler):
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(button("Fetch", id=btn_id)),
            on_click(btn_id)(handler),
        )
    )


def test_track_c_wave2_parser_http_get_rejects_wrong_arity():
    def _bad():
        body = http_get("https://example.com", "a", "b")
        preview = body

    with pytest.raises(RuntimeError, match="http_get expects 1 or 2 string arguments"):
        _build_with_bad_handler("bad_fetch_arity", _bad)


def test_track_c_wave2_parser_http_get_rejects_non_string_url():
    def _bad():
        body = http_get(1, "fallback")
        preview = body

    with pytest.raises(RuntimeError, match="http_get argument 'url' must be a constant string"):
        _build_with_bad_handler("bad_fetch_type", _bad)


def test_track_c_wave2_parser_http_get_rejects_non_string_default():
    def _bad():
        body = http_get("https://example.com", 42)
        preview = body

    with pytest.raises(RuntimeError, match="http_get argument 'default_value' must be a constant string"):
        _build_with_bad_handler("bad_fetch_default_type", _bad)


def test_track_c_wave2_parser_http_get_status_rejects_non_string_url():
    def _bad():
        code = http_get_status(1)
        probe = code

    with pytest.raises(RuntimeError, match="http_get_status argument 'url' must be a constant string"):
        _build_with_bad_handler("bad_fetch_status_type", _bad)


def test_track_c_wave2_parser_http_get_error_rejects_non_string_url():
    def _bad():
        code = http_get_error(1)
        probe = code

    with pytest.raises(RuntimeError, match="http_get_error argument 'url' must be a constant string"):
        _build_with_bad_handler("bad_fetch_error_type", _bad)


def test_track_c_wave2_parser_http_get_route_rejects_wrong_arity():
    def _bad():
        http_get_route("https://example.com", "success_btn")

    with pytest.raises(RuntimeError, match="http_get_route expects 3 or 4 string arguments"):
        _build_with_bad_handler("bad_fetch_route_arity", _bad)


def test_track_c_wave2_parser_http_get_retry_rejects_wrong_arity():
    def _bad():
        body = http_get_retry("https://example.com", 1, 50, "fallback", "extra")
        preview = body

    with pytest.raises(RuntimeError, match="http_get_retry expects 3 or 4 arguments"):
        _build_with_bad_handler("bad_fetch_retry_arity", _bad)


def test_track_c_wave2_parser_http_get_retry_rejects_non_int_retries():
    def _bad():
        body = http_get_retry("https://example.com", "1", 50, "fallback")
        preview = body

    with pytest.raises(RuntimeError, match="http_get_retry argument 'retries' must be an integer constant"):
        _build_with_bad_handler("bad_fetch_retry_retries", _bad)


def test_track_c_wave2_parser_http_get_retry_rejects_non_int_backoff():
    def _bad():
        body = http_get_retry("https://example.com", 1, "50", "fallback")
        preview = body

    with pytest.raises(RuntimeError, match="http_get_retry argument 'backoff_ms' must be an integer constant"):
        _build_with_bad_handler("bad_fetch_retry_backoff", _bad)


def test_track_c_wave2_parser_http_get_retry_rejects_non_string_default():
    def _bad():
        body = http_get_retry("https://example.com", 1, 50, 7)
        preview = body

    with pytest.raises(RuntimeError, match="http_get_retry argument 'default_value' must be a constant string"):
        _build_with_bad_handler("bad_fetch_retry_default", _bad)


def test_track_c_wave2_parser_http_get_json_field_rejects_wrong_arity():
    def _bad():
        value = http_get_json_field("https://example.com/data.json", "title")
        preview = value

    with pytest.raises(RuntimeError, match="http_get_json_field expects exactly 3 string arguments"):
        _build_with_bad_handler("bad_fetch_json_arity", _bad)


def test_track_c_wave2_parser_http_get_json_field_rejects_non_string_url():
    def _bad():
        value = http_get_json_field(7, "title", "fallback")
        preview = value

    with pytest.raises(RuntimeError, match="http_get_json_field argument 'url' must be a constant string"):
        _build_with_bad_handler("bad_fetch_json_url", _bad)


def test_track_c_wave2_parser_http_get_json_field_rejects_non_string_key():
    def _bad():
        value = http_get_json_field("https://example.com/data.json", 7, "fallback")
        preview = value

    with pytest.raises(RuntimeError, match="http_get_json_field argument 'key' must be a constant string"):
        _build_with_bad_handler("bad_fetch_json_key", _bad)


def test_track_c_wave2_parser_http_get_json_field_rejects_non_string_fallback():
    def _bad():
        value = http_get_json_field("https://example.com/data.json", "title", 7)
        preview = value

    with pytest.raises(RuntimeError, match="http_get_json_field argument 'fallback' must be a constant string"):
        _build_with_bad_handler("bad_fetch_json_fallback", _bad)


def test_track_c_wave2_parser_http_get_json_field_error_rejects_wrong_arity():
    def _bad():
        code = http_get_json_field_error("https://example.com/data.json")
        preview = code

    with pytest.raises(RuntimeError, match="http_get_json_field_error expects exactly 2 string arguments"):
        _build_with_bad_handler("bad_fetch_json_err_arity", _bad)


def test_track_c_wave2_parser_http_get_json_field_error_rejects_non_string_key():
    def _bad():
        code = http_get_json_field_error("https://example.com/data.json", 7)
        preview = code

    with pytest.raises(RuntimeError, match="http_get_json_field_error argument 'key' must be a constant string"):
        _build_with_bad_handler("bad_fetch_json_err_key", _bad)


def test_track_c_wave2_http_get_route_rejects_unknown_handler_target():
    @on_click("dispatch_btn_missing")
    def _dispatch_missing_handler():
        http_get_route("https://example.com", "missing_success", "failure_btn")

    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("Init", id="label"),
                button("Dispatch", id="dispatch_btn_missing"),
                button("Failure", id="failure_btn"),
            ),
            _dispatch_missing_handler,
            _failure_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match="http_get_route argument 'success_target_id' references unknown on_click target"):
        prog.build()
