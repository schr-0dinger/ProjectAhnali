import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    check_location,
    location_enabled,
    on_click,
    text,
    ui,
)


@on_click("check_btn")
def _check_btn_handler():
    check_location()


@on_click("eval_btn")
def _eval_btn_handler():
    value = location_enabled()
    status_label.text = value


def test_track_c_wave6_location_enabled_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Location]),
            ui(
                text("status", id="status_label"),
                button("Check", id="check_btn"),
                button("Eval", id="eval_btn"),
            ),
            _check_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/LocationHelper;->isLocationEnabled(Landroid/app/Activity;)I" in merged


def test_track_c_wave6_location_enabled_requires_location_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("status", id="status_label"),
                button("Eval", id="eval_btn"),
            ),
            _eval_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] location_enabled requires Caps\.Location\."):
        prog.build()


def test_track_c_wave6_check_location_requires_location_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Check", id="check_btn")),
            _check_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] check_location requires Caps\.Location\."):
        prog.build()


def test_track_c_wave6_toolchain_emits_location_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Location]),
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
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "LocationHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static isLocationEnabled(Landroid/app/Activity;)I" in helper_smali
    assert "Landroid/location/LocationManager;->isProviderEnabled(Ljava/lang/String;)Z" in helper_smali


def test_track_c_wave6_parser_check_location_rejects_arguments():
    def _bad():
        check_location("unexpected")

    with pytest.raises(RuntimeError, match="check_location expects no arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Location]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave6_parser_location_enabled_rejects_arguments():
    def _bad():
        value = location_enabled("unexpected")
        status_label.text = value

    with pytest.raises(RuntimeError, match="location_enabled expects no arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Location]),
                ui(text("x", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
