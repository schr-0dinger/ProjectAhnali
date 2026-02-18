import pytest

from dsl.capabilities import (
    CAPABILITY_RUNTIME_ABI_VERSION,
    default_capability_runtime_mapping,
    resolve_runtime_bindings,
)
from dsl.app import (
    Switch,
    activity,
    app,
    button,
    list_view,
    on_change,
    on_click,
    state,
    ui,
)
from emit.smali_activity import emit_activity_wrapper_smali, emit_event_listener_smali


def test_runtime_abi_wrapper_zero_arg_main_signature():
    smali = emit_activity_wrapper_smali(
        activity_desc="Lcom/ahnali/preview/MainActivity;",
        target_desc="LTest;",
        target_sig="()V",
        emit_system_back_bridge=False,
    )

    assert ".class public Lcom/ahnali/preview/MainActivity;" in smali
    assert ".method public constructor <init>()V" in smali
    assert ".method protected onCreate(Landroid/os/Bundle;)V" in smali
    assert "invoke-static {}, LTest;->main()V" in smali


def test_runtime_abi_wrapper_activity_arg_and_back_bridge_signature():
    smali = emit_activity_wrapper_smali(
        activity_desc="Lcom/ahnali/preview/MainActivity;",
        target_desc="LTest;",
        target_sig="(Landroid/app/Activity;)V",
        emit_system_back_bridge=True,
        back_sig="()I",
        back_method="onSystemBack",
    )

    assert "invoke-static {p0}, LTest;->main(Landroid/app/Activity;)V" in smali
    assert ".method public onBackPressed()V" in smali
    assert "invoke-static {}, LTest;->onSystemBack()I" in smali
    assert "if-eqz v0, :ahnali_call_super" in smali
    assert "invoke-super {p0}, Landroid/app/Activity;->onBackPressed()V" in smali


def test_runtime_abi_wrapper_lifecycle_bridge_signature():
    smali = emit_activity_wrapper_smali(
        activity_desc="Lcom/ahnali/preview/MainActivity;",
        target_desc="LTest;",
        target_sig="(Landroid/app/Activity;)V",
        lifecycle_bridges=["onStart", "onResume", "onPause", "onStop", "onDestroy"],
    )

    assert ".method protected onStart()V" in smali
    assert ".method protected onResume()V" in smali
    assert ".method protected onPause()V" in smali
    assert ".method protected onStop()V" in smali
    assert ".method protected onDestroy()V" in smali
    assert "invoke-static {}, LTest;->onStart()V" in smali
    assert "invoke-static {}, LTest;->onResume()V" in smali
    assert "invoke-static {}, LTest;->onPause()V" in smali
    assert "invoke-static {}, LTest;->onStop()V" in smali
    assert "invoke-static {}, LTest;->onDestroy()V" in smali


