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
    open_external_result,
    share_file,
    share_file_error,
    share_file_result,
    text,
    ui,
)


@on_click("run_btn")
def _run_btn_handler():
    ok = share_file_result("content://ahnali/wave18", "Share file via", "text/plain")
    err = share_file_error("content://ahnali/wave18", "Share file via", "text/plain")
    open_ok = open_external_result("https://example.com/wave18")
    total = ok + open_ok
    if err == 0:
        status_label.text = "Wave18 file-share route"
        preview_label.text = total
    else:
        open_external("https://example.com/wave18-fallback")
        status_label.text = "Wave18 deterministic fallback"
        preview_label.text = "share-file-fallback"


def _build_wave18_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Sharing]),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Run", id="run_btn"),
            ),
            _run_btn_handler,
        )
    ).build()


def test_track_c_wave18_visible_flow_lowers_share_file_with_deterministic_fallback():
    prog = _build_wave18_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/ShareHelper;->shareFile("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->shareFileError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->openUri("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert "Wave18 deterministic fallback" in merged
    assert "https://example.com/wave18-fallback" in merged


def test_track_c_wave18_visible_flow_emits_share_helper(tmp_path):
    frontend = _build_wave18_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (runtime_root / "ShareHelper.smali").exists()
