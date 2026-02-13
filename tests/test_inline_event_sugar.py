from alpha_pipeline import alpha_pipeline
from dsl.app import app, activity, ui, button, Checkbox, on_click
import pytest


def _merged_smali(result):
    return result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())


def test_inline_on_click_button_sugar_compiles():
    prog = app(
        activity(
            "MainActivity",
            ui(
                button("Back", id="go_back", on_click=[]),
            ),
        )
    )

    smali = _merged_smali(alpha_pipeline(prog.build()))
    assert ".method public static onClick_go_back(Landroid/view/View;)V" in smali


def test_inline_on_change_checkbox_sugar_compiles():
    prog = app(
        activity(
            "MainActivity",
            ui(
                Checkbox("Accept", id="agree", on_change=[]),
            ),
        )
    )

    smali = _merged_smali(alpha_pipeline(prog.build()))
    assert ".method public static onChange_agree(Landroid/widget/CompoundButton;Z)V" in smali


def test_inline_and_explicit_duplicate_event_binding_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(
                button("Go", id="go", on_click=[]),
            ),
            on_click("go", []),
        )
    )

    with pytest.raises(RuntimeError, match="Duplicate event binding for click target 'go'"):
        prog.build()
