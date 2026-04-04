"""Button widget renderers."""

from dsl.ir_helpers import (
    add_view, assign, call_stmt, const, new, var,
)


def _render_button_like(ctx, item, parent_id, kind="button"):
    """Shared path for all button variants."""
    item.id = ctx._register_view(item.id, kind)
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


def render_button(ctx, item, parent_id):
    return _render_button_like(ctx, item, parent_id, "button")


def render_raised_button(ctx, item, parent_id):
    return _render_button_like(ctx, item, parent_id, "raised_button")


def render_flat_button(ctx, item, parent_id):
    return _render_button_like(ctx, item, parent_id, "flat_button")


def render_icon_button(ctx, item, parent_id):
    return _render_button_like(ctx, item, parent_id, "icon_button")


def render_fab(ctx, item, parent_id):
    return _render_button_like(ctx, item, parent_id, "fab")
