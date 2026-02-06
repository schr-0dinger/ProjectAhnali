from alpha_pipeline import alpha_pipeline
from tests.ir_stub import TryCatch, Assign


def test_cfg_simplify_preserves_try_regions():
    ir = [
        TryCatch(
            try_body=[Assign("x", 1)],
            except_body=[Assign("y", 2)],
            exception_type="Ljava/lang/Exception;",
        )
    ]

    result = alpha_pipeline(ir)
    smali = result["smali"]

    assert ".catch Ljava/lang/Exception;" in smali
