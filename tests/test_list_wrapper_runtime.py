from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import activity, app, button, on_click, text, ui


@on_click("count_btn")
def _count_list_items():
    items = ["a", "b", "c"]
    count = len(items)
    label.text = f"Count: {count}"


@on_click("count_int_btn")
def _count_int_list_items():
    values = [1, 2, 3, 4]
    label.text = f"Values: {len(values)}"


def test_list_literal_and_len_lower_to_list_wrapper_runtime_calls():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count", id="count_btn"),
            ),
            _count_list_items,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/ListWrapperRuntime;->create()Ljava/util/ArrayList;" in merged
    assert (
        "Lcom/ahnali/runtime/ListWrapperRuntime;->addString("
        "Ljava/util/ArrayList;Ljava/lang/String;)V"
    ) in merged
    assert "Lcom/ahnali/runtime/ListWrapperRuntime;->size(Ljava/util/ArrayList;)I" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_list_literal_with_ints_uses_boxing_helper_and_fstring_len():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Int", id="count_int_btn"),
            ),
            _count_int_list_items,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/ListWrapperRuntime;->addInt("
        "Ljava/util/ArrayList;I)V"
    ) in merged
    assert "Lcom/ahnali/runtime/ListWrapperRuntime;->size(Ljava/util/ArrayList;)I" in merged


def test_build_dir_emits_list_wrapper_runtime_helper(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count", id="count_btn"),
            ),
            _count_list_items,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "ListWrapperRuntime.smali"
    assert helper_path.exists()
    smali_text = helper_path.read_text(encoding="utf-8")
    assert ".method public static create()Ljava/util/ArrayList;" in smali_text
    assert ".method public static addString(Ljava/util/ArrayList;Ljava/lang/String;)V" in smali_text
    assert ".method public static addInt(Ljava/util/ArrayList;I)V" in smali_text
    assert ".method public static size(Ljava/util/ArrayList;)I" in smali_text
