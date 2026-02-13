from alpha_pipeline import alpha_pipeline
from dsl.app import (
    app,
    activity,
    state,
    ui,
    text,
    button,
    row,
    on_click,
    card,
    container,
    divider,
    icon,
    image,
    progress_bar,
    radio,
    radio_group,
    view,
    Slider,
    DropdownButton,
    PopupMenuButton,
    Checkbox,
    Switch,
    Theme,
    Style,
    color_state,
    dp,
)
from dsl.widgets import fill, size, wrap
import pytest


def _first_layout_params_ctor_args(frontend):
    for m in frontend.methods:
        for s in m.body:
            expr = getattr(s, "expr", None)
            if getattr(expr, "class_desc", "").endswith("LinearLayout$LayoutParams;"):
                return [a.value for a in expr.args]
    raise AssertionError("No LinearLayout$LayoutParams constructor found")


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


def test_pythonic_dsl_row_defaults_to_match_parent_width():
    prog = app(
        activity(
            "MainActivity",
            ui(
                row(
                    button("Tap", id="inc"),
                    id="button_row",
                ),
            ),
        )
    )

    frontend = prog.build()
    assert _first_layout_params_ctor_args(frontend) == [-1, -2]


def test_pythonic_dsl_width_height_widget_params():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Sized", id="sized", width="match_parent", height=48),
            ),
        )
    )

    frontend = prog.build()
    assert _first_layout_params_ctor_args(frontend) == [-1, 48]


def test_pythonic_dsl_explicit_sizing_helpers():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("A", id="a", layout=size(fill(), wrap())),
            ),
        )
    )
    frontend = prog.build()
    assert _first_layout_params_ctor_args(frontend) == [-1, -2]


def test_pythonic_dsl_max_width_alias():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Alias", id="alias", width="max_width", height="wrap"),
            ),
        )
    )

    frontend = prog.build()
    assert _first_layout_params_ctor_args(frontend) == [-1, -2]


def test_pythonic_dsl_splits_ui_build_into_helper_methods():
    prog = app(activity("MainActivity", ui(text("A", id="a"), button("B", id="b"))))
    smali = alpha_pipeline(prog.build())["smali_class"]
    assert ".method public static buildUi_0(Landroid/app/Activity;Landroid/view/ViewGroup;)V" in smali
    assert "buildUi_" in smali


def test_pythonic_dsl_row_weight_and_alignment():
    prog = app(
        activity(
            "MainActivity",
            ui(
                row(
                    button("A", id="a", weight=1),
                    button("B", id="b", weight=1),
                    id="r",
                    align="center",
                    arrangement="center",
                    weight_sum=2,
                ),
            ),
        )
    )
    smali = alpha_pipeline(prog.build())["smali_class"]
    assert "Landroid/widget/LinearLayout;->setWeightSum(F)V" in smali
    assert "Landroid/widget/LinearLayout$LayoutParams;->weight:F" in smali
    assert "Landroid/widget/LinearLayout;->setGravity(I)V" in smali


def test_pythonic_dsl_duplicate_widget_ids_fail():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("One", id="dup"),
                text("Two", id="dup"),
            ),
        )
    )

    with pytest.raises(RuntimeError, match="Duplicate widget id 'dup'"):
        prog.build()


def test_pythonic_dsl_root_is_scrollable():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("One", id="t1"),
                text("Two", id="t2"),
            ),
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert "Landroid/widget/ScrollView;" in smali
    assert "Landroid/view/ViewGroup;->addView(Landroid/view/View;)V" in smali


