"""Widget renderer registry.

Each widget type has a render function that takes (ctx, item, parent_id)
and returns a list of IR instructions.  The registry maps widget classes
to their render functions so _render_ui_core becomes a single dispatch.

Public widget classes (e.g. ListView) subclass the internal _UI* classes,
so we use isinstance checks rather than exact type matching.

Dispatch order matters: subclasses must appear before their base classes
so that isinstance checks resolve to the most specific renderer.

Subclass relationships (from dsl/widgets.py):
  _UIButtonBar → _UIRow → _UIColumn → _UIText
  _UICard → _UIColumn
  _UIContainer → _UIColumn
  _UIRadioGroup → _UIColumn
  _UIButton → (base for RaisedButton, FlatButton, IconButton, FAB, Slider, DropdownButton, PopupMenuButton)
  _UIText → (base for TextField, Checkbox, Radio, Switch, Icon, AppBar)
  _UIView → (base for Divider, Image, ProgressBar, ScrollView, HScrollView, NestedScrollView,
             ListView, GridView, RecyclerView, ViewPager, TabLayout, BottomNav, NavBar, NavRail,
             CoordinatorLayout, DrawerLayout, FragmentContainer, Frame, GridView, Image, etc.)
"""

from dsl.widgets import (
    _UIAppBar,
    _UIButton,
    _UIButtonBar,
    _UIBottomNavigationView,
    _UICard,
    _UICheckbox,
    _UIColumn,
    _UICoordinatorLayout,
    _UIContainer,
    _UIConstraint,
    _UIDrawerLayout,
    _UIDivider,
    _UIDropdownButton,
    _UIFlatButton,
    _UIFragmentContainer,
    _UIFloatingActionButton,
    _UIFrame,
    _UIGridView,
    _UIHorizontalScrollView,
    _UIIcon,
    _UIIconButton,
    _UIImage,
    _UIListView,
    _UINavigationBar,
    _UINavigationRail,
    _UINestedScrollView,
    _UIPopupMenuButton,
    _UIProgressBar,
    _UIRadio,
    _UIRadioGroup,
    _UIRelative,
    _UIRaisedButton,
    _UIRecyclerView,
    _UIRow,
    _UIScrollView,
    _UITabLayout,
    _UIScreen,
    _UISlider,
    _UISwitch,
    _UIText,
    _UITextField,
    _UIViewPager,
    _UIView,
)

from . import _buttons, _text_display, _input, _selection, _containers, _scroll, _lists, _navigation

# Ordered (class, renderer) pairs.  Checked with isinstance.
# Subclasses MUST come before their bases.
_RENDERERS = [
    # === Most specific types first ===

    # _UIButtonBar → _UIRow → _UIColumn → _UIText
    (_UIButtonBar, _containers.render_button_bar),
    (_UIRow, _containers.render_row),

    # _UICard → _UIColumn
    (_UICard, _containers.render_card),

    # _UIContainer → _UIColumn
    (_UIContainer, _containers.render_container),

    # _UIRadioGroup → _UIColumn
    (_UIRadioGroup, _input.render_radio_group),

    # _UIColumn → _UIText
    (_UIColumn, _containers.render_column),

    # Button subclasses → _UIButton
    (_UIFloatingActionButton, _buttons.render_fab),
    (_UIRaisedButton, _buttons.render_raised_button),
    (_UIFlatButton, _buttons.render_flat_button),
    (_UIIconButton, _buttons.render_icon_button),
    (_UISlider, _input.render_slider),
    (_UIDropdownButton, _selection.render_dropdown),
    (_UIPopupMenuButton, _selection.render_popup_menu),
    (_UIButton, _buttons.render_button),

    # Text subclasses → _UIText
    (_UITextField, _input.render_text_field),
    (_UICheckbox, _input.render_checkbox),
    (_UIRadio, _input.render_radio),
    (_UISwitch, _input.render_switch),
    (_UIIcon, _text_display.render_icon),
    (_UIAppBar, _text_display.render_app_bar),
    (_UIText, _text_display.render_text),

    # View subclasses → _UIView
    (_UIDivider, _text_display.render_divider),
    (_UIImage, _text_display.render_image),
    (_UIProgressBar, _text_display.render_progress_bar),
    (_UIScrollView, _scroll.render_scroll_view),
    (_UIHorizontalScrollView, _scroll.render_horizontal_scroll_view),
    (_UINestedScrollView, _scroll.render_nested_scroll_view),
    (_UIListView, _lists.render_list_view),
    (_UIGridView, _lists.render_grid_view),
    (_UIRecyclerView, _lists.render_recycler_view),
    (_UIViewPager, _navigation.render_view_pager),
    (_UITabLayout, _navigation.render_tab_layout),
    (_UIBottomNavigationView, _navigation.render_bottom_nav),
    (_UINavigationBar, _navigation.render_nav_bar),
    (_UINavigationRail, _navigation.render_nav_rail),
    (_UICoordinatorLayout, _containers.render_coordinator_layout),
    (_UIDrawerLayout, _navigation.render_drawer_layout),
    (_UIFragmentContainer, _navigation.render_fragment_container),
    (_UIFrame, _containers.render_frame),
    (_UIView, _text_display.render_view),

    # Non-subclass types (no ordering constraints relative to bases)
    (_UIRelative, _containers.render_relative),
    (_UIConstraint, _containers.render_constraint),
    (_UIScreen, _navigation.render_screen),
]


def render_widget(ctx, item, parent_id):
    """Dispatch to the correct renderer for *item*.

    Returns a list of IR instructions, or raises RuntimeError for
    unknown widget types.
    """
    for cls, fn in _RENDERERS:
        if isinstance(item, cls):
            return fn(ctx, item, parent_id)
    raise RuntimeError(f"Unsupported UI item: {item}")
