import re

import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import (
    Back,
    ClearStack,
    Navigate,
    PopToRoot,
    activity,
    app,
    button,
    clear_stack,
    on_click,
    pop_to_root,
    text,
    ui,
    Screen,
)


@on_click("to_second")
def _to_second():
    Navigate("Second")


@on_click("to_third")
def _to_third():
    Navigate("Third")


@on_click("to_root")
def _to_root():
    PopToRoot()


@on_click("clear_stack_btn")
def _clear_stack_btn():
    ClearStack()


@on_click("back_btn")
def _back_btn():
    Back()


def _handler_body(smali: str, method_name: str) -> str:
    match = re.search(
        rf"\.method public static {re.escape(method_name)}\(Landroid/view/View;\)V(.*?)\.end method",
        smali,
        re.S,
    )
    assert match, f"missing handler method {method_name}"
    return match.group(1)


def test_program4_navigation_ops_lowering():
    prog = app(
        activity(
            "MainActivity",
            ui(
                Screen(
                    "First",
                    button("Second", id="to_second"),
                    button("Root", id="to_root"),
                    button("Clear", id="clear_stack_btn"),
                    button("Back", id="back_btn"),
                ),
                Screen(
                    "Second",
                    button("Third", id="to_third"),
                    text("S2", id="s2"),
                ),
                Screen("Third", text("S3", id="s3")),
            ),
            _to_second,
            _to_third,
            _to_root,
            _clear_stack_btn,
            _back_btn,
        )
    ).build()

    result = alpha_pipeline(prog)
    merged = result["smali_class"] + "\n" + "\n".join(result.get("extra_smali_classes", {}).values())

    root_body = _handler_body(merged, "onClick_to_root")
    clear_body = _handler_body(merged, "onClick_clear_stack_btn")

    assert "nav_stack:[I" in root_body
    assert "sput" in root_body and "->nav_size:I" in root_body
    assert "setVisibility" in root_body

    assert "nav_stack:[I" in clear_body
    assert "sput" in clear_body and "->nav_size:I" in clear_body
    assert "setVisibility" not in clear_body


# Parser guardrails

def _build_with_handler(btn_id: str, handler):
    return app(
        activity(
            "MainActivity",
            ui(
                Screen("First", button("Run", id=btn_id)),
                Screen("Second", text("S2", id="s2")),
            ),
            on_click(btn_id)(handler),
        )
    )


def _bad_pop_to_root_args_handler():
    pop_to_root("unexpected")


def test_program4_parser_pop_to_root_rejects_args():
    with pytest.raises(RuntimeError, match="PopToRoot takes no arguments"):
        _build_with_handler("bad_pop_root", _bad_pop_to_root_args_handler)


def _bad_clear_stack_args_handler():
    clear_stack("unexpected")


def test_program4_parser_clear_stack_rejects_args():
    with pytest.raises(RuntimeError, match="ClearStack takes no arguments"):
        _build_with_handler("bad_clear_stack", _bad_clear_stack_args_handler)
