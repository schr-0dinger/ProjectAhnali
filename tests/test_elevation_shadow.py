import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import AppBar, activity, app, button, card, container, dp, text, ui, view


def _build_smali(*items):
    prog = app(activity("MainActivity", ui(*items))).build()
    return alpha_pipeline(prog)["smali_class"]


def test_elevation_and_shadow_lowering_across_phase7_coverage():
    smali = _build_smali(
        AppBar("Top", id="top", elevation=dp(4)),
        container(
            card(
                text(
                    "Shadow text",
                    id="title",
                    elevation=dp(1),
                    text_shadow_color="#66000000",
                    text_shadow_radius=dp(2),
                    text_shadow_dx=dp(1),
                    text_shadow_dy=dp(1),
                ),
                id="main_card",
                elevation=dp(2),
            ),
            id="main_container",
            elevation=dp(1),
        ),
        button("Tap", id="cta", elevation=dp(3), pressed_elevation=dp(8)),
    )

    assert smali.count("Landroid/view/View;->setElevation(F)V") >= 4
    assert "Landroid/widget/TextView;->setShadowLayer(FFFI)V" in smali
    assert (
        "Landroid/animation/ObjectAnimator;->ofFloat"
        "(Ljava/lang/Object;Ljava/lang/String;[F)Landroid/animation/ObjectAnimator;"
    ) in smali
    assert "Landroid/animation/StateListAnimator;->addState([ILandroid/animation/Animator;)V" in smali
    assert "Landroid/view/View;->setStateListAnimator(Landroid/animation/StateListAnimator;)V" in smali


def test_text_shadow_rejects_non_text_widgets():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view(id="box", width=8, height=8, text_shadow_radius=dp(1)),
            ),
        )
    )
    with pytest.raises(RuntimeError, match="text shadow is only supported on text-like widgets"):
        prog.build()
