"""Scroll container renderers."""

from dsl.ir_helpers import (
    add_view, assign, new, var,
)


def _render_scroll_view(ctx, item, parent_id, widget_class, kind):
    if len(item.items) != 1:
        raise RuntimeError(
            f"{kind} requires exactly one direct child; got {len(item.items)}."
        )
    item.id = ctx._register_view(item.id, kind)
    body = [assign(item.id, new(widget_class, args=[var("ctx")]))]
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    body.extend(ctx._build_ui_items(item.id, item.items))
    return body


def render_scroll_view(ctx, item, parent_id):
    return _render_scroll_view(ctx, item, parent_id,
                               "Landroid/widget/ScrollView;", "scroll_view")


def render_horizontal_scroll_view(ctx, item, parent_id):
    return _render_scroll_view(ctx, item, parent_id,
                               "Landroid/widget/HorizontalScrollView;", "horizontal_scroll_view")


def render_nested_scroll_view(ctx, item, parent_id):
    return _render_scroll_view(ctx, item, parent_id,
                               "Landroidx/core/widget/NestedScrollView;", "nested_scroll_view")