def test_pythonic_dsl_navigation_screens():
    from dsl.app import Screen, Navigate

    @on_click("go")
    def go():
        Navigate("Player")

    prog = app(
        activity(
            "MainActivity",
            ui(
                Screen(
                    "Home",
                    text("Home", id="home_title"),
                    button("Go", id="go"),
                ),
                Screen(
                    "Player",
                    text("Player", id="player_title"),
                ),
            ),
            go,
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert "Landroid/view/View;->setVisibility(I)V" in smali
    assert ".field public static view_screen_home" in smali
    assert ".field public static view_screen_player" in smali


@on_click("log_btn")
def log_btn():
    log("Ahnali", "clicked")


def test_pythonic_dsl_log_stmt():
    prog = app(
        activity(
            "MainActivity",
            ui(
                button("Log", id="log_btn"),
            ),
            log_btn,
        )
    )

    result = alpha_pipeline(prog.build())
    smali = result["smali_class"]
    handlers = result.get("extra_smali_classes", {}).get("LTestHandlers;", "")
    merged = smali + handlers
    assert "Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I" in merged


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

    result = alpha_pipeline(prog.build())
    smali = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
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


def test_pythonic_dsl_supports_missing_core_widgets():
    prog = app(
        activity(
            "MainActivity",
            ui(
                container(
                    card(
                        icon("*", id="glyph"),
                        divider(id="line"),
                        image(id="hero", src="ic_launcher", content_description="hero image"),
                        view(id="box", width="match_parent", height=8, background="#22000000"),
                        radio_group(
                            radio("A", id="r_a", checked=True),
                            radio("B", id="r_b"),
                            id="group",
                            orientation="vertical",
                        ),
                        progress_bar(id="progress", value=30, min=0, max=100),
                        id="main_card",
                    ),
                    id="root_container",
                ),
            ),
        )
    )
    smali = alpha_pipeline(prog.build())["smali_class"]
    assert "Landroid/widget/ImageView;" in smali
    assert "Landroid/widget/ProgressBar;" in smali
    assert "Landroid/widget/ProgressBar;-><init>(Landroid/content/Context;Landroid/util/AttributeSet;I)V" in smali
    assert "Landroid/widget/RadioGroup;" in smali
    assert "Landroid/view/View;" in smali
    assert "Landroid/content/res/Resources;->getIdentifier" in smali


def test_pythonic_dsl_button_allows_icon_plus_text():
    prog = app(
        activity(
            "MainActivity",
            ui(
                button("Save", id="save_btn", icon="ICON"),
            ),
        )
    ).build()
    assert "ICON Save" in set(prog.resources.values())


def test_pythonic_dsl_radiogroup_assigns_id_before_checked():
    prog = app(
        activity(
            "MainActivity",
            ui(
                radio_group(
                    radio("A", id="r_a", checked=True),
                    radio("B", id="r_b", checked=False),
                    id="group",
                ),
            ),
        )
    )
    smali = alpha_pipeline(prog.build())["smali_class"]
    first_set_id = smali.find("Landroid/view/View;->setId(I)V")
    first_set_checked = smali.find("Landroid/widget/RadioButton;->setChecked(Z)V")
    assert first_set_id != -1
    assert first_set_checked != -1
    assert first_set_id < first_set_checked


def test_pythonic_theme_button_excludes_slider_dropdown_and_popup():
    prog = app(
        activity(
            "MainActivity",
            Theme(
                button=Style(
                    background="#FF112233",
                    radius=dp(6),
                )
            ),
            ui(
                button("Styled", id="b"),
                Slider(id="s"),
                DropdownButton(id="d", items=["A", "B"]),
                PopupMenuButton("Menu", id="p", items=["X", "Y"]),
            ),
        )
    )
    smali = alpha_pipeline(prog.build())["smali_class"]
    # Only the real Button should receive theme.button background/radius styling.
    assert smali.count("Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V") == 1


def test_pythonic_popupmenu_autowires_default_show_behavior():
    prog = app(
        activity(
            "MainActivity",
            ui(
                PopupMenuButton("Menu", id="p", items=["X", "Y"]),
            ),
        )
    )
    result = alpha_pipeline(prog.build())
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert ".method public static onClick_p_popup(Landroid/view/View;)V" in merged
    assert "Landroid/widget/PopupMenu;-><init>(Landroid/content/Context;Landroid/view/View;)V" in merged
    assert "Landroid/widget/PopupMenu;->getMenu()Landroid/view/Menu;" in merged
    assert "Landroid/view/Menu;->add(Ljava/lang/CharSequence;)Landroid/view/MenuItem;" in merged
    assert "Landroid/widget/PopupMenu;->show()V" in merged


def test_wave_a_typography_attrs_lowering():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text(
                    "Typography",
                    id="t",
                    style=Style(
                        font_family="serif",
                        font_weight=700,
                        font_style="italic",
                        letter_spacing=0.15,
                        line_height=dp(20),
                        text_alignment="center",
                        all_caps=True,
                        max_lines=2,
                        ellipsize="end",
                    ),
                ),
            ),
        )
    )
    smali = alpha_pipeline(prog.build())["smali_class"]
    assert "Landroid/graphics/Typeface;->create(Ljava/lang/String;I)Landroid/graphics/Typeface;" in smali
    assert "Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V" in smali
    assert "Landroid/widget/TextView;->setLetterSpacing(F)V" in smali
    assert "Landroid/widget/TextView;->setLineSpacing(FF)V" in smali
    assert "Landroid/view/View;->setTextAlignment(I)V" in smali
    assert "Landroid/widget/TextView;->setAllCaps(Z)V" in smali
    assert "Landroid/widget/TextView;->setMaxLines(I)V" in smali
    assert "Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V" in smali


def test_wave_a_control_tinting_lowering():
    prog = app(
        activity(
            "MainActivity",
            ui(
                button("Tinted", id="btn", style=Style(tint="#FF336699")),
                Slider(
                    id="s",
                    style=Style(
                        thumb_tint="#FFFF0000",
                        track_tint="#FF00FF00",
                        progress_tint="#FF0000FF",
                    ),
                ),
                progress_bar(id="p", style=Style(progress_tint="#FF123456")),
                Checkbox("C", id="c", style=Style(button_tint="#FFABCDEF")),
                Switch(
                    "S",
                    id="sw",
                    style=Style(
                        thumb_tint="#FF222222",
                        track_tint="#FF333333",
                    ),
                ),
            ),
        )
    )
    smali = alpha_pipeline(prog.build())["smali_class"]
    assert "Landroid/view/View;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/SeekBar;->setThumbTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/SeekBar;->setProgressTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/SeekBar;->setProgressBackgroundTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/ProgressBar;->setProgressTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/ProgressBar;->setIndeterminateTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/CompoundButton;->setButtonTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/Switch;->setThumbTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/Switch;->setTrackTintList(Landroid/content/res/ColorStateList;)V" in smali


def test_wave_a_color_state_lowering_for_text_and_tint():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text(
                    "Stateful",
                    id="txt",
                    style=Style(
                        text_color=color_state(
                            default="#FF111111",
                            pressed="#FF222222",
                            disabled="#FF333333",
                        )
                    ),
                ),
                button(
                    "Stateful Tint",
                    id="btn",
                    style=Style(
                        tint=color_state(
                            default="#FFAAAAAA",
                            pressed="#FFBBBBBB",
                            focused="#FFCCCCCC",
                        )
                    ),
                ),
            ),
        )
    )
    smali = alpha_pipeline(prog.build())["smali_class"]
    assert "Landroid/content/res/ColorStateList;-><init>([[I[I)V" in smali
    assert "Landroid/widget/TextView;->setTextColor(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/view/View;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V" in smali
