import json

from apk.toolchain import emit_build_dir_from_program
from dsl.app import activity, app, app_config, button, on_click, text, ui
from tools.feature_runtime_plan import build_feature_runtime_plan_from_source


@on_click("copy_btn")
def _copy_text_for_runtime_plan():
    current = getattr(label, "text")
    label.text = current


def test_feature_runtime_plan_tool_builds_plan_from_source_text():
    payload = build_feature_runtime_plan_from_source(
        """
import android.widget

async def handler(items):
    values = [1, 2]
    mapping = {"a": 1}
    current = getattr(items, "name")
    await fetch()
    return mapping
"""
    )

    assert payload["schema_version"] == "feature_runtime_plan/1"
    assert "python.collections.list_wrapper" in payload["runtime_module_names"]
    assert "python.collections.dict_wrapper" in payload["runtime_module_names"]
    assert "python.introspection.reflection" in payload["runtime_module_names"]
    assert "python.async.async_runtime" in payload["runtime_module_names"]


def test_emit_build_dir_writes_runtime_plan_report(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            app_config(mode="reactive"),
            ui(
                text("Init", id="label"),
                button("Copy", id="copy_btn"),
            ),
            _copy_text_for_runtime_plan,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
    )

    report_path = out_dir / "runtime_plan.json"
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "feature_runtime_plan/1"
    assert payload["app_mode"] == "reactive"
    assert "app.mode.reactive" in payload["runtime_module_names"]
    assert "python.introspection.reflection" in payload["runtime_module_names"]
    assert payload["feature_usage_profile"]["source_kind"] == "merged"
