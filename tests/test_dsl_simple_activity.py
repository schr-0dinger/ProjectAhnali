from alpha_pipeline import alpha_pipeline
from dsl.app import simple_activity


def test_simple_activity_builds_smali():
    app = simple_activity().counter(0).button("Tap").on_click_increment("button")
    smali = alpha_pipeline(app.build())["smali_class"]
    assert "sget" in smali
    assert "sput" in smali
    assert "Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V" in smali
    assert "Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V" in smali
