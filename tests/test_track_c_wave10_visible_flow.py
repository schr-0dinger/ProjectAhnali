from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    clipboard_get,
    clipboard_set,
    on_click,
    open_external,
    share_text_error,
    text,
    ui,
)


@on_click("seed_btn")
def _seed_btn_handler():
    clipboard_set("wave10 clipboard payload")
    status_label.text = "Wave10 seed ready"


@on_click("run_btn")
def _run_btn_handler():
    err = share_text_error("Wave10 share payload", "Ahnali Share")
    clip = clipboard_get("wave10-fallback")
    if err == 0:
        preview_label.text = clip
        status_label.text = "Wave10 share route"
    else:
        open_external("https://example.com/wave10-fallback")
        preview_label.text = "share-fallback"
        status_label.text = "Wave10 deterministic fallback"



def _build_wave10_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Sharing, Caps.Clipboard]),
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


def test_track_c_wave10_visible_flow_lowers_sharing_clipboard_with_deterministic_fallback():
    prog = _build_wave10_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/ShareHelper;->shareTextError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->openUri("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ClipboardHelper;->setText("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ClipboardHelper;->getText("
        "Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged

    assert "Wave10 deterministic fallback" in merged
    assert "wave10 clipboard payload" in merged
    assert "https://example.com/wave10-fallback" in merged


def test_track_c_wave10_visible_flow_emits_sharing_clipboard_helpers(tmp_path):
    frontend = _build_wave10_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (runtime_root / "ShareHelper.smali").exists()
    assert (runtime_root / "ClipboardHelper.smali").exists()
