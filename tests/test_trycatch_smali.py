from alpha_pipeline import alpha_pipeline
from tests.ir_stub import TryCatch, Assign


def test_trycatch_emits_catchall_smali():
    ir = [
        TryCatch(
            try_body=[Assign("x", 1)],
            except_body=[Assign("y", 2)],
        )
    ]

    result = alpha_pipeline(ir)
    smali = result["smali"]
    cfg = result["cfg"]

    start, end, handler, _ = cfg.try_regions[0]

    assert f".catchall {{:B{start.id} .. :B{end.id}}} :B{handler.id}" in smali
