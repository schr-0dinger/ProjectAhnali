---
tags: [ahnali, validation, lint]
---

# Validation and Diagnostics

Back to: [[00_Home]]

This note summarizes major compile-time checks enforced by current lowering/parser.

## Identity and Structure

- duplicate widget ids are rejected (default-like ids may auto-suffix with warning)
- widget id reuse across screens is rejected
- unknown target ids in events/animation/constraints are rejected
- `ui(...)` cannot mix `Screen(...)` and non-screen top-level entries
- duplicate screen names are rejected
- strict child-count rules on structural widgets (`ScrollView`, `DrawerLayout`, `FragmentContainer`, etc.)

## Style Compatibility and Visual Validation

- incompatible style fields per widget kind are rejected
- invalid `layout` / spacing / gravity / relative / constraint forms are rejected
- invalid color/gradient/border/opacity/transform values are rejected
- `clip_children` only valid on container-like widgets
- `text_size` must use `sp(...)`
- image validations (`scale_type`, `image_alpha`, `image_matrix`) are enforced

## State and App Config

- invalid state key patterns/reserved names/collisions are rejected
- non-integer state literals are rejected
- invalid `app_config(mode=...)` values are rejected

## Event Binding Validation

- unsupported event kinds are rejected
- target-kind mismatch per event is rejected
- duplicate bindings on canonical listener slots are rejected
- popup conflict: `on_menu_item_selected` cannot be combined with explicit `on_click` for same popup id

## Input Validation

- invalid `input_type` / `ime_options` / `auto_capitalize`
- invalid `max_length` (`int >= 0`)
- strict bool checks for fields like `single_line`, `password`, `numeric_only`, etc.

## Data/List Validation

- list/grid/recycler items must be static primitive list/tuple
- unsupported symbolic `item_layout` values are rejected
- deterministic adapter lowering currently supports `simple_list_item_1` path

## Animation Validation

- unsupported properties/interpolators rejected
- unknown animation target id rejected
- empty animation group rejected
- non-numeric duration/delay/property values rejected

## Reactive Guardrails

- reactive statements/expressions require `app_config(mode="reactive")`
- static mode emits `[ReactiveModeError]` if reactive APIs are used

## HTTP Route Guardrails

- `http_get_route` / `http_get_route_async` allowed only in click-handler context
- route target ids must point to known click handlers

## Warnings (Degraded but Deterministic)

Common warnings include:
- style precedence overlap (`inline`, `style`, and `Theme` all setting same field)
- blur skipped when `min_sdk < 31`
- background `ColorState` default-only fallback behavior
- default border width fallback when color is set without explicit width
- duplicate default id auto-suffix
- global-state-across-screens warning

See also:
- [[04_Shared_Attributes]]
- [[10_Events_and_Handler_DSL]]
