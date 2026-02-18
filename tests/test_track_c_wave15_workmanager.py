import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    on_click,
    text,
    ui,
    work_cancel,
    work_enqueue,
    work_error,
    work_status,
)


@on_click("enqueue_btn")
def _enqueue_btn_handler():
    work_enqueue("sync_profile", 5)


@on_click("cancel_btn")
def _cancel_btn_handler():
    work_cancel("sync_profile")


@on_click("eval_btn")
def _eval_btn_handler():
    status = work_status("sync_profile")
    err = work_error("sync_profile")
    status_label.text = status
    error_label.text = err


def test_track_c_wave15_workmanager_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WorkManager]),
            ui(
                text("status", id="status_label"),
                text("error", id="error_label"),
                button("Enqueue", id="enqueue_btn"),
                button("Cancel", id="cancel_btn"),
                button("Eval", id="eval_btn"),
            ),
            _enqueue_btn_handler,
            _cancel_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/WorkHelper;->enqueueWork("
        "Landroid/app/Activity;Ljava/lang/String;I)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WorkHelper;->cancelWork("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WorkHelper;->getWorkStatus("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/WorkHelper;->getWorkStatusError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave15_work_enqueue_requires_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Enqueue", id="enqueue_btn")),
            _enqueue_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] work_enqueue requires Caps\.WorkManager\."):
        prog.build()


def test_track_c_wave15_work_status_requires_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), text("error", id="error_label"), button("Eval", id="eval_btn")),
            _eval_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] work_status requires Caps\.WorkManager\."):
        prog.build()


def test_track_c_wave15_toolchain_emits_work_helper_methods(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.WorkManager]),
            ui(button("Enqueue", id="enqueue_btn")),
            _enqueue_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "WorkHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static enqueueWork(Landroid/app/Activity;Ljava/lang/String;I)I" in helper_smali
    assert ".method public static enqueueWorkError(Landroid/app/Activity;Ljava/lang/String;I)I" in helper_smali
    assert ".method public static cancelWork(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static cancelWorkError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static getWorkStatus(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static getWorkStatusError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali


def test_track_c_wave15_parser_work_enqueue_rejects_negative_delay():
    def _bad():
        work_enqueue("sync_profile", -1)

    with pytest.raises(RuntimeError, match="work_enqueue argument 'delay_seconds' must be >= 0"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WorkManager]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave15_parser_work_status_rejects_non_string_name():
    def _bad():
        value = work_status(7)
        status_label.text = value

    with pytest.raises(RuntimeError, match="work_status argument 'name' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.WorkManager]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
