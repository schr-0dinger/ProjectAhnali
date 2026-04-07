from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import activity, app, button, on_click, text, ui


@on_click("copy_btn")
def _copy_label_text():
    current = getattr(label, "text")
    label.text = current


@on_click("direct_btn")
def _direct_getattr_set_text():
    label.text = getattr(label, "text")


def test_getattr_widget_text_lowers_to_reflection_runtime_call():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Copy", id="copy_btn"),
            ),
            _copy_label_text,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/ReflectionRuntime;->getText("
        "Landroid/widget/TextView;)Ljava/lang/String;"
    ) in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_getattr_widget_text_runtime_helper_is_emitted_in_build_dir(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Direct", id="direct_btn"),
            ),
            _direct_getattr_set_text,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "ReflectionRuntime.smali"
    assert helper_path.exists()
    smali_text = helper_path.read_text(encoding="utf-8")
    assert ".method public static getText(Landroid/widget/TextView;)Ljava/lang/String;" in smali_text
