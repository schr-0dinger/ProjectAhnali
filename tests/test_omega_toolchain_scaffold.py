# tests/test_omega_toolchain_scaffold.py


from apk.toolchain import emit_build_dir_from_program
from apk.project import render_manifest
from dsl.app import assign, const, method, program, ret


def test_emit_build_dir_writes_smali(tmp_path):
    out_dir = emit_build_dir_from_program(
        [assign("x", const(1))],
        out_dir=tmp_path,
        class_name="LTest;",
    )

    smali_path = out_dir / "smali" / "Test.smali"
    assert smali_path.exists()
    smali_text = smali_path.read_text(encoding="utf-8")
    assert ".class public LTest;" in smali_text


def test_emit_build_dir_with_wrapper_writes_activity_and_main(tmp_path):
    out_dir = emit_build_dir_from_program(
        [assign("x", const(1))],
        out_dir=tmp_path,
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/anali/preview/MainActivity;",
    )

    main_path = out_dir / "smali" / "Test.smali"
    activity_path = out_dir / "smali" / "com" / "anali" / "preview" / "MainActivity.smali"

    assert main_path.exists()
    assert activity_path.exists()

    main_text = main_path.read_text(encoding="utf-8")
    activity_text = activity_path.read_text(encoding="utf-8")

    assert ".class public LTest;" in main_text
    assert ".class public Lcom/anali/preview/MainActivity;" in activity_text
    assert "invoke-static {}, LTest;->main()V" in activity_text


def test_emit_build_dir_writes_resources_from_program(tmp_path):
    prog = program(
        [
            method(
                "main",
                return_type=None,
                body=[assign("x", const(1)), ret()],
            )
        ],
        resources={"app_name": "Widget Zoo", "greeting": "Hello"},
    )

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path,
        class_name="LTest;",
    )

    strings_path = out_dir / "res" / "values" / "strings.xml"
    assert strings_path.exists()
    xml = strings_path.read_text(encoding="utf-8")
    assert '<string name="app_name">Widget Zoo</string>' in xml
    assert '<string name="greeting">Hello</string>' in xml


def test_manifest_defaults_to_app_name_resource_label():
    manifest = render_manifest()
    assert 'android:label="@string/app_name"' in manifest
