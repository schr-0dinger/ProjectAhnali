import pytest

from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    check_connectivity,
    on_click,
    open_url,
    storage_clear,
    storage_exists,
    storage_get,
    storage_put,
    storage_remove,
    ui,
)


_ALL_WAVE1_CAPS = [Caps.URLLauncher, Caps.Connectivity, Caps.Storage]


def _build_with_handler(btn_id: str, handler):
    handler_spec = on_click(btn_id)(handler)
    return app(
        activity(
            "MainActivity",
            app_config(uses=_ALL_WAVE1_CAPS),
            ui(button("Run", id=btn_id)),
            handler_spec,
        )
    )


def _bad_open_url_arity_handler():
    open_url("https://example.com", "extra")


def test_track_c_wave1_parser_open_url_rejects_wrong_arity():
    with pytest.raises(RuntimeError, match="open_url expects exactly 1 string argument"):
        _build_with_handler("bad_open_url_arity", _bad_open_url_arity_handler)


def _bad_open_url_type_handler():
    open_url(123)


def test_track_c_wave1_parser_open_url_rejects_non_string_url():
    with pytest.raises(RuntimeError, match="open_url argument 'url' must be a constant string"):
        _build_with_handler("bad_open_url_type", _bad_open_url_type_handler)


def _bad_connectivity_args_handler():
    check_connectivity("unexpected")


def test_track_c_wave1_parser_check_connectivity_rejects_arguments():
    with pytest.raises(RuntimeError, match="check_connectivity expects no arguments"):
        _build_with_handler("bad_connectivity_args", _bad_connectivity_args_handler)


def _bad_storage_put_arity_handler():
    storage_put("only-key")


def test_track_c_wave1_parser_storage_put_rejects_wrong_arity():
    with pytest.raises(RuntimeError, match="storage_put expects exactly 2 string arguments"):
        _build_with_handler("bad_storage_put_arity", _bad_storage_put_arity_handler)


def _bad_storage_put_key_handler():
    storage_put(1, "value")


def test_track_c_wave1_parser_storage_put_rejects_non_string_key():
    with pytest.raises(RuntimeError, match="storage_put argument 'key' must be a constant string"):
        _build_with_handler("bad_storage_put_key", _bad_storage_put_key_handler)


def _bad_storage_get_arity_handler():
    value = storage_get("k", "d", "extra")
    preview = value


def test_track_c_wave1_parser_storage_get_rejects_wrong_arity():
    with pytest.raises(RuntimeError, match="storage_get expects 1 or 2 string arguments"):
        _build_with_handler("bad_storage_get_arity", _bad_storage_get_arity_handler)


def _bad_storage_get_default_handler():
    value = storage_get("k", 7)
    preview = value


def test_track_c_wave1_parser_storage_get_rejects_non_string_default():
    with pytest.raises(RuntimeError, match="storage_get argument 'default_value' must be a constant string"):
        _build_with_handler("bad_storage_get_default", _bad_storage_get_default_handler)


def _bad_storage_exists_arity_handler():
    value = storage_exists("k", "extra")
    preview = value


def test_track_c_wave1_parser_storage_exists_rejects_wrong_arity():
    with pytest.raises(RuntimeError, match="storage_exists expects exactly 1 string argument"):
        _build_with_handler("bad_storage_exists_arity", _bad_storage_exists_arity_handler)


def _bad_storage_exists_key_handler():
    value = storage_exists(9)
    preview = value


def test_track_c_wave1_parser_storage_exists_rejects_non_string_key():
    with pytest.raises(RuntimeError, match="storage_exists argument 'key' must be a constant string"):
        _build_with_handler("bad_storage_exists_key", _bad_storage_exists_key_handler)


def _bad_storage_remove_arity_handler():
    storage_remove("k", "extra")


def test_track_c_wave1_parser_storage_remove_rejects_wrong_arity():
    with pytest.raises(RuntimeError, match="storage_remove expects exactly 1 string argument"):
        _build_with_handler("bad_storage_remove_arity", _bad_storage_remove_arity_handler)


def _bad_storage_remove_key_handler():
    storage_remove(9)


def test_track_c_wave1_parser_storage_remove_rejects_non_string_key():
    with pytest.raises(RuntimeError, match="storage_remove argument 'key' must be a constant string"):
        _build_with_handler("bad_storage_remove_key", _bad_storage_remove_key_handler)


def _bad_storage_clear_arity_handler():
    storage_clear("unexpected")


def test_track_c_wave1_parser_storage_clear_rejects_wrong_arity():
    with pytest.raises(RuntimeError, match="storage_clear expects no arguments"):
        _build_with_handler("bad_storage_clear_arity", _bad_storage_clear_arity_handler)
