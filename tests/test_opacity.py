import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import AppBar, Style, activity, app, button, card, container, text, ui, view


def _build_smali(*items):
    prog = app(activity("MainActivity", ui(*items))).build()
    return alpha_pipeline(prog)["smali_class"]


def test_opacity_lowers_to_set_alpha_for_core_widgets():
    smali = _build_smali(
        AppBar("Top", id="top", opacity=0.8),
        container(
            card(
                text("Title", id="title", opacity=0.4),
                id="main_card",
                opacity=0.6,
            ),
            id="main_container",
            opacity=0.7,
        ),
        button("Tap", id="cta", opacity=0.9),
        view(id="box", width=8, height=8, opacity=0.5),
    )

    assert smali.count("Landroid/view/View;->setAlpha(F)V") >= 5


def test_opacity_from_style_lowers():
    smali = _build_smali(
        text("Styled", id="label", style=Style(opacity=0.25)),
    )
    assert "Landroid/view/View;->setAlpha(F)V" in smali


def test_opacity_out_of_range_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Bad", id="label", opacity=1.5),
            ),
        )
    )
    with pytest.raises(RuntimeError, match="out of range"):
        prog.build()
