"""Selection widget renderers (Dropdown, PopupMenu)."""

from dsl.ir_helpers import (
    add_view, assign, array_set, call, call_stmt, const, new, var,
)


def render_dropdown(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "dropdown")
    if item.layout is None:
        item.layout = ("wrap", "wrap")
    body = [
        assign(item.id, new("Landroid/widget/Spinner;", args=[var("ctx")])),
        assign(
            f"adapter_{item.id}",
            new("Landroid/widget/ArrayAdapter;", args=[var("ctx"), const(17367048)]),
        ),
    ]
    for val in item.items:
        item_key = ctx._add_string_resource(f"{item.id}_item", str(val))
        item_load, item_expr = ctx._load_string_expr(item_key, ctx_expr=var("ctx"), prefix=f"{item.id}_item")
        body.extend(item_load)
        body.append(
            call_stmt("add", args=[var(f"adapter_{item.id}"), item_expr],
                      return_type=None, invoke_kind="virtual",
                      owner="Landroid/widget/ArrayAdapter;")
        )
    body.extend([
        call_stmt("setDropDownViewResource",
                  args=[var(f"adapter_{item.id}"), const(17367049)],
                  return_type=None, invoke_kind="virtual",
                  owner="Landroid/widget/ArrayAdapter;"),
        call_stmt("setAdapter",
                  args=[var(item.id), var(f"adapter_{item.id}")],
                  return_type=None, invoke_kind="virtual",
                  owner="Landroid/widget/Spinner;"),
    ])
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_popup_menu(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "popup_button")
    ctx._popup_button_items[item.id] = [str(v) for v in (item.items or [])]
    body = [assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))]
    body.extend(
        ctx._set_text_from_resource(
            item.id, ctx._button_label(item),
            "Landroid/widget/Button;", f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body
