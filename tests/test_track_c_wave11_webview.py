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
    web_load,
    web_load_error,
    web_load_result,
    web_set_policy,
)


@on_click("policy_btn")
def _policy_btn_handler():
    web_set_policy(1, 1, 0, 0)


@on_click("load_btn")
def _load_btn_handler():
    web_load("https://example.com/wave11")


@on_click("eval_btn")
def _eval_btn_handler():
    ok = web_load_result("https://example.com/wave11")
    err = web_load_error("https://example.com/wave11")
    status_label.text = err
    preview_label.text = ok


@on_click("eval_only_btn")
def _eval_only_btn_handler():
    err = web_load_error("https://example.com/wave11")
    status_label.text = err


def test_track_c_wave11_webview_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WebView]),
            ui(
                text("status", id="status_label"),
                text("preview", id="preview_label"),
                button("Policy", id="policy_btn"),
                button("Load", id="load_btn"),
                button("Eval", id="eval_btn"),
            ),
            _policy_btn_handler,
            _load_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/WebHelper;->setPolicy("
        "Landroid/app/Activity;IIII)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->loadUrl("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->loadUrlError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave11_web_load_requires_webview_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Load", id="load_btn")),
            _load_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] web_load requires Caps\.WebView\."):
        prog.build()


def test_track_c_wave11_web_load_error_requires_webview_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), button("Eval", id="eval_only_btn")),
            _eval_only_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] web_load_error requires Caps\.WebView\."):
        prog.build()


def test_track_c_wave11_toolchain_emits_web_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WebView]),
            ui(button("Load", id="load_btn")),
            _load_btn_handler,
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
    assert ".method public static setPolicy(Landroid/app/Activity;IIII)I" in helper_smali
    assert ".method public static loadUrl(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static loadUrlError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali


def test_track_c_wave11_parser_web_set_policy_rejects_wrong_arity():
    def _bad():
        web_set_policy(1, 1, 0, 0, 1)

    with pytest.raises(RuntimeError, match="web_set_policy expects up to 4 integer/bool arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WebView]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave11_parser_web_set_policy_rejects_non_int_bool_value():
    def _bad():
        web_set_policy("yes")

    with pytest.raises(RuntimeError, match="web_set_policy argument 'js_enabled' must be an integer/bool constant"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WebView]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave11_parser_web_load_rejects_non_string_url():
    def _bad():
        web_load(7)

    with pytest.raises(RuntimeError, match="web_load argument 'url' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WebView]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
