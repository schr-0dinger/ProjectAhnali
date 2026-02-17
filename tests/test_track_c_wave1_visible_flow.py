from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    check_connectivity,
    on_click,
    open_url,
    storage_get,
    storage_put,
    storage_remove,
    text,
    ui,
)


@on_click("save_btn")
def _save_btn_handler():
    storage_put("homepage", "https://example.com")
    status_label.text = "Saved URL"


@on_click("load_btn")
def _load_btn_handler():
    homepage = storage_get("homepage", "https://example.com")
    preview_label.text = homepage
    status_label.text = "Loaded URL"


@on_click("clear_btn")
def _clear_btn_handler():
    storage_remove("homepage")
    preview_label.text = "(cleared)"
    status_label.text = "Cleared URL"


@on_click("check_btn")
def _check_btn_handler():
    check_connectivity()
    status_label.text = "Connectivity checked"


@on_click("open_btn")
def _open_btn_handler():
    open_url("https://example.com")
    status_label.text = "Opening browser"


def _build_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.URLLauncher, Caps.Connectivity, Caps.Storage]),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Save URL", id="save_btn"),
                button("Load URL", id="load_btn"),
                button("Clear URL", id="clear_btn"),
                button("Check Connectivity", id="check_btn"),
                button("Open URL", id="open_btn"),
            ),
            _save_btn_handler,
            _load_btn_handler,
            _clear_btn_handler,
            _check_btn_handler,
            _open_btn_handler,
        )
    ).build()


def test_track_c_wave1_visible_flow_lowers_all_helper_calls_and_visible_text_updates():
    prog = _build_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/StorageHelper;->putString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in merged
    assert "Lcom/ahnali/runtime/StorageHelper;->getString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in merged
    assert "Lcom/ahnali/runtime/StorageHelper;->remove(Landroid/app/Activity;Ljava/lang/String;)I" in merged
    assert "Lcom/ahnali/runtime/ConnectivityHelper;->isConnected(Landroid/app/Activity;)I" in merged
    assert "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl(Landroid/app/Activity;Ljava/lang/String;)I" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_track_c_wave1_visible_flow_emits_all_wave1_runtime_helpers(tmp_path):
    frontend = _build_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    smali_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (smali_root / "StorageHelper.smali").exists()
    assert (smali_root / "ConnectivityHelper.smali").exists()
    assert (smali_root / "UrlLauncherHelper.smali").exists()
