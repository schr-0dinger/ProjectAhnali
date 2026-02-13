from pathlib import Path

from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    AppBar,
    Checkbox,
    DropdownButton,
    Navigate,
    PopupMenuButton,
    RaisedButton,
    Screen,
    Slider,
    Switch,
    TextField,
    activity,
    animate,
    animate_elevation,
    app,
    app_config,
    button,
    card,
    color_state,
    container,
    dp,
    fade_in,
    gradient,
    horizontal_scroll_view,
    icon,
    list_view,
    on_change,
    on_click,
    on_focus_change,
    on_item_selected,
    on_menu_item_selected,
    on_text_change,
    parallel,
    progress_bar,
    radio,
    radio_group,
    scale,
    scroll_view,
    sequence,
    sp,
    style,
    text,
    theme,
    translate,
    ui,
    view,
)


def _emit_smali(tmp_path, phase_name: str, *activity_args):
    prog = app(activity("MainActivity", *activity_args)).build()
    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / phase_name,
        class_name="LTest;",
    )
    smali_root = out_dir / "smali"
    smali_text = "\n".join(
        p.read_text(encoding="utf-8")
        for p in sorted(smali_root.rglob("*.smali"))
    )
    return prog, out_dir, smali_text


def _smali_path(out_dir: Path, class_desc: str) -> Path:
    rel = class_desc[1:-1].replace("/", "/") + ".smali"
    return out_dir / "smali" / rel


def test_phase1_integration_smoke(tmp_path):
    _, _, smali = _emit_smali(
        tmp_path,
        "phase1",
        ui(
            text("Label", id="label", font_family="sans-serif", font_weight=700, letter_spacing=0.08, max_lines=1, ellipsize="end"),
            button("Button", id="btn", all_caps=True, text_alignment="center"),
            RaisedButton("Raised", id="raised", font_style="italic"),
            radio("R", id="radio1", line_height=sp(20)),
            Checkbox("C", id="check1", text_size=sp(14)),
            Switch("S", id="switch1", text_color="#FF223344"),
        ),
    )

    assert "Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V" in smali
    assert "Landroid/widget/TextView;->setLetterSpacing(F)V" in smali
    assert "Landroid/widget/TextView;->setLineSpacing(FF)V" in smali
    assert "Landroid/view/View;->setTextAlignment(I)V" in smali
    assert "Landroid/widget/TextView;->setAllCaps(Z)V" in smali
    assert "Landroid/widget/TextView;->setMaxLines(I)V" in smali
    assert "Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V" in smali


def test_phase2_integration_smoke(tmp_path):
    _, _, smali = _emit_smali(
        tmp_path,
        "phase2",
        ui(
            Slider(
                id="seek",
                value=35,
                thumb_tint="#FFAA0000",
                progress_tint="#FF00AA00",
                track_tint="#FF0000AA",
            ),
            progress_bar(id="progress", value=70, progress_tint="#FF8844CC"),
            Switch("Switch", id="sw", thumb_tint="#FFEECC00", track_tint="#FF333333"),
            Checkbox("Check", id="cb", button_tint="#FF00CCFF"),
            button("Tinted", id="btn", tint="#FF123456"),
        ),
    )

    assert "Landroid/widget/SeekBar;->setThumbTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/SeekBar;->setProgressTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/SeekBar;->setProgressBackgroundTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/ProgressBar;->setProgressTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/ProgressBar;->setIndeterminateTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/Switch;->setThumbTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/Switch;->setTrackTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/CompoundButton;->setButtonTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/view/View;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V" in smali


def test_phase3_integration_smoke(tmp_path):
    cs = color_state(default="#FF102030", pressed="#FF203040", disabled="#FF304050")
    _, _, smali = _emit_smali(
        tmp_path,
        "phase3",
        ui(
            text("Stateful", id="t", text_color=cs),
            Slider(id="seek_cs", value=20, progress_tint=cs, thumb_tint=cs, track_tint=cs),
            Checkbox("Stateful check", id="cb_cs", button_tint=cs),
            button("Tinted", id="btn_cs", tint=cs),
        ),
    )

    assert "Landroid/content/res/ColorStateList;-><init>([[I[I)V" in smali
    assert "Landroid/widget/TextView;->setTextColor(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/SeekBar;->setProgressTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/CompoundButton;->setButtonTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/view/View;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V" in smali


