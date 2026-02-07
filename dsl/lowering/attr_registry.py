# dsl/lowering/attr_registry.py

from dataclasses import dataclass
from typing import Callable, Optional, Sequence


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
    # value_loader is a symbolic hook name, not a function (keeps registry pure)


ATTR_METHODS = {
    # ---- layout / view ----
    "padding": AttrMethod(
        method="setPadding",
        owner="Landroid/view/View;",
        arg_types=["I", "I", "I", "I"],
        value_loader="dimen_px_4",
    ),

    "gravity": AttrMethod(
        method="setGravity",
        arg_types=["I"],
        owner_resolver="gravity_owner",
    ),

    # ---- text ----
    "text_color": AttrMethod(
        method="setTextColor",
        owner="Landroid/widget/TextView;",
        arg_types=["I"],
        value_loader="color",
    ),
}
