from __future__ import annotations

from dsl.ir_helpers import add_view, assign, call_stmt, const, linear_layout, new, var
from dsl.widgets import (
    _UIAppBar,
    _UIButton,
    _UICard,
    _UICheckbox,
    _UIColumn,
    _UIDivider,
    _UIDropdownButton,
    _UIFlatButton,
    _UIFloatingActionButton,
    _UIIcon,
    _UIIconButton,
    _UIImage,
    _UIPopupMenuButton,
    _UIProgressBar,
    _UIRadio,
    _UIRaisedButton,
    _UISlider,
    _UISwitch,
    _UITextField,
    _UIText,
    _UIView,
    Dp,
)


_MATERIAL_BUTTON = "Lcom/google/android/material/button/MaterialButton;"
_MATERIAL_TOOLBAR = "Lcom/google/android/material/appbar/MaterialToolbar;"
_MATERIAL_FAB = "Lcom/google/android/material/floatingactionbutton/FloatingActionButton;"
_MATERIAL_TEXT_FIELD = "Lcom/google/android/material/textfield/TextInputEditText;"
_MATERIAL_CHECKBOX = "Lcom/google/android/material/checkbox/MaterialCheckBox;"
_MATERIAL_RADIO = "Lcom/google/android/material/radiobutton/MaterialRadioButton;"
_MATERIAL_SWITCH = "Lcom/google/android/material/switchmaterial/SwitchMaterial;"
_MATERIAL_SLIDER = "Lcom/google/android/material/slider/Slider;"
_MATERIAL_PROGRESS_LINEAR = "Lcom/google/android/material/progressindicator/LinearProgressIndicator;"
_MATERIAL_PROGRESS_CIRCULAR = "Lcom/google/android/material/progressindicator/CircularProgressIndicator;"
_MATERIAL_TEXT = "Lcom/google/android/material/textview/MaterialTextView;"
_MATERIAL_DROPDOWN = "Lcom/google/android/material/textfield/MaterialAutoCompleteTextView;"
_MATERIAL_TEXT_INPUT_LAYOUT = "Lcom/google/android/material/textfield/TextInputLayout;"
_MATERIAL_DIVIDER = "Lcom/google/android/material/divider/MaterialDivider;"
_MATERIAL_CARD = "Lcom/google/android/material/card/MaterialCardView;"
_MATERIAL_IMAGE = "Lcom/google/android/material/imageview/ShapeableImageView;"

# TODO(material-pending): Implement remaining Material surfaces in this plugin.
# Input:
# - Number field specialization (input_type=number / decimal / phone)
# - Rating
# - Transfer list
# - Toggle button + button toggle group (MaterialButtonToggleGroup)
# Data display:
# - Avatar
# - Badge
# - Chip / chip group
# - List
# - Table
# - Tooltip
# Feedback:
# - Material alert dialog (replace AlertDialog fallback)
# - Alert surface
# - Backdrop
# - Skeleton / placeholder
# Surfaces:
# - Accordion / expandable panels
# - Paper
# Navigation:
# - Bottom navigation
# - Breadcrumbs
# - Drawer
# - Link
# - Pagination
# - Speed dial
# - Stepper
# - Tabs


def _collect_material_deps(ui_items, click_specs):
    # Material-only UI path requires these AndroidX dependencies.
    required_aars = {
        "material",
        "appcompat",
        "core",
        "coordinatorlayout",
        "activity",
        "fragment",
        "savedstate",
        "drawerlayout",
        "recyclerview",
        "transition",
        "cardview",
        "cursoradapter",
        "emoji2",
        "interpolator",
        "customview",
    }
    # AppCompat/Material runtime also needs androidx.collection classes.
    jar_allowlist = {
        "collection",
    }
    return required_aars, jar_allowlist


