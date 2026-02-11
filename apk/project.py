# apk/project.py

from pathlib import Path

from passes.regalloc_naive import RegisterAllocatorNaive
from emit.smali_activity import emit_activity_smali


# ------------------------------------------------------------
# AndroidManifest.xml (LAUNCHABLE)
# ------------------------------------------------------------

def render_manifest(
    *,
    application_id: str = "com.anali.preview",
    min_sdk: int = 21,
    target_sdk: int = 33,
    version_code: int = 1,
    version_name: str = "1.0",
    debuggable: bool = False,
    show_action_bar: bool = True,
    activity_name: str = ".MainActivity",
    label: str = "@string/app_name",
    icon: str | None = None,
    permissions: list[str] | None = None,
    permission_entries: list[str] | None = None,
    application_entries: list[str] | None = None,
) -> str:
    debug_attr = ' android:debuggable="true"' if debuggable else ""
    theme_attr = ""
    if not show_action_bar:
        theme_attr = ' android:theme="@android:style/Theme.Material.Light.NoActionBar"'
    icon_attr = f' android:icon="{icon}"' if icon else ""
    perm_lines = []
    if permissions:
        seen = set()
        for perm in permissions:
            if perm in seen:
                continue
            seen.add(perm)
            perm_lines.append(f'<uses-permission android:name="{perm}" />')
    for entry in permission_entries or []:
        entry = (entry or "").strip()
        if not entry:
            continue
        perm_lines.append(entry)
    perm_block = ""
    if perm_lines:
        formatted = []
        seen = set()
        for line in perm_lines:
            if line in seen:
                continue
            seen.add(line)
            formatted.append("    " + line)
        perm_block = "\n" + "\n".join(formatted)
    app_block = ""
    if application_entries:
        formatted = []
        seen = set()
        for entry in application_entries:
            entry = (entry or "").strip()
            if not entry or entry in seen:
                continue
            seen.add(entry)
            for line in entry.splitlines():
                formatted.append("        " + line.strip())
        if formatted:
            app_block = "\n" + "\n".join(formatted)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{application_id}"
    android:versionCode="{version_code}"
    android:versionName="{version_name}">

    <uses-sdk
        android:minSdkVersion="{min_sdk}"
        android:targetSdkVersion="{target_sdk}" />{perm_block}

    <application
        android:label="{label}"
        android:allowBackup="false"{debug_attr}{theme_attr}{icon_attr}>{app_block}

        <activity
            android:name="{activity_name}"
            android:exported="true">

            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>

        </activity>

    </application>

</manifest>
"""


ANDROID_MANIFEST = render_manifest()


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
