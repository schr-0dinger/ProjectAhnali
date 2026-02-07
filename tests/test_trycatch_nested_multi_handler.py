from alpha_pipeline import alpha_pipeline
from dsl.app import assign, const, method, program, try_catch


def test_trycatch_nested_multi_handler_regions_and_smali():
    prog = program(
        [
            method(
                "main",
                body=[
                    try_catch(
                        try_body=[
                            try_catch(
                                try_body=[assign("x", const(1))],
                                handlers=[
                                    ("Ljava/lang/RuntimeException;", [assign("r", const(2))]),
                                    (None, [assign("rc", const(3))]),
                                ],
                            ),
                        ],
                        handlers=[
                            ("Ljava/lang/Exception;", [assign("e", const(4))]),
                            (None, [assign("ec", const(5))]),
                        ],
                    )
                ],
            )
        ]
    )

    result = alpha_pipeline(prog)
    cfg = result["cfg"]
    smali = result["smali_class"]

    assert len(cfg.try_regions) == 4
    assert smali.count(".catchall") >= 2
    assert "Ljava/lang/RuntimeException;" in smali
    assert "Ljava/lang/Exception;" in smali
