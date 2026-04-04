# UI Surface Expansion - Where We Are

This is the tracker for UI depth and polish. The rules are simple: everything stays AOT-compiled, deterministic, and static. No reactive runtime, no implicit diffing, no dynamic widget trees. Animations are explicit and imperative.

## Ground rules

Every phase has to respect these:
- Named handlers only, statically registered
- Compile-time ID validation on everything
- Deterministic lowering - no guessing at runtime
- Lint errors for unsupported widget/style combos
- Focused tests plus at least one integration smoke per phase

## What's done

### Phase 1: Typography
Font family, weight, style, letter spacing, line height, text alignment, all-caps, max lines, ellipsize. All lowered to the right TextView APIs. Covers Text, Button family, Radio/Checkbox/Switch. Still need to hit Dropdown and PopupMenu text surfaces.

### Phase 2: Control Tinting
Tint, thumb tint, track tint, progress tint, button tint - all wired to the right Android APIs across Slider, ProgressBar, Switch, Checkbox/Radio, and Button.

### Phase 3: ColorStateList DSL
`ColorState(default, pressed, disabled, selected, focused)` with deterministic state ordering. Works on text color, tint, and progress fields. Background tint uses default-color fallback with a lint warning for now.

### Phase 4: Events
Added `on_change`, `on_text_change`, `on_item_selected`, `on_menu_item_selected`, `on_focus_change`. Each maps to the right Android listener (OnSeekBarChangeListener, TextWatcher, OnItemSelectedListener, etc).

### Phase 5: Input Configuration
TextField got `input_type`, `ime_options`, `max_length`, `single_line`, `password`, `auto_capitalize`, `numeric_only`. All lowered correctly.

### Phase 6: Accessibility
`content_description` and `important_for_accessibility` on all widgets.

### Phase 7: Elevation and Shadow
Elevation, pressed elevation, text shadow (color, radius, dx/dy). Covers Card, Button, Container, AppBar, Text.

### Phase 8: Visual Effects
Opacity, borders (width, color, per-corner radius), gradient backgrounds, ripple, clip-to-outline, clip-children, blur (API 31+ with compile-time guard), static transforms (rotation, scale, translation).

### Phase 9: Explicit Animations
`animate(id, ...)` with helpers for fade, rotate, scale, translate, elevation. Composition via `sequence()` and `parallel()`. Navigation transitions (fade, slide in four directions). All imperative - no state-bound or diff-based animation.

### Phase 10: Theme Expansion
Added input, selector, progress, icon, container, and appbar theme channels. Precedence is enforced: inline > style > theme > defaults.

### Phase 11: Scroll Controls
ScrollView and HorizontalScrollView with single-child enforcement.

### Phase 12: Static List View
`ListView(items=[...], item_layout=...)` with deterministic adapter generation. No runtime diffing.

### Phase 13: Validation and Linting
Checks for incompatible style fields, invalid state keys, unsupported event bindings, duplicate IDs, missing animation targets, blur below API 31, bad gradient configs. Error messages include widget ID and field name.

## What's next (Phase 14: Material Plugin)

Not started yet. When we get here, we're looking at:

**Input:** number fields, rating controls, chip groups, toggle button groups, transfer lists.

**Data display:** avatars, badges, chips, tables, tooltips, typography presets.

**Feedback:** Material alerts, backdrops, proper Material dialogs (replace the platform fallback), skeleton loaders.

**Navigation:** bottom nav, breadcrumbs, drawers, pagination, speed dial, steppers, tabs.

## What we're not doing

No reactive hooks. No CSS cascade engine. No dynamic theme switching in v1. No shader DSL. No runtime layout diffing. These aren't up for debate - they'd break the deterministic model.
