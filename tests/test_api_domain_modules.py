from dsl import api as legacy_api
from dsl.api_domains import capabilities, hybrid, interaction, motion, state, structure, style


def test_api_domain_modules_expose_legacy_compatible_symbols():
    assert structure.app is legacy_api.app
    assert structure.activity is legacy_api.activity
    assert structure.Frame is legacy_api.Frame
    assert structure.GridView is legacy_api.GridView
    assert structure.NestedScrollView is legacy_api.NestedScrollView
    assert structure.ViewPager is legacy_api.ViewPager
    assert structure.TabLayout is legacy_api.TabLayout
    assert structure.BottomNavigationView is legacy_api.BottomNavigationView
    assert structure.CoordinatorLayout is legacy_api.CoordinatorLayout
    assert structure.RecyclerView is legacy_api.RecyclerView
    assert structure.NavigationBar is legacy_api.NavigationBar
    assert structure.NavigationRail is legacy_api.NavigationRail
    assert structure.DrawerLayout is legacy_api.DrawerLayout
    assert structure.FragmentContainer is legacy_api.FragmentContainer
    assert structure.frame is legacy_api.frame
    assert structure.grid_view is legacy_api.grid_view
    assert structure.nested_scroll_view is legacy_api.nested_scroll_view
    assert structure.view_pager is legacy_api.view_pager
    assert structure.tab_layout is legacy_api.tab_layout
    assert structure.bottom_navigation_view is legacy_api.bottom_navigation_view
    assert structure.coordinator_layout is legacy_api.coordinator_layout
    assert structure.recycler_view is legacy_api.recycler_view
    assert structure.navigation_bar is legacy_api.navigation_bar
    assert structure.navigation_rail is legacy_api.navigation_rail
    assert structure.drawer_layout is legacy_api.drawer_layout
    assert structure.fragment_container is legacy_api.fragment_container
    assert style.theme is legacy_api.theme
    assert interaction.on_click is legacy_api.on_click
    assert interaction.on_slider_change is legacy_api.on_slider_change
    assert interaction.on_long_click is legacy_api.on_long_click
    assert interaction.on_touch is legacy_api.on_touch
    assert interaction.on_double_tap is legacy_api.on_double_tap
    assert interaction.on_swipe is legacy_api.on_swipe
    assert interaction.on_scroll is legacy_api.on_scroll
    assert interaction.on_fling is legacy_api.on_fling
    assert interaction.on_pinch is legacy_api.on_pinch
    assert interaction.on_zoom is legacy_api.on_zoom
    assert interaction.on_rotate_gesture is legacy_api.on_rotate_gesture
    assert interaction.on_scale_gesture_detector is legacy_api.on_scale_gesture_detector
    assert interaction.on_drag is legacy_api.on_drag
    assert interaction.on_drop is legacy_api.on_drop
    assert interaction.on_editor_action is legacy_api.on_editor_action
    assert interaction.on_key is legacy_api.on_key
    assert interaction.pop_to_root is legacy_api.pop_to_root
    assert interaction.clear_stack is legacy_api.clear_stack
    assert state.on_start is legacy_api.on_start
    assert state.on_resume is legacy_api.on_resume
    assert state.on_pause is legacy_api.on_pause
    assert state.on_stop is legacy_api.on_stop
    assert state.on_destroy is legacy_api.on_destroy
    assert state.storage_put is legacy_api.storage_put
    assert state.datastore_put is legacy_api.datastore_put
    assert state.file_write is legacy_api.file_write
    assert state.sqlite_put is legacy_api.sqlite_put
    assert state.room_put is legacy_api.room_put
    assert state.encrypted_storage_put is legacy_api.encrypted_storage_put
    assert capabilities.open_url is legacy_api.open_url
    assert motion.animate is legacy_api.animate


def test_hybrid_domain_placeholder_is_stable():
    assert hybrid.HYBRID_API_STATUS == "planned"
