# Anali UI Surface Expansion TODO (v1)

Last updated: 2026-02-11

Goal:
- Expand UI depth and polish while preserving:
- Ahead-of-time compilation
- Deterministic smali emission
- No reactive runtime
- No implicit property diffing
- No dynamic widget trees

All animations and effects must be explicit and imperative.

## Global Constraints (Apply to Every Phase)

- [ ] Keep handlers named and statically registered (no lambdas/dynamic callbacks).
- [ ] Keep compile-time ID validation for all widget/event references.
- [ ] Keep deterministic lowering only (no runtime behavior inference).
- [ ] Add compile-time lint for unsupported widget/style combinations.
- [ ] Add focused lowering tests and at least one integration smoke test per phase.

## Phase 1: Typography v1

### DSL and Style Surface (`dsl/widgets.py`)
- [ ] Add `font_family` to `Style`.
- [ ] Add `font_weight` to `Style`.
- [ ] Add `font_style` to `Style`.
- [ ] Add `letter_spacing` to `Style`.
- [ ] Add `line_height` to `Style`.
- [ ] Add `text_alignment` to `Style`.
- [ ] Add `all_caps` to `Style`.
- [ ] Add `max_lines` to `Style`.
- [ ] Add `ellipsize` to `Style`.

### Lowering (`dsl/lowering/attr_registry.py`, `dsl/lowering/context.py`)
- [ ] Lower `font_*` to `setTypeface`.
- [ ] Lower `letter_spacing` to `setLetterSpacing`.
- [ ] Lower `line_height` to `setLineSpacing`.
- [ ] Lower `text_alignment` to `setTextAlignment`.
- [ ] Lower `all_caps` to `setAllCaps`.
- [ ] Lower `max_lines` to `setMaxLines`.
- [ ] Lower `ellipsize` to `setEllipsize`.

### Coverage
- [ ] Text
- [ ] Button family
- [ ] Radio / Checkbox / Switch
- [ ] Dropdown text surface
- [ ] Popup menu item text surface

## Phase 2: Control Tinting v1

### DSL and Style Surface (`dsl/widgets.py`)
- [ ] Add `tint`.
- [ ] Add `thumb_tint`.
- [ ] Add `track_tint`.
- [ ] Add `progress_tint`.
- [ ] Add `button_tint`.

### Lowering (`dsl/lowering/context.py`)
- [ ] Slider: `setThumbTintList`.
- [ ] Slider: `setProgressTintList`.
- [ ] Slider: `setProgressBackgroundTintList`.
- [ ] ProgressBar: `setProgressTintList`.
- [ ] ProgressBar: `setIndeterminateTintList`.
- [ ] Switch: `setThumbTintList`.
- [ ] Switch: `setTrackTintList`.
- [ ] Checkbox/Radio: `setButtonTintList`.
- [ ] Button: `setBackgroundTintList`.

## Phase 3: ColorStateList DSL

### DSL (`dsl/widgets.py` or `dsl/colors.py`)
- [ ] Add `ColorState(default=..., pressed=..., disabled=..., selected=..., focused=...)`.
- [ ] Validate allowed keys: `default`, `pressed`, `disabled`, `selected`, `focused`.
- [ ] Deterministic state ordering for emitted arrays.

### Lowering (`dsl/lowering/context.py`)
- [ ] Convert `ColorState` to `ColorStateList`.
- [ ] Support `ColorState` in `text_color`.
- [ ] Support `ColorState` in `background`/tint channels.
- [ ] Support `ColorState` in progress/tint fields.

## Phase 4: Event Surface Expansion

### DSL API (`dsl/app.py`, `dsl/widgets.py`)
- [ ] Add `on_change`.
- [ ] Add `on_text_change`.
- [ ] Add `on_item_selected`.
- [ ] Add `on_menu_item_selected`.
- [ ] Add `on_focus_change`.

### Lowering (`dsl/lowering/context.py`, support listener classes)
- [ ] Slider -> `OnSeekBarChangeListener`.
- [ ] Switch/Checkbox -> `OnCheckedChangeListener`.
- [ ] RadioGroup -> `OnCheckedChangeListener`.
- [ ] TextField -> `TextWatcher`.
- [ ] Dropdown -> `OnItemSelectedListener`.
- [ ] PopupMenu -> `OnMenuItemClickListener`.

### Constraints
- [ ] Named handlers only.
- [ ] Compile-time ID validation.
- [ ] No dynamic registration at runtime.

## Phase 5: Input Configuration

### DSL (`dsl/widgets.py`)
- [ ] Add TextField fields: `input_type`, `ime_options`, `max_length`, `single_line`, `password`, `auto_capitalize`, `numeric_only`.

### Lowering (`dsl/lowering/context.py`)
- [ ] `setInputType`.
- [ ] `setImeOptions`.
- [ ] `setFilters`.
- [ ] `setSingleLine`.
- [ ] `setTransformationMethod`.

## Phase 6: Accessibility

### DSL (`dsl/widgets.py`)
- [ ] Add `content_description`.
- [ ] Add `important_for_accessibility`.
- [ ] Add `accessibility_label` alias.

### Lowering (`dsl/lowering/context.py`)
- [ ] `setContentDescription`.
- [ ] `setImportantForAccessibility`.

## Phase 7: Elevation and Shadow

