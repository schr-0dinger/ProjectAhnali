from __future__ import annotations

def _collect_material_deps(ui_items, click_specs):
    # Minimal dependency set to compile Material widgets/resources when enabled.
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
    return required_aars, set()


def register(registry):
    # Route all widgets through this plugin when enabled. For now, we defer to
    # core rendering; this keeps behavior unchanged while making the boundary
    # explicit for future Material renderers.
    registry.register_ui(object, lambda ctx, item, parent_id: ctx._render_ui_core(item, parent_id), priority=100)
    registry.register_deps("material", _collect_material_deps, priority=50)
