from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import Caps, activity, app, app_config, button, on_click, storage_put, ui


@on_click("save_btn")
def _save_btn_handler():
    storage_put("greeting", "hello")


def test_track_c_wave1_storage_put_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(button("Save", id="save_btn")),
            _save_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->putString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave1_storage_put_requires_storage_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Save", id="save_btn")),
            _save_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Storage capability is missing")
    except RuntimeError as exc:
        assert "storage_put requires Storage capability" in str(exc)


def test_track_c_wave1_toolchain_emits_storage_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(button("Save", id="save_btn")),
            _save_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "StorageHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert (
        ".method public static putString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in helper_smali
    assert "Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;" in helper_smali
