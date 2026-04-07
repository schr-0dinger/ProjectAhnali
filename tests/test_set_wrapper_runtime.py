from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import activity, app, button, on_click, text, ui


@on_click("count_set_btn")
def _count_set_items():
    values = {"a", "b", "c"}
    total = len(values)
    label.text = f"Unique: {total}"


@on_click("count_set_int_btn")
def _count_set_int_items():
    numbers = {1, 2, 3, 4}
    label.text = f"Numbers: {len(numbers)}"


def test_set_literal_and_len_lower_to_set_wrapper_runtime_calls():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Set", id="count_set_btn"),
            ),
            _count_set_items,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/SetWrapperRuntime;->create()Ljava/util/HashSet;" in merged
    assert (
        "Lcom/ahnali/runtime/SetWrapperRuntime;->addString("
        "Ljava/util/HashSet;Ljava/lang/String;)V"
    ) in merged
    assert "Lcom/ahnali/runtime/SetWrapperRuntime;->size(Ljava/util/HashSet;)I" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_set_literal_with_ints_uses_boxing_helper_and_fstring_len():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Set Int", id="count_set_int_btn"),
            ),
            _count_set_int_items,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/SetWrapperRuntime;->addInt("
        "Ljava/util/HashSet;I)V"
    ) in merged
    assert "Lcom/ahnali/runtime/SetWrapperRuntime;->size(Ljava/util/HashSet;)I" in merged


def test_build_dir_emits_set_wrapper_runtime_helper(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Set", id="count_set_btn"),
            ),
            _count_set_items,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "SetWrapperRuntime.smali"
    assert helper_path.exists()
    smali_text = helper_path.read_text(encoding="utf-8")
    assert ".method public static create()Ljava/util/HashSet;" in smali_text
    assert ".method public static addString(Ljava/util/HashSet;Ljava/lang/String;)V" in smali_text
    assert ".method public static addInt(Ljava/util/HashSet;I)V" in smali_text
    assert ".method public static size(Ljava/util/HashSet;)I" in smali_text
