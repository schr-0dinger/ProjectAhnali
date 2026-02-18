---
tags: [ahnali, events, handlers]
---

# Events and Handler DSL

Back to: [[00_Home]]

## Event Specs

### Core

- `on_click(target_id, stmts=None)`
- `on_click_map(mapping)`
- `on_change(target_id, stmts=None)`
- `on_slider_change(target_id, stmts=None)`
- `on_text_change(target_id, stmts=None)`
- `on_item_selected(target_id, stmts=None)`
- `on_menu_item_selected(target_id, stmts=None)`
- `on_focus_change(target_id, stmts=None)`

### Extended interaction

- `on_long_click`
- `on_touch`
- `on_double_tap`
- `on_swipe`
- `on_scroll`
- `on_fling`
- `on_pinch`
- `on_zoom`
- `on_rotate_gesture`
- `on_scale_gesture_detector`
- `on_drag`
- `on_drop`
- `on_editor_action`
- `on_key`

### Lifecycle hooks

- `on_start`
- `on_resume`
- `on_pause`
- `on_stop`
- `on_destroy`

All hook helpers support decorator or explicit `stmts` usage.

## Inline Event Attributes

Widgets support inline event attrs (`on_click=...`, `on_change=...`, etc.).

Rules:
- inline + explicit duplicate binding for same canonical slot is rejected
- alias collisions are normalized deterministically:
  - touch-family events share one touch listener slot per target
  - `drop` shares drag slot with `drag`
  - `slider_change` shares change slot semantics

## Target Type Constraints

- `on_click`: `button`, `raised_button`, `flat_button`, `icon_button`, `fab`, `popup_button`
- `on_change`: `checkbox`, `switch`, `radio`, `slider`, `radio_group`
- `on_slider_change`: `slider` only
- `on_text_change` / `on_editor_action`: `text_field` only
- `on_item_selected`: `dropdown` only
- `on_menu_item_selected`: `popup_button` only
- all targets must exist in `ui(...)`

## Supported Handler Statements (Parser Path)

Supported statement families include:
- assignment and augmented assignment (`x = ...`, `x += 1`)
- view text set (`label.text = ...`)
- `if`/`else`, `while`
- feedback: `toast`, `snackbar`, `simple_dialog`, `log`, `exit_app`
- navigation: `Navigate`, `Back`, `Replace`, `PopToRoot`, `ClearStack`
- animation: `animate`, helpers, `sequence`, `parallel`
- permission/capability helpers
- web/notification/http helpers
- storage + backend helpers (`datastore_*`, `file_*`, `sqlite_*`, `room_*`, `encrypted_*`, `secure_*`)
- reactive helpers (`observable`, `set_observable`, `derived`, `listen`, `bind_text`) when app mode is reactive

## Expression Support (Parser Path)

Supported expression families include:
- constants, symbols
- binary math/comparisons/boolean ops/unary ops
- f-strings (limited lowering)
- capability expressions (`permission_granted`, `clipboard_get`, `notify_result/error`, web result/error helpers)
- HTTP expressions (`http_get*`, async token expressions)
- storage/backend expressions (`storage_get/exists`, backend `get/exists`)
- reactive expression `observable_get` (reactive mode)

## Notes

- handler parser is intentionally constrained for deterministic lowering.
- many capability/helper call arguments are required to be compile-time constants in parser path.
- runtime dynamic callback registration is not part of this model.

See also:
- [[08_Feedback_and_Utility_Components]]
- [[11_Navigation_State_and_Screens]]
