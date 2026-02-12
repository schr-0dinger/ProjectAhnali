import pytest

from dsl.app import app, activity, app_config, ui, Screen
from dsl.widgets import Constraint, Text
from dsl.api import on_click
from dsl.widgets import Button, snackbar


def test_constraint_in_screen_requires_declared_dep_by_default():
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
    with pytest.raises(RuntimeError, match="Missing declared dependencies: \\[constraintlayout\\]"):
        prog.build()


def test_constraint_in_screen_with_explicit_dep_builds():
    prog = app(
        activity(
            "MainActivity",
            app_config(deps=["constraintlayout"]),
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
    assert "constraintlayout-core" in (built.jar_allowlist or [])
    assert "collection" in (built.jar_allowlist or [])


@on_click("go")
def _show_snackbar():
    snackbar("Saved")


def test_constraint_in_screen_auto_deps_enabled_builds():
    prog = app(
        activity(
            "MainActivity",
            app_config(auto_deps=True),
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


def test_snackbar_requires_declared_material_dep_by_default():
    prog = app(
        activity(
            "MainActivity",
            ui(Button("Go", id="go")),
            _show_snackbar,
        )
    )
    with pytest.raises(RuntimeError, match="Missing declared dependencies: \\[material\\]"):
        prog.build()


def test_snackbar_with_explicit_material_dep_builds():
    prog = app(
        activity(
            "MainActivity",
            app_config(deps=["material"]),
            ui(Button("Go", id="go")),
            _show_snackbar,
        )
    )
    built = prog.build()
    assert "material" in (built.required_artifacts or [])
