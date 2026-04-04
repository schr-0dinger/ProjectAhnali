---
tags: [ahnali, api, validation, lint, diagnostics]
---

# Validation and Diagnostics

> [!abstract] The compiler catches mistakes before they reach your device
> Every phase has validation gates. If something's wrong, you get a clear error message with the widget ID and field name.

## Compile-time checks

### Widget and style validation

| Check | What it catches |
|---|---|
| Incompatible style field | Applying `font_weight` to a non-text widget |
| Invalid state keys | Using a state key that wasn't declared |
| Unsupported event binding | `on_text_change` on a Button |
| Duplicate IDs | Two widgets with `id="label"` |
| Missing animation target | `animate("nonexistent", ...)` |
| Invalid gradient config | Missing start or end color |
| Blur below API 31 | `blur_radius` when `min_sdk < 31` |

### Structure validation

| Check | What it catches |
|---|---|
| Screen mixing | Regular widgets alongside `Screen(...)` at the same level |
| ScrollView child count | More than one direct child in `ScrollView` |
| DrawerLayout children | Not exactly two children (content + drawer) |
| FragmentContainer children | Any direct children in v1 |
| ViewPager initial page | `initial_page` out of range |
| Tab/Nav selected index | `selected_index` out of range |

### Capability validation

If you use a capability without declaring it:

```
[CapabilityError] http_get requires Caps.Networking. Fix: add app_config(uses=[Caps.Networking]) to activity(...).
```

### Reactive mode validation

If you use a reactive API in static mode:

```
[ReactiveModeError] observable requires reactive mode. Fix: set app_config(mode='reactive') in activity(...).
```

### Event handler validation

| Check | What it catches |
|---|---|
| Popup handler conflict | Both `on_click` and `on_menu_item_selected` on the same popup |
| Missing handler target | Navigation target ID doesn't resolve to a valid handler |
| Invalid handler syntax | Malformed handler expression |

## Error message format

Errors follow a standard pattern:

```
[ErrorType] Description. Fix: specific instruction.
```

The message always includes:
- The widget ID (when applicable)
- The field name (when applicable)
- A concrete fix suggestion

## Warnings

Warnings don't block compilation but you should pay attention:

- **Blur below API 31** — blur is skipped, fallback is used
- **Background ColorState** — currently uses default color with lint warning
- **Style overlap** — inline and theme channel both set the same field
- **Dropdown text surface** — typography support is partial
- **Popup menu item text** — typography support is partial

## Lint hardening (Phase 13)

The validation layer covers:

- Style field compatibility per widget type
- State key validity
- Event binding target constraints
- ID uniqueness
- Animation target existence
- API-level guards (blur)
- Gradient configuration validity

All checks have focused tests and at least one integration smoke test.

## Learn more

- Shared attributes: [[30 - API Reference/03 - Shared Attributes]]
- Component matrix: [[30 - API Reference/13 - Component Attribute Matrix]]
- Capability errors: [[40 - Capabilities/01 - Overview]]
