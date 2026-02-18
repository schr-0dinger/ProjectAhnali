import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    create_notification_channel,
    notify,
    notify_error,
    notify_result,
    on_click,
    text,
    ui,
)


@on_click("notify_btn")
def _notify_btn_handler():
    create_notification_channel("ahnali_wave8", "Ahnali Wave 8")
    notify("Wave8", "Hello from Ahnali", "ahnali_wave8")


@on_click("eval_btn")
def _eval_btn_handler():
    result = notify_result("Wave8", "Hello from Ahnali", "ahnali_wave8")
    err = notify_error("Wave8", "Hello from Ahnali", "ahnali_wave8")
    preview_label.text = result
    status_label.text = err


def test_track_c_wave8_notifications_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Notifications]),
            ui(
                text("status", id="status_label"),
                text("preview", id="preview_label"),
                button("Notify", id="notify_btn"),
                button("Eval", id="eval_btn"),
            ),
            _notify_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/NotificationHelper;->createChannel("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/NotificationHelper;->postNotification("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/NotificationHelper;->postNotificationError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave8_notify_result_requires_notifications_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), text("preview", id="preview_label"), button("Eval", id="eval_btn")),
            _eval_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] notify_result requires Caps\.Notifications\."):
        prog.build()


def test_track_c_wave8_create_channel_requires_notifications_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Notify", id="notify_btn")),
            _notify_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] create_notification_channel requires Caps\.Notifications\."):
        prog.build()


def test_track_c_wave8_toolchain_emits_notification_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Notifications]),
            ui(button("Notify", id="notify_btn")),
            _notify_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "NotificationHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static createChannel(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert (
        ".method public static postNotification(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
        in helper_smali
    )
    assert (
        ".method public static postNotificationError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
        in helper_smali
    )


def test_track_c_wave8_parser_notify_rejects_wrong_arity():
    def _bad():
        notify("only-title")

    with pytest.raises(RuntimeError, match="notify expects 2 or 3 string arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Notifications]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave8_parser_notify_result_rejects_non_string_body():
    def _bad():
        value = notify_result("title", 7, "ahnali_wave8")
        status_label.text = value

    with pytest.raises(RuntimeError, match="notify_result argument 'body' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Notifications]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave8_parser_create_channel_rejects_non_string_name():
    def _bad():
        create_notification_channel("ahnali_wave8", 9)

    with pytest.raises(
        RuntimeError,
        match="create_notification_channel argument 'channel_name' must be a constant string",
    ):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Notifications]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
