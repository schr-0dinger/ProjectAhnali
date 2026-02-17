import pytest

from apk.toolchain import emit_build_dir_from_program
from alpha_pipeline import alpha_pipeline
from dsl.app import GridView, activity, app, grid_view, ui


def test_grid_view_static_lowering_uses_deterministic_generated_adapter():
    prog = app(
        activity(
            "MainActivity",
            ui(
                grid_view(
                    id="tiles",
                    items=["A", "B", 3, True],
                    num_columns=3,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_tiles:Landroid/widget/GridView;" in smali
    assert "Lcom/ahnali/preview/AhnaliListAdapter_tiles;" in smali
    assert "Landroid/widget/GridView;->setAdapter(Landroid/widget/ListAdapter;)V" in smali
    assert "Landroid/widget/GridView;->setNumColumns(I)V" in smali
    assert any(
        entry[0] == "Lcom/ahnali/preview/AhnaliListAdapter_tiles;" and entry[3] == "list_adapter"
        for entry in prog.support_classes
    )


def test_grid_view_class_shape_accepts_items_item_layout_and_num_columns():
    prog = app(
        activity(
            "MainActivity",
            ui(
                GridView(
                    id="tiles_class",
                    items=["A", "B"],
                    item_layout="simple_list_item_1",
                    num_columns=2,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_tiles_class:Landroid/widget/GridView;" in smali


def test_grid_view_rejects_invalid_dataset_and_num_columns():
    with pytest.raises(RuntimeError, match="GridView items must be a list or tuple"):
        grid_view(id="bad", items="not-a-list")

    with pytest.raises(RuntimeError, match="GridView items must contain only static primitive values"):
        grid_view(id="bad2", items=[{"x": 1}])

    with pytest.raises(RuntimeError, match="GridView num_columns must be an integer"):
        grid_view(id="bad_cols_type", items=["A"], num_columns="2")

    with pytest.raises(RuntimeError, match="GridView num_columns must be >= 1"):
        grid_view(id="bad_cols_val", items=["A"], num_columns=0)


def test_grid_view_rejects_unknown_item_layout_name():
    with pytest.raises(RuntimeError, match="Unsupported GridView item_layout"):
        grid_view(id="bad_layout", items=["A"], item_layout="custom_row")


def test_grid_view_rejects_non_default_item_layout_for_deterministic_adapter():
    prog = app(
        activity(
            "MainActivity",
            ui(
                grid_view(
                    id="custom_layout",
                    items=["A"],
                    item_layout=0x1090004,
                )
            ),
        )
    )
    with pytest.raises(RuntimeError, match="deterministic adapter path; use simple_list_item_1"):
        prog.build()


def test_grid_view_emits_adapter_support_class_with_holder_bind_logic(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                grid_view(
                    id="tiles_emit",
                    items=["A", "B", "C"],
                    num_columns=2,
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
        / "AhnaliListAdapter_tiles_emit.smali"
    )
    assert adapter_path.exists()
    adapter_smali = adapter_path.read_text(encoding="utf-8")
    assert ".super Landroid/widget/BaseAdapter;" in adapter_smali
    assert "Landroid/view/View;->setTag(Ljava/lang/Object;)V" in adapter_smali
    assert "Landroid/view/View;->getTag()Ljava/lang/Object;" in adapter_smali
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in adapter_smali
