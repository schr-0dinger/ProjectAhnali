---
tags: [ahnali, api-reference, events, handlers, decorators, inline]
---

# 09 — Events and Handlers

> [!abstract] What this covers
> All event decorators, inline event attributes, target type constraints, and the handler action statements available inside event handlers.

Related: [[03 - Shared Attributes]] · [[07 - Feedback and Utility]] · [[10 - Navigation and Screens]] · [[11 - Animation DSL]]

---

## Event Decorators

Every event decorator requires a **named handler function**. The decorator form is:

```python
@on_click("target_id")
def handler_name():
    # handler body
```

### Core Events

| Decorator | Signature | Typical Targets |
|---|---|---|
| `on_click` | `on_click(target_id, stmts=None)` | Buttons, popup menus |
| `on_change` | `on_change(target_id, stmts=None)` | Checkbox, Switch, Radio, Slider, RadioGroup |
| `on_slider_change` | `on_slider_change(target_id, stmts=None)` | Slider only |
| `on_text_change` | `on_text_change(target_id, stmts=None)` | TextField |
| `on_item_selected` | `on_item_selected(target_id, stmts=None)` | DropdownButton |
| `on_menu_item_selected` | `on_menu_item_selected(target_id, stmts=None)` | PopupMenuButton |
| `on_focus_change` | `on_focus_change(target_id, stmts=None)` | Focusable widgets |

### Extended Interaction Events

| Decorator | Purpose |
|---|---|
| `on_long_click` | Long press |
| `on_touch` | Raw touch events |
| `on_double_tap` | Double tap gesture |
| `on_swipe` | Swipe gesture |
| `on_scroll` | Scroll events |
| `on_fling` | Fling gesture |
| `on_pinch` | Pinch gesture |
| `on_zoom` | Zoom gesture |
| `on_rotate_gesture` | Rotate gesture |
| `on_scale_gesture_detector` | Scale gesture |
| `on_drag` | Drag events |
| `on_drop` | Drop events (shares drag slot with `on_drag`) |
| `on_editor_action` | IME action (TextField) |
| `on_key` | Key events |

### Lifecycle Hooks

| Decorator | Fires When |
|---|---|
| `on_start` | Activity starts |
| `on_resume` | Activity resumes |
| `on_pause` | Activity pauses |
| `on_stop` | Activity stops |
| `on_destroy` | Activity is destroyed |

All hook helpers support both decorator and explicit `stmts` usage.

---

## Inline Event Attributes

Widgets support inline event attrs as constructor kwargs (Group I):

```python
button("Save", id="save_btn", on_click=toast("Saved!"))
checkbox("Remember me", id="remember", on_change=log("changed"))
text_field(id="search", on_text_change=log("typing"))
```

> [!warning] Inline + explicit duplicate binding is rejected
> If you bind both an inline attribute and an explicit decorator to the same widget and canonical slot, the compiler rejects it.

### Alias Normalization

The compiler normalizes alias collisions deterministically:

- Touch-family events (`on_touch`, `on_double_tap`, etc.) share one touch listener slot per target
- `on_drop` shares the drag slot with `on_drag`
- `on_slider_change` shares change slot semantics with `on_change`

---

## Target Type Constraints

> [!important] Not every event works on every widget
> The compiler validates that the target widget type supports the event kind.

| Event | Valid Target Types |
|---|---|
| `on_click` | `button`, `raised_button`, `flat_button`, `icon_button`, `fab`, `popup_button` |
| `on_change` | `checkbox`, `switch`, `radio`, `slider`, `radio_group` |
| `on_slider_change` | `slider` only |
| `on_text_change` / `on_editor_action` | `text_field` only |
| `on_item_selected` | `dropdown` only |
| `on_menu_item_selected` | `popup_button` only |

> [!note] All targets must exist
> Every target ID referenced in an event spec must resolve to a widget defined in `ui(...)`. Unknown targets fail at compile time.

---

## Handler Actions

Inside handler bodies, you can use these statement families:

### Feedback

| Statement | Effect |
|---|---|
| `toast("msg")` | Show toast |
| `snackbar("msg")` | Show snackbar |
| `simple_dialog("title", "msg")` | Show dialog |
| `log("msg")` | Log to console |
| `exit_app()` | Terminate app |

### Navigation

| Statement | Effect |
|---|---|
| `Navigate("ScreenName")` | Push screen onto stack |
| `Back()` | Pop current screen |
| `Replace("ScreenName")` | Replace current screen |
| `PopToRoot()` | Pop to first screen |
| `ClearStack()` | Clear all screens |

### Animation

| Statement | Effect |
|---|---|
| `animate("target", ...)` | Animate a widget property |
| `fade_in("target", ...)` | Fade in helper |
| `fade_out("target", ...)` | Fade out helper |
| `rotate("target", value, ...)` | Rotation helper |
| `scale("target", value, ...)` | Scale helper |
| `translate("target", x, y, ...)` | Translation helper |
| `sequence(...)` | Sequential animation group |
| `parallel(...)` | Parallel animation group |

### State and Logic

- Assignment and augmented assignment: `x = ...`, `x += 1`
- View property set: `label.text = ...`
- `if` / `else`, `while`
- Observable helpers (reactive mode): `observable`, `set_observable`, `bind_text`, `derived`, `listen`

### Capabilities

- Permission checks: `check_permission`, `request_permission`
- HTTP: `http_get`, `http_get_route`, `http_get_route_async`
- Storage: `storage_put`, `storage_get`, backend-specific helpers
- WebView: `web_load`, `web_add_js_bridge`
- Notifications: `notify`, `create_notification_channel`
- Clipboard: `clipboard_set`, `clipboard_get`
- Sharing: `share_text`

---

## Expression Support

The handler parser supports these expression families:

- Constants and symbols
- Binary math, comparisons, boolean ops, unary ops
- F-strings (limited lowering)
- Capability expressions: `permission_granted`, `clipboard_get`, `notify_result/error`, web result/error
- HTTP expressions: `http_get*`, async token expressions
- Storage/backend expressions: `storage_get/exists`, backend `get/exists`
- Reactive expressions: `observable_get` (reactive mode only)

---

## Constraints

> [!warning] Handler parser is intentionally constrained
> - Many capability helper arguments must be compile-time constants
> - Runtime dynamic callback registration is not part of this model
> - The parser ensures deterministic lowering to Smali

See [[20 - Core Concepts/02 - Compiler Pipeline]] for how handlers flow through the compilation stages.

---

## See Also

- [[07 - Feedback and Utility]] — toast, snackbar, dialog, exit_app
- [[10 - Navigation and Screens]] — Navigate, Back, Replace, PopToRoot, ClearStack
- [[11 - Animation DSL]] — animate, sequence, parallel
- [[12 - Validation and Diagnostics]] — event binding validation
- [[13 - Component Attribute Matrix]] — which components support inline events
