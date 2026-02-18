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
    web_choose_file_error,
    web_cookie_get,
    web_cookie_set,
)


@on_click("seed_btn")
def _seed_btn_handler():
    web_cookie_set("https://example.com", "ahnali=wave13")
    status_label.text = "Wave13 cookie seeded"


@on_click("run_btn")
def _run_btn_handler():
    choose_err = web_choose_file_error("*/*")
    cookie_value = web_cookie_get("https://example.com", "wave13-no-cookie")
    if choose_err == 0:
        preview_label.text = cookie_value
        status_label.text = "Wave13 file route"
    else:
        open_external("https://example.com/wave13-file-cookie-fallback")
        preview_label.text = "wave13-file-fallback"
        status_label.text = "Wave13 deterministic fallback"



def _build_wave13_visible_flow_frontend():
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


def test_track_c_wave13_visible_flow_lowers_file_cookie_with_deterministic_fallback():
    prog = _build_wave13_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/WebHelper;->chooseFileError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->setCookie("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WebHelper;->getCookie("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->openUri("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged

    assert "Wave13 deterministic fallback" in merged
    assert "wave13-file-fallback" in merged
    assert "https://example.com/wave13-file-cookie-fallback" in merged


def test_track_c_wave13_visible_flow_emits_web_and_sharing_helpers(tmp_path):
    frontend = _build_wave13_visible_flow_frontend()
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
