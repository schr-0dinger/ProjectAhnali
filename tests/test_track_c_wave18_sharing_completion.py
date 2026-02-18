import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    on_click,
    open_external,
    open_external_result,
    share_file,
    share_file_error,
    share_file_result,
    text,
    ui,
)


@on_click("share_file_btn")
def _share_file_btn_handler():
    share_file("content://ahnali/wave18", "Share file via", "text/plain")


@on_click("open_btn")
def _open_btn_handler():
    open_external("https://example.com/wave18")


@on_click("eval_btn")
def _eval_btn_handler():
    ok = share_file_result("content://ahnali/wave18", "Share file via", "text/plain")
    err = share_file_error("content://ahnali/wave18", "Share file via", "text/plain")
    open_ok = open_external_result("https://example.com/wave18")
    total = ok + open_ok
    status_label.text = err
    preview_label.text = total


@on_click("eval_only_btn")
def _eval_only_btn_handler():
    ok = open_external_result("https://example.com/wave18")
    status_label.text = ok


def test_track_c_wave18_sharing_completion_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Sharing]),
            ui(
                text("status", id="status_label"),
                text("preview", id="preview_label"),
                button("ShareFile", id="share_file_btn"),
                button("Open", id="open_btn"),
                button("Eval", id="eval_btn"),
            ),
            _share_file_btn_handler,
            _open_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/ShareHelper;->shareFile("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->shareFileError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->openUri("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave18_share_file_requires_sharing_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("ShareFile", id="share_file_btn")),
            _share_file_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] share_file requires Caps\.Sharing\."):
        prog.build()


def test_track_c_wave18_open_external_result_requires_sharing_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), button("Eval", id="eval_only_btn")),
            _eval_only_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] open_external_result requires Caps\.Sharing\."):
        prog.build()


def test_track_c_wave18_toolchain_emits_share_file_methods(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Sharing]),
            ui(button("ShareFile", id="share_file_btn")),
            _share_file_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "ShareHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static shareFile(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static shareFileError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali


def test_track_c_wave18_parser_share_file_rejects_non_string_uri():
    def _bad():
        share_file(7, "Share file via", "text/plain")

    with pytest.raises(RuntimeError, match="share_file argument 'uri' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Sharing]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave18_parser_share_file_error_rejects_non_string_mime():
    def _bad():
        value = share_file_error("content://ahnali/wave18", "Share file via", 7)
        status_label.text = value

    with pytest.raises(RuntimeError, match="share_file_error argument 'mime_type' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Sharing]),
                ui(text("status", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
