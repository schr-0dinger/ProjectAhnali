import pytest

from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    DropdownButton,
    PopupMenuButton,
    Switch,
    TextField,
    activity,
    app,
    button,
    on_change,
    on_focus_change,
    on_item_selected,
    on_menu_item_selected,
    on_text_change,
    text,
    ui,
)


@on_change("toggle")
def _on_toggle():
    label.text = "toggled"


@on_text_change("input")
def _on_text_input():
    label.text = "typing"


@on_item_selected("choices")
def _on_choice_selected():
    label.text = "picked"


@on_focus_change("input_focus")
def _on_focus():
    label.text = "focus"


@on_menu_item_selected("menu")
def _on_menu_item():
    label.text = "menu"


def test_emit_change_listener_for_switch(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                Switch("Toggle", id="toggle"),
            ),
            _on_toggle,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    listener = out_dir / "smali" / "com" / "anali" / "preview" / "AnaliChangeListener_toggle.smali"
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")

    assert listener.exists()
    assert "implements Landroid/widget/CompoundButton$OnCheckedChangeListener;" in listener_text
    assert "invoke-static {p1, p2}, LTestHandlers;->onChange_toggle(Landroid/widget/CompoundButton;Z)V" in listener_text
    assert "Landroid/widget/CompoundButton;->setOnCheckedChangeListener" in main_smali


def test_emit_text_change_listener_for_text_field(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                TextField(id="input"),
            ),
            _on_text_input,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    listener = out_dir / "smali" / "com" / "anali" / "preview" / "AnaliTextChangeListener_input.smali"
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")

    assert listener.exists()
    assert "implements Landroid/text/TextWatcher;" in listener_text
    assert "afterTextChanged(Landroid/text/Editable;)V" in listener_text
    assert "invoke-static {p1}, LTestHandlers;->onTextChange_input(Landroid/text/Editable;)V" in listener_text
    assert "Landroid/widget/TextView;->addTextChangedListener(Landroid/text/TextWatcher;)V" in main_smali


def test_emit_item_selected_listener_for_dropdown(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                DropdownButton(id="choices", items=["A", "B"]),
            ),
            _on_choice_selected,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    listener = out_dir / "smali" / "com" / "anali" / "preview" / "AnaliItemSelectedListener_choices.smali"
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")

    assert listener.exists()
    assert "implements Landroid/widget/AdapterView$OnItemSelectedListener;" in listener_text
    assert (
        "invoke-static {p1, p2, p3, p4, p5}, LTestHandlers;->onItemSelected_choices(Landroid/widget/AdapterView;Landroid/view/View;IJ)V"
        in listener_text
    )
    assert "Landroid/widget/AdapterView;->setOnItemSelectedListener" in main_smali


def test_emit_focus_change_listener(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                TextField(id="input_focus"),
            ),
            _on_focus,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    listener = out_dir / "smali" / "com" / "anali" / "preview" / "AnaliFocusChangeListener_input_focus.smali"
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")

    assert listener.exists()
    assert "implements Landroid/view/View$OnFocusChangeListener;" in listener_text
    assert "invoke-static {p1, p2}, LTestHandlers;->onFocusChange_input_focus(Landroid/view/View;Z)V" in listener_text
    assert "Landroid/view/View;->setOnFocusChangeListener" in main_smali


def test_emit_popup_menu_item_selected_listener(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                PopupMenuButton("Menu", id="menu", items=["A", "B"]),
            ),
            _on_menu_item,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    listener = out_dir / "smali" / "com" / "anali" / "preview" / "AnaliMenuItemListener_menu.smali"
    auto_popup_click = out_dir / "smali" / "com" / "anali" / "preview" / "AnaliClickListener_menu_popup.smali"
    handlers_smali = (out_dir / "smali" / "TestHandlers.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")

    assert listener.exists()
    assert auto_popup_click.exists()
    assert "implements Landroid/widget/PopupMenu$OnMenuItemClickListener;" in listener_text
    assert "invoke-static {p1}, LTestHandlers;->onMenuItemSelected_menu(Landroid/view/MenuItem;)V" in listener_text
    assert "return v0" in listener_text
    assert "Landroid/widget/PopupMenu;->setOnMenuItemClickListener" in handlers_smali


def test_on_text_change_rejects_non_text_field_target():
    bad_spec = on_text_change("btn", [])
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                button("Tap", id="btn"),
            ),
            bad_spec,
        )
    )
    with pytest.raises(RuntimeError, match="on_text_change target 'btn' must be text_field"):
        prog.build()
