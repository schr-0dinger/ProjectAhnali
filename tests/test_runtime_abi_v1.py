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
        "change",
        "slider_change",
        "radiogroup_change",
        "text_change",
        "item_selected",
        "focus_change",
        "menu_item_selected",
        "list_adapter",
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
        "Permissions",
        "Sensors",
        "Storage",
        "URLLauncher",
        "Video",
        "WebView",
    ]


def test_runtime_abi_capability_mapping_alias_resolution_contract():
    bindings = resolve_runtime_bindings(["File Picker", "URL launcher", "FilePicker", "URLLauncher"])
    assert [binding.capability for binding in bindings] == ["FilePicker", "URLLauncher"]


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
