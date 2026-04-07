from alpha_pipeline import alpha_pipeline
from dsl.app import activity, app, button, on_click, state, text, ui


@on_click("float_btn")
def _show_float_conversion():
    ratio = float(count)
    label.text = str(ratio)


@on_click("int_btn")
def _show_int_conversion():
    whole = int(float(count))
    label.text = str(whole)


@on_click("type_btn")
def _show_type_name():
    values = ("a", "b")
    label.text = type(values)


@on_click("isinstance_btn")
def _show_isinstance_result():
    values = {"a", "b"}
    label.text = str(isinstance(values, set))


def test_float_conversion_and_stringification_lower_cleanly():
    prog = app(
        activity(
            "MainActivity",
            state(count=7),
            ui(text("Init", id="label"), button("Float", id="float_btn")),
            _show_float_conversion,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "int-to-float" in merged
    assert "Ljava/lang/String;->valueOf(F)Ljava/lang/String;" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_nested_int_float_conversion_lowers_cleanly():
    prog = app(
        activity(
            "MainActivity",
            state(count=9),
            ui(text("Init", id="label"), button("Int", id="int_btn")),
            _show_int_conversion,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "int-to-float" in merged
    assert "float-to-int" in merged
    assert "Ljava/lang/String;->valueOf(I)Ljava/lang/String;" in merged


def test_type_builtin_lowers_to_supported_type_name_string():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Type", id="type_btn")),
            _show_type_name,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "TupleWrapperRuntime" in merged
    assert "Ljava/lang/CharSequence;" in merged
    assert "type" not in merged.lower() or "type(" not in merged


def test_isinstance_builtin_lowers_to_int_result_and_stringifies():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Is", id="isinstance_btn")),
            _show_isinstance_result,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "SetWrapperRuntime" in merged
    assert "Ljava/lang/String;->valueOf(I)Ljava/lang/String;" in merged
