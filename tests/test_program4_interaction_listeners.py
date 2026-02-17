import pytest

from apk.toolchain import emit_build_dir_from_program
from dsl.app import (
    TextField,
    activity,
    app,
    button,
    on_double_tap,
    on_drag,
    on_drop,
    on_editor_action,
    on_fling,
    on_key,
    on_long_click,
    on_pinch,
    on_rotate_gesture,
    on_scale_gesture_detector,
    on_scroll,
    on_swipe,
    on_touch,
    text,
    ui,
    view,
    on_zoom,
)


@on_long_click("long_btn")
def _on_long_click():
    label.text = "long"


@on_touch("touch_box")
def _on_touch():
    label.text = "touch"


@on_double_tap("double_box")
def _on_double_tap():
    label.text = "double"


@on_swipe("swipe_box")
def _on_swipe():
    label.text = "swipe"


@on_scroll("scroll_box")
def _on_scroll():
    label.text = "scroll"


@on_fling("fling_box")
def _on_fling():
    label.text = "fling"


@on_pinch("pinch_box")
def _on_pinch():
    label.text = "pinch"


@on_zoom("zoom_box")
def _on_zoom():
    label.text = "zoom"


@on_rotate_gesture("rotate_box")
def _on_rotate_gesture():
    label.text = "rotate"


@on_scale_gesture_detector("scale_box")
def _on_scale_gesture_detector():
    label.text = "scale"


@on_drag("drag_box")
def _on_drag():
    label.text = "drag"


@on_drop("drop_box")
def _on_drop():
    label.text = "drop"


@on_editor_action("input_action")
def _on_editor_action():
    label.text = "editor"


@on_key("key_btn")
def _on_key():
    label.text = "key"


