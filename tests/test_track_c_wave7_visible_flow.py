from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    check_permission,
    on_click,
    open_url,
    permission_granted,
    storage_get,
    storage_put,
    text,
    ui,
)


@on_click("seed_btn")
def _seed_btn_handler():
    storage_put("perm_hint", "Camera permission required")
    status_label.text = "Wave7 cache seeded"


@on_click("check_btn")
def _check_btn_handler():
    granted = permission_granted("android.permission.CAMERA")
    if granted == 1:
        open_url("https://example.com/camera-ready")
        preview_label.text = "camera-ready"
        status_label.text = "Wave7 permission granted"
    else:
        check_permission("android.permission.CAMERA")
        hint = storage_get("perm_hint", "permission-required")
        preview_label.text = hint
        status_label.text = "Wave7 deterministic fallback"


def _build_wave7_visible_flow_frontend():
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Permissions, Caps.Storage, Caps.URLLauncher]),
            ui(
                text("Status: ready", id="status_label"),
                text("Preview: none", id="preview_label"),
                button("Seed", id="seed_btn"),
                button("Check", id="check_btn"),
            ),
            _seed_btn_handler,
            _check_btn_handler,
        )
    ).build()


def test_track_c_wave7_visible_flow_lowers_permissions_storage_url_launcher_with_deterministic_fallback():
    prog = _build_wave7_visible_flow_frontend()
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Lcom/ahnali/runtime/PermissionHelper;->isGranted(Landroid/app/Activity;Ljava/lang/String;)I" in merged
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->putString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->getString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl(Landroid/app/Activity;Ljava/lang/String;)I" in merged

    assert "Wave7 deterministic fallback" in merged
    assert "Camera permission required" in merged
    assert "https://example.com/camera-ready" in merged


def test_track_c_wave7_visible_flow_emits_permissions_storage_url_launcher_helpers(tmp_path):
    frontend = _build_wave7_visible_flow_frontend()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )

    runtime_root = out_dir / "smali" / "com" / "ahnali" / "runtime"
    assert (runtime_root / "PermissionHelper.smali").exists()
    assert (runtime_root / "StorageHelper.smali").exists()
    assert (runtime_root / "UrlLauncherHelper.smali").exists()
