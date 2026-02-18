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
    web_load_error,
    web_load_result,
    web_set_policy,
)


@on_click("seed_btn")
def _seed_btn_handler():
    web_set_policy(1, 1, 0, 0)
    status_label.text = "Wave11 policy ready"


@on_click("run_btn")
def _run_btn_handler():
    err = web_load_error("http://example.com/wave11-cleartext")
    if err == 0:
        payload = web_load_result("https://example.com/wave11")
        preview_label.text = payload
        status_label.text = "Wave11 web route"
    else:
        open_external("https://example.com/wave11-fallback")
        preview_label.text = "web-policy-blocked"
        status_label.text = "Wave11 deterministic fallback"



def _build_wave11_visible_flow_frontend():
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


def test_track_c_wave11_visible_flow_lowers_web_with_deterministic_policy_fallback():
    prog = _build_wave11_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/WebHelper;->setPolicy("
        "Landroid/app/Activity;IIII)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->loadUrlError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->loadUrl("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->openUri("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged

    assert "Wave11 deterministic fallback" in merged
    assert "http://example.com/wave11-cleartext" in merged
    assert "https://example.com/wave11-fallback" in merged


def test_track_c_wave11_visible_flow_emits_web_and_sharing_helpers(tmp_path):
    frontend = _build_wave11_visible_flow_frontend()
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
