import pytest

from dsl.android import signatures as sig


def test_dynamic_signature_lookup_from_android_jar():
    jar = sig._find_android_jar()
    if jar is None:
        pytest.skip("android.jar not found for dynamic lookup test")

    saved_method = sig._METHOD_SIGS
    saved_ctor = sig._CTOR_SIGS
    saved_loaded = set(sig._DYNAMIC_LOADED)
    saved_missing = set(sig._DYNAMIC_MISSING)
    try:
        sig._METHOD_SIGS = {}
        sig._CTOR_SIGS = {}
        sig._DYNAMIC_LOADED.clear()
        sig._DYNAMIC_MISSING.clear()

        ret, args = sig._resolve_signature(
            "getPackageName",
            [],
            return_type=None,
            arg_types=None,
            invoke_kind="virtual",
            owner="Landroid/content/Context;",
        )
        assert ret == "Ljava/lang/String;"
        assert args == []
    finally:
        sig._METHOD_SIGS = saved_method
        sig._CTOR_SIGS = saved_ctor
        sig._DYNAMIC_LOADED = saved_loaded
        sig._DYNAMIC_MISSING = saved_missing
