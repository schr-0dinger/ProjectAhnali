from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, assign, const, try_catch


def test_trycatch_multi_handler_ordering():
    prog = program([
        method(
            "main",
            body=[
                try_catch(
                    try_body=[assign("x", const(1))],
                    handlers=[
                        ("Ljava/lang/RuntimeException;", [assign("a", const(1))]),
                        ("Ljava/lang/Exception;", [assign("b", const(2))]),
                        (None, [assign("c", const(3))]),
                    ],
                )
            ],
        )
    ])

    result = alpha_pipeline(prog)
    smali = result["smali_class"]

    first = smali.find("Ljava/lang/RuntimeException;")
    second = smali.find("Ljava/lang/Exception;")
    third = smali.find(".catchall")

    assert first != -1 and second != -1 and third != -1
    assert first < second < third


def test_trycatch_catchall_not_last_rejected():
    prog = program([
        method(
            "main",
            body=[
                try_catch(
                    try_body=[assign("x", const(1))],
                    handlers=[
                        (None, [assign("c", const(3))]),
                        ("Ljava/lang/Exception;", [assign("b", const(2))]),
                    ],
                )
            ],
        )
    ])

    try:
        alpha_pipeline(prog)
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass
