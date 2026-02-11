import zipfile

from apk.toolchain import _read_aar_manifest_entries


def test_aar_manifest_entries_parsed(tmp_path):
    manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.lib">

    <uses-permission android:name="android.permission.INTERNET" />

    <application>
        <provider
            android:name="com.example.lib.Provider"
            android:authorities="com.example.lib.provider" />
    </application>

</manifest>
"""
    aar_path = tmp_path / "dummy.aar"
    with zipfile.ZipFile(aar_path, "w") as zf:
        zf.writestr("AndroidManifest.xml", manifest)
    perm_entries, app_entries = _read_aar_manifest_entries(aar_path)
    assert any("uses-permission" in entry for entry in perm_entries)
    assert any("provider" in entry for entry in app_entries)
