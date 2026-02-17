from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import Caps, activity, app, app_config, button, on_click, open_url, ui


@on_click("open_btn")
def _open_btn_handler():
    open_url("https://example.com")


def test_track_c_wave1_open_url_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.URLLauncher]),
            ui(button("Open", id="open_btn")),
            _open_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/UrlLauncherHelper;->openUrl(Landroid/app/Activity;Ljava/lang/String;)I" in merged


def test_track_c_wave1_open_url_requires_url_launcher_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Open", id="open_btn")),
            _open_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when URLLauncher capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] open_url requires Caps.URLLauncher." in str(exc)
        assert "Fix: add app_config(uses=[Caps.URLLauncher]) to activity(...)." in str(exc)


def test_track_c_wave1_toolchain_emits_url_launcher_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.URLLauncher]),
            ui(button("Open", id="open_btn")),
            _open_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "UrlLauncherHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static openUrl(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert "Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V" in helper_smali
