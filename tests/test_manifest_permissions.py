from apk.project import render_manifest


def test_render_manifest_includes_permissions():
    manifest = render_manifest(
        permissions=[
            "android.permission.INTERNET",
            "android.permission.CAMERA",
        ]
    )
    assert 'uses-permission android:name="android.permission.INTERNET"' in manifest
    assert 'uses-permission android:name="android.permission.CAMERA"' in manifest


def test_render_manifest_no_action_bar_default_theme():
    manifest = render_manifest(show_action_bar=False)
    assert 'android:theme="@android:style/Theme.Material.Light.NoActionBar"' in manifest


def test_render_manifest_explicit_theme_overrides_default():
    manifest = render_manifest(
        show_action_bar=False,
        theme="@style/Theme.AppCompat.Light.NoActionBar",
    )
    assert 'android:theme="@style/Theme.AppCompat.Light.NoActionBar"' in manifest
    assert '@android:style/Theme.Material.Light.NoActionBar' not in manifest
