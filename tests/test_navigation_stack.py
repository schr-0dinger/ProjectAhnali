from alpha_pipeline import alpha_pipeline
from dsl.app import app, activity, ui, Screen, on_click, Navigate, Back, Replace, text, button


@on_click("go")
def go():
    Navigate("Second")


@on_click("back")
def back_btn():
    Back()


@on_click("rep")
def rep():
    Replace("Second")


def test_navigation_stack_fields_and_handlers():
    prog = app(
        activity(
            "MainActivity",
            ui(
                Screen(
                    "First",
                    button("Go", id="go"),
                    button("Back", id="back"),
                    button("Rep", id="rep"),
                ),
                Screen("Second", text("Two", id="t2")),
            ),
            go,
            back_btn,
            rep,
        )
    )

    result = alpha_pipeline(prog.build())
    smali = result["smali_class"]
    assert ".field public static nav_stack:[I" in smali
    assert ".field public static nav_size:I" in smali
    assert ".field public static nav_current:I" in smali
    handlers = "\n".join(result.get("extra_smali_classes", {}).values())
    merged = smali + "\n" + handlers
    assert "setVisibility" in merged
