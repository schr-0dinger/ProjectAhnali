from dsl.capabilities import DEFAULT_CAPABILITY_REGISTRY, Caps, Perms


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
