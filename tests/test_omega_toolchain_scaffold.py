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