### DSL (`dsl/widgets.py`)
- [ ] Add `elevation`.
- [ ] Add `pressed_elevation`.
- [ ] Add `text_shadow_color`.
- [ ] Add `text_shadow_radius`.
- [ ] Add `text_shadow_dx`.
- [ ] Add `text_shadow_dy`.

### Lowering (`dsl/lowering/context.py`)
- [ ] `setElevation`.
- [ ] Text-only `setShadowLayer`.
- [ ] Optional pressed elevation animation path (explicit only).

### Coverage
- [ ] Card
- [ ] Button
- [ ] Container
- [ ] AppBar
- [ ] Text

## Phase 8: Visual Effects Pack v1

### 8.1 Opacity
- [ ] Add `opacity`.
- [ ] Lower to `setAlpha`.

### 8.2 Border
- [ ] Add `border_width`.
- [ ] Add `border_color`.
- [ ] Add `border_radius` (allow per-corner model).
- [ ] Lower via `GradientDrawable` stroke.

### 8.3 Gradient Background
- [ ] Add `Gradient(start, end, direction)`.
- [ ] Lower to `GradientDrawable` gradients.

### 8.4 Ripple
- [ ] Add `ripple_color`.
- [ ] Lower to `RippleDrawable`.

### 8.5 Clip and Outline
- [ ] Add `clip_to_outline`.
- [ ] Add `clip_children`.
- [ ] Lower to `setClipToOutline` / `setClipChildren`.

### 8.6 Blur (API 31+)
- [ ] Add `blur_radius`.
- [ ] Lower to `RenderEffect.createBlurEffect`.
- [ ] Warn at compile time when `min_sdk < 31`.

### 8.7 Static Transforms
- [ ] Add `rotation`.
- [ ] Add `scale_x`.
- [ ] Add `scale_y`.
- [ ] Add `translation_x`.
- [ ] Add `translation_y`.
- [ ] Lower to corresponding view setters.

## Phase 9: Explicit Animation DSL (Imperative Only)

### DSL (`dsl/app.py` or `dsl/animation.py`)
- [ ] Add `animate(id, ...)`.
- [ ] Add helpers: `fade_in`, `fade_out`, `rotate`, `scale`, `translate`, `animate_elevation`.
- [ ] Add composition helpers: `sequence(...)`, `parallel(...)`.

### Supported Properties
- [ ] `rotate`
- [ ] `scale`
- [ ] `scale_x`
- [ ] `scale_y`
- [ ] `translate_x`
- [ ] `translate_y`
- [ ] `alpha`
- [ ] `elevation`

### Common Params
- [ ] `duration`
- [ ] `delay`
- [ ] `interpolator`

### Lowering
- [ ] `ViewPropertyAnimator`.
- [ ] `ObjectAnimator`.
- [ ] `AnimatorSet`.

### Navigation Transitions
- [ ] Add `Screen(..., transition=...)`.
- [ ] Support `fade`, `slide_left`, `slide_right`, `slide_up`, `slide_down`.
- [ ] Lower to predefined animator methods.

### Forbidden (must stay forbidden)
- [ ] No state-bound implicit animations.
- [ ] No diff-based recomposition.
- [ ] No reactive animation runtime.

## Phase 10: Theme Expansion

### Theme Channels (`dsl/widgets.py`)
- [ ] Add `input`.
- [ ] Add `selector`.
- [ ] Add `progress`.
- [ ] Add `icon`.
- [ ] Add `container`.
- [ ] Add `appbar`.

### Resolution Order
- [ ] Enforce `inline attrs > style= > Theme channel > widget defaults`.
- [ ] Add lint/tests for deterministic precedence.

## Phase 11: Scroll Controls

### DSL and Validation
- [ ] Add `ScrollView`.
- [ ] Add `HorizontalScrollView`.
- [ ] Enforce single direct child at compile time.

### Lowering
- [ ] Emit corresponding widget constructors and layout wiring.

## Phase 12: RecyclerView (Static v1)

### DSL
- [ ] Add `ListView(items=[...], item_layout=...)` static-only shape.

### Lowering
- [ ] Deterministic adapter class generation.
- [ ] Stable view holder + bind logic.
- [ ] Compile-time-only dataset (no runtime diffing).

## Phase 13: Validation and Linting

### Compile-time Checks
- [ ] Style field incompatible with widget.
- [ ] Invalid state keys.
- [ ] Unsupported event binding target.
- [ ] Duplicate IDs.
- [ ] Animation target ID not found.
- [ ] Blur below API 31.
- [ ] Invalid gradient config.

### Diagnostics
- [ ] Error messages with widget id and field name.
- [ ] Warnings for degraded fallback behavior.

## Non-Goals (Locked)

- [ ] No reactive hooks.
- [ ] No CSS-style cascade engine.
- [ ] No dynamic theme switching in v1.
- [ ] No shader DSL in v1.
- [ ] No runtime layout diffing/recomposition.

## Execution Order (Recommended)

- [ ] Wave A: Phases 1, 2, 3 (style primitives + state colors).
- [ ] Wave B: Phases 4, 5, 6 (events + input + accessibility).
- [ ] Wave C: Phases 7, 8 (visual polish primitives).
- [ ] Wave D: Phase 9 (explicit animation layer).
- [ ] Wave E: Phases 10, 11, 12, 13 (theme expansion + containers + validation hardening).
