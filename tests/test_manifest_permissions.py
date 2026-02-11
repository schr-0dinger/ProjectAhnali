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
