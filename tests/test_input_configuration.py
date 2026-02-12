import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import TextField, activity, app, ui


def _build_smali(*items):
    prog = app(activity("MainActivity", ui(*items))).build()
    return alpha_pipeline(prog)["smali_class"]


def test_text_field_input_configuration_lowers_to_expected_calls():
    smali = _build_smali(
        TextField(
            "",
            id="input",
            input_type="email",
            ime_options="done|no_fullscreen",
            max_length=24,
            single_line=True,
            password=True,
            auto_capitalize="words",
        )
    )

    assert "Landroid/widget/TextView;->setInputType(I)V" in smali
    assert "Landroid/widget/TextView;->setImeOptions(I)V" in smali
    assert "Landroid/widget/TextView;->setFilters([Landroid/text/InputFilter;)V" in smali
    assert "Landroid/widget/TextView;->setSingleLine(Z)V" in smali
    assert (
        "Landroid/text/method/PasswordTransformationMethod;->getInstance()"
        "Landroid/text/method/PasswordTransformationMethod;"
    ) in smali
    assert (
        "Landroid/widget/TextView;->setTransformationMethod"
        "(Landroid/text/method/TransformationMethod;)V"
    ) in smali
    assert "Landroid/text/InputFilter$LengthFilter;-><init>(I)V" in smali


def test_text_field_numeric_only_triggers_input_type_lowering():
    smali = _build_smali(TextField("", id="input", numeric_only=True))
    assert "Landroid/widget/TextView;->setInputType(I)V" in smali


def test_text_field_invalid_input_type_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(TextField("", id="input", input_type="unsupported_mode")),
        )
    )
    with pytest.raises(RuntimeError, match="Unsupported input_type"):
        prog.build()


def test_text_field_invalid_ime_options_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(TextField("", id="input", ime_options="done|unknown_option")),
        )
    )
    with pytest.raises(RuntimeError, match="Unsupported ime_options token"):
        prog.build()


def test_text_field_invalid_auto_capitalize_for_number_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(TextField("", id="input", input_type="number", auto_capitalize="words")),
        )
    )
    with pytest.raises(RuntimeError, match="auto_capitalize is only valid for text input types"):
        prog.build()


def test_text_field_negative_max_length_fails():
    prog = app(
        activity(
            "MainActivity",
            ui(TextField("", id="input", max_length=-1)),
        )
    )
    with pytest.raises(RuntimeError, match="max_length must be >= 0"):
        prog.build()
