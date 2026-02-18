from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    alarm_schedule,
    alarm_status,
    app,
    app_config,
    button,
    job_schedule,
    job_status,
    on_click,
    open_url,
    text,
    ui,
    work_enqueue,
    work_status,
)


@on_click("seed_btn")
def _seed_btn_handler():
    work_enqueue("sync_profile", 3)
    alarm_schedule("sync_alarm", 7)
    job_schedule(11, 15)


@on_click("run_btn")
def _run_btn_handler():
    work_state = work_status("sync_profile")
    alarm_state = alarm_status("sync_alarm")
    job_state = job_status(11)
    total_state = work_state + alarm_state + job_state
    if total_state > 0:
        status_label.text = "Wave17 background scheduled"
        preview_label.text = total_state
    else:
        open_url("https://example.com/wave17-fallback")
        status_label.text = "Wave17 deterministic fallback"
        preview_label.text = "background-fallback"


def _build_wave17_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WorkManager, Caps.AlarmManager, Caps.JobScheduler, Caps.URLLauncher]),
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


def test_track_c_wave17_visible_flow_lowers_background_work_with_deterministic_fallback():
    prog = _build_wave17_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Lcom/ahnali/runtime/WorkHelper;->enqueueWork(Landroid/app/Activity;Ljava/lang/String;I)I" in merged
    assert "Lcom/ahnali/runtime/AlarmHelper;->scheduleAlarm(Landroid/app/Activity;Ljava/lang/String;I)I" in merged
    assert "Lcom/ahnali/runtime/JobHelper;->scheduleJob(Landroid/app/Activity;II)I" in merged
    assert "Lcom/ahnali/runtime/WorkHelper;->getWorkStatus(Landroid/app/Activity;Ljava/lang/String;)I" in merged
    assert "Lcom/ahnali/runtime/AlarmHelper;->getAlarmStatus(Landroid/app/Activity;Ljava/lang/String;)I" in merged
    assert "Lcom/ahnali/runtime/JobHelper;->getJobStatus(Landroid/app/Activity;I)I" in merged
    assert "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl(Landroid/app/Activity;Ljava/lang/String;)I" in merged
    assert "Wave17 deterministic fallback" in merged
    assert "https://example.com/wave17-fallback" in merged


def test_track_c_wave17_visible_flow_emits_background_helpers(tmp_path):
    frontend = _build_wave17_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (runtime_root / "WorkHelper.smali").exists()
    assert (runtime_root / "AlarmHelper.smali").exists()
    assert (runtime_root / "JobHelper.smali").exists()
    assert (runtime_root / "UrlLauncherHelper.smali").exists()
