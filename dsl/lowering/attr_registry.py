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
}
