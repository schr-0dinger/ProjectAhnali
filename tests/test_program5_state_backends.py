import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    datastore_clear,
    datastore_exists,
    datastore_get,
    datastore_put,
    datastore_remove,
    encrypted_storage_clear,
    encrypted_storage_exists,
    encrypted_storage_get,
    encrypted_storage_put,
    encrypted_storage_remove,
    file_clear,
    file_exists,
    file_read,
    file_remove,
    file_write,
    on_click,
    room_clear,
    room_exists,
    room_get,
    room_put,
    room_remove,
    sqlite_clear,
    sqlite_exists,
    sqlite_get,
    sqlite_put,
    sqlite_remove,
    text,
    ui,
)


@on_click("datastore_btn")
def _datastore_handler():
    datastore_put("greeting", "hello")
    msg = datastore_get("greeting", "fallback")
    label.text = msg
    datastore_exists("greeting")
    datastore_remove("greeting")
    datastore_clear()


@on_click("file_btn")
def _file_handler():
    file_write("notes.txt", "hello")
    msg = file_read("notes.txt", "fallback")
    label.text = msg
    file_exists("notes.txt")
    file_remove("notes.txt")
    file_clear()


@on_click("sqlite_btn")
def _sqlite_handler():
    sqlite_put("session", "abc")
    msg = sqlite_get("session", "fallback")
    label.text = msg
    sqlite_exists("session")
    sqlite_remove("session")
    sqlite_clear()


@on_click("room_btn")
def _room_handler():
    room_put("profile", "ready")
    msg = room_get("profile", "fallback")
    label.text = msg
    room_exists("profile")
    room_remove("profile")
    room_clear()


@on_click("enc_btn")
def _encrypted_handler():
    encrypted_storage_put("token", "abc")
    msg = encrypted_storage_get("token", "fallback")
    label.text = msg
    encrypted_storage_exists("token")
    encrypted_storage_remove("token")
    encrypted_storage_clear()


def _build_state_backend_prog(handler):
    return app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Storage]),
            ui(
                text("Init", id="label"),
                button("Run", id=getattr(handler, "target_id", getattr(handler, "button_id", "")) or "run_btn"),
            ),
            handler,
        )
    ).build()


@pytest.mark.parametrize(
    "handler, expected_invokes",
    [
        (
            _datastore_handler,
            [
                "->dataStorePutString(",
                "->dataStoreGetString(",
                "->dataStoreExists(",
                "->dataStoreRemove(",
                "->dataStoreClear(",
            ],
        ),
        (
            _file_handler,
            [
                "->fileWriteString(",
                "->fileReadString(",
                "->fileExists(",
                "->fileRemove(",
                "->fileClear(",
            ],
        ),
        (
            _sqlite_handler,
            [
                "->sqlitePutString(",
                "->sqliteGetString(",
                "->sqliteExists(",
                "->sqliteRemove(",
                "->sqliteClear(",
            ],
        ),
        (
            _room_handler,
            [
                "->roomPutString(",
                "->roomGetString(",
                "->roomExists(",
                "->roomRemove(",
                "->roomClear(",
            ],
        ),
        (
            _encrypted_handler,
            [
                "->encryptedPutString(",
                "->encryptedGetString(",
                "->encryptedExists(",
                "->encryptedRemove(",
                "->encryptedClear(",
            ],
        ),
    ],
)
def test_program5_state_backend_calls_lower_to_storage_helper_methods(handler, expected_invokes):
    prog = _build_state_backend_prog(handler)
    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    for fragment in expected_invokes:
        assert "Lcom/ahnali/runtime/StorageHelper;" + fragment in merged


def test_program5_storage_helper_emits_program5_backend_methods(tmp_path):
    frontend = _build_state_backend_prog(_datastore_handler)
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "StorageHelper.smali"
    helper_smali = helper_path.read_text(encoding="utf-8")

    assert ".method public static dataStorePutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static fileWriteString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static sqlitePutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static roomPutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali
    assert ".method public static encryptedPutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in helper_smali


@on_click("no_caps")
def _no_caps_datastore_handler():
    datastore_put("k", "v")


def test_program5_datastore_requires_storage_capability():
    prog = app(activity("MainActivity", ui(button("Save", id="no_caps")), _no_caps_datastore_handler))
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] datastore_put requires Caps\.Storage\."):
        prog.build()


def _bad_datastore_put_arity_handler():
    datastore_put("only-key")


def _bad_file_read_default_handler():
    file_read("notes.txt", 1)


def _bad_sqlite_clear_arity_handler():
    sqlite_clear("extra")


def _bad_room_exists_key_handler():
    room_exists(9)


def _bad_encrypted_get_arity_handler():
    encrypted_storage_get("k", "d", "extra")


@pytest.mark.parametrize(
    "handler, pattern",
    [
        (_bad_datastore_put_arity_handler, "datastore_put expects exactly 2 string arguments"),
        (_bad_file_read_default_handler, "file_read argument 'default_value' must be a constant string"),
        (_bad_sqlite_clear_arity_handler, "sqlite_clear expects no arguments"),
        (_bad_room_exists_key_handler, "room_exists argument 'key' must be a constant string"),
        (_bad_encrypted_get_arity_handler, "encrypted_storage_get expects 1 or 2 string arguments"),
    ],
)
def test_program5_parser_rejects_invalid_state_backend_shapes(handler, pattern):
    with pytest.raises(RuntimeError, match=pattern):
        click_spec = on_click("run_btn")(handler)
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Storage]),
                ui(button("Run", id="run_btn")),
                click_spec,
            )
        ).build()
