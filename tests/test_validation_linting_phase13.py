import pytest

from dsl.app import (
    Style,
    activity,
    animate,
    app,
    app_config,
    button,
    color_state,
    gradient,
    on_click,
    sp,
    state,
    text,
    ui,
    view,
)


def test_phase13_style_field_incompatible_with_widget_fails_with_widget_and_field():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view(
                    id="box",
                    width=24,
                    height=24,
                    style=Style(text_size=sp(14)),
                )
            ),
        )
    )
    with pytest.raises(
        RuntimeError,
        match=r"Incompatible style field 'text_size' on widget 'box'",
    ):
        prog.build()


def test_phase13_invalid_state_key_fails():
    prog = app(
        activity(
            "MainActivity",
            state(**{"bad-key": 1}),
            ui(text("ok", id="label")),
        )
    )
    with pytest.raises(RuntimeError, match=r"Invalid state key 'bad-key'"):
        prog.build()


@on_click("go")
def _anim_missing_target():
    animate("missing_target", alpha=0.7, duration=120)


def test_phase13_animation_target_id_not_found_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Go", id="go")),
            _anim_missing_target,
        )
    )
    with pytest.raises(RuntimeError, match=r"Unknown animation target 'missing_target'"):
        prog.build()


def test_phase13_invalid_gradient_color_config_fails_with_widget_field():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view(
                    id="grad_box",
                    width=32,
                    height=32,
                    background=gradient("not-a-color", "#FFFFFFFF", "left_to_right"),
                )
            ),
        )
    )
    with pytest.raises(
        RuntimeError,
        match=r"Invalid gradient config on 'grad_box\.background\.start'",
    ):
        prog.build()


def test_phase13_warns_for_degraded_fallback_behaviors():
    prog = app(
        activity(
            "MainActivity",
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
    ).build()

    assert any("bordered.border_width" in warning for warning in prog.lint_warnings)
    assert any("state_bg.background" in warning for warning in prog.lint_warnings)
    assert any("blur_radius is ignored" in warning for warning in prog.lint_warnings)
