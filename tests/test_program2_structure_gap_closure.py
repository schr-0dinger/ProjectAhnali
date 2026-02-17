import pytest

from alpha_pipeline import alpha_pipeline
from dsl.app import (
    DrawerLayout,
    FragmentContainer,
    NavigationBar,
    NavigationRail,
    RecyclerView,
    activity,
    app,
    column,
    drawer_layout,
    fragment_container,
    navigation_bar,
    navigation_rail,
    percent,
    recycler_view,
    row,
    text,
    ui,
)


def test_program2_recycler_view_static_model_lowers_with_layout_manager():
    prog = app(
        activity(
            "MainActivity",
            ui(
                recycler_view(
                    id="feed",
                    items=["A", "B", 3, True],
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_feed:Landroidx/recyclerview/widget/RecyclerView;" in smali
    assert (
        "Landroidx/recyclerview/widget/RecyclerView;->setLayoutManager("
        "Landroidx/recyclerview/widget/RecyclerView$LayoutManager;)V"
    ) in smali


def test_program2_recycler_view_class_shape_and_validation():
    prog = app(
        activity(
            "MainActivity",
            ui(
                RecyclerView(
                    id="feed_cls",
                    items=["One", "Two"],
                ),
            ),
        )
    ).build()
    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_feed_cls:Landroidx/recyclerview/widget/RecyclerView;" in smali

    with pytest.raises(RuntimeError, match="RecyclerView items must be a list or tuple"):
        recycler_view(id="bad_feed", items="not-a-list")
    with pytest.raises(RuntimeError, match="RecyclerView items must contain only static primitive values"):
        recycler_view(id="bad_feed_item", items=[{"x": 1}])


def test_program2_navigation_bar_and_rail_static_models():
    prog = app(
        activity(
            "MainActivity",
            ui(
                navigation_bar(
                    id="main_nav",
                    items=["Home", "Profile"],
                    selected_index=1,
                ),
                navigation_rail(
                    id="rail_nav",
                    items=["Inbox", "Sent"],
                    selected_index=0,
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert (
        ".field public static view_main_nav:Lcom/google/android/material/bottomnavigation/BottomNavigationView;"
        in smali
    )
    assert (
        ".field public static view_rail_nav:Lcom/google/android/material/navigationrail/NavigationRailView;"
        in smali
    )
    assert "Landroid/view/Menu;->add(IIILjava/lang/CharSequence;)Landroid/view/MenuItem;" in smali
    assert "Lcom/google/android/material/bottomnavigation/BottomNavigationView;->setSelectedItemId(I)V" in smali
    assert "Lcom/google/android/material/navigationrail/NavigationRailView;->setSelectedItemId(I)V" in smali


def test_program2_navigation_bar_and_rail_class_shape_and_validation():
    prog = app(
        activity(
            "MainActivity",
            ui(
                NavigationBar(id="main_nav_cls", items=["A", "B"], selected_index=0),
                NavigationRail(id="rail_nav_cls", items=["A", "B"], selected_index=1),
            ),
        )
    ).build()
    smali = alpha_pipeline(prog)["smali_class"]
    assert (
        ".field public static view_main_nav_cls:Lcom/google/android/material/bottomnavigation/BottomNavigationView;"
        in smali
    )
    assert (
        ".field public static view_rail_nav_cls:Lcom/google/android/material/navigationrail/NavigationRailView;"
        in smali
    )

    with pytest.raises(RuntimeError, match="NavigationBar items must be a list or tuple"):
        navigation_bar(id="bad_nav", items="not-a-list")
    with pytest.raises(RuntimeError, match="NavigationBar selected_index 1 is out of range"):
        navigation_bar(id="bad_nav_idx", items=["x"], selected_index=1)
    with pytest.raises(RuntimeError, match="NavigationRail items must be a list or tuple"):
        navigation_rail(id="bad_rail", items="not-a-list")
    with pytest.raises(RuntimeError, match="NavigationRail selected_index 1 is out of range"):
        navigation_rail(id="bad_rail_idx", items=["x"], selected_index=1)


def test_program2_drawer_layout_and_fragment_container_models():
    prog = app(
        activity(
            "MainActivity",
            ui(
                drawer_layout(
                    column(text("Content", id="content_text"), id="content_col"),
                    column(text("Drawer", id="drawer_text"), id="drawer_col"),
                    id="root_drawer",
                ),
                fragment_container(id="frag_host"),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_root_drawer:Landroidx/drawerlayout/widget/DrawerLayout;" in smali
    assert ".field public static view_frag_host:Landroidx/fragment/app/FragmentContainerView;" in smali

    with pytest.raises(RuntimeError, match="DrawerLayout requires exactly two direct children"):
        drawer_layout(text("Only one", id="only"), id="drawer_bad")
    with pytest.raises(RuntimeError, match="FragmentContainer does not accept direct children"):
        fragment_container(text("No children allowed", id="nope"), id="frag_bad")


def test_program2_drawer_layout_and_fragment_container_class_shape():
    prog = app(
        activity(
            "MainActivity",
            ui(
                DrawerLayout(
                    column(text("C", id="c"), id="c_col"),
                    column(text("D", id="d"), id="d_col"),
                    id="drawer_cls",
                ),
                FragmentContainer(id="frag_cls"),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert ".field public static view_drawer_cls:Landroidx/drawerlayout/widget/DrawerLayout;" in smali
    assert ".field public static view_frag_cls:Landroidx/fragment/app/FragmentContainerView;" in smali


def test_program2_percent_layout_modifier_covers_width_and_height_paths():
    prog = app(
        activity(
            "MainActivity",
            ui(
                row(
                    text("half", id="half", width=percent(50)),
                    id="row_shell",
                ),
                column(
                    text("quarter", id="quarter", height=percent(25)),
                    id="col_shell",
                ),
            ),
        )
    ).build()

    smali = alpha_pipeline(prog)["smali_class"]
    assert "Landroid/widget/LinearLayout$LayoutParams;->weight:F" in smali

    with pytest.raises(RuntimeError, match="Percent width is only supported in horizontal rows"):
        app(
            activity(
                "MainActivity",
                ui(column(text("bad", id="bad_w", width=percent(50)), id="bad_col")),
            )
        ).build()

    with pytest.raises(RuntimeError, match="Percent height is only supported in vertical columns"):
        app(
            activity(
                "MainActivity",
                ui(row(text("bad", id="bad_h", height=percent(50)), id="bad_row")),
            )
        ).build()