@pytest.mark.parametrize(
    "kind, iface, callback_sig, invoke_sig, extra_fragments",
    [
        (
            "click",
            "Landroid/view/View$OnClickListener;",
            ".method public onClick(Landroid/view/View;)V",
            "invoke-static {p1}, LTarget;->handle(Landroid/view/View;)V",
            [],
        ),
        (
            "long_click",
            "Landroid/view/View$OnLongClickListener;",
            ".method public onLongClick(Landroid/view/View;)Z",
            "invoke-static {p1}, LTarget;->handle(Landroid/view/View;)V",
            [
                "const/4 v0, 0x1",
                "return v0",
            ],
        ),
        (
            "touch",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [
                "const/4 v0, 0x1",
                "return v0",
            ],
        ),
        (
            "double_tap",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [],
        ),
        (
            "swipe",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [],
        ),
        (
            "scroll",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [],
        ),
        (
            "fling",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [],
        ),
        (
            "pinch",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [],
        ),
        (
            "zoom",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [],
        ),
        (
            "rotate_gesture",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [],
        ),
        (
            "scale_gesture_detector",
            "Landroid/view/View$OnTouchListener;",
            ".method public onTouch(Landroid/view/View;Landroid/view/MotionEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/MotionEvent;)V",
            [],
        ),
        (
            "drag",
            "Landroid/view/View$OnDragListener;",
            ".method public onDrag(Landroid/view/View;Landroid/view/DragEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/DragEvent;)V",
            [],
        ),
        (
            "drop",
            "Landroid/view/View$OnDragListener;",
            ".method public onDrag(Landroid/view/View;Landroid/view/DragEvent;)Z",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Landroid/view/DragEvent;)V",
            [],
        ),
        (
            "editor_action",
            "Landroid/widget/TextView$OnEditorActionListener;",
            ".method public onEditorAction(Landroid/widget/TextView;ILandroid/view/KeyEvent;)Z",
            "invoke-static {p1, p2, p3}, LTarget;->handle(Landroid/widget/TextView;ILandroid/view/KeyEvent;)V",
            [],
        ),
        (
            "key",
            "Landroid/view/View$OnKeyListener;",
            ".method public onKey(Landroid/view/View;ILandroid/view/KeyEvent;)Z",
            "invoke-static {p1, p2, p3}, LTarget;->handle(Landroid/view/View;ILandroid/view/KeyEvent;)V",
            [],
        ),
        (
            "change",
            "Landroid/widget/CompoundButton$OnCheckedChangeListener;",
            ".method public onCheckedChanged(Landroid/widget/CompoundButton;Z)V",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/widget/CompoundButton;Z)V",
            [],
        ),
        (
            "slider_change",
            "Landroid/widget/SeekBar$OnSeekBarChangeListener;",
            ".method public onProgressChanged(Landroid/widget/SeekBar;IZ)V",
            "invoke-static {p1, p2, p3}, LTarget;->handle(Landroid/widget/SeekBar;IZ)V",
            [
                ".method public onStartTrackingTouch(Landroid/widget/SeekBar;)V",
                ".method public onStopTrackingTouch(Landroid/widget/SeekBar;)V",
            ],
        ),
        (
            "radiogroup_change",
            "Landroid/widget/RadioGroup$OnCheckedChangeListener;",
            ".method public onCheckedChanged(Landroid/widget/RadioGroup;I)V",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/widget/RadioGroup;I)V",
            [],
        ),
        (
            "text_change",
            "Landroid/text/TextWatcher;",
            ".method public afterTextChanged(Landroid/text/Editable;)V",
            "invoke-static {p1}, LTarget;->handle(Landroid/text/Editable;)V",
            [
                ".method public beforeTextChanged(Ljava/lang/CharSequence;III)V",
                ".method public onTextChanged(Ljava/lang/CharSequence;III)V",
            ],
        ),
        (
            "item_selected",
            "Landroid/widget/AdapterView$OnItemSelectedListener;",
            ".method public onItemSelected(Landroid/widget/AdapterView;Landroid/view/View;IJ)V",
            "invoke-static {p1, p2, p3, p4, p5}, LTarget;->handle(Landroid/widget/AdapterView;Landroid/view/View;IJ)V",
            [
                ".method public onNothingSelected(Landroid/widget/AdapterView;)V",
            ],
        ),
        (
            "focus_change",
            "Landroid/view/View$OnFocusChangeListener;",
            ".method public onFocusChange(Landroid/view/View;Z)V",
            "invoke-static {p1, p2}, LTarget;->handle(Landroid/view/View;Z)V",
            [],
        ),
        (
            "menu_item_selected",
            "Landroid/widget/PopupMenu$OnMenuItemClickListener;",
            ".method public onMenuItemClick(Landroid/view/MenuItem;)Z",
            "invoke-static {p1}, LTarget;->handle(Landroid/view/MenuItem;)V",
            [
                "const/4 v0, 0x1",
                "return v0",
            ],
        ),
    ],
)
def test_runtime_abi_listener_kind_contract(kind, iface, callback_sig, invoke_sig, extra_fragments):
    smali = emit_event_listener_smali(
        class_desc="Lcom/ahnali/preview/AhnaliAbiContract;",
        target_desc="LTarget;",
        target_method="handle",
        listener_kind=kind,
    )

    assert ".super Ljava/lang/Object;" in smali
    assert f".implements {iface}" in smali
    assert ".method public constructor <init>()V" in smali
    assert callback_sig in smali
    assert invoke_sig in smali
    for fragment in extra_fragments:
        assert fragment in smali