def test_phase4_integration_smoke(tmp_path):
    prog, out_dir, smali = _emit_smali(
        tmp_path,
        "phase4",
        ui(
            text("Status", id="status"),
            Switch("S", id="toggle"),
            TextField("", id="input"),
            DropdownButton(id="choices", items=["A", "B"]),
            PopupMenuButton("Menu", id="menu", items=["X", "Y"]),
        ),
        on_change("toggle", []),
        on_text_change("input", []),
        on_item_selected("choices", []),
        on_focus_change("input", []),
        on_menu_item_selected("menu", []),
    )

    assert "Landroid/widget/CompoundButton;->setOnCheckedChangeListener" in smali
    assert "Landroid/widget/TextView;->addTextChangedListener(Landroid/text/TextWatcher;)V" in smali
    assert "Landroid/widget/AdapterView;->setOnItemSelectedListener" in smali
    assert "Landroid/view/View;->setOnFocusChangeListener" in smali
    assert "Landroid/widget/PopupMenu;->setOnMenuItemClickListener" in smali
    assert _smali_path(out_dir, "Lcom/ahnali/preview/AhnaliChangeListener_toggle;").exists()
    assert _smali_path(out_dir, "Lcom/ahnali/preview/AhnaliTextChangeListener_input;").exists()
    assert _smali_path(out_dir, "Lcom/ahnali/preview/AhnaliItemSelectedListener_choices;").exists()
    assert _smali_path(out_dir, "Lcom/ahnali/preview/AhnaliFocusChangeListener_input;").exists()
    assert _smali_path(out_dir, "Lcom/ahnali/preview/AhnaliMenuItemListener_menu;").exists()
    assert any(entry[3] == "menu_item_selected" for entry in prog.support_classes)


def test_phase5_integration_smoke(tmp_path):
    _, _, smali = _emit_smali(
        tmp_path,
        "phase5",
        ui(
            TextField(
                "",
                id="input_cfg",
                input_type="email",
                ime_options="done|no_fullscreen",
                max_length=32,
                single_line=True,
                password=True,
                auto_capitalize="words",
            )
        ),
    )

    assert "Landroid/widget/TextView;->setInputType(I)V" in smali
    assert "Landroid/widget/TextView;->setImeOptions(I)V" in smali
    assert "Landroid/widget/TextView;->setFilters([Landroid/text/InputFilter;)V" in smali
    assert "Landroid/widget/TextView;->setSingleLine(Z)V" in smali
    assert "Landroid/widget/TextView;->setTransformationMethod(Landroid/text/method/TransformationMethod;)V" in smali


def test_phase6_integration_smoke(tmp_path):
    _, _, smali = _emit_smali(
        tmp_path,
        "phase6",
        ui(
            text("Accessible", id="label", content_description="Accessible label"),
            view(
                id="box",
                width=24,
                height=24,
                accessibility_label="Decorative box",
                important_for_accessibility="no_hide_descendants",
            ),
        ),
    )

    assert "Landroid/view/View;->setContentDescription(Ljava/lang/CharSequence;)V" in smali
    assert "Landroid/view/View;->setImportantForAccessibility(I)V" in smali


def test_phase7_integration_smoke(tmp_path):
    _, _, smali = _emit_smali(
        tmp_path,
        "phase7",
        ui(
            AppBar("Top", id="top", elevation=dp(4), inline=True),
            container(
                card(
                    text(
                        "Shadow",
                        id="shadow_text",
                        text_shadow_color="#66000000",
                        text_shadow_radius=dp(2),
                        text_shadow_dx=dp(1),
                        text_shadow_dy=dp(1),
                        elevation=dp(1),
                    ),
                    id="card_a",
                    elevation=dp(2),
                ),
                id="container_a",
                elevation=dp(1),
            ),
            button("Elevate", id="btn_elev", elevation=dp(3), pressed_elevation=dp(7)),
        ),
    )

    assert "Landroid/view/View;->setElevation(F)V" in smali
    assert "Landroid/widget/TextView;->setShadowLayer(FFFI)V" in smali
    assert "Landroid/animation/StateListAnimator;->addState([ILandroid/animation/Animator;)V" in smali
    assert "Landroid/view/View;->setStateListAnimator(Landroid/animation/StateListAnimator;)V" in smali


