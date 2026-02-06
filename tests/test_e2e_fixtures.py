from alpha_pipeline import alpha_pipeline
from dsl.app import (
    program,
    method,
    assign,
    const,
    ret,
    try_catch,
    throw,
    hello_world_activity,
    button_view,
    set_content_view,
    var,
    linear_layout,
    add_view,
)
from alpha_pipeline import alpha_pipeline
from ir.types import AnaliType


def test_e2e_helloworld_smali_golden():
    smali = alpha_pipeline(hello_world_activity())["smali_class"]
    assert ".class public LTest;" in smali
    assert ".method public static main(Landroid/app/Activity;)V" in smali
    assert "new-instance" in smali
    assert "Landroid/widget/TextView;-><init>(Landroid/content/Context;)V" in smali
    assert "Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V" in smali
    assert "Landroid/app/Activity;->setContentView(Landroid/view/View;)V" in smali


def test_e2e_trycatch_smali_golden():
    prog = program([
        method(
            "main",
            return_type=AnaliType.INT,
            body=[
                try_catch(
                    try_body=[
                        assign("x", const(1)),
                        throw(const(0)),
                    ],
                    except_body=[
                        assign("x", const(2)),
                    ],
                    exception_type="Ljava/lang/Exception;",
                ),
                ret(const(3)),
            ],
        )
    ])

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".method public static main()I" in smali
    assert ".catch Ljava/lang/Exception;" in smali
    assert "throw" in smali


def test_e2e_widgets_button_smali_golden():
    prog = program([
        method(
            "main",
            params=["ctx"],
            param_types=["Landroid/app/Activity;"],
            return_type=None,
            body=[
                *button_view("btn", var("ctx"), "Click"),
                set_content_view(var("ctx"), var("btn")),
                ret(),
            ],
        )
    ])

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/widget/Button;-><init>(Landroid/content/Context;)V" in smali
    assert "Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V" in smali
    assert "Landroid/app/Activity;->setContentView(Landroid/view/View;)V" in smali


def test_e2e_linear_layout_add_view_smali_golden():
    prog = program([
        method(
            "main",
            params=["ctx"],
            param_types=["Landroid/app/Activity;"],
            return_type=None,
            body=[
                *linear_layout("root", var("ctx"), "vertical"),
                *button_view("btn", var("ctx"), "Click"),
                add_view(var("root"), var("btn")),
                set_content_view(var("ctx"), var("root")),
                ret(),
            ],
        )
    ])

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V" in smali
    assert "Landroid/widget/LinearLayout;->setOrientation(I)V" in smali
    assert "Landroid/view/ViewGroup;->addView(Landroid/view/View;)V" in smali
