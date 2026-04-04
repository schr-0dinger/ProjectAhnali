"""Navigation surface renderers (ViewPager, TabLayout, BottomNav, NavBar, NavRail, DrawerLayout, FragmentContainer, Screen)."""

from dsl.ir_helpers import (
    add_view, assign, call, call_stmt, const, linear_layout, new, relative_layout, var,
)


def render_view_pager(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "view_pager")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    body = [
        assign(item.id, new("Landroidx/viewpager/widget/ViewPager;", args=[var("ctx")])),
    ]
    for idx, page_item in enumerate(item.items):
        page_root_id = ctx._register_view(f"__{item.id}_page_{idx + 1}", "column")
        body.extend(linear_layout(page_root_id, var("ctx"), "vertical"))
        ctx._container_orientation[page_root_id] = "vertical"
        page_lp = f"lp_{page_root_id}"
        body.append(
            assign(page_lp, new("Landroidx/viewpager/widget/ViewPager$LayoutParams;",
                                args=[const(-1), const(-1)], arg_types=["I", "I"]))
        )
        body.extend(
            ctx._emit_attr_call(view_id=page_root_id, attr_name="layout_params", raw_value=var(page_lp))
        )
        body.append(add_view(var(item.id), var(page_root_id)))
        body.extend(ctx._capture_view_static(page_root_id))
        body.extend(ctx._build_ui_items(page_root_id, (page_item,)))
    body.append(
        call_stmt("setCurrentItem", args=[var(item.id), const(int(item.initial_page))],
                  return_type=None, arg_types=["I"], invoke_kind="virtual",
                  owner="Landroidx/viewpager/widget/ViewPager;")
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def _render_menu_nav(ctx, item, parent_id, kind, menu_id_base):
    """Shared path for BottomNavigationView, NavigationBar, NavigationRail."""
    if kind == "bottom_navigation_view":
        widget_class = "Lcom/google/android/material/bottomnavigation/BottomNavigationView;"
    elif kind == "navigation_bar":
        widget_class = "Lcom/google/android/material/bottomnavigation/BottomNavigationView;"
    elif kind == "navigation_rail":
        widget_class = "Lcom/google/android/material/navigationrail/NavigationRailView;"
    else:
        raise RuntimeError(f"Unknown nav kind: {kind}")

    item.id = ctx._register_view(item.id, kind)
    if item.layout is None:
        if kind == "navigation_rail":
            item.layout = ("wrap", "match_parent")
        else:
            item.layout = ("match_parent", "wrap")

    body = [assign(item.id, new(widget_class, args=[var("ctx")]))]
    menu_name = f"menu_{item.id}"
    body.append(
        assign(menu_name, call("getMenu", args=[var(item.id)],
                               return_type="Landroid/view/Menu;", arg_types=[],
                               invoke_kind="virtual", owner=widget_class))
    )
    for idx, label in enumerate(item.items):
        item_key = ctx._add_string_resource(f"{item.id}_item_{idx}", label)
        item_load, item_expr = ctx._load_string_expr(item_key, ctx_expr=var("ctx"), prefix=f"{item.id}_item_{idx}")
        menu_item_name = f"{item.id}_menu_item_{idx}"
        menu_item_id = menu_id_base + idx
        body.extend(item_load)
        body.append(
            assign(menu_item_name, call("add", args=[var(menu_name), const(0), const(menu_item_id), const(idx), item_expr],
                                        return_type="Landroid/view/MenuItem;",
                                        arg_types=["I", "I", "I", "Ljava/lang/CharSequence;"],
                                        invoke_kind="interface", owner="Landroid/view/Menu;"))
        )
        if idx == item.selected_index:
            body.append(
                assign(menu_item_name, call("setChecked", args=[var(menu_item_name), const(1)],
                                            return_type="Landroid/view/MenuItem;", arg_types=["Z"],
                                            invoke_kind="interface", owner="Landroid/view/MenuItem;"))
            )
    body.append(
        call_stmt("setSelectedItemId", args=[var(item.id), const(menu_id_base + item.selected_index)],
                  return_type=None, arg_types=["I"], invoke_kind="virtual", owner=widget_class)
    )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_bottom_nav(ctx, item, parent_id):
    return _render_menu_nav(ctx, item, parent_id, "bottom_navigation_view", 1000)


def render_nav_bar(ctx, item, parent_id):
    return _render_menu_nav(ctx, item, parent_id, "navigation_bar", 2000)


def render_nav_rail(ctx, item, parent_id):
    return _render_menu_nav(ctx, item, parent_id, "navigation_rail", 3000)


def render_tab_layout(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "tab_layout")
    if item.layout is None:
        item.layout = ("match_parent", "wrap")
    body = [
        assign(item.id, new("Lcom/google/android/material/tabs/TabLayout;", args=[var("ctx")])),
    ]
    for idx, label in enumerate(item.tabs):
        tab_key = ctx._add_string_resource(f"{item.id}_tab_{idx}", label)
        tab_load, tab_expr = ctx._load_string_expr(tab_key, ctx_expr=var("ctx"), prefix=f"{item.id}_tab_{idx}")
        tab_name = f"{item.id}_tab_{idx}"
        body.extend(tab_load)
        body.append(assign(tab_name, call("newTab", args=[var(item.id)],
                                          return_type="Lcom/google/android/material/tabs/TabLayout$Tab;",
                                          arg_types=[], invoke_kind="virtual",
                                          owner="Lcom/google/android/material/tabs/TabLayout;")))
        body.append(assign(tab_name, call("setText", args=[var(tab_name), tab_expr],
                                          return_type="Lcom/google/android/material/tabs/TabLayout$Tab;",
                                          arg_types=["Ljava/lang/CharSequence;"], invoke_kind="virtual",
                                          owner="Lcom/google/android/material/tabs/TabLayout$Tab;")))
        body.append(
            call_stmt("addTab", args=[var(item.id), var(tab_name), const(1 if idx == item.selected_index else 0)],
                      return_type=None,
                      arg_types=["Lcom/google/android/material/tabs/TabLayout$Tab;", "Z"],
                      invoke_kind="virtual", owner="Lcom/google/android/material/tabs/TabLayout;")
        )
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_drawer_layout(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "drawer_layout")
    body = [
        assign(item.id, new("Landroidx/drawerlayout/widget/DrawerLayout;", args=[var("ctx")])),
    ]
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    body.extend(ctx._build_ui_items(item.id, item.items))
    return body


def render_fragment_container(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "fragment_container")
    if item.layout is None:
        item.layout = ("match_parent", "match_parent")
    body = [
        assign(item.id, new("Landroidx/fragment/app/FragmentContainerView;", args=[var("ctx")])),
    ]
    body.extend(ctx._apply_view_layout(item, parent_id))
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    return body


def render_screen(ctx, item, parent_id):
    item.id = ctx._register_view(item.id, "screen")
    ctx._screen_map[item.name] = item.id
    ctx._screens.append((item.name, item.id))
    ctx._screen_transitions[item.name] = ctx._normalize_screen_transition(getattr(item, "transition", None))
    ctx._container_orientation[item.id] = "vertical"
    body = list(relative_layout(item.id, var("ctx")))
    body.extend(ctx._apply_view_layout(item, parent_id))
    # Default visibility: first screen visible, others gone.
    vis = 0 if len(ctx._screens) == 1 else 8
    body.append(
        call_stmt("setVisibility", args=[var(item.id), const(vis)],
                  return_type=None, arg_types=["I"], invoke_kind="virtual",
                  owner="Landroid/view/View;")
    )
    body.append(add_view(var(parent_id), var(item.id)))
    body.extend(ctx._capture_view_static(item.id))
    prev_screen = ctx._current_screen
    ctx._current_screen = item.name
    try:
        from dsl.widgets import _UIColumn
        screen_root = _UIColumn(*item.items, id=f"{item.id}_root", layout=("match_parent", "match_parent"))
        screen_root.id = ctx._register_view(screen_root.id, "column")
        ctx._container_orientation[screen_root.id] = "vertical"
        body.extend(linear_layout(screen_root.id, var("ctx"), "vertical"))
        body.extend(ctx._apply_view_layout(screen_root, item.id))
        body.append(add_view(var(item.id), var(screen_root.id)))
        body.extend(ctx._capture_view_static(screen_root.id))
        body.extend(ctx._build_ui_items(screen_root.id, screen_root.items))
    finally:
        ctx._current_screen = prev_screen
    return body
