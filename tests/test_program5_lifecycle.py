from apk.toolchain import emit_build_dir_from_program
from dsl.app import activity, app, on_destroy, on_pause, on_resume, on_start, on_stop, state, ui


@on_start
def _on_start_handler():
    launches += 1


@on_resume
def _on_resume_handler():
    launches += 1


@on_pause
def _on_pause_handler():
    launches += 1


@on_stop
def _on_stop_handler():
    launches += 1


@on_destroy
def _on_destroy_handler():
    launches += 1


def test_program5_lifecycle_hooks_compile_static_methods():
    prog = app(
        activity(
            "MainActivity",
            state(launches=0),
            ui(),
            _on_start_handler,
            _on_resume_handler,
            _on_pause_handler,
            _on_stop_handler,
            _on_destroy_handler,
        )
    ).build()

    names = {getattr(method, "name", "") for method in prog.methods}
    assert "onStart" in names
    assert "onResume" in names
    assert "onPause" in names
    assert "onStop" in names
    assert "onDestroy" in names


def test_program5_toolchain_wrapper_emits_lifecycle_bridges(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            state(launches=0),
            ui(),
            _on_start_handler,
            _on_resume_handler,
            _on_pause_handler,
            _on_stop_handler,
            _on_destroy_handler,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/ahnali/preview/MainActivity;",
        wrapper_target_desc="LTest;",
        wrapper_target_sig="(Landroid/app/Activity;)V",
    )
    wrapper_path = out_dir / "smali" / "com" / "ahnali" / "preview" / "MainActivity.smali"
    wrapper_smali = wrapper_path.read_text(encoding="utf-8")

    assert ".method protected onStart()V" in wrapper_smali
    assert ".method protected onResume()V" in wrapper_smali
    assert ".method protected onPause()V" in wrapper_smali
    assert ".method protected onStop()V" in wrapper_smali
    assert ".method protected onDestroy()V" in wrapper_smali
    assert "invoke-static {}, LTest;->onStart()V" in wrapper_smali
    assert "invoke-static {}, LTest;->onResume()V" in wrapper_smali
    assert "invoke-static {}, LTest;->onPause()V" in wrapper_smali
    assert "invoke-static {}, LTest;->onStop()V" in wrapper_smali
    assert "invoke-static {}, LTest;->onDestroy()V" in wrapper_smali
