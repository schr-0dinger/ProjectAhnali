import pytest

from apk.toolchain import emit_build_dir_from_program
from alpha_pipeline import alpha_pipeline
from dsl.app import ListView, activity, app, list_view, ui


def test_list_view_static_lowering_uses_deterministic_generated_adapter():
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
    assert "Lcom/ahnali/preview/AhnaliListAdapter_todos;" in smali
    assert "Landroid/widget/ListView;->setAdapter(Landroid/widget/ListAdapter;)V" in smali
    assert "todos_item" in prog.resources
    assert any(
        entry[0] == "Lcom/ahnali/preview/AhnaliListAdapter_todos;" and entry[3] == "list_adapter"
        for entry in prog.support_classes
    )


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


def test_list_view_rejects_non_default_item_layout_for_deterministic_adapter():
    prog = app(
        activity(
            "MainActivity",
            ui(
                list_view(
                    id="custom_layout",
                    items=["A"],
                    item_layout=0x1090004,
                )
            ),
        )
    )
    with pytest.raises(RuntimeError, match="deterministic adapter path; use simple_list_item_1"):
        prog.build()


def test_list_view_emits_adapter_support_class_with_holder_bind_logic(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                list_view(
                    id="todos_emit",
                    items=["A", "B", "C"],
                )
            ),
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_target_sig="(Landroid/app/Activity;)V",
    )

    adapter_path = (
        out_dir
        / "smali"
        / "com"
        / "ahnali"
        / "preview"
        / "AhnaliListAdapter_todos_emit.smali"
    )
    assert adapter_path.exists()
    adapter_smali = adapter_path.read_text(encoding="utf-8")
    assert ".super Landroid/widget/BaseAdapter;" in adapter_smali
    assert "Landroid/view/View;->setTag(Ljava/lang/Object;)V" in adapter_smali
    assert "Landroid/view/View;->getTag()Ljava/lang/Object;" in adapter_smali
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in adapter_smali
