from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    http_async_body,
    http_async_cancel,
    http_async_error,
    http_async_progress,
    http_async_status,
    http_get_route_async,
    on_click,
    open_url,
    state,
    text,
    ui,
)


@on_click("start_btn")
def _start_btn_handler():
    async_token = http_get_route_async(
        "https://example.com/health",
        "ok_btn",
        "fail_btn",
        "offline",
        "progress_btn",
        2,
        2500,
    )
    status_label.text = "Async started"


@on_click("progress_btn")
def _progress_btn_handler():
    p = http_async_progress(async_token)
    status_label.text = p


@on_click("cancel_btn")
def _cancel_btn_handler():
    http_async_cancel(async_token)
    status_label.text = "Cancel requested"


@on_click("ok_btn")
def _ok_btn_handler():
    code = http_async_status(async_token)
    body = http_async_body(async_token, "offline")
    err = http_async_error(async_token)
    preview_label.text = body
    if err == 0:
        status_label.text = "Async success"
    else:
        status_label.text = code


@on_click("fail_btn")
def _fail_btn_handler():
    err = http_async_error(async_token)
    body = http_async_body(async_token, "offline")
    preview_label.text = body
    if err == 7:
        status_label.text = "Async cancelled"
    else:
        status_label.text = "Async failed"
    open_url("https://example.com/help")


def _build_wave3_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Networking, Caps.URLLauncher]),
            state(async_token=0),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Start Async", id="start_btn"),
                button("Progress", id="progress_btn"),
                button("Cancel", id="cancel_btn"),
                button("OK", id="ok_btn"),
                button("FAIL", id="fail_btn"),
            ),
            _start_btn_handler,
            _progress_btn_handler,
            _cancel_btn_handler,
            _ok_btn_handler,
            _fail_btn_handler,
        )
    ).build()


def test_track_c_wave3_visible_flow_lowers_tokened_async_routing_and_fallback_ui_updates():
    prog = _build_wave3_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Lcom/ahnali/runtime/HttpHelper;->nextAsyncToken()I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->startAsyncWithToken(ILjava/lang/Runnable;)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->cancelAsync(I)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncProgress(I)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncStatus(I)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncError(I)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncBody(ILjava/lang/String;)Ljava/lang/String;" in merged
    assert "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl(Landroid/app/Activity;Ljava/lang/String;)I" in merged

    assert "Lcom/ahnali/preview/AhnaliUiRunnable_ok_btn;" in merged
    assert "Lcom/ahnali/preview/AhnaliUiRunnable_fail_btn;" in merged
    assert "Lcom/ahnali/preview/AhnaliUiRunnable_progress_btn;" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged
    assert "Async cancelled" in merged
    assert "offline" in merged


def test_track_c_wave3_visible_flow_emits_worker_and_runtime_helpers(tmp_path):
    frontend = _build_wave3_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    preview_root = out_dir / "smali" / "com" / "ahnali" / "preview"
    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"

    assert (preview_root / "AhnaliHttpRouteAsyncWorker.smali").exists()
    assert (preview_root / "AhnaliUiRunnable_progress_btn.smali").exists()
    assert (runtime_root / "HttpHelper.smali").exists()
    assert (runtime_root / "UrlLauncherHelper.smali").exists()
