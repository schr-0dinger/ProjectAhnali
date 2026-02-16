# Ahnali Runtime ABI v1 Contract

Status: Frozen for v1  
Effective date: 2026-02-16  
Scope: Generated helper/runtime bridge classes emitted by the current AOT toolchain.

This document defines the ABI contract for helper classes that connect generated app code to Android runtime callbacks.

## 1) Scope and Non-Scope

In scope:
- Wrapper Activity bridge (`MainActivity`-style generated class)
- Event listener helper classes (`Ahnali*Listener_*`)
- Static ListView adapter helper class (`AhnaliListAdapter_*`)
- `ProgramIR.support_classes` entry schema used by toolchain emission
- Capability-to-runtime mapping contract for registered capabilities
- Track C Wave 1 capability helper ABI: URL launcher helper

Out of scope:
- Future capability module helper APIs beyond URL launcher helper (network/storage wave expansion planned separately)
- Internal compiler IR structures that are not emitted into helper Smali classes

## 2) Descriptor and Naming Conventions

- Class and method signatures use Smali descriptors.
- Default helper package is `Lcom/ahnali/preview/`.
- Suffixes tied to widget ids are ABI-stable naming patterns.

Stable helper class descriptor patterns:
- Wrapper activity: `Lcom/ahnali/preview/MainActivity;` (default; configurable)
- Click listener: `Lcom/ahnali/preview/AhnaliClickListener_<target_id>;`
- Toggle/radio/switch change listener: `Lcom/ahnali/preview/AhnaliChangeListener_<target_id>;`
- Text change listener: `Lcom/ahnali/preview/AhnaliTextChangeListener_<target_id>;`
- Item selected listener: `Lcom/ahnali/preview/AhnaliItemSelectedListener_<target_id>;`
- Focus change listener: `Lcom/ahnali/preview/AhnaliFocusChangeListener_<target_id>;`
- Popup menu item selected listener: `Lcom/ahnali/preview/AhnaliMenuItemListener_<target_id>;`
- Auto popup click listener: `Lcom/ahnali/preview/AhnaliClickListener_<popup_id>_popup;`
- Static list adapter: `Lcom/ahnali/preview/AhnaliListAdapter_<view_id>;`

## 3) Wrapper Activity ABI

Generated class (default descriptor `Lcom/ahnali/preview/MainActivity;`) must expose:

- `.method public constructor <init>()V`
- `.method protected onCreate(Landroid/os/Bundle;)V`

`onCreate` invocation contract:
- If target signature starts with `()`, wrapper calls: `invoke-static {}, <target_desc>->main()V`
- Otherwise wrapper passes activity instance: `invoke-static {p0}, <target_desc>->main(Landroid/app/Activity;)V`

Optional back bridge (enabled when `onSystemBack` exists and wrapper bridge is emitted):
- `.method public onBackPressed()V`
- Must call: `invoke-static {}, <target_desc>->onSystemBack()I`
- Return semantics: `1` means "handled" and suppresses `invoke-super ... onBackPressed()V`; `0` means "not handled" and wrapper must call `invoke-super ... onBackPressed()V`

Target class ABI required by wrapper:
- `main()V` or `main(Landroid/app/Activity;)V` (selected by configured wrapper target signature)
- Optional `onSystemBack()I` when back bridge is enabled

## 4) Event Listener Helper ABI

All non-adapter listener helper classes must:
- Extend `Ljava/lang/Object;`
- Implement the matching Android listener interface
- Expose `.method public constructor <init>()V`
- Forward callback arguments to a static handler method on `target_desc`

Stable listener-kind mapping:

| Kind | Interface | Required callback methods | Target static method signature |
|---|---|---|---|
| `click` | `Landroid/view/View$OnClickListener;` | `onClick(Landroid/view/View;)V` | `<target_method>(Landroid/view/View;)V` |
| `change` | `Landroid/widget/CompoundButton$OnCheckedChangeListener;` | `onCheckedChanged(Landroid/widget/CompoundButton;Z)V` | `<target_method>(Landroid/widget/CompoundButton;Z)V` |
| `slider_change` | `Landroid/widget/SeekBar$OnSeekBarChangeListener;` | `onProgressChanged(Landroid/widget/SeekBar;IZ)V`, `onStartTrackingTouch(Landroid/widget/SeekBar;)V`, `onStopTrackingTouch(Landroid/widget/SeekBar;)V` | `<target_method>(Landroid/widget/SeekBar;IZ)V` |
| `radiogroup_change` | `Landroid/widget/RadioGroup$OnCheckedChangeListener;` | `onCheckedChanged(Landroid/widget/RadioGroup;I)V` | `<target_method>(Landroid/widget/RadioGroup;I)V` |
| `text_change` | `Landroid/text/TextWatcher;` | `beforeTextChanged(Ljava/lang/CharSequence;III)V`, `onTextChanged(Ljava/lang/CharSequence;III)V`, `afterTextChanged(Landroid/text/Editable;)V` | `<target_method>(Landroid/text/Editable;)V` |
| `item_selected` | `Landroid/widget/AdapterView$OnItemSelectedListener;` | `onItemSelected(Landroid/widget/AdapterView;Landroid/view/View;IJ)V`, `onNothingSelected(Landroid/widget/AdapterView;)V` | `<target_method>(Landroid/widget/AdapterView;Landroid/view/View;IJ)V` |
| `focus_change` | `Landroid/view/View$OnFocusChangeListener;` | `onFocusChange(Landroid/view/View;Z)V` | `<target_method>(Landroid/view/View;Z)V` |
| `menu_item_selected` | `Landroid/widget/PopupMenu$OnMenuItemClickListener;` | `onMenuItemClick(Landroid/view/MenuItem;)Z` | `<target_method>(Landroid/view/MenuItem;)V` and listener returns constant `true` |

