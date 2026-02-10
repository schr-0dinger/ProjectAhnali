from dsl.app import app, activity, ui, Screen
from dsl.widgets import Constraint, Text


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
