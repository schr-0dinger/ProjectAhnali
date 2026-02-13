from alpha_pipeline import alpha_pipeline
from dsl.app import (
    array_get,
    array_set,
    assign,
    call,
    check_cast,
    const,
    method,
    new_array,
    primitive_cast,
    program,
    ret,
    var,
)
from ir.types import AhnaliType


def test_dsl_new_array_cast_and_invoke_interface_super_lowering():
    prog = program(
        [
            method(
                "main",
                params=["list", "obj"],
                param_types=["Ljava/util/List;", "Ljava/lang/Object;"],
                return_type=AhnaliType.INT,
                body=[
                    assign("n", const(3)),
                    assign("arr", new_array(var("n"), "I")),
                    array_set(var("arr"), const(0), "I", const(7)),
                    assign("x", array_get(var("arr"), const(0), "I")),
                    assign("f", primitive_cast(var("x"), "I", "F")),
                    assign("s", check_cast(var("obj"), "Ljava/lang/String;")),
                    assign(
                        "sz",
                        call(
                            "size",
                            args=[var("list")],
                            return_type=AhnaliType.INT,
                            arg_types=["Ljava/util/List;"],
                            invoke_kind="interface",
                            owner="Ljava/util/List;",
                        ),
                    ),
                    assign(
                        "ts",
                        call(
                            "toString",
                            args=[var("obj")],
                            return_type="Ljava/lang/String;",
                            arg_types=["Ljava/lang/Object;"],
                            invoke_kind="super",
                            owner="Ljava/lang/Object;",
                        ),
                    ),
                    ret(var("sz")),
                ],
            )
        ]
    )

    smali = alpha_pipeline(prog)["smali_class"]
    assert "new-array" in smali
    assert "aput" in smali
    assert "aget" in smali
    assert "int-to-float" in smali
    assert "check-cast" in smali
    assert "invoke-interface" in smali
    assert "invoke-super" in smali
