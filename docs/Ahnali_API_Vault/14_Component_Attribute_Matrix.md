---
tags: [ahnali, api, matrix, components]
---

# Component Attribute Matrix

Back to: [[00_Home]]

Use with [[04_Shared_Attributes]].

## Shared Group Legend

- `A`: Layout and positioning
- `B`: Text/typography
- `C`: Tint/state color
- `D`: Accessibility
- `E`: Elevation/shadow
- `F`: Visual effects/transforms
- `G`: Background surface
- `H`: Image-specific display
- `I`: Inline event attrs

## Matrix

| Component | Category | Shared Groups | Specific Attributes |
| --- | --- | --- | --- |
| `Text` / `text(...)` | Content | A, B, C, D, E, F, G, I | `text` |
| `View` / `view(...)` | Generic visual | A, C, D, E, F, G, I | none |
| `Button` / `button(...)` | Action | A, B, C, D, E, F, G, I | `text`, `icon` |
| `RaisedButton` / `raised_button(...)` | Action variant | A, B, C, D, E, F, G, I | `text` |
| `FlatButton` / `flat_button(...)` | Action variant | A, B, C, D, E, F, G, I | `text` |
| `IconButton` / `icon_button(...)` | Action variant | A, B, C, D, E, F, G, I | `text` |
| `FloatingActionButton` / `floating_action_button(...)` | Action variant | A, B, C, D, E, F, G, I | `text`, `floating=True` |
| `AppBar` / `app_bar(...)` | Top bar | A, B, C, D, E, F, G, I | `inline` |
| `Icon` / `icon(...)` | Content icon text | A, B, C, D, E, F, G, I | `name` |
| `Image` / `image(...)` | Content image | A, C, D, E, F, G, H, I | `src` |
| `Divider` / `divider(...)` | Separator | A, C, D, E, F, G, I | `color`, `thickness` |
| `Row` / `row(...)` | Layout container | A, D, E, F, G | `items`, `align`, `arrangement`, `weight_sum` |
| `Column` / `column(...)` | Layout container | A, D, E, F, G | `items`, `align`, `arrangement`, `weight_sum` |
| `Relative` / `relative(...)` | Layout container | A, D, E, F, G | `items` |
| `Constraint` / `constraint(...)` | Layout container | A, D, E, F, G | `items` |
| `Frame` / `frame(...)` | Layout container | A, C, D, E, F, G, I | `items` |
| `Container` / `container(...)` | Semantic container | A, D, E, F, G | `items` |
| `Card` / `card(...)` | Semantic surface | A, D, E, F, G | `items` |
| `ButtonBar` / `button_bar(...)` | Layout helper | A, D, E, F, G | `items` |
| `ScrollView` / `scroll_view(...)` | Scroll container | A, C, D, E, F, G, I | exactly one child |
| `HorizontalScrollView` / `horizontal_scroll_view(...)` | Scroll container | A, C, D, E, F, G, I | exactly one child |
| `NestedScrollView` / `nested_scroll_view(...)` | Scroll container | A, C, D, E, F, G, I | exactly one child |
| `ViewPager` / `view_pager(...)` | Pager | A, C, D, E, F, G, I | `items`, `initial_page` |
| `TabLayout` / `tab_layout(...)` | Tabs | A, C, D, E, F, G, I | `tabs`, `selected_index` |
| `BottomNavigationView` / `bottom_navigation_view(...)` | Navigation | A, C, D, E, F, G, I | `items`, `selected_index` |
| `NavigationBar` / `navigation_bar(...)` | Navigation | A, C, D, E, F, G, I | `items`, `selected_index` |
| `NavigationRail` / `navigation_rail(...)` | Navigation | A, C, D, E, F, G, I | `items`, `selected_index` |
| `CoordinatorLayout` / `coordinator_layout(...)` | Layout container | A, C, D, E, F, G, I | `items` |
| `DrawerLayout` / `drawer_layout(...)` | Layout container | A, C, D, E, F, G, I | exactly two children |
| `FragmentContainer` / `fragment_container(...)` | Fragment host | A, C, D, E, F, G, I | no direct children |
| `TextField` / `text_field(...)` | Input | A, B, C, D, E, F, G, I | `text`, `hint`, `input_type`, `ime_options`, `max_length`, `single_line`, `password`, `auto_capitalize`, `numeric_only` |
| `Checkbox` / `checkbox(...)` | Input/select | A, B, C, D, E, F, G, I | `text`, `checked` |
| `Radio` / `radio(...)` | Input/select | A, B, C, D, E, F, G, I | `text`, `checked` |
| `Switch` / `switch(...)` | Input/select | A, B, C, D, E, F, G, I | `text`, `checked` |
| `Slider` / `slider(...)` | Input/select | A, B, C, D, E, F, G, I | `value`, `min`, `max` |
| `RadioGroup` / `radio_group(...)` | Input container | A, D, E, F, G, I | `items`, `orientation` |
| `DropdownButton` / `dropdown_button(...)` | Selection | A, B, C, D, E, F, G, I | `items` |
| `PopupMenuButton` / `popup_menu_button(...)` | Selection/action | A, B, C, D, E, F, G, I | `text`, `items` |
| `ProgressBar` / `progress_bar(...)` | Feedback | A, C, D, E, F, G, I | `value`, `min`, `max`, `indeterminate` |
| `ListView` / `list_view(...)` | Static list | A, C, D, E, F, G, I | `items`, `item_layout` |
| `GridView` / `grid_view(...)` | Static grid | A, C, D, E, F, G, I | `items`, `item_layout`, `num_columns` |
| `RecyclerView` / `recycler_view(...)` | Static recycler | A, C, D, E, F, G, I | `items` |
| `Screen` / `screen(...)` | Navigation root | fixed screen container fields | `name`, `id` (optional), `transition`, `items` |

## Utility Constructors

- `simple_dialog`, `toast`, `snackbar`, `exit_app`
- `style`, `theme`, `color_state`, `gradient`, `presets`, `state`

## Notes

- For event decorators and target constraints, see [[10_Events_and_Handler_DSL]].
- For capability/network/storage helpers, see [[08_Feedback_and_Utility_Components]].
