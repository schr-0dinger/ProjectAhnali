import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    deep_link_error,
    deep_link_get,
    on_click,
    text,
    ui,
)


@on_click("resolve_btn")
def _resolve_btn_handler():
    value = deep_link_get("ahnali://fallback")
    err = deep_link_error()
    preview_label.text = value
    status_label.text = err


@on_click("error_btn")
def _error_btn_handler():
    err = deep_link_error()
    status_label.text = err


def test_track_c_wave14_deep_link_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.DeepLinking]),
            ui(
                text("status", id="status_label"),
                text("preview", id="preview_label"),
                button("Resolve", id="resolve_btn"),
            ),
            _resolve_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/DeepLinkHelper;->getLaunchUri("
        "Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/DeepLinkHelper;->getLaunchUriError("
        "Landroid/app/Activity;)I"
    ) in merged


def test_track_c_wave14_deep_link_requires_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), button("Resolve", id="resolve_btn")),
            _resolve_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] deep_link_get requires Caps\.DeepLinking\."):
        prog.build()


def test_track_c_wave14_deep_link_error_requires_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), button("Error", id="error_btn")),
            _error_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] deep_link_error requires Caps\.DeepLinking\."):
        prog.build()


def test_track_c_wave14_toolchain_emits_deep_link_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.DeepLinking]),
            ui(
                text("status", id="status_label"),
                text("preview", id="preview_label"),
                button("Resolve", id="resolve_btn"),
            ),
            _resolve_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "DeepLinkHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static getLaunchUri(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;" in helper_smali
    assert ".method public static getLaunchUriError(Landroid/app/Activity;)I" in helper_smali


def test_track_c_wave14_parser_deep_link_get_rejects_wrong_arity():
    def _bad():
        value = deep_link_get("a", "b")
        status_label.text = value

    with pytest.raises(RuntimeError, match="deep_link_get expects 0 or 1 string argument"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.DeepLinking]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave14_parser_deep_link_get_rejects_non_string_fallback():
    def _bad():
        value = deep_link_get(7)
        status_label.text = value

    with pytest.raises(RuntimeError, match="deep_link_get argument 'fallback' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.DeepLinking]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave14_parser_deep_link_error_rejects_arity():
    def _bad():
        value = deep_link_error("extra")
        status_label.text = value

    with pytest.raises(RuntimeError, match="deep_link_error expects no arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.DeepLinking]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
