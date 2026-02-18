from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    on_click,
    open_external,
    text,
    ui,
    web_add_js_bridge_error,
    web_add_js_bridge_result,
    web_set_policy,
)


@on_click("seed_btn")
def _seed_btn_handler():
    web_set_policy(0, 1, 0, 0)
    status_label.text = "Wave12 JS bridge policy ready"


@on_click("run_btn")
def _run_btn_handler():
    err = web_add_js_bridge_error("ahnali_bridge")
    if err == 0:
        bridge_ok = web_add_js_bridge_result("ahnali_bridge")
        preview_label.text = bridge_ok
        status_label.text = "Wave12 js bridge route"
    else:
        open_external("https://example.com/wave12-js-bridge-fallback")
        preview_label.text = "js-bridge-policy-blocked"
        status_label.text = "Wave12 deterministic fallback"



def _build_wave12_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WebView, Caps.Sharing]),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Seed", id="seed_btn"),
                button("Run", id="run_btn"),
            ),
            _seed_btn_handler,
            _run_btn_handler,
        )
    ).build()


def test_track_c_wave12_visible_flow_lowers_web_js_bridge_with_deterministic_fallback():
    prog = _build_wave12_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/WebHelper;->setPolicy("
        "Landroid/app/Activity;IIII)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->addJsBridgeError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->addJsBridge("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->openUri("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged

    assert "Wave12 deterministic fallback" in merged
    assert "ahnali_bridge" in merged
    assert "https://example.com/wave12-js-bridge-fallback" in merged


def test_track_c_wave12_visible_flow_emits_web_and_sharing_helpers(tmp_path):
    frontend = _build_wave12_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (runtime_root / "WebHelper.smali").exists()
    assert (runtime_root / "ShareHelper.smali").exists()
