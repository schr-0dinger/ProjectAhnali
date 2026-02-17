import pytest

from alpha_pipeline import alpha_pipeline
from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    Caps,
    activity,
    app,
    app_config,
    button,
    check_permission,
    on_click,
    permission_granted,
    text,
    ui,
)


@on_click("check_btn")
def _check_btn_handler():
    check_permission("android.permission.CAMERA")


@on_click("eval_btn")
def _eval_btn_handler():
    granted = permission_granted("android.permission.CAMERA")
    status_label.text = granted


def test_track_c_wave7_permission_granted_lowers_to_runtime_helper_call():
    prog = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Permissions]),
            ui(
                text("status", id="status_label"),
                button("Check", id="check_btn"),
                button("Eval", id="eval_btn"),
            ),
            _check_btn_handler,
            _eval_btn_handler,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())
    assert "Lcom/ahnali/runtime/PermissionHelper;->isGranted(Landroid/app/Activity;Ljava/lang/String;)I" in merged


def test_track_c_wave7_permission_granted_requires_permissions_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("status", id="status_label"),
                button("Eval", id="eval_btn"),
            ),
            _eval_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] permission_granted requires Caps\.Permissions\."):
        prog.build()


def test_track_c_wave7_check_permission_requires_permissions_capability():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Check", id="check_btn")),
            _check_btn_handler,
        )
    )
    with pytest.raises(RuntimeError, match=r"\[CapabilityError\] check_permission requires Caps\.Permissions\."):
        prog.build()


def test_track_c_wave7_toolchain_emits_permission_helper_class(tmp_path):
    frontend = app(
        activity(
            "MainActivity",
            app_config(uses=[Caps.Permissions]),
            ui(button("Check", id="check_btn")),
            _check_btn_handler,
        )
    ).build()
    out_dir = emit_build_dir_from_program(
        frontend,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
    )
    helper_path = out_dir / "smali" / "com" / "ahnali" / "runtime" / "PermissionHelper.smali"
    assert helper_path.exists()
    helper_smali = helper_path.read_text(encoding="utf-8")
    assert ".method public static isGranted(Landroid/app/Activity;Ljava/lang/String;)I" in helper_smali
    assert "Landroid/app/Activity;->checkCallingOrSelfPermission(Ljava/lang/String;)I" in helper_smali


def test_track_c_wave7_parser_check_permission_rejects_wrong_args():
    def _bad():
        check_permission(7)

    with pytest.raises(RuntimeError, match="check_permission argument 'permission' must be a constant string"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Permissions]),
                ui(button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()


def test_track_c_wave7_parser_permission_granted_rejects_wrong_arity():
    def _bad():
        value = permission_granted()
        status_label.text = value

    with pytest.raises(RuntimeError, match="permission_granted expects exactly 1 string argument"):
        app(
            activity(
                "MainActivity",
                app_config(uses=[Caps.Permissions]),
                ui(text("x", id="status_label"), button("Bad", id="bad_btn")),
                on_click("bad_btn")(_bad),
            )
        ).build()
