---
tags: [anali, validation, lint]
---

# Validation and Diagnostics

Back to: [[00_Home]]

This note summarizes the major compile-time checks currently enforced.

## Identity and Structure

- duplicate widget ids are rejected (default ids may auto-suffix with warning in specific cases)
- widget id reuse across multiple screens is rejected
- unknown target ids in events/animation/constraints are rejected
- `ui(...)` cannot mix `Screen(...)` and non-screen top-level entries
- duplicate screen names are rejected

## Style Compatibility

- incompatible style fields on widget kind are rejected
- style compatibility is checked for both `style=` and Theme channel application

## State Validation

- invalid state key name patterns are rejected
- reserved runtime names are rejected
- collisions with generated view fields are rejected
- non-integer state literal values are rejected

## Event Binding Validation

- unsupported event kind -> rejected
- event target kind mismatch -> rejected
- malformed event specs -> rejected

## Input Validation

- invalid `input_type` / `ime_options` / `auto_capitalize`
- invalid `max_length` (must be integer >= 0)
- bool/type violations for strict fields

## Layout and Visual Validation

- invalid `layout` forms
- invalid spacing forms (`padding`/`margin`)
- invalid gravity values
- invalid relative rule or constraint forms
- invalid gradient config (direction/color)
- invalid opacity range
- invalid border config
- invalid transform numeric values
- `clip_children` only for container widget kinds

## ListView Validation

- `items` must be static primitive list/tuple
- unsupported symbolic `item_layout` rejected
- current deterministic adapter lowering supports `simple_list_item_1` path

## Animation Validation

- unsupported properties/interpolators rejected
- unknown animation target id rejected
- empty animation group rejected
- non-numeric duration/delay/property values rejected

## Warnings (Degraded but Deterministic)

Current warning patterns include:
- style precedence overlap warnings:
  - inline + style/theme overlap
- blur skipped warning:
  - `blur_radius` ignored when `min_sdk < 31`
- background ColorState fallback warning:
  - only default color used for background fill
- default border width warning:
  - if border color is set without border width
- duplicate default id auto-suffix warning

## Non-goals Enforced by Design

- no reactive runtime hooks
- no runtime diff/recomposition system
- no dynamic callback registration model

See also:
- [[04_Shared_Attributes]]
- [[10_Events_and_Handler_DSL]]
