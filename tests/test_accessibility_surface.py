import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import activity, app, image, text, ui, view


def _build_program(*items):
    return app(activity("MainActivity", ui(*items)))


def _build_smali(*items):
    prog = _build_program(*items).build()
    return alpha_pipeline(prog)["smali_class"]


def test_accessibility_content_description_lowers_for_generic_view():
    smali = _build_smali(
        view(
            id="box",
            width=8,
            height=8,
            content_description="Decorative box",
        )
    )

    assert "Landroid/view/View;->setContentDescription(Ljava/lang/CharSequence;)V" in smali


def test_accessibility_label_alias_lowers_for_text_and_image():
    prog = _build_program(
        text("Label", id="label", accessibility_label="Greeting label"),
        image(id="hero", src="ic_launcher", accessibility_label="Hero image"),
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/view/View;->setContentDescription(Ljava/lang/CharSequence;)V" in smali
    values = set(prog.resources.values())
    assert "Greeting label" in values
    assert "Hero image" in values


def test_accessibility_important_for_accessibility_lowers():
    smali = _build_smali(
        text("Label", id="label", important_for_accessibility="no_hide_descendants"),
    )
    assert "Landroid/view/View;->setImportantForAccessibility(I)V" in smali


def test_accessibility_invalid_important_for_accessibility_fails():
    prog = _build_program(
        text("Label", id="label", important_for_accessibility="blocked_mode"),
    )
    with pytest.raises(RuntimeError, match="Unsupported important_for_accessibility value"):
        prog.build()
