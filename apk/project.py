# apk/project.py

from pathlib import Path
from emit.smali_preview import emit_smali_preview
from passes.regalloc_naive import RegisterAllocatorNaive
from emit.smali_emit import emit_smali



ANDROID_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.anali.preview">

    <application
        android:label="AnaliPreview"
        android:allowBackup="false">
    </application>

</manifest>
"""


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


def emit_apktool_project(dalvik_blocks, out_dir="out_apk"):
    out = Path(out_dir)
    smali_dir = out / "smali"

    out.mkdir(parents=True, exist_ok=True)
    smali_dir.mkdir(parents=True, exist_ok=True)

    # 1. AndroidManifest.xml
    (out / "AndroidManifest.xml").write_text(
        ANDROID_MANIFEST, encoding="utf-8"
    )

    # 2. apktool.yml
    (out / "apktool.yml").write_text(
        APKTOOL_YML, encoding="utf-8"
    )

    # 3. Smali file
        # Register allocation
    allocator = RegisterAllocatorNaive(dalvik_blocks)
    reg_map, locals_count = allocator.allocate()

    smali_code = emit_smali(dalvik_blocks, reg_map, locals_count)

    (smali_dir / "Test.smali").write_text(
        smali_code, encoding="utf-8"
    )

    return out
