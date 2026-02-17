import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    http_async_cancel,
    http_async_error,
    http_async_progress,
    http_get_route_async,
    on_click,
    text,
    ui,
)


@on_click("probe_btn")
def _probe_btn_handler():
    http_get_route_async("https://example.com/health", "probe_ok_btn", "probe_fail_btn", "offline")


@on_click("probe_ok_btn")
def _probe_ok_btn_handler():
    status_label.text = "Async route: success"


@on_click("probe_fail_btn")
def _probe_fail_btn_handler():
    status_label.text = "Async route: fallback"


@on_click("cancel_btn")
def _cancel_btn_handler():
    http_async_cancel()
    status_label.text = "Cancel requested"


@on_click("progress_btn")
def _progress_btn_handler():
    p = http_async_progress()
    status_label.text = p


@on_click("error_btn")
def _error_btn_handler():
    e = http_async_error()
    status_label.text = e


def test_track_c_wave3_async_route_lowers_to_async_helper_and_runnable_support_classes():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("ready", id="status_label"),
                button("Probe", id="probe_btn"),
                button("OK", id="probe_ok_btn"),
                button("FAIL", id="probe_fail_btn"),
            ),
            _probe_btn_handler,
            _probe_ok_btn_handler,
            _probe_fail_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->startAsync("
        "Ljava/lang/Runnable;)I"
    ) in merged
    assert "Lcom/ahnali/preview/AhnaliHttpRouteAsyncWorker;" in merged
    assert "Lcom/ahnali/preview/AhnaliUiRunnable_probe_ok_btn;" in merged
    assert "Lcom/ahnali/preview/AhnaliUiRunnable_probe_fail_btn;" in merged

    support_entries = list(result.get("support_classes", []))
    assert (
        "Lcom/ahnali/preview/AhnaliHttpRouteAsyncWorker;",
        "",
        "LTestHandlers;",
        "http_route_async_worker",
    ) in support_entries
    assert (
        "Lcom/ahnali/preview/AhnaliUiRunnable_probe_ok_btn;",
        "onClick_probe_ok_btn",
        "LTestHandlers;",
        "ui_runnable_click",
    ) in support_entries
    assert (
        "Lcom/ahnali/preview/AhnaliUiRunnable_probe_fail_btn;",
        "onClick_probe_fail_btn",
        "LTestHandlers;",
        "ui_runnable_click",
    ) in support_entries


def test_track_c_wave3_async_route_requires_networking_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("ready", id="status_label"),
                button("Probe", id="probe_btn"),
                button("OK", id="probe_ok_btn"),
                button("FAIL", id="probe_fail_btn"),
            ),
            _probe_btn_handler,
            _probe_ok_btn_handler,
            _probe_fail_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Networking capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] http_get_route_async requires Caps.Networking." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Networking]) to activity(...)." in str(exc)


def test_track_c_wave3_async_cancel_progress_error_require_networking_capability():
    prog_cancel = app(
        activity(
            "MainActivity",
            ui(
                text("ready", id="status_label"),
                button("Cancel", id="cancel_btn"),
            ),
            _cancel_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] http_async_cancel requires Caps\.Networking\."):
        prog_cancel.build()

    prog_progress = app(
        activity(
            "MainActivity",
            ui(
                text("ready", id="status_label"),
                button("Progress", id="progress_btn"),
            ),
            _progress_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] http_async_progress requires Caps\.Networking\."):
        prog_progress.build()

    prog_error = app(
        activity(
            "MainActivity",
            ui(
                text("ready", id="status_label"),
                button("Error", id="error_btn"),
            ),
            _error_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] http_async_error requires Caps\.Networking\."):
        prog_error.build()


def test_track_c_wave3_async_route_rejects_unknown_handler_target():
    @on_click("probe_btn_missing")
    def _probe_missing_handler():
        http_get_route_async("https://example.com/health", "missing_ok", "probe_fail_btn", "offline")

    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("ready", id="status_label"),
                button("Probe", id="probe_btn_missing"),
                button("FAIL", id="probe_fail_btn"),
            ),
            _probe_missing_handler,
            _probe_fail_btn_handler,
        )
    )
    with pytest.raises(
        RuntimeError,
        match="http_get_route_async argument 'success_target_id' references unknown on_click target",
    ):
        prog.build()


def test_track_c_wave3_parser_http_get_route_async_rejects_wrong_arity():
    def _bad():
        http_get_route_async("https://example.com/health", "probe_ok_btn")

    with pytest.raises(RuntimeError, match="http_get_route_async expects 3 or 4 string arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(
                    text("ready", id="status_label"),
                    button("Probe", id="probe_btn_bad_arity"),
                    button("OK", id="probe_ok_btn"),
                    button("FAIL", id="probe_fail_btn"),
                ),
                on_click("probe_btn_bad_arity")(_bad),
                _probe_ok_btn_handler,
                _probe_fail_btn_handler,
            )
        ).build()


