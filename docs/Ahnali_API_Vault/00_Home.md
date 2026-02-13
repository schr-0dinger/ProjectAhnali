---
tags: [ahnali, api, docs, vault]
---

# Ahnali Getting Started + API Documentation (Code Reality)

This vault is generated from the current repository implementation and tests.
It documents the native/core DSL surface (Material plugin is paused and not part of default runtime behavior).

## Read This First

- [[01_Getting_Started]]
- [[02_App_Model_and_Build_Run]]
- [[03_Value_Types_and_Units]]

## API Reference (Classified)

- [[04_Shared_Attributes]]
- [[05_Structure_Components]]
- [[06_Content_and_Display_Components]]
- [[07_Input_and_Selection_Components]]
- [[08_Feedback_and_Utility_Components]]
- [[09_Theme_Style_and_Presets]]
- [[10_Events_and_Handler_DSL]]
- [[11_Navigation_State_and_Screens]]
- [[12_Animation_DSL]]
- [[13_Validation_and_Diagnostics]]
- [[14_Component_Attribute_Matrix]]

## Quick Reality Snapshot

- Deterministic AOT lowering pipeline is active.
- Named static handlers are required.
- `style=` + `Theme(...)` precedence is implemented.
- Phase 1..13 features are implemented in core path, with two known practical gaps:
  - Dropdown text surface coverage is still pending.
  - Popup menu item text surface coverage is still pending.
- `ColorState` background currently applies default color for fill and emits a lint warning for fallback behavior.

## Scope Notes

- This vault documents APIs in `dsl/widgets.py`, `dsl/api.py`, parser/AST behavior, and lowering/validation rules in `dsl/lowering/context.py`.
- Examples are Pythonic DSL examples intended for direct app scripts.
