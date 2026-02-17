from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import Caps, activity, app, app_config, button, check_connectivity, on_click, ui


@on_click("check_btn")
def _check_btn_handler():
    check_connectivity()


def test_track_c_wave1_check_connectivity_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Connectivity]),
            ui(button("Check", id="check_btn")),
            _check_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/ConnectivityHelper;->isConnected(Landroid/app/Activity;)I" in merged


def test_track_c_wave1_check_connectivity_requires_connectivity_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Check", id="check_btn")),
            _check_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Connectivity capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] check_connectivity requires Caps.Connectivity." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Connectivity]) to activity(...)." in str(exc)


def test_track_c_wave1_toolchain_emits_connectivity_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Connectivity]),
            ui(button("Check", id="check_btn")),
            _check_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "ConnectivityHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static isConnected(Landroid/app/Activity;)I" in helper_smali
    assert "Landroid/net/ConnectivityManager;->getActiveNetworkInfo()Landroid/net/NetworkInfo;" in helper_smali
