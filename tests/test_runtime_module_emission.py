from apk.toolchain import emit_build_dir_from_program
from dsl.analyzer import analyze_features, select_runtime_modules
from dsl.app import activity, app, app_config, button, on_click, text, ui


@on_click("go")
def _reactive_click_handler():
    if True:
        label.text = "clicked"


def test_runtime_selector_returns_reflection_runtime_helper_spec():
    profile = analyze_features(
        """
def handler(obj):
    return getattr(obj, "name")
"""
    )
    modules = select_runtime_modules(profile)
    reflection = next(module for module in modules if module.name == "python.introspection.reflection")
    assert reflection.helper_class_desc == "Lcom/ahnali/runtime/ReflectionRuntime;"
    assert reflection.helper_method == "getText"
    assert reflection.helper_sig == "(Landroid/widget/TextView;)Ljava/lang/String;"


def test_emit_build_dir_emits_selected_reactive_runtime_module_helper(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            app_config(mode="reactive"),
            ui(text("Init", id="label"), button("Go", id="go")),
            _reactive_click_handler,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "ReactiveRuntime.smali"
    assert helper_path.exists()
    smali_text = helper_path.read_text(encoding="utf-8")
    assert ".class public final Lcom/ahnali/runtime/ReactiveRuntime;" in smali_text
    assert ".method public static init()V" in smali_text
