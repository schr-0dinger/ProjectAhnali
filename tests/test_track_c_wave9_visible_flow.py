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
    create_notification_channel,
    notify_error,
    on_click,
    open_url,
    text,
    ui,
)


@on_click("seed_btn")
def _seed_btn_handler():
    create_notification_channel("ahnali_wave9", "Ahnali Wave 9")
    clipboard_set("https://example.com/wave9-clipboard")
    status_label.text = "Wave9 clipboard seeded"


@on_click("run_btn")
def _run_btn_handler():
    err = notify_error("Wave9", "Clipboard route", "ahnali_wave9")
    link = clipboard_get("https://example.com/wave9-fallback")
    if err == 0:
        open_url("https://example.com/wave9-clipboard-route")
        preview_label.text = link
        status_label.text = "Wave9 clipboard route"
    else:
        open_url("https://example.com/wave9-notify-fallback")
        preview_label.text = "notify-fallback"
        status_label.text = "Wave9 deterministic fallback"



def _build_wave9_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Clipboard, Caps.Notifications, Caps.URLLauncher]),
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


def test_track_c_wave9_visible_flow_lowers_clipboard_notifications_url_launcher_with_deterministic_fallback():
    prog = _build_wave9_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/ClipboardHelper;->setText("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ClipboardHelper;->getText("
        "Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/NotificationHelper;->postNotificationError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl(Landroid/app/Activity;Ljava/lang/String;)I" in merged

    assert "https://example.com/wave9-clipboard-route" in merged
    assert "https://example.com/wave9-notify-fallback" in merged
    assert "Wave9 deterministic fallback" in merged


def test_track_c_wave9_visible_flow_emits_clipboard_notifications_url_launcher_helpers(tmp_path):
    frontend = _build_wave9_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (runtime_root / "ClipboardHelper.smali").exists()
    assert (runtime_root / "NotificationHelper.smali").exists()
    assert (runtime_root / "UrlLauncherHelper.smali").exists()
