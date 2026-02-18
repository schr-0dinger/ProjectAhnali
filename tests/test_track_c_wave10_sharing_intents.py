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
    open_external_error,
    share_text,
    share_text_error,
    share_text_result,
    text,
    ui,
)


@on_click("share_btn")
def _share_btn_handler():
    share_text("Wave10 share payload", "Ahnali Share")


@on_click("open_btn")
def _open_btn_handler():
    open_external("https://example.com/wave10")


@on_click("eval_btn")
def _eval_btn_handler():
    ok = share_text_result("Wave10 share payload", "Ahnali Share")
    err = share_text_error("Wave10 share payload", "Ahnali Share")
    ext_err = open_external_error("https://example.com/wave10")
    total_err = err + ext_err
    preview_label.text = ok
    status_label.text = total_err


@on_click("open_eval_btn")
def _open_eval_btn_handler():
    err = open_external_error("https://example.com/wave10")
    status_label.text = err


def test_track_c_wave10_sharing_intents_lowers_to_runtime_helper_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Sharing]),
            ui(
                text("status", id="status_label"),
                text("preview", id="preview_label"),
                button("Share", id="share_btn"),
                button("Open", id="open_btn"),
                button("Eval", id="eval_btn"),
            ),
            _share_btn_handler,
            _open_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert (
        "Lcom/ahnali/runtime/ShareHelper;->shareText("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->shareTextError("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->openUri("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert (
        "Lcom/ahnali/runtime/ShareHelper;->openUriError("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave10_share_text_requires_sharing_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Share", id="share_btn")),
            _share_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] share_text requires Caps\.Sharing\."):
        prog.build()


def test_track_c_wave10_open_external_error_requires_sharing_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(text("status", id="status_label"), button("Eval", id="open_eval_btn")),
            _open_eval_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] open_external_error requires Caps\.Sharing\."):
        prog.build()


def test_track_c_wave10_toolchain_emits_share_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Sharing]),
            ui(button("Share", id="share_btn")),
            _share_btn_handler,
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
    assert ".method public static shareText(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static shareTextError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static openUri(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert ".method public static openUriError(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali


def test_track_c_wave10_parser_share_text_rejects_wrong_arity():
    def _bad():
        share_text("a", "b", "c")

    with pytest.raises(RuntimeError, match="share_text expects 1 or 2 string arguments"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Sharing]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave10_parser_open_external_rejects_non_string_uri():
    def _bad():
        open_external(7)

    with pytest.raises(RuntimeError, match="open_external argument 'uri' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Sharing]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
