import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import (
    BottomNavigationView,
    CoordinatorLayout,
    TabLayout,
    ViewPager,
    activity,
    app,
    bottom_navigation_view,
    coordinator_layout,
    tab_layout,
    text,
    ui,
    view_pager,
)


def test_program2_view_pager_static_model_lowers_and_sets_initial_page():
    prog = app(
        activity(
            "MainActivity",
            ui(
                view_pager(
                    text("Page A", id="page_a"),
                    text("Page B", id="page_b"),
                    id="pager",
                    initial_page=1,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_pager:Landroidx/viewpager/widget/ViewPager;" in smali
    assert "Landroidx/viewpager/widget/ViewPager;->setCurrentItem(I)V" in smali

    pager_children = []
    for method in [m for m in prog.methods if m.name.startswith("buildUi_")]:
        for stmt in method.body:
            call = getattr(stmt, "expr", None)
            if call is None:
                continue
            if getattr(call, "func_name", None) != "addView":
                continue
            if len(call.args) != 2:
                continue
            parent, child = call.args
            if getattr(parent, "name", None) == "pager" and getattr(child, "name", None):
                pager_children.append(child.name)
    assert len(pager_children) == 2


def test_program2_view_pager_class_shape_accepts_static_pages():
    prog = app(
        activity(
            "MainActivity",
            ui(
                ViewPager(
                    text("Page", id="page"),
                    id="pager_cls",
                    initial_page=0,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_pager_cls:Landroidx/viewpager/widget/ViewPager;" in smali


def test_program2_view_pager_rejects_invalid_page_shape():
    with pytest.raises(RuntimeError, match="ViewPager requires at least one page child"):
        view_pager(id="pager_empty")

    with pytest.raises(RuntimeError, match="ViewPager initial_page must be an integer"):
        view_pager(text("A"), id="pager_bad_type", initial_page=True)

    with pytest.raises(RuntimeError, match="ViewPager initial_page 1 is out of range"):
        view_pager(text("A"), id="pager_bad_range", initial_page=1)


def test_program2_tab_layout_lowers_to_material_tablayout():
    prog = app(
        activity(
            "MainActivity",
            ui(
                tab_layout(
                    id="tabs",
                    tabs=["Home", "Settings"],
                    selected_index=1,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_tabs:Lcom/google/android/material/tabs/TabLayout;" in smali
    assert "Lcom/google/android/material/tabs/TabLayout;->newTab()Lcom/google/android/material/tabs/TabLayout$Tab;" in smali
    assert "Lcom/google/android/material/tabs/TabLayout;->addTab(Lcom/google/android/material/tabs/TabLayout$Tab;Z)V" in smali


def test_program2_tab_layout_class_shape_accepts_static_tab_labels():
    prog = app(
        activity(
            "MainActivity",
            ui(
                TabLayout(
                    id="tabs_cls",
                    tabs=["One", "Two"],
                    selected_index=0,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_tabs_cls:Lcom/google/android/material/tabs/TabLayout;" in smali


def test_program2_tab_layout_rejects_invalid_shape():
    with pytest.raises(RuntimeError, match="TabLayout tabs must be a list or tuple"):
        tab_layout(id="tabs_bad_type", tabs="not-a-list")

    with pytest.raises(RuntimeError, match="TabLayout tabs must contain at least one label"):
        tab_layout(id="tabs_empty", tabs=[])

    with pytest.raises(RuntimeError, match="TabLayout tabs must contain only static primitive labels"):
        tab_layout(id="tabs_bad_item", tabs=[{"bad": 1}])

    with pytest.raises(RuntimeError, match="TabLayout selected_index must be an integer"):
        tab_layout(id="tabs_bad_idx_type", tabs=["A"], selected_index=False)

    with pytest.raises(RuntimeError, match="TabLayout selected_index 1 is out of range"):
        tab_layout(id="tabs_bad_idx_range", tabs=["A"], selected_index=1)


def test_program2_bottom_navigation_view_lowers_to_material_bottom_navigation():
    prog = app(
        activity(
            "MainActivity",
            ui(
                bottom_navigation_view(
                    id="bottom_nav",
                    items=["Feed", "Profile", "Settings"],
                    selected_index=2,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert (
        ".field public static view_bottom_nav:Lcom/google/android/material/bottomnavigation/BottomNavigationView;"
        in smali
    )
    assert "Lcom/google/android/material/bottomnavigation/BottomNavigationView;->getMenu()Landroid/view/Menu;" in smali
    assert "Landroid/view/Menu;->add(IIILjava/lang/CharSequence;)Landroid/view/MenuItem;" in smali
    assert "Lcom/google/android/material/bottomnavigation/BottomNavigationView;->setSelectedItemId(I)V" in smali


def test_program2_bottom_navigation_view_class_shape_accepts_static_items():
    prog = app(
        activity(
            "MainActivity",
            ui(
                BottomNavigationView(
                    id="bottom_nav_cls",
                    items=["A", "B"],
                    selected_index=0,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert (
        ".field public static view_bottom_nav_cls:Lcom/google/android/material/bottomnavigation/BottomNavigationView;"
        in smali
    )


def test_program2_bottom_navigation_view_rejects_invalid_shape():
    with pytest.raises(RuntimeError, match="BottomNavigationView items must be a list or tuple"):
        bottom_navigation_view(id="bottom_bad_type", items="not-a-list")

    with pytest.raises(RuntimeError, match="BottomNavigationView items must contain at least one label"):
        bottom_navigation_view(id="bottom_empty", items=[])

    with pytest.raises(RuntimeError, match="BottomNavigationView items must contain only static primitive labels"):
        bottom_navigation_view(id="bottom_bad_item", items=[object()])

    with pytest.raises(RuntimeError, match="BottomNavigationView selected_index must be an integer"):
        bottom_navigation_view(id="bottom_bad_idx_type", items=["A"], selected_index=True)

    with pytest.raises(RuntimeError, match="BottomNavigationView selected_index 1 is out of range"):
        bottom_navigation_view(id="bottom_bad_idx_range", items=["A"], selected_index=1)


def test_program2_coordinator_layout_lowers_to_androidx_coordinator_layout():
    prog = app(
        activity(
            "MainActivity",
            ui(
                coordinator_layout(
                    text("Inside", id="inside"),
                    id="coordinator",
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert (
        ".field public static view_coordinator:Landroidx/coordinatorlayout/widget/CoordinatorLayout;"
        in smali
    )


def test_program2_coordinator_layout_class_shape_accepts_children():
    prog = app(
        activity(
            "MainActivity",
            ui(
                CoordinatorLayout(
                    text("Inside class shape", id="inside_cls"),
                    id="coordinator_cls",
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert (
        ".field public static view_coordinator_cls:Landroidx/coordinatorlayout/widget/CoordinatorLayout;"
        in smali
    )
