import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import (
    HorizontalScrollView,
    NestedScrollView,
    ScrollView,
    activity,
    app,
    horizontal_scroll_view,
    nested_scroll_view,
    text,
    ui,
)


def test_scroll_view_lowers_to_android_scroll_view():
    prog = app(
        activity(
            "MainActivity",
            ui(
                ScrollView(
                    text("Inside", id="inside_text"),
                    id="sv",
                ),
            ),
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert ".field public static view_sv:Landroid/widget/ScrollView;" in smali


def test_horizontal_scroll_view_lowers_to_android_horizontal_scroll_view():
    prog = app(
        activity(
            "MainActivity",
            ui(
                horizontal_scroll_view(
                    text("Inside", id="inside_text"),
                    id="hsv",
                ),
            ),
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert ".field public static view_hsv:Landroid/widget/HorizontalScrollView;" in smali


def test_nested_scroll_view_lowers_to_androidx_nested_scroll_view():
    prog = app(
        activity(
            "MainActivity",
            ui(
                nested_scroll_view(
                    text("Inside", id="inside_text"),
                    id="nsv",
                ),
            ),
        )
    )

    smali = alpha_pipeline(prog.build())["smali_class"]
    assert ".field public static view_nsv:Landroidx/core/widget/NestedScrollView;" in smali


def test_scroll_views_require_single_direct_child():
    with pytest.raises(RuntimeError, match="requires exactly one direct child"):
        ScrollView(
            text("A", id="a"),
            text("B", id="b"),
            id="sv",
        )

    with pytest.raises(RuntimeError, match="requires exactly one direct child"):
        HorizontalScrollView(id="hsv")

    with pytest.raises(RuntimeError, match="requires exactly one direct child"):
        NestedScrollView(id="nsv")
