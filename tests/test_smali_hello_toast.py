from dsl.app import hello_world_activity
from alpha_pipeline import alpha_pipeline


def test_smali_emits_string_const_and_toast_calls():
    prog = hello_world_activity()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".method public static main(Landroid/app/Activity;)V" in smali
    assert "const-string" in smali
    assert "new-instance" in smali
    assert "Landroid/widget/TextView;-><init>(Landroid/content/Context;)V" in smali
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in smali
    assert "Landroid/app/Activity;->setContentView(Landroid/view/View;)V" in smali
