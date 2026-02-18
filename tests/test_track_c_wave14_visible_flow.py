from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    deep_link_error,
    deep_link_get,
    on_click,
    open_url,
    text,
    ui,
)


@on_click("run_btn")
def _run_btn_handler():
    link = deep_link_get("ahnali://fallback")
    err = deep_link_error()
    if err == 0:
        preview_label.text = link
        status_label.text = "Wave14 deep-link route"
    else:
        open_url("https://example.com/wave14-fallback")
        preview_label.text = "deep-link-fallback"
        status_label.text = "Wave14 deterministic fallback"


def _build_wave14_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.DeepLinking, Caps.URLLauncher]),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Run", id="run_btn"),
            ),
            _run_btn_handler,
        )
    ).build()


def test_track_c_wave14_visible_flow_lowers_deep_link_with_deterministic_fallback():
    prog = _build_wave14_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/DeepLinkHelper;->getLaunchUri("
        "Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/DeepLinkHelper;->getLaunchUriError("
        "Landroid/app/Activity;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert "Wave14 deterministic fallback" in merged
    assert "https://example.com/wave14-fallback" in merged


def test_track_c_wave14_visible_flow_emits_deep_link_and_url_helpers(tmp_path):
    frontend = _build_wave14_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (runtime_root / "DeepLinkHelper.smali").exists()
    assert (runtime_root / "UrlLauncherHelper.smali").exists()
