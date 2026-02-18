from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    create_notification_channel,
    notify_error,
    on_click,
    open_url,
    storage_get,
    storage_put,
    text,
    ui,
)


@on_click("seed_btn")
def _seed_btn_handler():
    create_notification_channel("ahnali_wave8", "Ahnali Wave 8")
    storage_put("notify_fallback", "notification-fallback")
    status_label.text = "Wave8 channel seeded"


@on_click("notify_btn")
def _notify_btn_handler():
    err = notify_error("Wave8", "Hello from Ahnali", "ahnali_wave8")
    if err == 0:
        open_url("https://example.com/notify-ok")
        preview_label.text = "notify-ready"
        status_label.text = "Wave8 notification delivered"
    else:
        hint = storage_get("notify_fallback", "notify-fallback")
        preview_label.text = hint
        status_label.text = "Wave8 deterministic fallback"



def _build_wave8_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Notifications, Caps.Storage, Caps.URLLauncher]),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Seed", id="seed_btn"),
                button("Notify", id="notify_btn"),
            ),
            _seed_btn_handler,
            _notify_btn_handler,
        )
    ).build()


def test_track_c_wave8_visible_flow_lowers_notifications_storage_url_launcher_with_deterministic_fallback():
    prog = _build_wave8_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/NotificationHelper;->postNotificationError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/NotificationHelper;->createChannel("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->putString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->getString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl(Landroid/app/Activity;Ljava/lang/String;)I" in merged

    assert "Wave8 deterministic fallback" in merged
    assert "notification-fallback" in merged
    assert "https://example.com/notify-ok" in merged


def test_track_c_wave8_visible_flow_emits_notifications_storage_url_launcher_helpers(tmp_path):
    frontend = _build_wave8_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (runtime_root / "NotificationHelper.smali").exists()
    assert (runtime_root / "StorageHelper.smali").exists()
    assert (runtime_root / "UrlLauncherHelper.smali").exists()
