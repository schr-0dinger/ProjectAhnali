from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    http_get_route,
    on_click,
    open_url,
    storage_get,
    storage_put,
    text,
    ui,
)


@on_click("save_btn")
def _save_btn_handler():
    storage_put("homepage", "https://example.com")
    status_label.text = "Saved URL"


@on_click("load_btn")
def _load_btn_handler():
    homepage = storage_get("homepage", "https://fallback.example")
    preview_label.text = homepage
    status_label.text = "Loaded URL"


@on_click("probe_btn")
def _probe_btn_handler():
    http_get_route("https://example.com/health", "probe_ok_btn", "probe_fail_btn", "offline")


@on_click("probe_ok_btn")
def _probe_ok_btn_handler():
    status_label.text = "Network route: success"


@on_click("probe_fail_btn")
def _probe_fail_btn_handler():
    preview_label.text = "offline"
    status_label.text = "Network route: fallback"


@on_click("open_btn")
def _open_btn_handler():
    open_url("https://example.com")
    status_label.text = "Opening browser"


def _build_wave2_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage, Caps.Networking, Caps.URLLauncher]),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Save URL", id="save_btn"),
                button("Load URL", id="load_btn"),
                button("Probe Route", id="probe_btn"),
                button("Open URL", id="open_btn"),
                button("Route Success", id="probe_ok_btn"),
                button("Route Fallback", id="probe_fail_btn"),
            ),
            _save_btn_handler,
            _load_btn_handler,
            _probe_btn_handler,
            _probe_ok_btn_handler,
            _probe_fail_btn_handler,
            _open_btn_handler,
        )
    ).build()


def test_track_c_wave2_visible_flow_lowers_storage_network_route_url_with_visible_fallback_branch():
    prog = _build_wave2_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/StorageHelper;->putString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->getString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetStatus("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGet("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpGetError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged

    # Route branch wiring is deterministic: both success and fallback handlers are emitted.
    assert "LTestHandlers;->onClick_probe_ok_btn(Landroid/view/View;)V" in merged
    assert "LTestHandlers;->onClick_probe_fail_btn(Landroid/view/View;)V" in merged

    # Visible UI updates in handlers.
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged
    assert "Network route: fallback" in merged
    assert "offline" in merged


def test_track_c_wave2_visible_flow_emits_storage_networking_urllauncher_helpers(tmp_path):
    frontend = _build_wave2_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    smali_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (smali_root / "StorageHelper.smali").exists()
    assert (smali_root / "HttpHelper.smali").exists()
    assert (smali_root / "UrlLauncherHelper.smali").exists()
