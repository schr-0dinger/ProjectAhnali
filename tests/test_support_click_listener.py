from apk.toolchain import emit_build_dir_from_program
from dsl.app import program, method, ret, var, button_view, set_content_view, on_click_view, click_handler


def test_emit_click_listener_support_class(tmp_path):
    prog = program([
        method(
            "main",
            params=["ctx"],
            param_types=["Landroid/app/Activity;"],
            return_type=None,
            body=[
                *button_view("btn", var("ctx"), "Tap"),
                *on_click_view(var("btn"), handler_name="onClick"),
                set_content_view(var("ctx"), var("btn")),
                ret(),
            ],
        ),
        click_handler("onClick", [
            ret(),
        ]),
    ])

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_target_sig="(Landroid/app/Activity;)V",
        emit_support_classes=True,
        click_listener_target_method="onClick",
    )

    listener_path = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliClickListener.smali"
    assert listener_path.exists()
    text = listener_path.read_text(encoding="utf-8")
    assert "implements Landroid/view/View$OnClickListener;" in text
    assert "invoke-static {p1}, LTest;->onClick(Landroid/view/View;)V" in text