def test_runtime_abi_list_adapter_contract_shape():
    smali = emit_event_listener_smali(
        class_desc="Lcom/ahnali/preview/AhnaliListAdapter_contract;",
        target_desc="LTarget;",
        target_method="0x1090003",
        listener_kind="list_adapter",
    )

    assert ".super Landroid/widget/BaseAdapter;" in smali
    assert ".field private final mInflater:Landroid/view/LayoutInflater;" in smali
    assert ".field private final mItems:[Ljava/lang/String;" in smali
    assert ".method public constructor <init>(Landroid/content/Context;[Ljava/lang/String;)V" in smali
    assert ".method public getCount()I" in smali
    assert ".method public getItem(I)Ljava/lang/Object;" in smali
    assert ".method public getItemId(I)J" in smali
    assert ".method public getView(ILandroid/view/View;Landroid/view/ViewGroup;)Landroid/view/View;" in smali
    assert "const v1, 0x1090003" in smali
    assert "Landroid/view/View;->setTag(Ljava/lang/Object;)V" in smali
    assert "Landroid/view/View;->getTag()Ljava/lang/Object;" in smali


def test_runtime_abi_ui_runnable_click_contract_shape():
    smali = emit_event_listener_smali(
        class_desc="Lcom/ahnali/preview/AhnaliUiRunnable_demo;",
        target_desc="LTarget;",
        target_method="onClick_demo",
        listener_kind="ui_runnable_click",
    )

    assert ".super Ljava/lang/Object;" in smali
    assert ".implements Ljava/lang/Runnable;" in smali
    assert ".field private final mView:Landroid/view/View;" in smali
    assert ".method public constructor <init>(Landroid/view/View;)V" in smali
    assert ".method public run()V" in smali
    assert "invoke-static {v0}, LTarget;->onClick_demo(Landroid/view/View;)V" in smali


def test_runtime_abi_http_route_async_worker_contract_shape():
    smali = emit_event_listener_smali(
        class_desc="Lcom/ahnali/preview/AhnaliHttpRouteAsyncWorker;",
        target_desc="LTarget;",
        target_method="unused",
        listener_kind="http_route_async_worker",
    )

    assert ".super Ljava/lang/Object;" in smali
    assert ".implements Ljava/lang/Runnable;" in smali
    assert ".field private final mCtx:Landroid/app/Activity;" in smali
    assert ".field private final mOnSuccess:Ljava/lang/Runnable;" in smali
    assert ".field private final mOnFailure:Ljava/lang/Runnable;" in smali
    assert ".field private final mOnProgress:Ljava/lang/Runnable;" in smali
    assert ".field private final mToken:I" in smali
    assert ".field private final mRetries:I" in smali
    assert ".field private final mTimeoutMs:I" in smali
    assert (
        ".method public constructor <init>(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/Runnable;Ljava/lang/Runnable;III)V"
        in smali
    )
    assert ".method public run()V" in smali
    assert "Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V" in smali
    assert (
        "Lcom/ahnali/runtime/HttpHelper;->httpRequestStatusWithTimeout("
        "Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I"
    ) in smali


@on_click("inc")
def _inc():
    count += 1


@on_change("toggle")
def _toggle():
    count += 1


def test_runtime_abi_support_classes_canonical_tuple_schema():
    prog = app(
        activity(
            "MainActivity",
            state(count=0),
            ui(
                button("+", id="inc"),
                Switch("Toggle", id="toggle"),
                list_view(id="todos", items=["A", "B"]),
            ),
            _inc,
            _toggle,
        )
    ).build()

    entries = prog.support_classes
    assert entries
    assert all(len(entry) == 4 for entry in entries)

    allowed_kinds = {
        "click",
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
        "change",
        "slider_change",
        "radiogroup_change",
        "text_change",
        "item_selected",
        "focus_change",
        "menu_item_selected",
        "list_adapter",
        "ui_runnable_click",
        "http_route_async_worker",
    }

    kinds = {kind for _, _, _, kind in entries}
    assert {"click", "change", "list_adapter"}.issubset(kinds)
    assert kinds.issubset(allowed_kinds)

    for class_desc, target_method, target_desc, kind in entries:
        assert class_desc.startswith("Lcom/ahnali/preview/Ahnali")
        assert class_desc.endswith(";")
        assert target_desc.startswith("L")
        assert target_desc.endswith(";")
        if kind == "list_adapter":
            int(str(target_method), 0)


