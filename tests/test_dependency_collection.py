from dsl.app import app, activity, ui, Screen
from dsl.widgets import Constraint, Text
from dsl.api import on_click
from dsl.widgets import Button, snackbar


def test_constraint_in_screen_requires_aar():
    prog = app(
        activity(
            "MainActivity",
            ui(
                Screen(
                    "Home",
                    Constraint(
                        Text("Hello", id="t"),
                    ),
                )
            ),
        )
    )
    built = prog.build()
    assert "constraintlayout" in (built.required_artifacts or [])


@on_click("go")
def _show_snackbar():
    snackbar("Saved")


def test_snackbar_requires_material_aar():
    prog = app(
        activity(
            "MainActivity",
            ui(Button("Go", id="go")),
            _show_snackbar,
        )
    )
    built = prog.build()
    assert "material" in (built.required_artifacts or [])
