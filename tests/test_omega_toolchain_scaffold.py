# tests/test_omega_toolchain_scaffold.py


from apk.toolchain import emit_build_dir_from_program
from dsl.app import assign, const


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