def test_runtime_abi_capability_mapping_surface_is_frozen_v1():
    assert CAPABILITY_RUNTIME_ABI_VERSION == "1.0.0"
    mapping = default_capability_runtime_mapping()
    assert sorted(mapping.keys()) == [
        "Audio",
        "Camera",
        "Connectivity",
        "FilePicker",
        "Location",
        "Maps",
        "Microphone",
        "Networking",
        "Notifications",
        "Permissions",
        "Sensors",
        "Storage",
        "URLLauncher",
        "Video",
        "WebView",
    ]


def test_runtime_abi_capability_mapping_alias_resolution_contract():
    bindings = resolve_runtime_bindings(
        ["File Picker", "Network", "URL launcher", "FilePicker", "Networking", "URLLauncher"]
    )
    assert [binding.capability for binding in bindings] == ["FilePicker", "Networking", "URLLauncher"]


def test_runtime_abi_url_launcher_helper_binding_contract():
    mapping = default_capability_runtime_mapping()
    binding = mapping["URLLauncher"]
    assert binding.mode == "helper_call"
    assert binding.helper_class_desc == "Lcom/ahnali/runtime/UrlLauncherHelper;"
    assert binding.helper_method == "openUrl"
    assert binding.helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)I"


def test_runtime_abi_connectivity_helper_binding_contract():
    mapping = default_capability_runtime_mapping()
    binding = mapping["Connectivity"]
    assert binding.mode == "helper_call"
    assert binding.helper_class_desc == "Lcom/ahnali/runtime/ConnectivityHelper;"
    assert binding.helper_method == "isConnected"
    assert binding.helper_sig == "(Landroid/app/Activity;)I"


def test_runtime_abi_storage_helper_binding_contract():
    mapping = default_capability_runtime_mapping()
    binding = mapping["Storage"]
    assert binding.mode == "helper_call"
    assert binding.helper_class_desc == "Lcom/ahnali/runtime/StorageHelper;"
    assert binding.helper_method == "putString"
    assert binding.helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"


def test_runtime_abi_location_helper_binding_contract():
    mapping = default_capability_runtime_mapping()
    binding = mapping["Location"]
    assert binding.mode == "helper_call"
    assert binding.helper_class_desc == "Lcom/ahnali/runtime/LocationHelper;"
    assert binding.helper_method == "isLocationEnabled"
    assert binding.helper_sig == "(Landroid/app/Activity;)I"


def test_runtime_abi_permissions_helper_binding_contract():
    mapping = default_capability_runtime_mapping()
    binding = mapping["Permissions"]
    assert binding.mode == "helper_call"
    assert binding.helper_class_desc == "Lcom/ahnali/runtime/PermissionHelper;"
    assert binding.helper_method == "isGranted"
    assert binding.helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)I"


def test_runtime_abi_notifications_helper_binding_contract():
    mapping = default_capability_runtime_mapping()
    binding = mapping["Notifications"]
    assert binding.mode == "helper_call"
    assert binding.helper_class_desc == "Lcom/ahnali/runtime/NotificationHelper;"
    assert binding.helper_method == "postNotification"
    assert (
        binding.helper_sig
        == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    )


def test_runtime_abi_networking_helper_binding_contract():
    mapping = default_capability_runtime_mapping()
    binding = mapping["Networking"]
    assert binding.mode == "helper_call"
    assert binding.helper_class_desc == "Lcom/ahnali/runtime/HttpHelper;"
    assert binding.helper_method == "httpGet"
    assert binding.helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
