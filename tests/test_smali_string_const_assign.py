from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, assign, const, call_stmt, var, ret


def test_string_const_assign_emits_const_string():
    prog = program([
        method(
            "main",
            params=["ctx"],
            param_types=["Landroid/app/Activity;"],
            return_type=None,
            body=[
                assign("msg", const("Hello, Ahnali!")),
                call_stmt(
                    "setTitle",
                    args=[var("ctx"), var("msg")],
                    return_type=None,
                    arg_types=["Ljava/lang/CharSequence;"],
                    invoke_kind="virtual",
                    owner="Landroid/app/Activity;",
                ),
                ret(),
            ],
        )
    ])

    smali = alpha_pipeline(prog)["smali_class"]
    assert "const-string" in smali
    assert "Landroid/app/Activity;->setTitle(Ljava/lang/CharSequence;)V" in smali
