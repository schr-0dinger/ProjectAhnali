from alpha_pipeline import alpha_pipeline
from apk.project import emit_apktool_project
from tests.ir_stub import Assign, If

ir = [
    Assign("x", 0),
    If("c", [Assign("x", 1)], [Assign("x", 2)]),
    Assign("y", "x"),
]

result = alpha_pipeline(ir)
emit_apktool_project(result["dalvik"], out_dir="out_apk")

print("apktool project written to out_apk/")
