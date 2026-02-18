---
tags: [ahnali, api, docs, vault]
---

# Ahnali Getting Started + API Documentation (Code Reality)

This vault reflects the current repository implementation in `dsl/api.py`, `dsl/widgets.py`, parser/lowering behavior, and active tests.

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
- App modes are real: `app_config(mode="static")` (default) and `app_config(mode="reactive")`.
- Inline widget events are supported (`on_click=...`, `on_change=...`, etc.) and merged with explicit event specs.
- Style precedence is deterministic: `inline attrs > style= > Theme channel > widget defaults`.
- Navigation stack ops include `Navigate`, `Back`, `Replace`, `PopToRoot`, `ClearStack`.
- Program 1..13 surfaces are active in core path, including async HTTP, WebView helpers, notifications, clipboard/share, and multi-backend state APIs.

## Known Practical Gaps

- Dropdown text-typography surface is still partial.
- Popup menu item text-typography surface is still partial.
- Background `ColorState` currently uses default color for fill (with lint fallback warning).

## Scope Notes

- This vault documents APIs in `dsl/widgets.py`, `dsl/api.py`, parser behavior (`dsl/parser.py`), and lowering/validation rules (`dsl/lowering/context.py`).
- Material plugin is not the default path; docs focus on core/native surface.
