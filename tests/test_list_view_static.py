import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import ListView, activity, app, list_view, ui


def test_list_view_static_lowering_uses_list_view_and_array_adapter():
    prog = app(
        activity(
            "MainActivity",
            ui(
                list_view(
                    id="todos",
                    items=["Buy milk", "Ship build", 3, True],
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_todos:Landroid/widget/ListView;" in smali
    assert "Landroid/widget/ArrayAdapter;-><init>(Landroid/content/Context;I)V" in smali
    assert "Landroid/widget/ListView;->setAdapter(Landroid/widget/ListAdapter;)V" in smali
    assert "todos_item" in prog.resources


def test_list_view_class_shape_accepts_items_and_item_layout():
    prog = app(
        activity(
            "MainActivity",
            ui(
                ListView(
                    id="todos_class",
                    items=["A", "B"],
                    item_layout="simple_list_item_1",
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_todos_class:Landroid/widget/ListView;" in smali


def test_list_view_rejects_non_static_dataset_shape():
    with pytest.raises(RuntimeError, match="ListView items must be a list or tuple"):
        list_view(id="bad", items="not-a-list")

    with pytest.raises(RuntimeError, match="ListView items must contain only static primitive values"):
        list_view(id="bad2", items=[{"x": 1}])


def test_list_view_rejects_unknown_item_layout_name():
    with pytest.raises(RuntimeError, match="Unsupported ListView item_layout"):
        list_view(id="bad_layout", items=["A"], item_layout="custom_row")