Handler owner contract:
- In pythonic DSL lowering, target handler owner is typically `LTestHandlers;`.
- Handler method names are deterministic: `onClick_<id>`, `onChange_<id>`, `onTextChange_<id>`, `onItemSelected_<id>`, `onFocusChange_<id>`, `onMenuItemSelected_<id>`

## 5) Static List Adapter Helper ABI

`list_adapter` kind emits a class that:
- Extends `Landroid/widget/BaseAdapter;`
- Declares fields: `mInflater:Landroid/view/LayoutInflater;`, `mItems:[Ljava/lang/String;`

Required methods:
- `.method public constructor <init>(Landroid/content/Context;[Ljava/lang/String;)V`
- `.method public getCount()I`
- `.method public getItem(I)Ljava/lang/Object;`
- `.method public getItemId(I)J`
- `.method public getView(ILandroid/view/View;Landroid/view/ViewGroup;)Landroid/view/View;`

Behavior contract:
- Uses deterministic holder pattern via `View.setTag/getTag`
- Binds `String` item values to `android.R.id.text1` (`0x1020014`) `TextView`
- Uses deterministic item layout resource id passed through support-class metadata

## 6) `support_classes` Entry ABI

Canonical v1 entry shape:
- `(class_desc, target_method, target_desc, kind)`

Where:
- `class_desc`: emitted helper class descriptor
- `target_method`: static method name on `target_desc`  
  For `list_adapter`, this is the decimal/string form of layout resource id.
- `target_desc`: class descriptor containing static callback method
- `kind`: one of `click`, `change`, `slider_change`, `radiogroup_change`, `text_change`, `item_selected`, `focus_change`, `menu_item_selected`, `list_adapter`

Compatibility note:
- Toolchain currently accepts legacy tuple lengths (2/3 entries), but 4-entry form is the stable ABI form for v1.

## 7) Versioning Rules

Versioning model: `MAJOR.MINOR.PATCH`.

`MAJOR` bump required for any breaking ABI change, including:
- Renaming/removing helper class descriptor patterns
- Changing method descriptors (argument or return types)
- Changing callback interface implementations
- Changing `onSystemBack()I` semantic meaning
- Removing accepted `kind` values

`MINOR` bump for additive, backward-compatible changes:
- New helper kind with new class pattern
- New optional helper class that does not modify existing signatures
- New optional methods that do not alter existing callback contracts

`PATCH` bump for non-ABI changes:
- Internal implementation refactors
- Performance changes with unchanged descriptors/signatures/semantics
- Documentation clarifications

Deprecation policy:
- Any planned removal/rename must be announced in docs first and preserved for at least one `MINOR` cycle before a `MAJOR` removal.

## 8) Capability Mapping Companion Contract

- Companion mapping document: `docs/capability_runtime_mapping_v1.md`
- Code source of truth: `dsl/capabilities.py`
- ABI version constant: `CAPABILITY_RUNTIME_ABI_VERSION = "1.0.0"`
- Capability modes are `permission_only` or `helper_call`.
- Track C Wave 1 helper-call binding:
  - Capability: `URLLauncher`
  - Helper class: `Lcom/ahnali/runtime/UrlLauncherHelper;`
  - Helper method/sig: `openUrl(Landroid/app/Activity;Ljava/lang/String;)I`
  - Return semantics: `1` on successful dispatch to `Activity.startActivity`, `0` on null input or caught exception.

## 9) Conformance References

Current behavior is enforced by tests including:
- `tests/test_runtime_abi_v1.py`
- `tests/test_capabilities.py`
- `tests/test_support_click_listener.py`
- `tests/test_event_surface_listeners.py`
- `tests/test_navigation_stack.py`
- `tests/test_omega_toolchain_scaffold.py`
- `tests/test_list_view_static.py`
