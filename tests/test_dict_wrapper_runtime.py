from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import activity, app, button, on_click, text, ui


@on_click("count_dict_btn")
def _count_dict_items():
    mapping = {"a": 1, "b": 2}
    total = len(mapping)
    label.text = f"Entries: {total}"


@on_click("count_dict_string_btn")
def _count_dict_string_items():
    names = {"first": "Ada", "second": "Linus"}
    label.text = f"Names: {len(names)}"


def test_dict_literal_and_len_lower_to_dict_wrapper_runtime_calls():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Dict", id="count_dict_btn"),
            ),
            _count_dict_items,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/DictWrapperRuntime;->create()Ljava/util/HashMap;" in merged
    assert (
        "Lcom/ahnali/runtime/DictWrapperRuntime;->putInt("
        "Ljava/util/HashMap;Ljava/lang/String;I)V"
    ) in merged
    assert "Lcom/ahnali/runtime/DictWrapperRuntime;->size(Ljava/util/HashMap;)I" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_dict_literal_with_string_values_uses_string_helper_and_fstring_len():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Dict Strings", id="count_dict_string_btn"),
            ),
            _count_dict_string_items,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/DictWrapperRuntime;->putString("
        "Ljava/util/HashMap;Ljava/lang/String;Ljava/lang/String;)V"
    ) in merged
    assert "Lcom/ahnali/runtime/DictWrapperRuntime;->size(Ljava/util/HashMap;)I" in merged


def test_build_dir_emits_dict_wrapper_runtime_helper(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Count Dict", id="count_dict_btn"),
            ),
            _count_dict_items,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "DictWrapperRuntime.smali"
    assert helper_path.exists()
    smali_text = helper_path.read_text(encoding="utf-8")
    assert ".method public static create()Ljava/util/HashMap;" in smali_text
    assert ".method public static putString(Ljava/util/HashMap;Ljava/lang/String;Ljava/lang/String;)V" in smali_text
    assert ".method public static putInt(Ljava/util/HashMap;Ljava/lang/String;I)V" in smali_text
    assert ".method public static size(Ljava/util/HashMap;)I" in smali_text
