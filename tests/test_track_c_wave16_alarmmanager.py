import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    alarm_cancel,
    alarm_error,
    alarm_schedule,
    alarm_status,
    app,
    app_config,
    button,
    on_click,
    text,
    ui,
)


@on_click("schedule_btn")
def _schedule_btn_handler():
    alarm_schedule("sync_alarm", 15)


@on_click("cancel_btn")
def _cancel_btn_handler():
    alarm_cancel("sync_alarm")


@on_click("eval_btn")
def _eval_btn_handler():
    status = alarm_status("sync_alarm")
    err = alarm_error("sync_alarm")
    status_label.text = status
    error_label.text = err


def test_track_c_wave16_alarmmanager_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.AlarmManager]),
            ui(
                text("status", id="status_label"),
                text("error", id="error_label"),
                button("Schedule", id="schedule_btn"),
                button("Cancel", id="cancel_btn"),
                button("Eval", id="eval_btn"),
            ),
            _schedule_btn_handler,
            _cancel_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/AlarmHelper;->scheduleAlarm("
        "Landroid/app/Activity;Ljava/lang/String;I)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/AlarmHelper;->cancelAlarm("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/AlarmHelper;->getAlarmStatus("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/AlarmHelper;->getAlarmStatusError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave16_alarm_schedule_requires_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Schedule", id="schedule_btn")),
            _schedule_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] alarm_schedule requires Caps\.AlarmManager\."):
        prog.build()


def test_track_c_wave16_alarm_status_requires_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), text("error", id="error_label"), button("Eval", id="eval_btn")),
            _eval_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] alarm_status requires Caps\.AlarmManager\."):
        prog.build()


def test_track_c_wave16_toolchain_emits_alarm_helper_methods(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.AlarmManager]),
            ui(button("Schedule", id="schedule_btn")),
            _schedule_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "AlarmHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static scheduleAlarm(Landroid/app/Activity;Ljava/lang/String;I)I" in helper_smali
    assert ".method public static scheduleAlarmError(Landroid/app/Activity;Ljava/lang/String;I)I" in helper_smali
    assert ".method public static cancelAlarm(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static cancelAlarmError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static getAlarmStatus(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static getAlarmStatusError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali


def test_track_c_wave16_parser_alarm_schedule_rejects_negative_trigger():
    def _bad():
        alarm_schedule("sync_alarm", -3)

    with pytest.raises(RuntimeError, match="alarm_schedule argument 'trigger_seconds' must be >= 0"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.AlarmManager]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave16_parser_alarm_error_rejects_wrong_arity():
    def _bad():
        value = alarm_error()
        status_label.text = value

    with pytest.raises(RuntimeError, match="alarm_error expects exactly 1 string argument"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.AlarmManager]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
