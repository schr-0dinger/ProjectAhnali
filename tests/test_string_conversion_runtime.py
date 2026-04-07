from alpha_pipeline import alpha_pipeline
from dsl.app import activity, app, button, on_click, state, text, ui


@on_click("show_count_str_btn")
def _show_count_as_str():
    label_text = str(count)
    label.text = label_text


@on_click("show_len_str_btn")
def _show_len_as_str():
    values = [1, 2, 3]
    label.text = str(len(values))


def test_str_assignment_from_int_symbol_lowers_to_string_valueof():
    prog = app(
        activity(
            "MainActivity",
            state(count=7),
            ui(
                text("Init", id="label"),
                button("Show", id="show_count_str_btn"),
            ),
            _show_count_as_str,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Ljava/lang/String;->valueOf(I)Ljava/lang/String;" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_direct_set_text_from_str_len_lowers_to_valueof_and_len_helper():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Show Len", id="show_len_str_btn"),
            ),
            _show_len_as_str,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/ListWrapperRuntime;->size(Ljava/util/ArrayList;)I" in merged
    assert "Ljava/lang/String;->valueOf(I)Ljava/lang/String;" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged
