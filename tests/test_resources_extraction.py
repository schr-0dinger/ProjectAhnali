from alpha_pipeline import alpha_pipeline
from dsl.app import app, activity, ui, on_click, state
from dsl.widgets import AppBar, Button, Text, TextField


def test_widget_strings_extracted_to_resources_and_loaded_via_getstring():
    prog = app(
        activity(
            "MainActivity",
            ui(
                AppBar("Widget Zoo"),
                Text("Hello", id="label"),
                Button("Go", id="go"),
                TextField("", id="input", hint="Type something"),
            ),
        )
    ).build()

    values = set(prog.resources.values())
    assert "Widget Zoo" in values
    assert "Hello" in values
    assert "Go" in values
    assert "Type something" in values

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/content/res/Resources;->getString(I)Ljava/lang/String;" in smali
    assert "Landroid/content/res/Resources;->getIdentifier" not in smali
    assert '"Hello"' not in smali
    assert '"Go"' not in smali


@on_click("go")
def _go():
    toast("Saved")
    simple_dialog("Done", "Saved successfully")


def test_click_handler_literals_are_resource_backed():
    prog = app(
        activity(
            "MainActivity",
            ui(Button("Go", id="go")),
            _go,
        )
    ).build()

    values = set(prog.resources.values())
    assert "Saved" in values
    assert "Done" in values
    assert "Saved successfully" in values
    assert prog.resource_ids

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/content/res/Resources;->getString(I)Ljava/lang/String;" in smali
    assert '"Saved"' not in smali
    assert '"Done"' not in smali


@on_click("go")
def _fmt():
    label.text = f"Count: {count} step {step}"


def test_fstring_static_fragments_are_resource_backed():
    prog = app(
        activity(
            "MainActivity",
            state(count=0, step=1),
            ui(
                Text("x", id="label"),
                Button("Go", id="go"),
            ),
            _fmt,
        )
    ).build()

    values = set(prog.resources.values())
    assert "Count: " in values
    assert " step " in values

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/content/res/Resources;->getString(I)Ljava/lang/String;" in smali
    assert '"Count: "' not in smali
    assert '" step "' not in smali


def test_widget_style_values_extracted_to_typed_resources():
    prog = app(
        activity(
            "MainActivity",
            ui(
                Text(
                    "Styled",
                    id="label",
                    text_color="#112233",
                    background="#FFEEDDCC",
                    text_size=18,
                    padding=12,
                    margin=8,
                    radius=10,
                ),
            ),
        )
    ).build()

    assert prog.resource_colors
    assert prog.resource_dimens
    assert any(v.endswith("px") or v.endswith("sp") for v in prog.resource_dimens.values())

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/content/res/Resources;->getColor(I)I" in smali
    assert "Landroid/content/res/Resources;->getDimensionPixelSize(I)I" in smali
    assert "Landroid/content/res/Resources;->getDimension(I)F" in smali
    assert "Landroid/widget/TextView;->setTextSize(IF)V" in smali


@on_click("go")
def _snack():
    snackbar("Saved")


def test_snackbar_uses_material_when_available_with_toast_fallback():
    prog = app(
        activity(
            "MainActivity",
            ui(Button("Go", id="go")),
            _snack,
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/widget/Toast;->makeText" in smali
    assert "Lcom/google/android/material/snackbar/Snackbar;->make" not in smali
