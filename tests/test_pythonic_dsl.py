from alpha_pipeline import alpha_pipeline
from dsl.app import app, activity, state, ui, text, button, on_click
import pytest


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


def test_pythonic_dsl_widget_style_attrs_lowering():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text(
                    "Hello",
                    id="label",
                    padding=16,
                    margin=(8, 4),
                    layout="wrap",
                ),
            ),
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert "Landroid/view/View;->setPadding(IIII)V" in smali
    assert "Landroid/view/ViewGroup$MarginLayoutParams;->setMargins(IIII)V" in smali


@on_click("inc_flow")
def inc_flow():
    local = 0
    if (count > 0 and step > 0) or not (count == 7):
        local = count + step
    else:
        local = step
    while local > 0:
        count = count - 1
        local -= 1
    label.text = f"Count: {count}"


def test_pythonic_dsl_if_while_boolops_lowering():
    prog = app(
        activity(
            "MainActivity",
            state(count=4, step=2),
            ui(
                text("Count: 0", id="label"),
                button("+", id="inc_flow"),
            ),
            inc_flow,
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert ".method public static onClick_inc_flow(Landroid/view/View;)V" in smali
    assert "if-" in smali
    assert "goto" in smali


@on_click("bad")
def bad():
    count = missing + 1


def test_pythonic_dsl_undefined_symbol_fails_early():
    prog = app(
        activity(
            "MainActivity",
            state(count=0),
            ui(button("bad", id="bad")),
            bad,
        )
    )
    with pytest.raises(RuntimeError, match="Undefined variable 'missing'"):
        prog.build()


@on_click("bad_text")
def bad_text():
    label.text = 123


def test_pythonic_dsl_set_text_typecheck():
    prog = app(
        activity(
            "MainActivity",
            state(count=0),
            ui(
                text("Count: 0", id="label"),
                button("bad", id="bad_text"),
            ),
            bad_text,
        )
    )
    with pytest.raises(RuntimeError, match="expects a string or f-string"):
        prog.build()
