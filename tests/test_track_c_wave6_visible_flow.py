from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    http_async_body,
    http_async_error,
    http_async_json_field,
    http_get_route_async,
    location_enabled,
    on_click,
    state,
    storage_get,
    storage_put,
    text,
    ui,
)


@on_click("seed_btn")
def _seed_btn_handler():
    storage_put("nearby_hint", "No location. Showing cached results.")
    status_label.text = "Wave6 cache seeded"


@on_click("start_btn")
def _start_btn_handler():
    async_token = http_get_route_async(
        "https://example.com/nearby.json",
        "ok_btn",
        "fail_btn",
        "offline-body",
        "progress_btn",
        1,
        2400,
        "GET",
        "",
        "",
    )
    status_label.text = "Wave6 request started"


@on_click("ok_btn")
def _ok_btn_handler():
    loc = location_enabled()
    if loc == 1:
        title = http_async_json_field(async_token, "title", "offline-title")
        preview_label.text = title
        status_label.text = "Wave6 location success"
    else:
        cached = storage_get("nearby_hint", "No location fallback")
        preview_label.text = cached
        status_label.text = "Wave6 location fallback"


@on_click("progress_btn")
def _progress_btn_handler():
    status_label.text = "Wave6 progress ping"


@on_click("fail_btn")
def _fail_btn_handler():
    err = http_async_error(async_token)
    body = http_async_body(async_token, "offline-body")
    if err == 7:
        cached = storage_get("nearby_hint", "No location fallback")
        preview_label.text = cached
    else:
        preview_label.text = body
    status_label.text = "Wave6 deterministic fallback"


def _build_wave6_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Location, Caps.Storage, Caps.Networking]),
            state(async_token=0),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Seed", id="seed_btn"),
                button("Start", id="start_btn"),
                button("Progress", id="progress_btn"),
                button("OK", id="ok_btn"),
                button("FAIL", id="fail_btn"),
            ),
            _seed_btn_handler,
            _start_btn_handler,
            _progress_btn_handler,
            _ok_btn_handler,
            _fail_btn_handler,
        )
    ).build()


def test_track_c_wave6_visible_flow_combines_location_networking_storage_with_deterministic_fallback():
    prog = _build_wave6_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Lcom/ahnali/runtime/LocationHelper;->isLocationEnabled(Landroid/app/Activity;)I" in merged
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
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncError(I)I" in merged
    assert "Lcom/ahnali/runtime/HttpHelper;->getAsyncBody(ILjava/lang/String;)Ljava/lang/String;" in merged

    assert "Wave6 location fallback" in merged
    assert "Wave6 deterministic fallback" in merged
    assert "No location. Showing cached results." in merged
    assert "offline-body" in merged


def test_track_c_wave6_visible_flow_emits_location_storage_networking_helpers(tmp_path):
    frontend = _build_wave6_visible_flow_frontend()
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
    assert (runtime_root / "LocationHelper.smali").exists()
    assert (runtime_root / "StorageHelper.smali").exists()
    assert (runtime_root / "HttpHelper.smali").exists()
