from alpha_pipeline import alpha_pipeline
from dsl.app import activity, app, button, on_click, text, ui


@on_click("strip_btn")
def _show_strip_result():
    raw = "  Ahnali  "
    clean = raw.strip()
    label.text = clean


@on_click("replace_btn")
def _show_replace_and_upper_result():
    word = "ahnali"
    loud = word.replace("a", "A").upper()
    label.text = loud


@on_click("fmt_btn")
def _show_fstring_string_method_result():
    raw = "  Codex  "
    label.text = f"Name: {raw.strip()}"


@on_click("type_btn")
def _show_type_method_result():
    values = ("a", "b")
    label.text = type(values).upper()


@on_click("split_btn")
def _show_split_result():
    raw = "a,b,c"
    parts = raw.split(",")
    label.text = str(len(parts))


@on_click("join_btn")
def _show_join_result():
    values = ["A", "B", "C"]
    label.text = "-".join(values)


@on_click("chain_btn")
def _show_join_split_chain_result():
    label.text = "|".join("x,y".split(","))


def test_strip_method_lowers_to_trim_and_sets_text():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Strip", id="strip_btn")),
            _show_strip_result,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Ljava/lang/String;->trim()Ljava/lang/String;" in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_replace_and_upper_method_chain_lower_cleanly():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Replace", id="replace_btn")),
            _show_replace_and_upper_result,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;" in merged
    assert "Ljava/lang/String;->toUpperCase()Ljava/lang/String;" in merged


def test_string_method_is_supported_inside_fstring():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Fmt", id="fmt_btn")),
            _show_fstring_string_method_result,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Ljava/lang/String;->trim()Ljava/lang/String;" in merged
    assert "Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;" in merged


def test_upper_method_can_wrap_supported_type_result():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Type", id="type_btn")),
            _show_type_method_result,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "TupleWrapperRuntime" in merged
    assert "Ljava/lang/String;->toUpperCase()Ljava/lang/String;" in merged


def test_split_method_lowers_to_runtime_helper_and_len():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Split", id="split_btn")),
            _show_split_result,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "StringMethodsRuntime" in merged
    assert "->split(Ljava/lang/String;Ljava/lang/String;)Ljava/util/ArrayList;" in merged
    assert "ListWrapperRuntime;->size(Ljava/util/ArrayList;)I" in merged


def test_join_method_lowers_to_runtime_helper_for_list_symbol():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Join", id="join_btn")),
            _show_join_result,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "StringMethodsRuntime" in merged
    assert "->joinList(Ljava/lang/String;Ljava/util/ArrayList;)Ljava/lang/String;" in merged


def test_join_can_consume_nested_split_result():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Init", id="label"), button("Chain", id="chain_btn")),
            _show_join_split_chain_result,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "->split(Ljava/lang/String;Ljava/lang/String;)Ljava/util/ArrayList;" in merged
    assert "->joinList(Ljava/lang/String;Ljava/util/ArrayList;)Ljava/lang/String;" in merged
