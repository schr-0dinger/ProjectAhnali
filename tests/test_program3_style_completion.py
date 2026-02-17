import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import Gradient, TextField, activity, app, color_state, dp, image, progress_bar, style, text, ui, view


def _build_smali(*items):
    prog = app(activity("MainActivity", ui(*items))).build()
    return alpha_pipeline(prog)["smali_class"]


def test_program3_style_gap_surfaces_lowering():
    smali = _build_smali(
        TextField(
            "",
            id="inp",
            hint="Email",
            hint_color=color_state(default="#FF223344", focused="#FF445566"),
            highlight_color="#AA55AA00",
            text_tint="#FF112233",
        ),
        progress_bar(
            id="p",
            value=40,
            progress_tint="#FF0099FF",
            secondary_progress_tint="#FF66CCFF",
        ),
        image(
            id="img",
            src=0x7F020000,
            tint="#FF00FF00",
            adjust_view_bounds=True,
            image_alpha=180,
            image_matrix=(1.0, 0.0, 4.0, 0.0, 1.0, 6.0, 0.0, 0.0, 1.0),
        ),
        image(id="img_crop", src=0x7F020000, crop=True),
        image(id="img_inside", src=0x7F020000, center_inside=True),
        view(
            id="radial",
            width=32,
            height=32,
            background=Gradient("#FF000000", "#FFFFFFFF", kind="radial", radius=dp(20)),
        ),
        view(
            id="sweep",
            width=32,
            height=32,
            background=Gradient("#FF111111", "#FF999999", kind="sweep"),
        ),
    )

    assert "Landroid/widget/TextView;->setHintTextColor(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/TextView;->setHighlightColor(I)V" in smali
    assert "Landroid/widget/TextView;->setCompoundDrawableTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/ProgressBar;->setSecondaryProgressTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/ImageView;->setImageTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/ImageView;->setAdjustViewBounds(Z)V" in smali
    assert "Landroid/widget/ImageView;->setImageAlpha(I)V" in smali
    assert "Landroid/graphics/Matrix;->setValues([F)V" in smali
    assert "Landroid/widget/ImageView;->setImageMatrix(Landroid/graphics/Matrix;)V" in smali
    assert "Landroid/widget/ImageView;->setScaleType(Landroid/widget/ImageView$ScaleType;)V" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setGradientType(I)V" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setGradientRadius(F)V" in smali


def test_program3_radial_gradient_requires_radius():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view(
                    id="bad",
                    width=24,
                    height=24,
                    background=Gradient("#FF000000", "#FFFFFFFF", kind="radial"),
                )
            ),
        )
    )
    with pytest.raises(RuntimeError, match=r"radial gradients require radius"):
        prog.build()


def test_program3_image_crop_center_inside_conflict_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(image(id="bad_image", src=0x7F020000, crop=True, center_inside=True)),
        )
    )
    with pytest.raises(RuntimeError, match=r"cannot set both crop=True and center_inside=True"):
        prog.build()


def test_program3_image_matrix_shape_validation():
    prog = app(
        activity(
            "MainActivity",
            ui(image(id="bad_matrix", src=0x7F020000, image_matrix=(1.0, 0.0, 0.0))),
        )
    )
    with pytest.raises(RuntimeError, match=r"image_matrix must be a 9-number sequence"):
        prog.build()


def test_program3_image_alpha_range_validation():
    prog = app(
        activity(
            "MainActivity",
            ui(image(id="bad_alpha", src=0x7F020000, image_alpha=999)),
        )
    )
    with pytest.raises(RuntimeError, match=r"image_alpha 999 is out of range"):
        prog.build()


def test_program3_image_scale_type_style_incompatible_on_text():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text(
                    "bad",
                    id="bad_style",
                    style=style(scale_type="fit_xy"),
                )
            ),
        )
    )
    with pytest.raises(RuntimeError, match=r"Incompatible style field 'scale_type' on widget 'bad_style'"):
        prog.build()
