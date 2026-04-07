from dsl.analyzer import analyze_features, select_runtime_modules
from dsl.app import activity, app, app_config, button, on_click, text, ui
from dsl.capabilities import Caps


def test_analyze_features_detects_phase1_python_signals():
    source = """
import android.widget
from java.util import ArrayList

class Demo:
    pass

async def loader(items):
    values = [1, 2, 3]
    mapping = {"a": 1}
    flags = {1, 2}
    pair = (1, 2)
    for item in values:
        if item > 0:
            print(str(item))
    value = getattr(items, "name")
    await fetch()
    return mapping
"""

    profile = analyze_features(source)

    assert profile.collections["list"] is True
    assert profile.collections["dict"] is True
    assert profile.collections["set"] is True
    assert profile.collections["tuple"] is True
    assert profile.control_flow["for"] is True
    assert profile.control_flow["if"] is True
    assert profile.functions["def"] is True
    assert profile.functions["return"] is True
    assert profile.classes["class"] is True
    assert profile.async_features["async_def"] is True
    assert profile.async_features["await"] is True
    assert profile.introspection["getattr"] is True
    assert profile.imports["import"] is True
    assert profile.imports["import_from"] is True
    assert profile.android_api["android_import"] is True
    assert profile.android_api["java_import"] is True


def test_select_runtime_modules_maps_profile_to_runtime_modules():
    source = """
import android.widget

async def loader():
    items = [1, 2]
    data = {"a": 1}
    pair = (1, 2)
    names = {1, 2}
    value = getattr(items, "append")
    await fetch()
    return items
"""

    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "core.static" in names
    assert "python.collections.list_wrapper" in names
    assert "python.collections.dict_wrapper" in names
    assert "python.collections.set_wrapper" in names
    assert "python.collections.tuple_wrapper" in names
    assert "python.introspection.reflection" in names
    assert "python.async.async_runtime" in names
    assert "python.imports.static_loader" in names


def test_phase3_android_bindings_are_detected_and_selected():
    source = """
def launch():
    uri = android_uri_parse("https://ahnali.dev")
    intent = android_intent_view(uri)
    chooser = android_intent_chooser(intent, "Open with")
    android_start_activity(chooser)
"""

    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert profile.android_api["uri_binding"] is True
    assert profile.android_api["intent_binding"] is True
    assert profile.android_api["activity_binding"] is True
    assert "android.bindings.uri" in names
    assert "android.bindings.intent" in names
    assert "android.bindings.activity" in names


@on_click("open_btn")
def _open_docs_for_phase3_runtime_plan():
    uri = android_uri_parse("https://ahnali.dev")
    intent = android_intent_view(uri)
    chooser = android_intent_chooser(intent, "Open with")
    android_start_activity(chooser)


def test_app_build_attaches_phase1_runtime_plan_metadata():
    spec = app(
        activity(
            "MainActivity",
            app_config(mode="reactive", uses=[Caps.Networking]),
            ui(text("Hello", id="label")),
        )
    )

    program = spec.build()

    assert program.feature_usage_profile.source_kind == "merged"
    assert program.feature_usage_profile.runtime["reactive_mode"] is True
    assert program.feature_usage_profile.capabilities == ("Networking",)
    assert "core.static" in program.runtime_module_names
    assert "app.mode.reactive" in program.runtime_module_names
    assert "capability.Networking" in program.runtime_module_names


def test_app_build_attaches_phase3_android_binding_metadata():
    spec = app(
        activity(
            "MainActivity",
            ui(
                text("Hello", id="label"),
                button("Open", id="open_btn"),
            ),
            _open_docs_for_phase3_runtime_plan,
        )
    )

    program = spec.build()

    assert program.feature_usage_profile.android_api["uri_binding"] is True
    assert program.feature_usage_profile.android_api["intent_binding"] is True
    assert program.feature_usage_profile.android_api["activity_binding"] is True
    assert "android.bindings.uri" in program.runtime_module_names
    assert "android.bindings.intent" in program.runtime_module_names
    assert "android.bindings.activity" in program.runtime_module_names
