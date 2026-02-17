import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    http_async_body,
    http_async_error,
    http_async_json_array_length,
    http_async_json_field,
    http_async_json_field_error,
    http_async_progress,
    http_get_route_async,
    on_click,
    text,
    ui,
)


@on_click("start_btn")
def _start_btn_handler():
    token = http_get_route_async(
        "https://example.com/api",
        "ok_btn",
        "fail_btn",
        "offline",
        "progress_btn",
        2,
        2200,
        "POST",
        "Authorization:Bearer abc",
        "{\"q\":1}",
    )
    status_label.text = token


@on_click("progress_btn")
def _progress_btn_handler():
    p = http_async_progress()
    status_label.text = p


@on_click("ok_btn")
def _ok_btn_handler():
    t = 1
    title = http_async_json_field(t, "title", "n/a")
    preview_label.text = title


@on_click("fail_btn")
def _fail_btn_handler():
    t = 1
    code = http_async_json_field_error(t, "title")
    err = http_async_error(t)
    size = http_async_json_array_length(t, 0)
    body = http_async_body(t, "offline")
    status_label.text = code
    if err == 0:
        preview_label.text = body
    else:
        status_label.text = size


def _build_wave4_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("Status", id="status_label"),
                text("Preview", id="preview_label"),
                button("Start", id="start_btn"),
                button("Progress", id="progress_btn"),
                button("OK", id="ok_btn"),
                button("FAIL", id="fail_btn"),
            ),
            _start_btn_handler,
            _progress_btn_handler,
            _ok_btn_handler,
            _fail_btn_handler,
        )
    ).build()


def test_track_c_wave4_route_options_and_typed_async_json_lowering():
    prog = _build_wave4_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Lcom/ahnali/runtime/HttpHelper;->startAsyncWithToken(ILjava/lang/Runnable;)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncJsonField(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncJsonFieldError(ILjava/lang/String;)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncJsonArrayLength(II)I" in merged


def test_track_c_wave4_toolchain_emits_multitoken_state_and_json_adapter_methods(tmp_path):
    frontend = _build_wave4_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "HttpHelper.smali"
    worker_path = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliHttpRouteAsyncWorker.smali"
    assert helper_path.exists()
    assert worker_path.exists()

    helper_smali = helper_path.read_text(encoding="utf-8")
    worker_smali = worker_path.read_text(encoding="utf-8")

    assert ".field private static sAsyncCancelByToken:Landroid/util/SparseIntArray;" in helper_smali
    assert ".field private static sAsyncProgressByToken:Landroid/util/SparseIntArray;" in helper_smali
    assert ".field private static sAsyncErrorByToken:Landroid/util/SparseIntArray;" in helper_smali
    assert ".field private static sAsyncStatusByToken:Landroid/util/SparseIntArray;" in helper_smali
    assert ".field private static sAsyncBodyByToken:Ljava/util/HashMap;" in helper_smali

    assert ".method private static ensureAsyncStores()V" in helper_smali
    assert ".method private static initAsyncToken(I)V" in helper_smali
    assert ".method public static nextAsyncToken()I" in helper_smali
    assert ".method public static startAsyncWithToken(ILjava/lang/Runnable;)I" in helper_smali
    assert ".method public static getAsyncJsonFieldError(ILjava/lang/String;)I" in helper_smali
    assert ".method public static getAsyncJsonField(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in helper_smali
    assert ".method public static getAsyncJsonArrayLengthError(I)I" in helper_smali
    assert ".method public static getAsyncJsonArrayLength(II)I" in helper_smali

    assert "const/4 v0, 0x5" in helper_smali
    assert "const/4 v0, 0x6" in helper_smali
    assert "const/16 v0, 0x8" in helper_smali

    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpRequestWithTimeout("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;"
    ) in worker_smali
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpRequestStatusWithTimeout("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I"
    ) in worker_smali


def test_track_c_wave4_parser_rejects_invalid_route_option_types():
    def _bad_method():
        http_get_route_async("https://example.com", "ok_btn", "fail_btn", "offline", "", 1, 2000, 7)

    with pytest.raises(RuntimeError, match="http_get_route_async argument 'method' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(button("Start", id="bad_method_btn"), button("OK", id="ok_btn"), button("FAIL", id="fail_btn")),
                on_click("bad_method_btn")(_bad_method),
                _ok_btn_handler,
                _fail_btn_handler,
            )
        ).build()

    def _bad_headers():
        http_get_route_async("https://example.com", "ok_btn", "fail_btn", "offline", "", 1, 2000, "GET", 7)

    with pytest.raises(RuntimeError, match="http_get_route_async argument 'headers' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(button("Start", id="bad_headers_btn"), button("OK", id="ok_btn"), button("FAIL", id="fail_btn")),
                on_click("bad_headers_btn")(_bad_headers),
                _ok_btn_handler,
                _fail_btn_handler,
            )
        ).build()

    def _bad_body():
        http_get_route_async("https://example.com", "ok_btn", "fail_btn", "offline", "", 1, 2000, "GET", "", 7)

    with pytest.raises(RuntimeError, match="http_get_route_async argument 'body' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(button("Start", id="bad_body_btn"), button("OK", id="ok_btn"), button("FAIL", id="fail_btn")),
                on_click("bad_body_btn")(_bad_body),
                _ok_btn_handler,
                _fail_btn_handler,
            )
        ).build()


def test_track_c_wave4_parser_rejects_invalid_typed_async_json_args():
    def _bad_json_key():
        t = 1
        value = http_async_json_field(t, 7, "x")
        status_label.text = value

    with pytest.raises(RuntimeError, match="http_async_json_field argument 'key' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(text("x", id="status_label"), button("Bad", id="bad_json_key_btn")),
                on_click("bad_json_key_btn")(_bad_json_key),
            )
        ).build()

    def _bad_json_fallback():
        t = 1
        value = http_async_json_field(t, "title", 7)
        status_label.text = value

    with pytest.raises(RuntimeError, match="http_async_json_field argument 'fallback' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(text("x", id="status_label"), button("Bad", id="bad_json_fallback_btn")),
                on_click("bad_json_fallback_btn")(_bad_json_fallback),
            )
        ).build()

    def _bad_array_fallback():
        t = 1
        value = http_async_json_array_length(t, "x")
        status_label.text = value

    with pytest.raises(RuntimeError, match="http_async_json_array_length argument 'fallback' must be an integer constant"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(text("x", id="status_label"), button("Bad", id="bad_array_fallback_btn")),
                on_click("bad_array_fallback_btn")(_bad_array_fallback),
            )
        ).build()
