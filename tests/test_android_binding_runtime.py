from alpha_pipeline import alpha_pipeline
from dsl.app import activity, app, button, on_click, text, ui


@on_click("open_btn")
def _open_docs_with_android_bindings():
    uri = android_uri_parse("https://ahnali.dev")
    intent = android_intent_view(uri)
    chooser = android_intent_chooser(intent, "Open with")
    android_start_activity(chooser)


@on_click("quick_btn")
def _open_docs_with_nested_android_bindings():
    android_start_activity(
        android_intent_chooser(
            android_intent_view(android_uri_parse("https://ahnali.dev/docs")),
            "Quick open",
        )
    )


def test_android_bindings_lower_to_uri_intent_and_start_activity_calls():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Open", id="open_btn"),
            ),
            _open_docs_with_android_bindings,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;" in merged
    assert "Landroid/content/Intent;-><init>(Ljava/lang/String;)V" in merged
    assert "Landroid/content/Intent;->setData(Landroid/net/Uri;)Landroid/content/Intent;" in merged
    assert "Landroid/content/Intent;->createChooser(Landroid/content/Intent;Ljava/lang/CharSequence;)Landroid/content/Intent;" in merged
    assert "Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V" in merged


def test_android_start_activity_supports_nested_binding_expressions():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Quick", id="quick_btn"),
            ),
            _open_docs_with_nested_android_bindings,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;" in merged
    assert "Landroid/content/Intent;->createChooser(Landroid/content/Intent;Ljava/lang/CharSequence;)Landroid/content/Intent;" in merged
    assert "Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V" in merged
