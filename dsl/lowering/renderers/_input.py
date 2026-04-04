"""Input widget renderers."""

from dsl.ir_helpers import (
    add_view, assign, call_stmt, const, new, var,
)


def render_text_field(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "text_field")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    body = [assign(item.id, new("Landroid/widget/EditText;", args=[var("ctx")]))]
    body.extend(
        ctx._set_text_from_resource(
            item.id, item.text or "",
            "Landroid/widget/EditText;", f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    if item.hint:
        hint_key = ctx._add_string_resource(f"{item.id}_hint", item.hint)
        hint_load, hint_expr = ctx._load_string_expr(hint_key, ctx_expr=var("ctx"), prefix=f"{item.id}_hint")
        body.extend(hint_load)
        body.append(
            call_stmt("setHint", args=[var(item.id), hint_expr], return_type=None,
                      invoke_kind="virtual", owner="Landroid/widget/EditText;")
        )
    body.extend(ctx._build_text_field_input_config_stmts(item))
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_checkbox(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "checkbox")
    body = [
        assign(item.id, new("Landroid/widget/CheckBox;", args=[var("ctx")])),
        call_stmt("setChecked", args=[var(item.id), const(1 if item.checked else 0)],
                  return_type=None, arg_types=["Z"], invoke_kind="virtual",
                  owner="Landroid/widget/CheckBox;"),
    ]
    body.extend(
        ctx._set_text_from_resource(
            item.id, item.text or "",
            "Landroid/widget/CheckBox;", f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_radio(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "radio")
    body = [assign(item.id, new("Landroid/widget/RadioButton;", args=[var("ctx")]))]
    # RadioGroup tracks checked ids; register before setting checked state.
    body.extend(ctx._capture_view_static(item.id))
    body.append(
        call_stmt("setChecked", args=[var(item.id), const(1 if item.checked else 0)],
                  return_type=None, arg_types=["Z"], invoke_kind="virtual",
                  owner="Landroid/widget/RadioButton;")
    )
    body.extend(
        ctx._set_text_from_resource(
            item.id, item.text or "",
            "Landroid/widget/RadioButton;", f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    return body


def render_switch(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "switch")
    body = [
        assign(item.id, new("Landroid/widget/Switch;", args=[var("ctx")])),
        call_stmt("setChecked", args=[var(item.id), const(1 if item.checked else 0)],
                  return_type=None, arg_types=["Z"], invoke_kind="virtual",
                  owner="Landroid/widget/Switch;"),
    ]
    body.extend(
        ctx._set_text_from_resource(
            item.id, item.text or "",
            "Landroid/widget/Switch;", f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_slider(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "slider")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    body = [
        assign(item.id, new("Landroid/widget/SeekBar;", args=[var("ctx")])),
        call_stmt("setMax", args=[var(item.id), const(int(item.max) - int(item.min))],
                  return_type=None, invoke_kind="virtual",
                  owner="Landroid/widget/SeekBar;"),
        call_stmt("setProgress", args=[var(item.id), const(int(item.value) - int(item.min))],
                  return_type=None, invoke_kind="virtual",
                  owner="Landroid/widget/SeekBar;"),
    ]
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_radio_group(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "radio_group")
    orientation = "horizontal" if item.orientation == "horizontal" else "vertical"
    ctx._container_orientation[item.id] = orientation
    body = [assign(item.id, new("Landroid/widget/RadioGroup;", args=[var("ctx")]))]
    body.append(
        call_stmt("setOrientation",
                  args=[var(item.id), const(0 if orientation == "horizontal" else 1)],
                  return_type=None, invoke_kind="virtual",
                  owner="Landroid/widget/LinearLayout;")
    )
    if item.weight_sum is not None:
        body.extend(
            ctx._emit_attr_call(view_id=item.id, attr_name="weight_sum", raw_value=item.weight_sum)
        )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    body.extend(ctx._build_ui_items(item.id, item.items))
    return body
