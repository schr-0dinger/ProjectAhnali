from alpha_pipeline import alpha_pipeline
from dsl.app import app, activity, state, ui, text, button, on_click


def test_pythonic_dsl_counter_smali():
    prog = app(
        activity(
            "MainActivity",
            state(count=0),
            ui(
                text("Count: 0", id="label"),
                button("+", id="inc"),
                button("-", id="dec"),
            ),
            on_click("inc", [
                "count = count + 1",
                "label.text = f'Count: {count}'",
            ]),
            on_click("dec", [
                "count = count - 1",
                "label.text = f'Count: {count}'",
            ]),
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert ".field private static count:I" in smali
    assert "sget" in smali
    assert "sput" in smali
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in smali
