from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    on_click,
    storage_clear,
    storage_exists,
    storage_get,
    storage_put,
    storage_remove,
    text,
    ui,
)


@on_click("save_btn")
def _save_btn_handler():
    storage_put("greeting", "hello")


@on_click("load_btn")
def _load_btn_handler():
    msg = storage_get("greeting", "fallback")
    label.text = msg


@on_click("remove_btn")
def _remove_btn_handler():
    storage_remove("greeting")


@on_click("exists_btn")
def _exists_btn_handler():
    exists = storage_exists("greeting")
    label.text = exists


@on_click("clear_btn")
def _clear_btn_handler():
    storage_clear()


def test_track_c_wave1_storage_put_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(button("Save", id="save_btn")),
            _save_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->putString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave1_storage_get_lowers_to_runtime_helper_call_and_symbol_set_text():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(
                text("Init", id="label"),
                button("Load", id="load_btn"),
            ),
            _load_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->getString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_track_c_wave1_storage_remove_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(button("Remove", id="remove_btn")),
            _remove_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->remove("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged


def test_track_c_wave1_storage_exists_lowers_to_runtime_helper_call_and_symbol_set_text():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(
                text("Init", id="label"),
                button("Exists", id="exists_btn"),
            ),
            _exists_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->exists("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in merged
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in merged


def test_track_c_wave1_storage_clear_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(button("Clear", id="clear_btn")),
            _clear_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert (
        "Lcom/ahnali/runtime/StorageHelper;->clear("
        "Landroid/app/Activity;)I"
    ) in merged


def test_track_c_wave1_storage_put_requires_storage_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Save", id="save_btn")),
            _save_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Storage capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] storage_put requires Caps.Storage." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Storage]) to activity(...)." in str(exc)


@on_click("load_btn_no_caps")
def _load_btn_handler_no_caps():
    storage_get("greeting", "fallback")


def test_track_c_wave1_storage_get_requires_storage_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Load", id="load_btn_no_caps")),
            _load_btn_handler_no_caps,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Storage capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] storage_get requires Caps.Storage." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Storage]) to activity(...)." in str(exc)


def test_track_c_wave1_storage_remove_requires_storage_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Remove", id="remove_btn")),
            _remove_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Storage capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] storage_remove requires Caps.Storage." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Storage]) to activity(...)." in str(exc)


def test_track_c_wave1_storage_exists_requires_storage_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Init", id="label"),
                button("Exists", id="exists_btn"),
            ),
            _exists_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Storage capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] storage_exists requires Caps.Storage." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Storage]) to activity(...)." in str(exc)


def test_track_c_wave1_storage_clear_requires_storage_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Clear", id="clear_btn")),
            _clear_btn_handler,
        )
    )
    try:
        prog.build()
        raise AssertionError("Expected build() to fail when Storage capability is missing")
    except RuntimeError as exc:
        assert "[CapabilityError] storage_clear requires Caps.Storage." in str(exc)
        assert "Fix: add app_config(uses=[Caps.Storage]) to activity(...)." in str(exc)


def test_track_c_wave1_toolchain_emits_storage_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(button("Save", id="save_btn")),
            _save_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "StorageHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert (
        ".method public static putString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ) in helper_smali
    assert (
        ".method public static getString("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ) in helper_smali
    assert (
        ".method public static remove("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in helper_smali
    assert (
        ".method public static exists("
        "Landroid/app/Activity;Ljava/lang/String;)I"
    ) in helper_smali
    assert (
        ".method public static clear("
        "Landroid/app/Activity;)I"
    ) in helper_smali
    assert "Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;" in helper_smali
    assert (
        "Landroid/content/SharedPreferences;->contains("
        "Ljava/lang/String;)Z"
    ) in helper_smali
    assert (
        "Landroid/content/SharedPreferences$Editor;->remove("
        "Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;"
    ) in helper_smali
    assert (
        "Landroid/content/SharedPreferences$Editor;->clear()"
        "Landroid/content/SharedPreferences$Editor;"
    ) in helper_smali
