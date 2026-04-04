"""List widget renderers (ListView, GridView, RecyclerView)."""

from dsl.ir_helpers import (
    add_view, assign, array_set, call_stmt, const, new, new_array, var,
)


def render_list_view(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "list_view")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    item_layout_res = int(item.item_layout_res)
    if item_layout_res != 0x1090003:
        raise RuntimeError(
            f"ListView '{item.id}' item_layout={item_layout_res} is not yet supported by "
            "the deterministic adapter path; use simple_list_item_1."
        )
    adapter_name = f"adapter_{item.id}"
    items_array_name = f"items_{item.id}"
    adapter_class_desc = f"Lcom/ahnali/preview/AhnaliListAdapter_{item.id};"
    body = [
        assign(item.id, new("Landroid/widget/ListView;", args=[var("ctx")])),
        assign(items_array_name, new_array(const(len(item.items)), "Ljava/lang/String;")),
    ]
    for idx, val in enumerate(item.items):
        item_key = ctx._add_string_resource(f"{item.id}_item", str(val))
        item_load, item_expr = ctx._load_string_expr(item_key, ctx_expr=var("ctx"), prefix=f"{item.id}_item")
        body.extend(item_load)
        body.append(array_set(var(items_array_name), const(idx), "Ljava/lang/String;", item_expr))
    body.extend([
        assign(adapter_name, new(adapter_class_desc, args=[var("ctx"), var(items_array_name)],
                                arg_types=["Landroid/content/Context;", "[Ljava/lang/String;"])),
        call_stmt("setAdapter", args=[var(item.id), var(adapter_name)],
                  return_type=None, invoke_kind="virtual", owner="Landroid/widget/ListView;"),
    ])
    ctx._queue_support_class(adapter_class_desc, str(item_layout_res), "LTest;", "list_adapter")
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_grid_view(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "grid_view")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    item_layout_res = int(item.item_layout_res)
    if item_layout_res != 0x1090003:
        raise RuntimeError(
            f"GridView '{item.id}' item_layout={item_layout_res} is not yet supported by "
            "the deterministic adapter path; use simple_list_item_1."
        )
    adapter_name = f"adapter_{item.id}"
    items_array_name = f"items_{item.id}"
    adapter_class_desc = f"Lcom/ahnali/preview/AhnaliListAdapter_{item.id};"
    body = [
        assign(item.id, new("Landroid/widget/GridView;", args=[var("ctx")])),
        call_stmt("setNumColumns", args=[var(item.id), const(int(item.num_columns))],
                  return_type=None, invoke_kind="virtual", owner="Landroid/widget/GridView;"),
        assign(items_array_name, new_array(const(len(item.items)), "Ljava/lang/String;")),
    ]
    for idx, val in enumerate(item.items):
        item_key = ctx._add_string_resource(f"{item.id}_item", str(val))
        item_load, item_expr = ctx._load_string_expr(item_key, ctx_expr=var("ctx"), prefix=f"{item.id}_item")
        body.extend(item_load)
        body.append(array_set(var(items_array_name), const(idx), "Ljava/lang/String;", item_expr))
    body.extend([
        assign(adapter_name, new(adapter_class_desc, args=[var("ctx"), var(items_array_name)],
                                arg_types=["Landroid/content/Context;", "[Ljava/lang/String;"])),
        call_stmt("setAdapter", args=[var(item.id), var(adapter_name)],
                  return_type=None, invoke_kind="virtual", owner="Landroid/widget/GridView;"),
    ])
    ctx._queue_support_class(adapter_class_desc, str(item_layout_res), "LTest;", "list_adapter")
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_recycler_view(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "recycler_view")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    lm_name = f"lm_{item.id}"
    body = [
        assign(item.id, new("Landroidx/recyclerview/widget/RecyclerView;", args=[var("ctx")])),
        assign(lm_name, new("Landroidx/recyclerview/widget/LinearLayoutManager;", args=[var("ctx")])),
        call_stmt("setLayoutManager", args=[var(item.id), var(lm_name)],
                  return_type=None,
                  arg_types=["Landroidx/recyclerview/widget/RecyclerView$LayoutManager;"],
                  invoke_kind="virtual", owner="Landroidx/recyclerview/widget/RecyclerView;"),
    ]
    for idx, val in enumerate(item.items):
        row_id = ctx._register_view(f"__{item.id}_row_{idx + 1}", "text")
        body.append(assign(row_id, new("Landroid/widget/TextView;", args=[var("ctx")])))
        body.extend(
            ctx._set_text_from_resource(
                row_id, str(val), "Landroid/widget/TextView;",
                f"{row_id}_text", ctx_expr=var("ctx"),
            )
        )
        body.append(add_view(var(item.id), var(row_id)))
        body.extend(ctx._capture_view_static(row_id))
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body
