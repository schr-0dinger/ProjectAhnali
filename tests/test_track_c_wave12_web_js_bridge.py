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
    web_add_js_bridge,
    web_add_js_bridge_error,
    web_add_js_bridge_result,
    web_set_policy,
)


@on_click("policy_btn")
def _policy_btn_handler():
    web_set_policy(1, 1, 0, 0)


@on_click("bridge_btn")
def _bridge_btn_handler():
    web_add_js_bridge("ahnali_bridge")


@on_click("eval_btn")
def _eval_btn_handler():
    ok = web_add_js_bridge_result("ahnali_bridge")
    err = web_add_js_bridge_error("ahnali_bridge")
    status_label.text = err
    preview_label.text = ok


@on_click("eval_only_btn")
def _eval_only_btn_handler():
    err = web_add_js_bridge_error("ahnali_bridge")
    status_label.text = err


def test_track_c_wave12_web_js_bridge_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WebView]),
            ui(
                text("status", id="status_label"),
                text("preview", id="preview_label"),
                button("Policy", id="policy_btn"),
                button("Bridge", id="bridge_btn"),
                button("Eval", id="eval_btn"),
            ),
            _policy_btn_handler,
            _bridge_btn_handler,
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
        "Lcom/ahnali/runtime/WebHelper;->addJsBridge("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->addJsBridgeError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave12_web_add_js_bridge_requires_webview_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Bridge", id="bridge_btn")),
            _bridge_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] web_add_js_bridge requires Caps\.WebView\."):
        prog.build()


def test_track_c_wave12_web_add_js_bridge_error_requires_webview_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), button("Eval", id="eval_only_btn")),
            _eval_only_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] web_add_js_bridge_error requires Caps\.WebView\."):
        prog.build()


def test_track_c_wave12_toolchain_emits_web_helper_js_bridge_methods(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WebView]),
            ui(button("Bridge", id="bridge_btn")),
            _bridge_btn_handler,
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
    assert ".method public static addJsBridge(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static addJsBridgeError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali


def test_track_c_wave12_parser_web_add_js_bridge_rejects_wrong_arity():
    def _bad():
        web_add_js_bridge("ahnali_bridge", "extra")

    with pytest.raises(RuntimeError, match="web_add_js_bridge expects exactly 1 string argument"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WebView]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave12_parser_web_add_js_bridge_rejects_non_string_name():
    def _bad():
        web_add_js_bridge(7)

    with pytest.raises(RuntimeError, match="web_add_js_bridge argument 'bridge_name' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WebView]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
