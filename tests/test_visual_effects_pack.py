import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import Gradient, activity, app, column, dp, gradient, text, ui, view


def _build_smali(*items):
    prog = app(activity("MainActivity", ui(*items))).build()
    return alpha_pipeline(prog)["smali_class"]


def test_visual_effects_border_gradient_ripple_clip_lowering():
    smali = _build_smali(
        column(
            view(
                id="fx_box",
                width=64,
                height=64,
                background=Gradient("#FF112233", "#FF445566", "top_to_bottom"),
                border_width=dp(2),
                border_color="#FFFF0000",
                border_radius=(dp(4), dp(8), dp(12), dp(16)),
                ripple_color="#33000000",
                clip_to_outline=True,
            ),
            id="fx_container",
            clip_children=False,
        ),
    )

    assert "Landroid/graphics/drawable/GradientDrawable;->setOrientation" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setColors([I)V" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setStroke(II)V" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setCornerRadii([F)V" in smali
    assert (
        "Landroid/graphics/drawable/RippleDrawable;-><init>"
        "(Landroid/content/res/ColorStateList;Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;)V"
    ) in smali
    assert "Landroid/view/View;->setClipToOutline(Z)V" in smali
    assert "Landroid/view/ViewGroup;->setClipChildren(Z)V" in smali


def test_visual_effects_border_radius_scalar_uses_corner_radius():
    smali = _build_smali(
        view(
            id="card_like",
            width=64,
            height=64,
            background="#FF202020",
            border_radius=dp(10),
        )
    )
    assert "Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V" in smali


def test_visual_effects_gradient_helper_function():
    smali = _build_smali(
        view(
            id="g",
            width=32,
            height=32,
            background=gradient("#FF000000", "#FFFFFFFF", "left_to_right"),
        )
    )
    assert "Landroid/graphics/drawable/GradientDrawable;->setOrientation" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setColors([I)V" in smali


def test_visual_effects_invalid_gradient_direction_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view(
                    id="bad_gradient",
                    width=32,
                    height=32,
                    background=Gradient("#FF000000", "#FFFFFFFF", "sideways"),
                )
            ),
        )
    )
    with pytest.raises(RuntimeError, match="Unsupported Gradient direction"):
        prog.build()


def test_visual_effects_clip_children_non_container_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("bad", id="bad", clip_children=True),
            ),
        )
    )
    with pytest.raises(RuntimeError, match="clip_children is only supported on container widgets"):
        prog.build()


def test_visual_effects_border_width_requires_color():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view(id="bad_border", width=32, height=32, border_width=dp(2)),
            ),
        )
    )
    with pytest.raises(RuntimeError, match="border_color is required when border_width is set"):
        prog.build()
