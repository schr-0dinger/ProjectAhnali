import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    on_click,
    text,
    ui,
    web_choose_file,
    web_choose_file_error,
    web_choose_file_result,
    web_cookie_get,
    web_cookie_get_error,
    web_cookie_set,
    web_cookie_set_error,
    web_cookie_set_result,
)


@on_click("choose_btn")
def _choose_btn_handler():
    web_choose_file("image/*")


@on_click("cookie_btn")
def _cookie_btn_handler():
    web_cookie_set("https://example.com", "ahnali=wave13")


@on_click("eval_btn")
def _eval_btn_handler():
    choose_ok = web_choose_file_result("image/*")
    choose_err = web_choose_file_error("image/*")
    cookie_ok = web_cookie_set_result("https://example.com", "ahnali=wave13")
    cookie_err = web_cookie_set_error("https://example.com", "ahnali=wave13")
    cookie_value = web_cookie_get("https://example.com", "no-cookie")
    cookie_get_err = web_cookie_get_error("https://example.com")
    total_err = choose_err + cookie_err + cookie_get_err
    total_ok = choose_ok + cookie_ok
    preview_label.text = cookie_value
    status_label.text = total_err
    bridge_label.text = total_ok


@on_click("eval_only_btn")
def _eval_only_btn_handler():
    err = web_cookie_get_error("https://example.com")
    status_label.text = err


def test_track_c_wave13_web_file_cookie_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WebView]),
            ui(
                text("status", id="status_label"),
                text("preview", id="preview_label"),
                text("bridge", id="bridge_label"),
                button("Choose", id="choose_btn"),
                button("Cookie", id="cookie_btn"),
                button("Eval", id="eval_btn"),
            ),
            _choose_btn_handler,
            _cookie_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/WebHelper;->chooseFile("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->chooseFileError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->setCookie("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->setCookieError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->getCookie("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->getCookieError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave13_web_choose_file_requires_webview_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Choose", id="choose_btn")),
            _choose_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] web_choose_file requires Caps\.WebView\."):
        prog.build()


def test_track_c_wave13_web_cookie_get_error_requires_webview_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), button("Eval", id="eval_only_btn")),
            _eval_only_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] web_cookie_get_error requires Caps\.WebView\."):
        prog.build()


def test_track_c_wave13_toolchain_emits_web_helper_file_cookie_methods(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WebView]),
            ui(button("Choose", id="choose_btn")),
            _choose_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "WebHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static chooseFile(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static chooseFileError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static setCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static setCookieError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static getCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in helper_smali
    assert ".method public static getCookieError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali


def test_track_c_wave13_parser_web_choose_file_rejects_non_string_mime():
    def _bad():
        web_choose_file(7)

    with pytest.raises(RuntimeError, match="web_choose_file argument 'mime_type' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WebView]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave13_parser_web_cookie_set_rejects_wrong_arity():
    def _bad():
        web_cookie_set("https://example.com")

    with pytest.raises(RuntimeError, match="web_cookie_set expects exactly 2 string arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WebView]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave13_parser_web_cookie_get_rejects_non_string_fallback():
    def _bad():
        value = web_cookie_get("https://example.com", 7)
        status_label.text = value

    with pytest.raises(RuntimeError, match="web_cookie_get argument 'fallback' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WebView]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
