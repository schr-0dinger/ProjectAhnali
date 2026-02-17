from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    check_connectivity,
    http_async_body,
    http_async_error,
    http_async_json_field,
    http_async_json_field_error,
    http_async_progress,
    http_get_route_async,
    on_click,
    state,
    storage_get,
    storage_put,
    text,
    ui,
)


@on_click("seed_cache_btn")
def _seed_cache_btn_handler():
    storage_put("last_title", "cached-offline")
    status_label.text = "Cache seeded"


@on_click("start_btn")
def _start_btn_handler():
    check_connectivity()
    async_token = http_get_route_async(
        "https://example.com/data.json",
        "ok_btn",
        "fail_btn",
        "offline-payload",
        "progress_btn",
        1,
        2400,
        "POST",
        "X-Demo: wave5",
        "{\"mode\":\"demo\"}",
    )
    status_label.text = "Wave5 fetch started"


@on_click("progress_btn")
def _progress_btn_handler():
    p = http_async_progress(async_token)
    status_label.text = p


@on_click("ok_btn")
def _ok_btn_handler():
    title = http_async_json_field(async_token, "title", "cached-offline")
    code = http_async_json_field_error(async_token, "title")
    if code == 0:
        preview_label.text = title
        storage_put("last_status", "wave5-success")
        status_label.text = "Wave5 success"
    else:
        cached = storage_get("last_title", "cached-offline")
        preview_label.text = cached
        status_label.text = "Wave5 fallback cache"


@on_click("fail_btn")
def _fail_btn_handler():
    err = http_async_error(async_token)
    body = http_async_body(async_token, "offline-payload")
    cached = storage_get("last_title", "cached-offline")
    if err == 7:
        preview_label.text = cached
    else:
        preview_label.text = body
    status_label.text = "Wave5 deterministic fallback"


def _build_wave5_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage, Caps.Networking, Caps.Connectivity]),
            state(async_token=0),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Seed Cache", id="seed_cache_btn"),
                button("Start", id="start_btn"),
                button("Progress", id="progress_btn"),
                button("OK", id="ok_btn"),
                button("FAIL", id="fail_btn"),
            ),
            _seed_cache_btn_handler,
            _start_btn_handler,
            _progress_btn_handler,
            _ok_btn_handler,
            _fail_btn_handler,
        )
    ).build()


def test_track_c_wave5_visible_flow_lowers_network_storage_connectivity_with_deterministic_fallback():
    prog = _build_wave5_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Lcom/ahnali/runtime/ConnectivityHelper;->isConnected(Landroid/app/Activity;)I" in merged
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->putString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->getString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->startAsyncWithToken(ILjava/lang/Runnable;)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncJsonField(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncJsonFieldError(ILjava/lang/String;)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncError(I)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncBody(ILjava/lang/String;)Ljava/lang/String;" in merged

    assert "Lcom/ahnali/preview/AhnaliUiRunnable_ok_btn;" in merged
    assert "Lcom/ahnali/preview/AhnaliUiRunnable_fail_btn;" in merged
    assert "Lcom/ahnali/preview/AhnaliUiRunnable_progress_btn;" in merged

    assert "Wave5 fallback cache" in merged
    assert "Wave5 deterministic fallback" in merged
    assert "cached-offline" in merged
    assert "offline-payload" in merged


def test_track_c_wave5_visible_flow_emits_required_runtime_helpers(tmp_path):
    frontend = _build_wave5_visible_flow_frontend()
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
    assert (runtime_root / "StorageHelper.smali").exists()
    assert (runtime_root / "ConnectivityHelper.smali").exists()

    worker_smali = (preview_root / "AhnaliHttpRouteAsyncWorker.smali").read_text(encoding="utf-8")
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpRequestWithTimeout("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;"
    ) in worker_smali
