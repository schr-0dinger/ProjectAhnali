# apk/project.py

from pathlib import Path

from passes.regalloc_naive import RegisterAllocatorNaive
from emit.smali_activity import emit_activity_smali


# ------------------------------------------------------------
# AndroidManifest.xml (LAUNCHABLE)
# ------------------------------------------------------------

ANDROID_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.anali.preview"
    android:versionCode="1"
    android:versionName="1.0">

    <uses-sdk
        android:minSdkVersion="21"
        android:targetSdkVersion="33" />

    <application
        android:label="AnaliPreview"
        android:allowBackup="false">

        <activity
            android:name=".MainActivity"
            android:exported="true">

            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>

        </activity>

    </application>

</manifest>
"""


# ------------------------------------------------------------
# apktool.yml (minimal but valid)
# ------------------------------------------------------------

APKTOOL_YML = """!!brut.androlib.meta.MetaInfo
apkFileName: AnaliPreview.apk
isFrameworkApk: false
packageInfo:
  forcedPackageId: '127'
sdkInfo:
  minSdkVersion: '21'
  targetSdkVersion: '33'
versionInfo:
  versionCode: '1'
  versionName: '1.0'
"""


# ------------------------------------------------------------
# Project emitter
# ------------------------------------------------------------

def emit_apktool_project(dalvik_blocks, out_dir="out_apk"):
    out = Path(out_dir)
    smali_dir = out / "smali"

    out.mkdir(parents=True, exist_ok=True)
    smali_dir.mkdir(parents=True, exist_ok=True)

    # 1. AndroidManifest.xml
    (out / "AndroidManifest.xml").write_text(
        ANDROID_MANIFEST,
        encoding="utf-8",
    )

    # 2. apktool.yml
    (out / "apktool.yml").write_text(
        APKTOOL_YML,
        encoding="utf-8",
    )

    # 3. Register allocation
    allocator = RegisterAllocatorNaive(dalvik_blocks)
    reg_map, locals_count = allocator.allocate()

    # 4. Activity smali
    smali_code = emit_activity_smali(
        dalvik_blocks,
        reg_map,
        locals_count,
        package="com/anali/preview",
        activity="MainActivity",
    )

    (smali_dir / "MainActivity.smali").write_text(
        smali_code,
        encoding="utf-8",
    )

    return out
