from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If, TryCatch


def test_cfg_simplify_preserves_branch_and_catch():
    ir = [
        Assign("x", 1),
        TryCatch(
            try_body=[
                If("x", [Assign("y", 1)], [Assign("y", 2)]),
                Assign("z", "y"),
            ],
            except_body=[Assign("e", 3)],
            exception_type="Ljava/lang/Exception;",
        ),
        If("z", [], []),
    ]

    result = alpha_pipeline(ir)
    smali = result["smali"]

    # Branch + catch must survive simplification
    assert "if-" in smali
    assert ".catch Ljava/lang/Exception;" in smali
