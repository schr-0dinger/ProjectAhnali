import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import Caps, activity, app, app_config, button, http_get, on_click, text, ui


@on_click("fetch_btn")
def _fetch_btn_handler():
    body = http_get("https://example.com", "offline")
    label.text = body


@on_click("fetch_stmt_btn")
def _fetch_stmt_btn_handler():
    http_get("https://example.com", "offline")


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
    assert "Ljava/net/URL;->openConnection()Ljava/net/URLConnection;" in helper_smali
    assert "Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V" in helper_smali


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
