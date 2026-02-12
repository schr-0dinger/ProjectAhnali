import io
import zipfile
import xml.etree.ElementTree as ET

from apk.toolchain import _read_aar_manifest_entries, _read_aar_package


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


def test_aar_manifest_entries_strip_tools_namespace_attrs(tmp_path):
    manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    package="com.example.lib">
    <application>
        <provider
            android:name="com.example.lib.InitProvider"
            android:authorities="${applicationId}.androidx-startup"
            android:exported="false"
            tools:node="merge" />
    </application>
</manifest>
"""
    aar_path = tmp_path / "dummy_tools.aar"
    with zipfile.ZipFile(aar_path, "w") as zf:
        zf.writestr("AndroidManifest.xml", manifest)

    _, app_entries = _read_aar_manifest_entries(aar_path)
    assert app_entries
    entry = app_entries[0]
    assert "{http://schemas.android.com/tools}" not in entry
    assert "tools:node" not in entry
    ET.fromstring(
        f'<root xmlns:android="http://schemas.android.com/apk/res/android">{entry}</root>'
    )


def test_aar_manifest_entries_block_startup_components(tmp_path):
    manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.lib">
    <application>
        <provider
            android:name="androidx.startup.InitializationProvider"
            android:authorities="${applicationId}.androidx-startup"
            android:exported="false" />
        <receiver
            android:name="androidx.profileinstaller.ProfileInstallReceiver"
            android:exported="true" />
        <service
            android:name="com.example.lib.RealService"
            android:exported="false" />
    </application>
</manifest>
"""
    aar_path = tmp_path / "dummy_blocklist.aar"
    with zipfile.ZipFile(aar_path, "w") as zf:
        zf.writestr("AndroidManifest.xml", manifest)

    _, app_entries = _read_aar_manifest_entries(aar_path)
    assert all("androidx.startup.InitializationProvider" not in entry for entry in app_entries)
    assert all("androidx.profileinstaller.ProfileInstallReceiver" not in entry for entry in app_entries)
    assert any("com.example.lib.RealService" in entry for entry in app_entries)


def test_read_aar_package_prefers_package_over_class_name(tmp_path):
    manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="androidx.startup">
    <application>
        <provider android:name="androidx.startup.InitializationProvider" />
    </application>
</manifest>
"""
    classes_buf = io.BytesIO()
    with zipfile.ZipFile(classes_buf, "w") as classes_zip:
        classes_zip.writestr("androidx/startup/AppInitializer.class", b"\x00")
        classes_zip.writestr("androidx/startup/InitializationProvider.class", b"\x00")

    aar_path = tmp_path / "dummy_pkg.aar"
    with zipfile.ZipFile(aar_path, "w") as zf:
        zf.writestr("AndroidManifest.xml", manifest)
        zf.writestr("classes.jar", classes_buf.getvalue())

    assert _read_aar_package(aar_path) == "androidx.startup"