def test_track_c_wave3_parser_http_get_route_async_rejects_non_string_url():
    def _bad():
        http_get_route_async(7, "probe_ok_btn", "probe_fail_btn", "offline")

    with pytest.raises(RuntimeError, match="http_get_route_async argument 'url' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(
                    text("ready", id="status_label"),
                    button("Probe", id="probe_btn_bad_url"),
                    button("OK", id="probe_ok_btn"),
                    button("FAIL", id="probe_fail_btn"),
                ),
                on_click("probe_btn_bad_url")(_bad),
                _probe_ok_btn_handler,
                _probe_fail_btn_handler,
            )
        ).build()


def test_track_c_wave3_parser_http_async_cancel_progress_error_reject_args():
    def _bad_cancel():
        http_async_cancel(1)

    with pytest.raises(RuntimeError, match="http_async_cancel expects no arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(
                    text("ready", id="status_label"),
                    button("Cancel", id="cancel_bad_btn"),
                ),
                on_click("cancel_bad_btn")(_bad_cancel),
            )
        ).build()

    def _bad_progress():
        p = http_async_progress(1)
        status_label.text = p

    with pytest.raises(RuntimeError, match="http_async_progress expects no arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(
                    text("ready", id="status_label"),
                    button("Progress", id="progress_bad_btn"),
                ),
                on_click("progress_bad_btn")(_bad_progress),
            )
        ).build()

    def _bad_error():
        e = http_async_error(1)
        status_label.text = e

    with pytest.raises(RuntimeError, match="http_async_error expects no arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Networking]),
                ui(
                    text("ready", id="status_label"),
                    button("Error", id="error_bad_btn"),
                ),
                on_click("error_bad_btn")(_bad_error),
            )
        ).build()


def test_track_c_wave3_async_cancel_progress_error_lower_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("ready", id="status_label"),
                button("Cancel", id="cancel_btn"),
                button("Progress", id="progress_btn"),
                button("Error", id="error_btn"),
            ),
            _cancel_btn_handler,
            _progress_btn_handler,
            _error_btn_handler,
        )
    ).build()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/HttpHelper;->cancelAsync()I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncProgress()I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncError()I" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_track_c_wave3_toolchain_emits_async_route_support_classes_and_http_helper_async_method(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking]),
            ui(
                text("ready", id="status_label"),
                button("Probe", id="probe_btn"),
                button("OK", id="probe_ok_btn"),
                button("FAIL", id="probe_fail_btn"),
            ),
            _probe_btn_handler,
            _probe_ok_btn_handler,
            _probe_fail_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    preview_root = out_dir / "smali" / "com" / "ahnali" / "preview"
    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    worker_path = preview_root / "AhnaliHttpRouteAsyncWorker.smali"
    success_runnable = preview_root / "AhnaliUiRunnable_probe_ok_btn.smali"
    failure_runnable = preview_root / "AhnaliUiRunnable_probe_fail_btn.smali"
    helper_path = runtime_root / "HttpHelper.smali"

    assert worker_path.exists()
    assert success_runnable.exists()
    assert failure_runnable.exists()
    assert helper_path.exists()

    worker_smali = worker_path.read_text(encoding="utf-8")
    assert ".implements Ljava/lang/Runnable;" in worker_smali
    assert "Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V" in worker_smali
    assert "Lcom/ahnali/runtime/HttpHelper;->httpGetStatus(Landroid/app/Activity;Ljava/lang/String;)I" in worker_smali
    assert "Lcom/ahnali/runtime/HttpHelper;->httpGetError(Landroid/app/Activity;Ljava/lang/String;)I" in worker_smali
    assert "Lcom/ahnali/runtime/HttpHelper;->setAsyncProgress(I)V" in worker_smali
    assert "Lcom/ahnali/runtime/HttpHelper;->setAsyncError(I)V" in worker_smali
    assert "Lcom/ahnali/runtime/HttpHelper;->shouldCancel()I" in worker_smali

    success_smali = success_runnable.read_text(encoding="utf-8")
    assert ".implements Ljava/lang/Runnable;" in success_smali
    assert "LTestHandlers;->onClick_probe_ok_btn(Landroid/view/View;)V" in success_smali

    failure_smali = failure_runnable.read_text(encoding="utf-8")
    assert ".implements Ljava/lang/Runnable;" in failure_smali
    assert "LTestHandlers;->onClick_probe_fail_btn(Landroid/view/View;)V" in failure_smali

    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static startAsync(Ljava/lang/Runnable;)I" in helper_smali
    assert ".method public static cancelAsync()I" in helper_smali
    assert ".method public static shouldCancel()I" in helper_smali
    assert ".method public static setAsyncProgress(I)V" in helper_smali
    assert ".method public static getAsyncProgress()I" in helper_smali
    assert ".method public static setAsyncError(I)V" in helper_smali
    assert ".method public static getAsyncError()I" in helper_smali
    assert ".field private static sAsyncCancel:I" in helper_smali
    assert ".field private static sAsyncProgress:I" in helper_smali
    assert ".field private static sAsyncError:I" in helper_smali
    assert "Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V" in helper_smali
    assert "Ljava/lang/Thread;->start()V" in helper_smali
    assert "const/4 v5, 0x7" in worker_smali
