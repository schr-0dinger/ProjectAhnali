import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import (
    activity,
    app,
    app_config,
    bind_text,
    button,
    derived,
    observable,
    observable_get,
    on_click,
    set_observable,
    text,
    ui,
)


@on_click("run_btn")
def _static_reactive_handler():
    observable("greeting", "hello")
    bind_text("status_label", "greeting")


def test_reactive_mode_is_rejected_in_static_default_mode():
    with pytest.raises(RuntimeError, match=r"\[ReactiveModeError\].*app_config\(mode='reactive'\)"):
        app(
            activity(
                "MainActivity",
                ui(
                    text("Status", id="status_label"),
                    button("Run", id="run_btn"),
                ),
                _static_reactive_handler,
            )
        ).build()


def test_app_config_mode_rejects_invalid_values():
    with pytest.raises(RuntimeError, match="app_config mode must be 'static' or 'reactive'"):
        app_config(mode="dynamic")


@on_click("run_btn")
def _reactive_handler_basic():
    observable("greeting", "hello")
    bind_text("status_label", "greeting")
    set_observable("greeting", "world")


def test_reactive_mode_emits_reactive_fields_and_text_binding_calls():
    prog = app(
        activity(
            "MainActivity",
            app_config(mode="reactive"),
            ui(
                text("Status", id="status_label"),
                button("Run", id="run_btn"),
            ),
            _reactive_handler_basic,
        )
    ).build()

    assert getattr(prog, "app_mode", "") == "reactive"
    result = alpha_pipeline(prog)
    smali = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "rx_greeting:Ljava/lang/String;" in smali
    assert "world" in smali
    assert "setText" in smali


@on_click("run_btn")
def _reactive_handler_derived():
    observable("name", "ahnali")
    derived("name_label", "name", "Name: ", "!")
    value = observable_get("name_label", "n/a")
    status_label.text = value


def test_reactive_derived_and_observable_get_compile_deterministically():
    prog = app(
        activity(
            "MainActivity",
            app_config(mode="reactive"),
            ui(
                text("Status", id="status_label"),
                button("Run", id="run_btn"),
            ),
            _reactive_handler_derived,
        )
    ).build()
    result = alpha_pipeline(prog)
    smali = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    assert "rx_name_label:Ljava/lang/String;" in smali
    assert "Name: " in smali
    assert "Ljava/lang/String;->concat" in smali



def _bad_observable_arity_handler():
    observable("x")



def _bad_observable_type_handler():
    observable("x", True)



def _bad_bind_arity_handler():
    bind_text("status_label")



def _bad_derived_kw_type_handler():
    derived("a", "b", prefix=1)



def _bad_observable_get_type_handler():
    value = observable_get("x", 7)
    status_label.text = value



def _build_with_handler(handler):
    handler_spec = on_click("run_btn")(handler)
    return app(
        activity(
            "MainActivity",
            app_config(mode="reactive"),
            ui(
                text("Status", id="status_label"),
                button("Run", id="run_btn"),
            ),
            handler_spec,
        )
    )



def test_reactive_parser_rejects_invalid_shapes_and_types():
    with pytest.raises(RuntimeError, match="observable expects exactly 2 arguments"):
        _build_with_handler(_bad_observable_arity_handler)
    with pytest.raises(RuntimeError, match="observable argument 'initial' must be"):
        _build_with_handler(_bad_observable_type_handler)
    with pytest.raises(RuntimeError, match="bind_text expects exactly 2 string arguments"):
        _build_with_handler(_bad_bind_arity_handler)
    with pytest.raises(RuntimeError, match="derived keyword 'prefix' must be a constant string"):
        _build_with_handler(_bad_derived_kw_type_handler)
    with pytest.raises(RuntimeError, match="observable_get argument 'fallback' must be a constant string"):
        _build_with_handler(_bad_observable_get_type_handler)