def _finalize_view(ctx, item, parent_id, body):
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def _layout_proxy(item, view_id, *, layout_override=None):
    return _UIView(
        id=view_id,
        layout=layout_override if layout_override is not None else getattr(item, "layout", None),
        width=getattr(item, "width", None),
        height=getattr(item, "height", None),
        padding=getattr(item, "padding", None),
        margin=getattr(item, "margin", None),
        gravity=getattr(item, "gravity", None),
        weight=getattr(item, "weight", None),
        relative=getattr(item, "relative", None),
        constraints=getattr(item, "constraints", None),
        background=getattr(item, "background", None),
        radius=getattr(item, "radius", None),
        tint=getattr(item, "tint", None),
        thumb_tint=getattr(item, "thumb_tint", None),
        track_tint=getattr(item, "track_tint", None),
        progress_tint=getattr(item, "progress_tint", None),
        button_tint=getattr(item, "button_tint", None),
        style=getattr(item, "style", None),
    )


def _build_text_input_shell(ctx, item, parent_id, *, end_icon_mode=None):
    shell_id = ctx._register_view(f"{item.id}_layout", "view")
    shell_item = _layout_proxy(item, shell_id)
    body = [
        assign(
            shell_id,
            new(
                _MATERIAL_TEXT_INPUT_LAYOUT,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        ),
        call_stmt(
            "setBoxBackgroundMode",
            args=[var(shell_id), const(2)],
            return_type=None,
            arg_types=["I"],
            invoke_kind="virtual",
            owner=_MATERIAL_TEXT_INPUT_LAYOUT,
        ),
    ]
    if end_icon_mode is not None:
        body.append(
            call_stmt(
                "setEndIconMode",
                args=[var(shell_id), const(int(end_icon_mode))],
                return_type=None,
                arg_types=["I"],
                invoke_kind="virtual",
                owner=_MATERIAL_TEXT_INPUT_LAYOUT,
            )
        )
    body.extend(ctx._apply_view_layout(shell_item, parent_id))
    body.append(add_view(var(parent_id), var(shell_id)))
    return body, shell_id


def _render_material_app_bar(ctx, item, parent_id):
    body = []
    title_key = ctx._add_string_resource("app_name", item.text)
    title_load, title_expr = ctx._load_string_expr(title_key, ctx_expr=var("ctx"), prefix="app_name")
    body.extend(title_load)
    body.append(
        call_stmt(
            "setTitle",
            args=[var("ctx"), title_expr],
            return_type=None,
            invoke_kind="virtual",
            owner="Landroid/app/Activity;",
        )
    )

    if not item.inline:
        return body

    item.id = ctx._register_view(item.id, "view")
    body.append(
        assign(
            item.id,
            new(
                _MATERIAL_TOOLBAR,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    )
    tb_key = ctx._add_string_resource(f"{item.id}_title", item.text)
    tb_load, tb_expr = ctx._load_string_expr(tb_key, ctx_expr=var("ctx"), prefix=f"{item.id}_title")
    body.extend(tb_load)
    body.append(
        call_stmt(
            "setTitle",
            args=[var(item.id), tb_expr],
            return_type=None,
            arg_types=["Ljava/lang/CharSequence;"],
            invoke_kind="virtual",
            owner="Landroidx/appcompat/widget/Toolbar;",
        )
    )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_button(ctx, item, parent_id, kind):
    item.id = ctx._register_view(item.id, kind)
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_BUTTON,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    ]
    body.extend(
        ctx._set_text_from_resource(
            item.id,
            ctx._button_label(item),
            "Landroid/widget/Button;",
            f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    if kind == "raised_button":
        body.append(
            call_stmt(
                "setElevation",
                args=[var(item.id), const(8.0)],
                return_type=None,
                arg_types=["F"],
                invoke_kind="virtual",
                owner="Landroid/view/View;",
            )
        )
    elif kind == "flat_button":
        body.append(
            call_stmt(
                "setElevation",
                args=[var(item.id), const(0.0)],
                return_type=None,
                arg_types=["F"],
                invoke_kind="virtual",
                owner="Landroid/view/View;",
            )
        )
        tint_setup, tint_expr = ctx._build_color_state_list_expr(
            item.id,
            "flat_bg_tint",
            "#00000000",
            ctx.theme_spec.palette,
        )
        body.extend(tint_setup)
        if tint_expr is not None:
            body.append(
                call_stmt(
                    "setBackgroundTintList",
                    args=[var(item.id), tint_expr],
                    return_type=None,
                    arg_types=["Landroid/content/res/ColorStateList;"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
    elif kind == "icon_button":
        if item.layout is None:
            item.layout = (Dp(48), Dp(48))
        radius_key = ctx._add_dimen_resource(f"{item.id}_icon_radius", Dp(24))
        radius_setup, radius_expr = ctx._load_dimen_px_expr(
            radius_key,
            ctx_expr=var("ctx"),
            prefix=f"{item.id}_icon_radius",
        )
        body.extend(radius_setup)
        body.append(
            call_stmt(
                "setCornerRadius",
                args=[var(item.id), radius_expr],
                return_type=None,
                arg_types=["I"],
                invoke_kind="virtual",
                owner=_MATERIAL_BUTTON,
            )
        )
        body.append(
            call_stmt(
                "setElevation",
                args=[var(item.id), const(0.0)],
                return_type=None,
                arg_types=["F"],
                invoke_kind="virtual",
                owner="Landroid/view/View;",
            )
        )
        icon_res = int(item.icon) if isinstance(item.icon, int) else 17301651
        body.append(
            call_stmt(
                "setIconResource",
                args=[var(item.id), const(icon_res)],
                return_type=None,
                arg_types=["I"],
                invoke_kind="virtual",
                owner=_MATERIAL_BUTTON,
            )
        )
        body.extend(
            ctx._set_text_from_resource(
                item.id,
                "",
                "Landroid/widget/Button;",
                f"{item.id}_icon_text",
                ctx_expr=var("ctx"),
            )
        )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_popup_button(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "popup_button")
    ctx._popup_button_items[item.id] = [str(v) for v in (item.items or [])]
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_BUTTON,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    ]
    body.extend(
        ctx._set_text_from_resource(
            item.id,
            ctx._button_label(item),
            "Landroid/widget/Button;",
            f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_fab(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "fab")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_FAB,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    ]
    if item.text:
        body.extend(
            ctx._set_text_from_resource(
                item.id,
                str(item.text),
                "Landroid/view/View;",
                f"{item.id}_content_desc",
                ctx_expr=var("ctx"),
                method_name="setContentDescription",
            )
        )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_text_field(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "text_field")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    body, shell_id = _build_text_input_shell(ctx, item, parent_id)
    body.extend(
        [
        assign(
            item.id,
            new(
                _MATERIAL_TEXT_FIELD,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
        ]
    )
    body.extend(
        ctx._set_text_from_resource(
            item.id,
            item.text or "",
            "Landroid/widget/EditText;",
            f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    if item.hint:
        hint_key = ctx._add_string_resource(f"{item.id}_hint", item.hint)
        hint_load, hint_expr = ctx._load_string_expr(hint_key, ctx_expr=var("ctx"), prefix=f"{item.id}_hint")
        body.extend(hint_load)
        body.append(
            call_stmt(
                "setHint",
                args=[var(shell_id), hint_expr],
                return_type=None,
                arg_types=["Ljava/lang/CharSequence;"],
                invoke_kind="virtual",
                owner=_MATERIAL_TEXT_INPUT_LAYOUT,
            )
        )
    input_item = _layout_proxy(item, item.id, layout_override=("match_parent", "wrap"))
    body.extend(ctx._apply_view_layout(input_item, shell_id))
    body.append(add_view(var(shell_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def _render_material_dropdown(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "view")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    body, shell_id = _build_text_input_shell(ctx, item, parent_id, end_icon_mode=3)
    adapter_name = f"adapter_{item.id}"
    body.extend(
        [
        assign(
            item.id,
            new(
                _MATERIAL_DROPDOWN,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        ),
        ]
    )
    input_item = _layout_proxy(item, item.id, layout_override=("match_parent", "wrap"))
    body.extend(ctx._apply_view_layout(input_item, shell_id))
    body.append(add_view(var(shell_id), var(item.id)))
    body.extend(
        [
        assign(
            adapter_name,
            new(
                "Landroid/widget/ArrayAdapter;",
                args=[var("ctx"), const(17367048)],
            ),
        ),
        ]
    )
    for val in item.items:
        item_key = ctx._add_string_resource(f"{item.id}_item", str(val))
        item_load, item_expr = ctx._load_string_expr(item_key, ctx_expr=var("ctx"), prefix=f"{item.id}_item")
        body.extend(item_load)
        body.append(
            call_stmt(
                "add",
                args=[var(adapter_name), item_expr],
                return_type=None,
                invoke_kind="virtual",
                owner="Landroid/widget/ArrayAdapter;",
            )
        )
    body.append(
        call_stmt(
            "setAdapter",
            args=[var(item.id), var(adapter_name)],
            return_type=None,
            arg_types=["Landroid/widget/ListAdapter;"],
            invoke_kind="virtual",
            owner="Landroid/widget/AutoCompleteTextView;",
        )
    )
    if item.items:
        first_key = ctx._add_string_resource(f"{item.id}_selected", str(item.items[0]))
        first_load, first_expr = ctx._load_string_expr(first_key, ctx_expr=var("ctx"), prefix=f"{item.id}_selected")
        body.extend(first_load)
        body.append(
            call_stmt(
                "setText",
                args=[var(item.id), first_expr, const(0)],
                return_type=None,
                arg_types=["Ljava/lang/CharSequence;", "Z"],
                invoke_kind="virtual",
                owner="Landroid/widget/AutoCompleteTextView;",
            )
        )
    body.extend(ctx._capture_view_static(item.id))
    return body


def _render_material_checkbox(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "checkbox")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_CHECKBOX,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        ),
        call_stmt(
            "setChecked",
            args=[var(item.id), const(1 if item.checked else 0)],
            return_type=None,
            arg_types=["Z"],
            invoke_kind="virtual",
            owner="Landroid/widget/CompoundButton;",
        ),
    ]
    body.extend(
        ctx._set_text_from_resource(
            item.id,
            item.text or "",
            "Landroid/widget/TextView;",
            f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_radio(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "radio")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_RADIO,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        ),
    ]
    body.extend(ctx._capture_view_static(item.id))
    body.append(
        call_stmt(
            "setChecked",
            args=[var(item.id), const(1 if item.checked else 0)],
            return_type=None,
            arg_types=["Z"],
            invoke_kind="virtual",
            owner="Landroid/widget/CompoundButton;",
        )
    )
    body.extend(
        ctx._set_text_from_resource(
            item.id,
            item.text or "",
            "Landroid/widget/TextView;",
            f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    return body


def _render_material_switch(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "view")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_SWITCH,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        ),
        call_stmt(
            "setChecked",
            args=[var(item.id), const(1 if item.checked else 0)],
            return_type=None,
            arg_types=["Z"],
            invoke_kind="virtual",
            owner="Landroid/widget/CompoundButton;",
        ),
    ]
    body.extend(
        ctx._set_text_from_resource(
            item.id,
            item.text or "",
            "Landroid/widget/TextView;",
            f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_slider(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "view")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    vmin = float(item.min)
    vmax = float(item.max)
    if vmax < vmin:
        vmax = vmin
    value = float(item.value)
    if value < vmin:
        value = vmin
    if value > vmax:
        value = vmax
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_SLIDER,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        ),
        call_stmt(
            "setValueFrom",
            args=[var(item.id), const(vmin)],
            return_type=None,
            arg_types=["F"],
            invoke_kind="virtual",
            owner=_MATERIAL_SLIDER,
        ),
        call_stmt(
            "setValueTo",
            args=[var(item.id), const(vmax)],
            return_type=None,
            arg_types=["F"],
            invoke_kind="virtual",
            owner=_MATERIAL_SLIDER,
        ),
        call_stmt(
            "setValue",
            args=[var(item.id), const(value)],
            return_type=None,
            arg_types=["F"],
            invoke_kind="virtual",
            owner=_MATERIAL_SLIDER,
        ),
    ]
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_progress(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "progress_bar")
    vmin = int(item.min)
    vmax = int(item.max)
    span = max(vmax - vmin, 0)
    progress = int(item.value) - vmin
    if progress < 0:
        progress = 0
    if progress > span:
        progress = span
    class_desc = _MATERIAL_PROGRESS_CIRCULAR if item.indeterminate else _MATERIAL_PROGRESS_LINEAR
    body = [
        assign(
            item.id,
            new(
                class_desc,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        ),
        call_stmt(
            "setIndeterminate",
            args=[var(item.id), const(1 if item.indeterminate else 0)],
            return_type=None,
            arg_types=["Z"],
            invoke_kind="virtual",
            owner="Landroid/widget/ProgressBar;",
        ),
    ]
    if not item.indeterminate:
        body.extend(
            [
                call_stmt(
                    "setMax",
                    args=[var(item.id), const(span)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/ProgressBar;",
                ),
                call_stmt(
                    "setProgress",
                    args=[var(item.id), const(progress)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/ProgressBar;",
                ),
            ]
        )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_divider(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "divider")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_DIVIDER,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    ]
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_card(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "view")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_CARD,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    ]
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))

    content_id = ctx._register_view(f"{item.id}_content", "column")
    ctx._container_orientation[content_id] = "vertical"
    content = _UIColumn(
        id=content_id,
        layout=("match_parent", "wrap"),
    )
    content.id = content_id

    body.extend(linear_layout(content_id, var("ctx"), "vertical"))
    body.extend(ctx._apply_view_layout(content, item.id))
    body.append(add_view(var(item.id), var(content_id)))
    body.extend(ctx._capture_view_static(content_id))
    body.extend(ctx._build_ui_items(content_id, item.items))
    return body


def _render_material_image(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "image")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_IMAGE,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    ]
    body.extend(ctx._set_image_source(item.id, item.src))
    if item.content_description:
        body.extend(
            ctx._set_text_from_resource(
                item.id,
                item.content_description,
                "Landroid/view/View;",
                f"{item.id}_content_desc",
                ctx_expr=var("ctx"),
                method_name="setContentDescription",
            )
        )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_icon(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "icon")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_TEXT,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    ]
    body.extend(
        ctx._set_text_from_resource(
            item.id,
            item.text,
            "Landroid/widget/TextView;",
            f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    return _finalize_view(ctx, item, parent_id, body)


def _render_material_text(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "text")
    body = [
        assign(
            item.id,
            new(
                _MATERIAL_TEXT,
                args=[var("ctx")],
                arg_types=["Landroid/content/Context;"],
            ),
        )
    ]
    body.extend(
        ctx._set_text_from_resource(
            item.id,
            item.text,
            "Landroid/widget/TextView;",
            f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    return _finalize_view(ctx, item, parent_id, body)


def register(registry):
    # UI renderers
    registry.register_ui(_UISlider, _render_material_slider, priority=340)
    registry.register_ui(_UIAppBar, _render_material_app_bar, priority=339)
    registry.register_ui(_UIFloatingActionButton, _render_material_fab, priority=338)
    registry.register_ui(_UIRaisedButton, lambda c, i, p: _render_material_button(c, i, p, "raised_button"), priority=337)
    registry.register_ui(_UIFlatButton, lambda c, i, p: _render_material_button(c, i, p, "flat_button"), priority=336)
    registry.register_ui(_UIIconButton, lambda c, i, p: _render_material_button(c, i, p, "icon_button"), priority=335)
    registry.register_ui(_UIDropdownButton, _render_material_dropdown, priority=334)
    registry.register_ui(_UIPopupMenuButton, _render_material_popup_button, priority=333)
    registry.register_ui(_UIButton, lambda c, i, p: _render_material_button(c, i, p, "button"), priority=332)
    registry.register_ui(_UITextField, _render_material_text_field, priority=331)
    registry.register_ui(_UICheckbox, _render_material_checkbox, priority=330)
    registry.register_ui(_UIRadio, _render_material_radio, priority=329)
    registry.register_ui(_UISwitch, _render_material_switch, priority=328)
    registry.register_ui(_UIProgressBar, _render_material_progress, priority=327)
    registry.register_ui(_UICard, _render_material_card, priority=326)
    registry.register_ui(_UIDivider, _render_material_divider, priority=325)
    registry.register_ui(_UIImage, _render_material_image, priority=324)
    registry.register_ui(_UIIcon, _render_material_icon, priority=323)
    registry.register_ui(_UIText, _render_material_text, priority=322)

    # Dependencies
    registry.register_deps("material", _collect_material_deps, priority=50)
