from alpha_pipeline import alpha_pipeline
from dsl.app import (
    Navigate,
    activity,
    animate,
    animate_elevation,
    app,
    button,
    fade_in,
    on_click,
    parallel,
    scale,
    sequence,
    text,
    translate,
    ui,
    view,
    Screen,
)


@on_click("go")
def _animate_btn():
    animate("box", alpha=0.6, rotate=25, duration=180, delay=20, interpolator="linear")
    animate_elevation("box", 8, duration=180)


def test_explicit_animate_uses_viewpropertyanimator_and_objectanimator():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view(id="box", width=40, height=40),
                button("Animate", id="go"),
            ),
            _animate_btn,
        )
    )
    result = alpha_pipeline(prog.build())
    smali = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;" in smali
    assert "Landroid/view/ViewPropertyAnimator;->alpha(F)Landroid/view/ViewPropertyAnimator;" in smali
    assert "Landroid/view/ViewPropertyAnimator;->rotation(F)Landroid/view/ViewPropertyAnimator;" in smali
    assert "Landroid/view/ViewPropertyAnimator;->setDuration(J)Landroid/view/ViewPropertyAnimator;" in smali
    assert "Landroid/view/ViewPropertyAnimator;->setStartDelay(J)Landroid/view/ViewPropertyAnimator;" in smali
    assert (
        "Landroid/animation/ObjectAnimator;->ofFloat"
        "(Ljava/lang/Object;Ljava/lang/String;[F)Landroid/animation/ObjectAnimator;"
    ) in smali


@on_click("go2")
def _animate_group_btn():
    sequence(
        fade_in("box", duration=120),
        parallel(
            translate("box", x=32, duration=160),
            scale("box", value=1.2, duration=160),
        ),
    )


def test_sequence_parallel_lower_to_animatorset():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view(id="box", width=40, height=40),
                button("Animate Group", id="go2"),
            ),
            _animate_group_btn,
        )
    )
    result = alpha_pipeline(prog.build())
    smali = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Landroid/animation/AnimatorSet;->playSequentially([Landroid/animation/Animator;)V" in smali
    assert "Landroid/animation/AnimatorSet;->playTogether([Landroid/animation/Animator;)V" in smali


@on_click("next")
def _go_next():
    Navigate("Second")


def test_screen_transition_lowering_for_navigation():
    prog = app(
        activity(
            "MainActivity",
            ui(
                Screen(
                    "First",
                    button("Next", id="next"),
                ),
                Screen(
                    "Second",
                    text("Two", id="second_text"),
                    transition="slide_left",
                ),
            ),
            _go_next,
        )
    )
    result = alpha_pipeline(prog.build())
    smali = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Landroid/view/View;->setTranslationX(F)V" in smali
    assert "Landroid/view/ViewPropertyAnimator;->translationX(F)Landroid/view/ViewPropertyAnimator;" in smali
