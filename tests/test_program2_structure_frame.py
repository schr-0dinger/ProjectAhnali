import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import activity, app, button, frame, row, text, ui
from ir.expr import Var
from ir.stmt import CallStmt


def test_program2_frame_layout_lowers_to_android_frame_layout():
    prog = app(
        activity(
            "MainActivity",
            ui(
                frame(
                    text("Top", id="top_text"),
                    button("Action", id="cta_btn"),
                    id="shell",
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_shell:Landroid/widget/FrameLayout;" in smali


def test_program2_layout_gravity_emits_linear_and_frame_layout_params_gravity_field():
    prog = app(
        activity(
            "MainActivity",
            ui(
                row(
                    text("Linear child", id="linear_child", layout_gravity="end"),
                    id="row_shell",
                ),
                frame(
                    text("Frame child", id="frame_child", layout_gravity="center"),
                    id="frame_shell",
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/widget/LinearLayout$LayoutParams;->gravity:I" in smali
    assert "Landroid/widget/FrameLayout$LayoutParams;->gravity:I" in smali


def test_program2_z_index_orders_children_deterministically_within_parent():
    prog = app(
        activity(
            "MainActivity",
            ui(
                frame(
                    text("Front", id="front", z_index=10),
                    text("Back", id="back", z_index=0),
                    id="z_frame",
                ),
            ),
        )
    ).build()

    build_ui = next(m for m in prog.methods if m.name.startswith("buildUi_"))
    added_children = []
    for stmt in build_ui.body:
        if not isinstance(stmt, CallStmt):
            continue
        call = stmt.expr
        if getattr(call, "func_name", None) != "addView":
            continue
        if len(call.args) != 2:
            continue
        parent, child = call.args
        if isinstance(parent, Var) and parent.name == "z_frame" and isinstance(child, Var):
            added_children.append(child.name)

    assert added_children == ["back", "front"]


def test_program2_layout_gravity_rejects_bool_values():
    with pytest.raises(RuntimeError, match="Invalid gravity value"):
        app(
            activity(
                "MainActivity",
                ui(
                    row(
                        text("bad", id="bad", layout_gravity=True),
                        id="r",
                    ),
                ),
            )
        ).build()
