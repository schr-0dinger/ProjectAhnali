import pytest

from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    DropdownButton,
    PopupMenuButton,
    Radio,
    RadioGroup,
    Slider,
    Switch,
    TextField,
    activity,
    app,
    button,
    on_change,
    on_focus_change,
    on_item_selected,
    on_menu_item_selected,
    on_slider_change,
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


@on_change("slider")
def _on_slider_change():
    label.text = "sliding"


@on_slider_change("slider_alias")
def _on_slider_change_alias():
    label.text = "alias sliding"


@on_change("group")
def _on_radio_group_change():
    label.text = "group changed"


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
    listener = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliChangeListener_toggle.smali"
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")

    assert listener.exists()
    assert "implements Landroid/widget/CompoundButton$OnCheckedChangeListener;" in listener_text
    assert "invoke-static {p1, p2}, LTestHandlers;->onChange_toggle(Landroid/widget/CompoundButton;Z)V" in listener_text
    assert "Landroid/widget/CompoundButton;->setOnCheckedChangeListener" in main_smali


def test_emit_change_listener_for_slider(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                Slider(id="slider", min=0, max=100, value=40),
            ),
            _on_slider_change,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    listener = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliChangeListener_slider.smali"
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")

    assert listener.exists()
    assert "implements Landroid/widget/SeekBar$OnSeekBarChangeListener;" in listener_text
    assert "onProgressChanged(Landroid/widget/SeekBar;IZ)V" in listener_text
    assert "invoke-static {p1, p2, p3}, LTestHandlers;->onChange_slider(Landroid/widget/SeekBar;IZ)V" in listener_text
    assert "Landroid/widget/SeekBar;->setOnSeekBarChangeListener" in main_smali


def test_emit_slider_change_alias_listener_for_slider(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                Slider(id="slider_alias", min=0, max=100, value=20),
            ),
            _on_slider_change_alias,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    listener = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliChangeListener_slider_alias.smali"
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")
    handlers = (out_dir / "smali" / "TestHandlers.smali").read_text(encoding="utf-8")

    assert listener.exists()
    assert "implements Landroid/widget/SeekBar$OnSeekBarChangeListener;" in listener_text
    assert (
        "invoke-static {p1, p2, p3}, "
        "LTestHandlers;->onSliderChange_slider_alias(Landroid/widget/SeekBar;IZ)V"
    ) in listener_text
    assert "Landroid/widget/SeekBar;->setOnSeekBarChangeListener" in main_smali
    assert ".method public static onSliderChange_slider_alias(Landroid/widget/SeekBar;IZ)V" in handlers
    assert any(
        entry[0] == "Lcom/ahnali/preview/AhnaliChangeListener_slider_alias;"
        and entry[3] == "slider_change"
        for entry in prog.support_classes
    )


def test_slider_change_alias_rejects_non_slider_target():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                Switch("Toggle", id="toggle_alias"),
            ),
            on_slider_change("toggle_alias", []),
        )
    )
    with pytest.raises(RuntimeError, match="on_slider_change target 'toggle_alias' must be slider"):
        prog.build()


def test_slider_change_alias_conflicts_with_on_change_for_same_target():
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                Slider(id="slider_dupe", min=0, max=100, value=40),
            ),
            on_change("slider_dupe", []),
            on_slider_change("slider_dupe", []),
        )
    )
    with pytest.raises(RuntimeError, match="Duplicate event binding"):
        prog.build()


def test_emit_change_listener_for_radio_group(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                RadioGroup(
                    Radio("A", id="radio_a"),
                    Radio("B", id="radio_b"),
                    id="group",
                ),
            ),
            _on_radio_group_change,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    listener = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliChangeListener_group.smali"
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")
    listener_text = listener.read_text(encoding="utf-8")

    assert listener.exists()
    assert "implements Landroid/widget/RadioGroup$OnCheckedChangeListener;" in listener_text
    assert "invoke-static {p1, p2}, LTestHandlers;->onChange_group(Landroid/widget/RadioGroup;I)V" in listener_text
    assert "Landroid/widget/RadioGroup;->setOnCheckedChangeListener" in main_smali


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
    listener = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliTextChangeListener_input.smali"
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
    listener = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliItemSelectedListener_choices.smali"
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
    listener = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliFocusChangeListener_input_focus.smali"
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
    listener = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliMenuItemListener_menu.smali"
    auto_popup_click = out_dir / "smali" / "com" / "ahnali" / "preview" / "AhnaliClickListener_menu_popup.smali"
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
