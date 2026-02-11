# dsl/lowering/attr_registry.py

from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class AttrMethod:
    """
    Metadata describing how a DSL attribute maps to an Android method call.
    """
    method: str                     # e.g. "setPadding"
    owner: Optional[str] = None                 # e.g. "Landroid/view/View;"
    invoke_kind: str = "virtual"
    arg_types: Optional[Sequence[str]] = None
    value_loader: Optional[str] = None
    owner_resolver: Optional[str] = None
    supported_kinds: Optional[Sequence[str]] = None
    arg_prefix: Optional[Sequence[object]] = None
    emit_kind: str = "call"  # call | field_set | custom
    field_name: Optional[str] = None
    field_desc: Optional[str] = None
    field_map: Optional[dict] = None
    # value_loader is a symbolic hook name, not a function (keeps registry pure)


ATTR_METHODS = {
    # ---- layout / view ----
    "padding": AttrMethod(
        method="setPadding",
        owner="Landroid/view/View;",
        arg_types=["I", "I", "I", "I"],
        value_loader="dimen_px_4",
        supported_kinds=None,
    ),

    "gravity": AttrMethod(
        method="setGravity",
        arg_types=["I"],
        owner_resolver="gravity_owner",
        supported_kinds=None,
    ),

    "align": AttrMethod(
        method="setGravity",
        arg_types=["I"],
        owner_resolver="gravity_owner",
        supported_kinds=None,
    ),

    "arrangement": AttrMethod(
        method="setGravity",
        arg_types=["I"],
        owner_resolver="gravity_owner",
        supported_kinds=None,
    ),

    "layout_params": AttrMethod(
        method="setLayoutParams",
        owner="Landroid/view/View;",
        arg_types=["Landroid/view/ViewGroup$LayoutParams;"],
        value_loader="layout_params",
        supported_kinds=None,
    ),

    "margin": AttrMethod(
        method="setMargins",
        owner="Landroid/view/ViewGroup$MarginLayoutParams;",
        arg_types=["I", "I", "I", "I"],
        value_loader="margin_px_4",
        supported_kinds=None,
    ),

    "weight": AttrMethod(
        method="weight",
        owner="Landroid/widget/LinearLayout$LayoutParams;",
        value_loader="layout_weight",
        emit_kind="field_set",
        field_name="weight",
        field_desc="F",
        supported_kinds=None,
    ),

    "weight_sum": AttrMethod(
        method="setWeightSum",
        owner="Landroid/widget/LinearLayout;",
        arg_types=["F"],
        value_loader="float",
        supported_kinds=["row", "column"],
    ),

    "relative": AttrMethod(
        method="addRule",
        owner="Landroid/widget/RelativeLayout$LayoutParams;",
        arg_types=["I", "I"],
        value_loader="relative_rules",
        supported_kinds=None,
    ),

    "constraints": AttrMethod(
        method="setConstraint",
        owner="Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;",
        value_loader="constraint_fields",
        supported_kinds=None,
        emit_kind="custom",
        field_map={
            "left_to_left": ("leftToLeft", "I"),
            "left_to_right": ("leftToRight", "I"),
            "right_to_left": ("rightToLeft", "I"),
            "right_to_right": ("rightToRight", "I"),
            "top_to_top": ("topToTop", "I"),
            "top_to_bottom": ("topToBottom", "I"),
            "bottom_to_top": ("bottomToTop", "I"),
            "bottom_to_bottom": ("bottomToBottom", "I"),
            "start_to_start": ("startToStart", "I"),
            "start_to_end": ("startToEnd", "I"),
            "end_to_start": ("endToStart", "I"),
            "end_to_end": ("endToEnd", "I"),
            "baseline_to_baseline": ("baselineToBaseline", "I"),
            "circle": ("circleConstraint", "I"),
            "circle_radius": ("circleRadius", "I"),
            "circle_angle": ("circleAngle", "F"),
            "horizontal_bias": ("horizontalBias", "F"),
            "vertical_bias": ("verticalBias", "F"),
        },
    ),

    # ---- text ----
    "text_color": AttrMethod(
        method="setTextColor",
        owner="Landroid/widget/TextView;",
        arg_types=["I"],
        value_loader="color",
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "text_size": AttrMethod(
        method="setTextSize",
        owner="Landroid/widget/TextView;",
        arg_types=["I", "F"],
        value_loader="dimen_sp_float",
        arg_prefix=[0],
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "typeface": AttrMethod(
        method="setTypeface",
        owner="Landroid/widget/TextView;",
        arg_types=["Landroid/graphics/Typeface;"],
        value_loader="typeface",
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "letter_spacing": AttrMethod(
        method="setLetterSpacing",
        owner="Landroid/widget/TextView;",
        arg_types=["F"],
        value_loader="float",
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "line_height": AttrMethod(
        method="setLineSpacing",
        owner="Landroid/widget/TextView;",
        arg_types=["F", "F"],
        value_loader="line_spacing",
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "text_alignment": AttrMethod(
        method="setTextAlignment",
        owner="Landroid/view/View;",
        arg_types=["I"],
        value_loader="text_alignment",
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "all_caps": AttrMethod(
        method="setAllCaps",
        owner="Landroid/widget/TextView;",
        arg_types=["Z"],
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "max_lines": AttrMethod(
        method="setMaxLines",
        owner="Landroid/widget/TextView;",
        arg_types=["I"],
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "ellipsize": AttrMethod(
        method="setEllipsize",
        owner="Landroid/widget/TextView;",
        arg_types=["Landroid/text/TextUtils$TruncateAt;"],
        value_loader="ellipsize",
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    "text_color_state": AttrMethod(
        method="setTextColor",
        owner="Landroid/widget/TextView;",
        arg_types=["Landroid/content/res/ColorStateList;"],
        value_loader="color_state_list",
        supported_kinds=[
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        ],
    ),

    # ---- background ----
    "background_color": AttrMethod(
        method="setBackgroundColor",
        owner="Landroid/view/View;",
        arg_types=["I"],
        value_loader="color",
        supported_kinds=None,
    ),

    "background": AttrMethod(
        method="setBackground",
        owner="Landroid/view/View;",
        value_loader="background",
        emit_kind="custom",
        supported_kinds=None,
    ),

    "tint": AttrMethod(
        method="setBackgroundTintList",
        owner="Landroid/view/View;",
        arg_types=["Landroid/content/res/ColorStateList;"],
        value_loader="color_state_list",
        supported_kinds=None,
    ),

    "thumb_tint": AttrMethod(
        method="setThumbTintList",
        owner_resolver="thumb_tint_owner",
        arg_types=["Landroid/content/res/ColorStateList;"],
        value_loader="color_state_list",
        supported_kinds=["slider", "switch"],
    ),

    "slider_track_tint": AttrMethod(
        method="setProgressBackgroundTintList",
        owner="Landroid/widget/SeekBar;",
        arg_types=["Landroid/content/res/ColorStateList;"],
        value_loader="color_state_list",
        supported_kinds=["slider"],
    ),

    "switch_track_tint": AttrMethod(
        method="setTrackTintList",
        owner="Landroid/widget/Switch;",
        arg_types=["Landroid/content/res/ColorStateList;"],
        value_loader="color_state_list",
        supported_kinds=["switch"],
    ),

    "progress_tint": AttrMethod(
        method="setProgressTintList",
        owner_resolver="progress_tint_owner",
        arg_types=["Landroid/content/res/ColorStateList;"],
        value_loader="color_state_list",
        supported_kinds=["slider", "progress_bar"],
    ),

    "indeterminate_tint": AttrMethod(
        method="setIndeterminateTintList",
        owner="Landroid/widget/ProgressBar;",
        arg_types=["Landroid/content/res/ColorStateList;"],
        value_loader="color_state_list",
        supported_kinds=["progress_bar"],
    ),

    "button_tint": AttrMethod(
        method="setButtonTintList",
        owner="Landroid/widget/CompoundButton;",
        arg_types=["Landroid/content/res/ColorStateList;"],
        value_loader="color_state_list",
        supported_kinds=["checkbox", "radio", "switch"],
    ),
}