def test_phase8_integration_smoke(tmp_path):
    _, _, smali = _emit_smali(
        tmp_path,
        "phase8",
        app_config(min_sdk=31),
        ui(
            container(
                view(
                    id="fx",
                    width=64,
                    height=64,
                    background=gradient("#FF111111", "#FF444444", "top_to_bottom"),
                    opacity=0.75,
                    border_width=dp(2),
                    border_color="#FFFF0000",
                    border_radius=(dp(4), dp(8), dp(12), dp(16)),
                    ripple_color="#33000000",
                    clip_to_outline=True,
                    rotation=12.0,
                    scale_x=1.1,
                    scale_y=0.9,
                    translation_x=6.0,
                    translation_y=-4.0,
                    blur_radius=dp(6),
                ),
                id="fx_parent",
                clip_children=False,
            ),
        ),
    )

    assert "Landroid/view/View;->setAlpha(F)V" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setColors([I)V" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setStroke(II)V" in smali
    assert "Landroid/graphics/drawable/GradientDrawable;->setCornerRadii([F)V" in smali
    assert "Landroid/graphics/drawable/RippleDrawable;-><init>" in smali
    assert "Landroid/view/View;->setClipToOutline(Z)V" in smali
    assert "Landroid/view/ViewGroup;->setClipChildren(Z)V" in smali
    assert "Landroid/view/View;->setRotation(F)V" in smali
    assert "Landroid/view/View;->setScaleX(F)V" in smali
    assert "Landroid/view/View;->setScaleY(F)V" in smali
    assert "Landroid/view/View;->setTranslationX(F)V" in smali
    assert "Landroid/view/View;->setTranslationY(F)V" in smali
    assert "Landroid/graphics/RenderEffect;->createBlurEffect" in smali
    assert "Landroid/view/View;->setRenderEffect(Landroid/graphics/RenderEffect;)V" in smali


def test_phase9_integration_smoke(tmp_path):
    prog, _, smali = _emit_smali(
        tmp_path,
        "phase9",
        ui(
            Screen(
                "First",
                view(id="box", width=40, height=40),
                button("Animate", id="go"),
                button("Next", id="next"),
            ),
            Screen("Second", text("Second", id="second_label"), transition="slide_left"),
        ),
        on_click(
            "go",
            [
                animate("box", alpha=0.7, rotate=15, duration=120, delay=20, interpolator="linear"),
                animate_elevation("box", 6, duration=120),
                sequence(
                    fade_in("box", duration=60),
                    parallel(
                        translate("box", x=18, duration=90),
                        scale("box", value=1.15, duration=90),
                    ),
                ),
            ],
        ),
        on_click("next", [Navigate("Second")]),
    )

    assert "Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;" in smali
    assert "Landroid/view/ViewPropertyAnimator;->alpha(F)Landroid/view/ViewPropertyAnimator;" in smali
    assert "Landroid/animation/ObjectAnimator;->ofFloat(Ljava/lang/Object;Ljava/lang/String;[F)Landroid/animation/ObjectAnimator;" in smali
    assert "Landroid/animation/AnimatorSet;->playSequentially([Landroid/animation/Animator;)V" in smali
    assert "Landroid/animation/AnimatorSet;->playTogether([Landroid/animation/Animator;)V" in smali
    assert "Landroid/view/ViewPropertyAnimator;->translationX(F)Landroid/view/ViewPropertyAnimator;" in smali
    assert ".field public static nav_stack:[I" in smali
    assert ".field public static nav_current:I" in smali


def test_phase10_integration_smoke(tmp_path):
    prog, _, smali = _emit_smali(
        tmp_path,
        "phase10",
        theme(
            input=style(text_size=sp(18)),
            selector=style(button_tint="#FF88AA00"),
            progress=style(progress_tint="#FF2266CC"),
            icon=style(text_color="#FF334455"),
            container=style(background="#FF111111"),
            appbar=style(background="#FF222222"),
        ),
        ui(
            AppBar("Top", id="top", inline=True),
            TextField("", id="inp"),
            Checkbox("Pick", id="sel"),
            progress_bar(id="prog", value=30),
            icon("*", id="ic"),
            container(id="ctr"),
        ),
    )

    assert "Landroid/widget/TextView;->setTextSize(IF)V" in smali
    assert "Landroid/widget/CompoundButton;->setButtonTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/ProgressBar;->setProgressTintList(Landroid/content/res/ColorStateList;)V" in smali
    assert "Landroid/widget/TextView;->setTextColor(I)V" in smali
    assert "ctr_background_color" in prog.resource_colors
    assert "top_background_color" in prog.resource_colors


def test_phase11_integration_smoke(tmp_path):
    _, _, smali = _emit_smali(
        tmp_path,
        "phase11",
        ui(
            scroll_view(text("Inside scroll", id="sv_text"), id="sv"),
            horizontal_scroll_view(text("Inside horizontal", id="hsv_text"), id="hsv"),
        ),
    )

    assert ".field public static view_sv:Landroid/widget/ScrollView;" in smali
    assert ".field public static view_hsv:Landroid/widget/HorizontalScrollView;" in smali


def test_phase12_integration_smoke(tmp_path):
    prog, out_dir, smali = _emit_smali(
        tmp_path,
        "phase12",
        ui(
            list_view(
                id="todos",
                items=["Buy milk", "Ship build", 3, True],
            ),
        ),
    )

    assert ".field public static view_todos:Landroid/widget/ListView;" in smali
    assert "Landroid/widget/ListView;->setAdapter(Landroid/widget/ListAdapter;)V" in smali
    assert any(
        entry[0] == "Lcom/ahnali/preview/AhnaliListAdapter_todos;" and entry[3] == "list_adapter"
        for entry in prog.support_classes
    )
    assert _smali_path(out_dir, "Lcom/ahnali/preview/AhnaliListAdapter_todos;").exists()


def test_phase13_integration_smoke(tmp_path):
    prog, _, _ = _emit_smali(
        tmp_path,
        "phase13",
        app_config(min_sdk=30),
        ui(
            view(
                id="bordered",
                width=24,
                height=24,
                border_color="#FF00FF00",
            ),
            view(
                id="state_bg",
                width=24,
                height=24,
                background=color_state(default="#FF101010", pressed="#FF202020"),
            ),
            view(
                id="blur_box",
                width=24,
                height=24,
                blur_radius=4,
            ),
        ),
    )

    assert any("bordered.border_width" in warning for warning in prog.lint_warnings)
    assert any("state_bg.background" in warning for warning in prog.lint_warnings)
    assert any("blur_radius is ignored" in warning for warning in prog.lint_warnings)
