"""Container widget renderers."""

from dsl.ir_helpers import (
    add_view, assign, call_stmt, constraint_layout,
    frame_layout, linear_layout, new, relative_layout, var,
)


def _render_linear_container(ctx, item, parent_id, orientation, kind):
    item.id = ctx._register_view(item.id, kind)
    ctx._container_orientation[item.id] = orientation
    body = list(linear_layout(item.id, var("ctx"), orientation))
    if item.weight_sum is not None:
        body.extend(
            ctx._emit_attr_call(view_id=item.id, attr_name="weight_sum", raw_value=item.weight_sum)
        )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    body.extend(ctx._build_ui_items(item.id, item.items))
    return body


def render_row(ctx, item, parent_id):
    return _render_linear_container(ctx, item, parent_id, "horizontal", "row")


def render_column(ctx, item, parent_id):
    return _render_linear_container(ctx, item, parent_id, "vertical", "column")


def render_container(ctx, item, parent_id):
    return _render_linear_container(ctx, item, parent_id, "vertical", "container")


def render_card(ctx, item, parent_id):
    return _render_linear_container(ctx, item, parent_id, "vertical", "card")


def render_button_bar(ctx, item, parent_id):
    return _render_linear_container(ctx, item, parent_id, "horizontal", "row")


def render_relative(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "relative")
    body = list(relative_layout(item.id, var("ctx")))
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    body.extend(ctx._build_ui_items(item.id, item.items))
    return body


def render_constraint(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "constraint")
    body = list(constraint_layout(item.id, var("ctx")))
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    body.extend(ctx._build_ui_items(item.id, item.items))
    return body


def render_frame(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "frame")
    body = list(frame_layout(item.id, var("ctx")))
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    body.extend(ctx._build_ui_items(item.id, item.items))
    return body


def render_coordinator_layout(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "coordinator_layout")
    body = [
        assign(item.id, new("Landroidx/coordinatorlayout/widget/CoordinatorLayout;", args=[var("ctx")])),
    ]
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    body.extend(ctx._build_ui_items(item.id, item.items))
    return body
