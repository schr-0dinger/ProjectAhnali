from alpha_pipeline import alpha_pipeline
from dsl.app import (
    AppBar,
    Checkbox,
    Container,
    Icon,
    ProgressBar,
    Style,
    TextField,
    Theme,
    activity,
    app,
    card,
    dp,
    sp,
    ui,
)


def test_phase10_theme_channels_apply_to_expected_widget_families():
    prog = app(
        activity(
            "MainActivity",
            Theme(
                input=Style(text_size=sp(18)),
                selector=Style(button_tint="#FFABCDEF"),
                progress=Style(progress_tint="#FF123456"),
                icon=Style(text_color="#FF654321"),
                container=Style(background="#FF111111"),
                appbar=Style(background="#FF222222"),
            ),
            ui(
                AppBar("Top", id="top", inline=True),
                TextField("", id="inp"),
                Checkbox("Pick", id="sel"),
                ProgressBar(id="prog", value=30),
                Icon("*", id="ic"),
                Container(id="ctr"),
            ),
        )
    ).build()

    result = alpha_pipeline(prog)
    smali = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    # input
    assert "Landroid/widget/TextView;->setTextSize(IF)V" in smali
    # selector
    assert "Landroid/widget/CompoundButton;->setButtonTintList(Landroid/content/res/ColorStateList;)V" in smali
    # progress
    assert "Landroid/widget/ProgressBar;->setProgressTintList(Landroid/content/res/ColorStateList;)V" in smali
    # icon
    assert "Landroid/widget/TextView;->setTextColor(I)V" in smali
    # container + appbar background lowering
    assert "ctr_background_color" in prog.resource_colors
    assert "top_background_color" in prog.resource_colors


def test_phase10_precedence_inline_over_style_over_theme_over_defaults_and_lint():
    prog = app(
        activity(
            "MainActivity",
            Theme(
                container=Style(
                    background="#FF101010",
                    radius=dp(2),
                    padding=dp(2),
                )
            ),
            ui(
                card(
                    id="c",
                    style=Style(
                        background="#FF202020",
                        radius=dp(4),
                        padding=dp(4),
                    ),
                    background="#FF303030",
                    radius=dp(6),
                    padding=dp(6),
                ),
            ),
        )
    ).build()

    # Inline wins over style/theme/default.
    assert prog.resource_colors.get("c_fill") == "#FF303030"
    assert prog.resource_dimens.get("c_corner_radius") == "6dp"
    assert prog.resource_dimens.get("c_padding_l") == "6dp"
    assert prog.resource_dimens.get("c_padding_t") == "6dp"
    assert prog.resource_dimens.get("c_padding_r") == "6dp"
    assert prog.resource_dimens.get("c_padding_b") == "6dp"

    assert any(
        "precedence is inline attrs > style= > Theme channel > widget defaults" in warning
        for warning in prog.lint_warnings
    )
