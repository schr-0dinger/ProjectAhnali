from dsl.capabilities import (
    CAPABILITY_RUNTIME_ABI_VERSION,
    DEFAULT_CAPABILITY_REGISTRY,
    Caps,
    Perms,
    default_capability_runtime_mapping,
    resolve_runtime_bindings,
)


def test_capability_registry_resolves_permissions():
    perms = DEFAULT_CAPABILITY_REGISTRY.resolve_permissions(
        ["Audio", "android.permission.INTERNET", "Audio"]
    )
    assert "android.permission.RECORD_AUDIO" in perms
    assert "android.permission.INTERNET" in perms
    assert perms.count("android.permission.RECORD_AUDIO") == 1


def test_caps_and_perms_helpers():
    perms = DEFAULT_CAPABILITY_REGISTRY.resolve_permissions([Caps.Location, Perms.CAMERA])
    assert "android.permission.ACCESS_FINE_LOCATION" in perms
    assert "android.permission.CAMERA" in perms


def test_capability_runtime_mapping_v1_shape():
    mapping = default_capability_runtime_mapping()
    assert CAPABILITY_RUNTIME_ABI_VERSION == "1.0.0"
    assert mapping
    for cap_name, binding in mapping.items():
        if cap_name == "URLLauncher":
            assert binding.mode == "helper_call"
            assert binding.helper_class_desc == "Lcom/ahnali/runtime/UrlLauncherHelper;"
            assert binding.helper_method == "openUrl"
            assert binding.helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)I"
        elif cap_name == "Connectivity":
            assert binding.mode == "helper_call"
            assert binding.helper_class_desc == "Lcom/ahnali/runtime/ConnectivityHelper;"
            assert binding.helper_method == "isConnected"
            assert binding.helper_sig == "(Landroid/app/Activity;)I"
        else:
            assert binding.mode == "permission_only"
            assert binding.helper_class_desc is None
            assert binding.helper_method is None
            assert binding.helper_sig is None


def test_resolve_runtime_bindings_dedupes_aliases_and_ignores_raw_permissions():
    bindings = resolve_runtime_bindings(
        [
            "FilePicker",
            "File Picker",
            "URL launcher",
            "URLLauncher",
            "android.permission.CAMERA",
            "CAMERA",
        ]
    )
    assert [b.capability for b in bindings] == ["FilePicker", "URLLauncher"]


def test_runtime_bindings_match_capability_permissions():
    mapping = default_capability_runtime_mapping()
    for cap_name, binding in mapping.items():
        resolved = DEFAULT_CAPABILITY_REGISTRY.resolve_permissions([cap_name])
        assert tuple(resolved) == binding.permissions
