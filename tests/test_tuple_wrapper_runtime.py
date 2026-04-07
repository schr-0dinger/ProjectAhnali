from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import activity, app, button, on_click, text, ui


@on_click("count_tuple_btn")
def _count_tuple_items():
    values = ("a", "b", "c")
    total = len(values)
    label.text = f"Tuple: {total}"


@on_click("count_tuple_int_btn")
def _count_tuple_int_items():
    numbers = (1, 2, 3, 4)
    label.text = f"Tuple ints: {len(numbers)}"


def test_tuple_literal_and_len_lower_to_tuple_wrapper_runtime_calls():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Tuple", id="count_tuple_btn"),
            ),
            _count_tuple_items,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/TupleWrapperRuntime;->create(I)[Ljava/lang/Object;" in merged
    assert (
        "Lcom/ahnali/runtime/TupleWrapperRuntime;->setString("
        "[Ljava/lang/Object;ILjava/lang/String;)V"
    ) in merged
    assert "Lcom/ahnali/runtime/TupleWrapperRuntime;->size([Ljava/lang/Object;)I" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_tuple_literal_with_ints_uses_boxing_helper_and_fstring_len():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Tuple Int", id="count_tuple_int_btn"),
            ),
            _count_tuple_int_items,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/TupleWrapperRuntime;->setInt("
        "[Ljava/lang/Object;II)V"
    ) in merged
    assert "Lcom/ahnali/runtime/TupleWrapperRuntime;->size([Ljava/lang/Object;)I" in merged


def test_build_dir_emits_tuple_wrapper_runtime_helper(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Tuple", id="count_tuple_btn"),
            ),
            _count_tuple_items,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "TupleWrapperRuntime.smali"
    assert helper_path.exists()
    smali_text = helper_path.read_text(encoding="utf-8")
    assert ".method public static create(I)[Ljava/lang/Object;" in smali_text
    assert ".method public static setString([Ljava/lang/Object;ILjava/lang/String;)V" in smali_text
    assert ".method public static setInt([Ljava/lang/Object;II)V" in smali_text
    assert ".method public static size([Ljava/lang/Object;)I" in smali_text
