"""Text and display widget renderers."""

from dsl.ir_helpers import (
    add_view, assign, call_stmt, const, new, var,
)
from dsl.widgets import ColorState
from dsl.android.resources import _parse_color


def render_text(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "text")
    body = [assign(item.id, new("Landroid/widget/TextView;", args=[var("ctx")]))]
    body.extend(
        ctx._set_text_from_resource(
            item.id, item.text,
            "Landroid/widget/TextView;", f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_icon(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "icon")
    body = [assign(item.id, new("Landroid/widget/TextView;", args=[var("ctx")]))]
    body.extend(
        ctx._set_text_from_resource(
            item.id, item.text,
            "Landroid/widget/TextView;", f"{item.id}_text",
            ctx_expr=var("ctx"),
        )
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_image(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "image")
    body = [assign(item.id, new("Landroid/widget/ImageView;", args=[var("ctx")]))]
    body.extend(ctx._set_image_source(item.id, item.src))
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_divider(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "divider")
    body = [assign(item.id, new("Landroid/view/View;", args=[var("ctx")]))]
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_progress_bar(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "progress_bar")
    min_value = int(item.min)
    max_value = int(item.max)
    span = max(max_value - min_value, 0)
    progress = int(item.value) - min_value
    if progress < 0:
        progress = 0
    if progress > span:
        progress = span

    if item.indeterminate:
        progress_ctor = new("Landroid/widget/ProgressBar;", args=[var("ctx")])
    else:
        progress_ctor = new(
            "Landroid/widget/ProgressBar;",
            args=[var("ctx"), const(0), const(0x1010078)],
            arg_types=["Landroid/content/Context;", "Landroid/util/AttributeSet;", "I"],
        )

    body = [assign(item.id, progress_ctor)]
    body.append(
        call_stmt("setIndeterminate", args=[var(item.id), const(1 if item.indeterminate else 0)],
                  return_type=None, arg_types=["Z"], invoke_kind="virtual",
                  owner="Landroid/widget/ProgressBar;")
    )
    if not item.indeterminate:
        body.append(call_stmt("setMax", args=[var(item.id), const(span)],
                              return_type=None, invoke_kind="virtual",
                              owner="Landroid/widget/ProgressBar;"))
        body.append(call_stmt("setProgress", args=[var(item.id), const(progress)],
                              return_type=None, invoke_kind="virtual",
                              owner="Landroid/widget/ProgressBar;"))
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_app_bar(ctx, item, parent_id):
    body = []
    if item.inline:
        item.id = ctx._register_view(item.id, "app_bar")
    title_key = ctx._add_string_resource("app_name", item.text)
    title_load, title_expr = ctx._load_string_expr(title_key, ctx_expr=var("ctx"), prefix="app_name")
    body.extend(title_load)
    body.append(
        call_stmt("setTitle", args=[var("ctx"), title_expr], return_type=None,
                  invoke_kind="virtual", owner="Landroid/app/Activity;")
    )
    if item.inline:
        palette = ctx.theme_spec.palette
        body.append(assign(item.id, new("Landroid/widget/Toolbar;", args=[var("ctx")])))
        body.extend(
            ctx._set_text_from_resource(
                item.id, item.text, "Landroid/widget/Toolbar;",
                f"{item.id}_title", ctx_expr=var("ctx"), method_name="setTitle",
            )
        )
        text_color_value = item.text_color
        if text_color_value is None and getattr(item, "style", None):
            text_color_value = item.style.text_color
        if isinstance(text_color_value, ColorState):
            text_color_value = _parse_color(text_color_value.default, palette)
        else:
            text_color_value = _parse_color(text_color_value, palette)
        if text_color_value is not None:
            color_key = ctx._add_color_resource(f"{item.id}_title", text_color_value)
            color_load, color_expr = ctx._load_color_expr(color_key, ctx_expr=var("ctx"), prefix=f"{item.id}_title")
            body.extend(color_load)
            body.append(
                call_stmt("setTitleTextColor", args=[var(item.id), color_expr],
                          return_type=None, arg_types=["I"], invoke_kind="virtual",
                          owner="Landroid/widget/Toolbar;")
            )
        body.extend(ctx._apply_view_layout(item, parent_id))
        body.append(add_view(var(parent_id), var(item.id)))
        body.extend(ctx._capture_view_static(item.id))
    return body


def render_view(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "view")
    body = [assign(item.id, new("Landroid/view/View;", args=[var("ctx")]))]
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body
