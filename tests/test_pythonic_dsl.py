from alpha_pipeline import alpha_pipeline
from dsl.app import app, activity, state, ui, text, button, on_click


@on_click("inc")
def inc():
    count = count + step
    label.text = f"Count: {count} step {step}"


@on_click("dec")
def dec():
    count -= 1
    label.text = f"Count: {count}"


def test_pythonic_dsl_counter_smali():
    prog = app(
        activity(
            "MainActivity",
            state(count=0, step=2),
            ui(
                text("Count: 0", id="label"),
                button("+", id="inc"),
                button("-", id="dec"),
            ),
            inc,
            dec,
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert ".field private static count:I" in smali
    assert "sget" in smali
    assert "sput" in smali
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in smali
