from alpha_pipeline import alpha_pipeline
from dsl.app import program, method, ret, var, toast, set_content_view, text_view, log_d


def test_signature_mapping_fills_args_and_return():
    prog = program([
        method(
            "main",
            params=["ctx"],
            param_types=["Landroid/app/Activity;"],
            return_type=None,
            body=[
                *text_view("tv", var("ctx"), "Hi"),
                *toast("t", var("ctx"), "Hi"),
                *log_d("TAG", "Hello"),
                set_content_view(var("ctx"), var("tv")),
                ret(),
            ],
        )
    ])

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in smali
    assert "Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;" in smali
    assert "Landroid/widget/Toast;->show()V" in smali
    assert "Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I" in smali
    assert "Landroid/app/Activity;->setContentView(Landroid/view/View;)V" in smali