def test_program4_extended_event_listener_emission(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            ui(
                text("Label", id="label"),
                button("Long", id="long_btn"),
                view(id="touch_box", width=12, height=12),
                view(id="double_box", width=12, height=12),
                view(id="swipe_box", width=12, height=12),
                view(id="scroll_box", width=12, height=12),
                view(id="fling_box", width=12, height=12),
                view(id="pinch_box", width=12, height=12),
                view(id="zoom_box", width=12, height=12),
                view(id="rotate_box", width=12, height=12),
                view(id="scale_box", width=12, height=12),
                view(id="drag_box", width=12, height=12),
                view(id="drop_box", width=12, height=12),
                TextField("", id="input_action"),
                button("Key", id="key_btn"),
            ),
            _on_long_click,
            _on_touch,
            _on_double_tap,
            _on_swipe,
            _on_scroll,
            _on_fling,
            _on_pinch,
            _on_zoom,
            _on_rotate_gesture,
            _on_scale_gesture_detector,
            _on_drag,
            _on_drop,
            _on_editor_action,
            _on_key,
        )
    ).build()

    out_dir = emit_build_dir_from_program(prog, out_dir=tmp_path / "build", class_name="LTest;")
    main_smali = (out_dir / "smali" / "Test.smali").read_text(encoding="utf-8")

    def _listener(name):
        return (out_dir / "smali" / "com" / "ahnali" / "preview" / name).read_text(encoding="utf-8")

    long_text = _listener("AhnaliLongClickListener_long_btn.smali")
    assert "implements Landroid/view/View$OnLongClickListener;" in long_text
    assert "invoke-static {p1}, LTestHandlers;->onLongClick_long_btn(Landroid/view/View;)V" in long_text
    assert "Landroid/view/View;->setOnLongClickListener" in main_smali

    touch_text = _listener("AhnaliTouchListener_touch_box.smali")
    assert "implements Landroid/view/View$OnTouchListener;" in touch_text
    assert "invoke-static {p1, p2}, LTestHandlers;->onTouch_touch_box(Landroid/view/View;Landroid/view/MotionEvent;)V" in touch_text
    assert "Landroid/view/View;->setOnTouchListener" in main_smali

    double_text = _listener("AhnaliDoubleTapListener_double_box.smali")
    assert "implements Landroid/view/View$OnTouchListener;" in double_text
    assert "invoke-static {p1, p2}, LTestHandlers;->onDoubleTap_double_box(Landroid/view/View;Landroid/view/MotionEvent;)V" in double_text

    swipe_text = _listener("AhnaliSwipeListener_swipe_box.smali")
    assert "invoke-static {p1, p2}, LTestHandlers;->onSwipe_swipe_box(Landroid/view/View;Landroid/view/MotionEvent;)V" in swipe_text

    scroll_text = _listener("AhnaliScrollListener_scroll_box.smali")
    assert "invoke-static {p1, p2}, LTestHandlers;->onScroll_scroll_box(Landroid/view/View;Landroid/view/MotionEvent;)V" in scroll_text

    fling_text = _listener("AhnaliFlingListener_fling_box.smali")
    assert "invoke-static {p1, p2}, LTestHandlers;->onFling_fling_box(Landroid/view/View;Landroid/view/MotionEvent;)V" in fling_text

    pinch_text = _listener("AhnaliPinchListener_pinch_box.smali")
    assert "invoke-static {p1, p2}, LTestHandlers;->onPinch_pinch_box(Landroid/view/View;Landroid/view/MotionEvent;)V" in pinch_text

    zoom_text = _listener("AhnaliZoomListener_zoom_box.smali")
    assert "invoke-static {p1, p2}, LTestHandlers;->onZoom_zoom_box(Landroid/view/View;Landroid/view/MotionEvent;)V" in zoom_text

    rotate_text = _listener("AhnaliRotateGestureListener_rotate_box.smali")
    assert "invoke-static {p1, p2}, LTestHandlers;->onRotateGesture_rotate_box(Landroid/view/View;Landroid/view/MotionEvent;)V" in rotate_text

    scale_text = _listener("AhnaliScaleGestureListener_scale_box.smali")
    assert (
        "invoke-static {p1, p2}, "
        "LTestHandlers;->onScaleGestureDetector_scale_box(Landroid/view/View;Landroid/view/MotionEvent;)V"
    ) in scale_text

    drag_text = _listener("AhnaliDragListener_drag_box.smali")
    assert "implements Landroid/view/View$OnDragListener;" in drag_text
    assert "invoke-static {p1, p2}, LTestHandlers;->onDrag_drag_box(Landroid/view/View;Landroid/view/DragEvent;)V" in drag_text
    assert "Landroid/view/View;->setOnDragListener" in main_smali

    drop_text = _listener("AhnaliDropListener_drop_box.smali")
    assert "implements Landroid/view/View$OnDragListener;" in drop_text
    assert "invoke-static {p1, p2}, LTestHandlers;->onDrop_drop_box(Landroid/view/View;Landroid/view/DragEvent;)V" in drop_text

    editor_text = _listener("AhnaliEditorActionListener_input_action.smali")
    assert "implements Landroid/widget/TextView$OnEditorActionListener;" in editor_text
    assert (
        "invoke-static {p1, p2, p3}, "
        "LTestHandlers;->onEditorAction_input_action(Landroid/widget/TextView;ILandroid/view/KeyEvent;)V"
    ) in editor_text
    assert "Landroid/widget/TextView;->setOnEditorActionListener" in main_smali

    key_text = _listener("AhnaliKeyListener_key_btn.smali")
    assert "implements Landroid/view/View$OnKeyListener;" in key_text
    assert "invoke-static {p1, p2, p3}, LTestHandlers;->onKey_key_btn(Landroid/view/View;ILandroid/view/KeyEvent;)V" in key_text
    assert "Landroid/view/View;->setOnKeyListener" in main_smali

    kinds = {kind for _, _, _, kind in prog.support_classes}
    assert {
        "long_click",
        "touch",
        "double_tap",
        "swipe",
        "scroll",
        "fling",
        "pinch",
        "zoom",
        "rotate_gesture",
        "scale_gesture_detector",
        "drag",
        "drop",
        "editor_action",
        "key",
    }.issubset(kinds)


def test_program4_on_editor_action_requires_text_field_target():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Label", id="label"), button("Nope", id="btn")),
            on_editor_action("btn", []),
        )
    )
    with pytest.raises(RuntimeError, match="on_editor_action target 'btn' must be text_field"):
        prog.build()


def test_program4_touch_alias_conflict_rules_are_deterministic():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Label", id="label"), view(id="gesture_box", width=12, height=12)),
            on_touch("gesture_box", []),
            on_swipe("gesture_box", []),
        )
    )
    with pytest.raises(RuntimeError, match="Duplicate event binding"):
        prog.build()


def test_program4_drag_drop_conflict_rules_are_deterministic():
    prog = app(
        activity(
            "MainActivity",
            ui(text("Label", id="label"), view(id="drag_box", width=12, height=12)),
            on_drag("drag_box", []),
            on_drop("drag_box", []),
        )
    )
    with pytest.raises(RuntimeError, match="Duplicate event binding"):
        prog.build()
