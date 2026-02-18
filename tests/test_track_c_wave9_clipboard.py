import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    clipboard_get,
    clipboard_set,
    on_click,
    text,
    ui,
)


@on_click("copy_btn")
def _copy_btn_handler():
    clipboard_set("Wave9 clipboard value")


@on_click("paste_btn")
def _paste_btn_handler():
    value = clipboard_get("clipboard-fallback")
    preview_label.text = value


def test_track_c_wave9_clipboard_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Clipboard]),
            ui(
                text("preview", id="preview_label"),
                button("Copy", id="copy_btn"),
                button("Paste", id="paste_btn"),
            ),
            _copy_btn_handler,
            _paste_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/ClipboardHelper;->setText("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ClipboardHelper;->getText("
        "Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged


def test_track_c_wave9_clipboard_get_requires_clipboard_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("preview", id="preview_label"), button("Paste", id="paste_btn")),
            _paste_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] clipboard_get requires Caps\.Clipboard\."):
        prog.build()


def test_track_c_wave9_clipboard_set_requires_clipboard_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Copy", id="copy_btn")),
            _copy_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] clipboard_set requires Caps\.Clipboard\."):
        prog.build()


def test_track_c_wave9_toolchain_emits_clipboard_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Clipboard]),
            ui(button("Copy", id="copy_btn")),
            _copy_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "ClipboardHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static setText(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static getText(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;" in helper_smali


def test_track_c_wave9_parser_clipboard_set_rejects_wrong_arity():
    def _bad():
        clipboard_set("a", "b")

    with pytest.raises(RuntimeError, match="clipboard_set expects exactly 1 string argument"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Clipboard]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave9_parser_clipboard_get_rejects_non_string_fallback():
    def _bad():
        value = clipboard_get(7)
        preview_label.text = value

    with pytest.raises(RuntimeError, match="clipboard_get argument 'fallback' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Clipboard]),
                ui(text("preview", id="preview_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
