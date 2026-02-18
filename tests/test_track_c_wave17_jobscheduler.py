import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    job_cancel,
    job_error,
    job_schedule,
    job_status,
    on_click,
    text,
    ui,
)


@on_click("schedule_btn")
def _schedule_btn_handler():
    job_schedule(7, 30)


@on_click("cancel_btn")
def _cancel_btn_handler():
    job_cancel(7)


@on_click("eval_btn")
def _eval_btn_handler():
    status = job_status(7)
    err = job_error(7)
    status_label.text = status
    error_label.text = err


def test_track_c_wave17_jobscheduler_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.JobScheduler]),
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
        "Lcom/ahnali/runtime/JobHelper;->scheduleJob("
        "Landroid/app/Activity;II)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/JobHelper;->cancelJob("
        "Landroid/app/Activity;I)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/JobHelper;->getJobStatus("
        "Landroid/app/Activity;I)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/JobHelper;->getJobStatusError("
        "Landroid/app/Activity;I)I"
    ) in merged


def test_track_c_wave17_job_schedule_requires_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Schedule", id="schedule_btn")),
            _schedule_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] job_schedule requires Caps\.JobScheduler\."):
        prog.build()


def test_track_c_wave17_job_status_requires_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), text("error", id="error_label"), button("Eval", id="eval_btn")),
            _eval_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] job_status requires Caps\.JobScheduler\."):
        prog.build()


def test_track_c_wave17_toolchain_emits_job_helper_methods_with_api_guard(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.JobScheduler]),
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
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "JobHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static scheduleJob(Landroid/app/Activity;II)I" in helper_smali
    assert ".method public static scheduleJobError(Landroid/app/Activity;II)I" in helper_smali
    assert ".method public static cancelJob(Landroid/app/Activity;I)I" in helper_smali
    assert ".method public static cancelJobError(Landroid/app/Activity;I)I" in helper_smali
    assert ".method public static getJobStatus(Landroid/app/Activity;I)I" in helper_smali
    assert ".method public static getJobStatusError(Landroid/app/Activity;I)I" in helper_smali
    assert "Landroid/os/Build$VERSION;->SDK_INT:I" in helper_smali


def test_track_c_wave17_parser_job_schedule_rejects_non_positive_id():
    def _bad():
        job_schedule(0, 10)

    with pytest.raises(RuntimeError, match="job_schedule argument 'job_id' must be > 0"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.JobScheduler]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave17_parser_job_error_rejects_non_int():
    def _bad():
        value = job_error("x")
        status_label.text = value

    with pytest.raises(RuntimeError, match="job_error argument 'job_id' must be a constant integer"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.JobScheduler]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
