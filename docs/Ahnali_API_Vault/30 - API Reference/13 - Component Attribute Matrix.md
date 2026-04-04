---
tags: [ahnali, api, matrix, reference]
---

# Component Attribute Matrix

> [!abstract] Every component, every attribute, one table
> Use this with [[30 - API Reference/03 - Shared Attributes]] to see exactly what each component supports.

## Shared group legend

| Group | What it covers |
|---|---|
| A | Layout and positioning |
| B | Text/typography |
| C | Tint/stateful colors |
| D | Accessibility |
| E | Elevation/shadow |
| F | Visual effects/transforms |
| G | Background surface |
| H | Image-specific display |
| I | Inline event attrs |

## Components

| Component | Category | Groups | Specific attributes |
|---|---|---|---|
| `Text` | Content | A, B, C, D, E, F, G, I | `text` |
| `View` | Generic visual | A, C, D, E, F, G, I | - |
| `Button` | Action | A, B, C, D, E, F, G, I | `text`, `icon` |
| `RaisedButton` | Action variant | A, B, C, D, E, F, G, I | `text` |
| `FlatButton` | Action variant | A, B, C, D, E, F, G, I | `text` |
| `IconButton` | Action variant | A, B, C, D, E, F, G, I | `text` |
| `FloatingActionButton` | Action variant | A, B, C, D, E, F, G, I | `text`, `floating=True` |
| `AppBar` | Top bar | A, B, C, D, E, F, G, I | `inline` |
| `Icon` | Content icon | A, B, C, D, E, F, G, I | `name` |
| `Image` | Content image | A, C, D, E, F, G, H, I | `src` |
| `Divider` | Separator | A, C, D, E, F, G, I | `color`, `thickness` |
| `Row` | Layout container | A, D, E, F, G | `items`, `align`, `arrangement`, `weight_sum` |
| `Column` | Layout container | A, D, E, F, G | `items`, `align`, `arrangement`, `weight_sum` |
| `Relative` | Layout container | A, D, E, F, G | `items` |
| `Constraint` | Layout container | A, D, E, F, G | `items` |
| `Frame` | Layout container | A, C, D, E, F, G, I | `items` |
| `Container` | Semantic container | A, D, E, F, G | `items` |
| `Card` | Semantic surface | A, D, E, F, G | `items` |
| `ButtonBar` | Layout helper | A, D, E, F, G | `items` |
| `ScrollView` | Scroll container | A, C, D, E, F, G, I | exactly one child |
| `HorizontalScrollView` | Scroll container | A, C, D, E, F, G, I | exactly one child |
| `NestedScrollView` | Scroll container | A, C, D, E, F, G, I | exactly one child |
| `ViewPager` | Pager | A, C, D, E, F, G, I | `items`, `initial_page` |
| `TabLayout` | Tabs | A, C, D, E, F, G, I | `tabs`, `selected_index` |
| `BottomNavigationView` | Navigation | A, C, D, E, F, G, I | `items`, `selected_index` |
| `NavigationBar` | Navigation | A, C, D, E, F, G, I | `items`, `selected_index` |
| `NavigationRail` | Navigation | A, C, D, E, F, G, I | `items`, `selected_index` |
| `CoordinatorLayout` | Layout container | A, C, D, E, F, G, I | `items` |
| `DrawerLayout` | Layout container | A, C, D, E, F, G, I | exactly two children |
| `FragmentContainer` | Fragment host | A, C, D, E, F, G, I | no direct children |
| `TextField` | Input | A, B, C, D, E, F, G, I | `text`, `hint`, `input_type`, `ime_options`, `max_length`, `single_line`, `password`, `auto_capitalize`, `numeric_only` |
| `Checkbox` | Input/select | A, B, C, D, E, F, G, I | `text`, `checked` |
| `Radio` | Input/select | A, B, C, D, E, F, G, I | `text`, `checked` |
| `Switch` | Input/select | A, B, C, D, E, F, G, I | `text`, `checked` |
| `Slider` | Input/select | A, B, C, D, E, F, G, I | `value`, `min`, `max` |
| `RadioGroup` | Input container | A, D, E, F, G, I | `items`, `orientation` |
| `DropdownButton` | Selection | A, B, C, D, E, F, G, I | `items` |
| `PopupMenuButton` | Selection/action | A, B, C, D, E, F, G, I | `text`, `items` |
| `ProgressBar` | Feedback | A, C, D, E, F, G, I | `value`, `min`, `max`, `indeterminate` |
| `ListView` | Static list | A, C, D, E, F, G, I | `items`, `item_layout` |
| `GridView` | Static grid | A, C, D, E, F, G, I | `items`, `item_layout`, `num_columns` |
| `RecyclerView` | Static recycler | A, C, D, E, F, G, I | `items` |
| `Screen` | Navigation root | fixed container fields | `name`, `id` (optional), `transition`, `items` |

## Utility constructors

These aren't components but they're part of the DSL surface:

- `toast(message, duration=0)`
- `snackbar(message, duration=0)`
- `simple_dialog(title, message)`
- `exit_app()`
- `style(...)`, `theme(...)`, `color_state(...)`, `gradient(...)`, `presets()`, `state(...)`

## Learn more

- Shared attributes detail: [[30 - API Reference/03 - Shared Attributes]]
- Structure components: [[30 - API Reference/04 - Structure Components]]
- Input and selection: [[30 - API Reference/06 - Input and Selection]]
