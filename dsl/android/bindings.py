from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AndroidBindingSpec:
    name: str
    mode: str
    lowering: str
    owner_desc: str | None = None
    member_name: str | None = None
    invoke_kind: str | None = None
    arg_types: tuple[str, ...] = field(default_factory=tuple)
    return_type: str | None = None
    analyzer_flags: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""


def default_android_binding_registry() -> dict[str, AndroidBindingSpec]:
    bindings = [
        AndroidBindingSpec(
            name="android_uri_parse",
            mode="expr",
            lowering="direct_call",
            owner_desc="Landroid/net/Uri;",
            member_name="parse",
            invoke_kind="static",
            arg_types=("Ljava/lang/String;",),
            return_type="Landroid/net/Uri;",
            analyzer_flags=("uri_binding",),
            description="Parse a bounded string expression into android.net.Uri.",
        ),
        AndroidBindingSpec(
            name="android_intent_view",
            mode="expr",
            lowering="custom_factory",
            owner_desc="Landroid/content/Intent;",
            member_name="<init>+setData",
            invoke_kind="direct",
            arg_types=("Landroid/net/Uri;",),
            return_type="Landroid/content/Intent;",
            analyzer_flags=("intent_binding",),
            description="Create ACTION_VIEW intents for supported Uri values.",
        ),
        AndroidBindingSpec(
            name="android_intent_chooser",
            mode="expr",
            lowering="direct_call",
            owner_desc="Landroid/content/Intent;",
            member_name="createChooser",
            invoke_kind="static",
            arg_types=("Landroid/content/Intent;", "Ljava/lang/CharSequence;"),
            return_type="Landroid/content/Intent;",
            analyzer_flags=("intent_binding",),
            description="Wrap a supported Intent in a chooser dialog Intent.",
        ),
        AndroidBindingSpec(
            name="android_start_activity",
            mode="stmt",
            lowering="direct_call",
            owner_desc="Landroid/app/Activity;",
            member_name="startActivity",
            invoke_kind="virtual",
            arg_types=("Landroid/content/Intent;",),
            return_type=None,
            analyzer_flags=("activity_binding",),
            description="Launch a supported Intent through the current Activity context.",
        ),
    ]
    return {binding.name: binding for binding in bindings}


def get_android_binding(name: str) -> AndroidBindingSpec | None:
    return default_android_binding_registry().get(str(name))
