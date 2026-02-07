from alpha_pipeline import alpha_pipeline
from dsl.app import app, activity, ui
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
    assert "Landroid/content/res/Resources;->getIdentifier" in smali
    assert "Landroid/content/res/Resources;->getString(I)Ljava/lang/String;" in smali
    assert '"Hello"' not in smali
    assert '"Go"' not in smali
