---
tags: [ahnali, animation]
---

# Animation DSL (Explicit/Imperative)

Back to: [[00_Home]]

## Core API

- `animate(target, property_name=None, value=None, *, duration=None, delay=None, interpolator=None, **properties)`
- helpers:
  - `fade_in(target, ...)`
  - `fade_out(target, ...)`
  - `rotate(target, value, ...)`
  - `scale(target, value=None, *, x=None, y=None, ...)`
  - `translate(target, x=None, y=None, ...)`
  - `animate_elevation(target, value, ...)`
- composition:
  - `sequence(*animations)`
  - `parallel(*animations)`

## Animatable Properties

Normalized property keys:
- `rotate` (`rotation` alias)
- `scale` (expands to both axes)
- `scale_x`, `scale_y` (`scalex`/`scaley` aliases)
- `translate_x`, `translate_y` (`translation_x`/`translation_y` aliases)
- `alpha`
- `elevation`

## Timing and Interpolators

- `duration`: numeric -> int ms
- `delay`: numeric -> int ms
- `interpolator`:
  - `linear`
  - `accelerate` (`ease_in` alias)
  - `decelerate` (`ease_out` alias)
  - `accelerate_decelerate` (`ease_in_out` alias)

## Validation Rules

- unknown property -> compile-time error
- non-numeric property value -> error
- unknown target id -> error
- empty animation/group -> error
- unsupported interpolator -> error

## Example: Direct Animate

```python
@on_click("animate")
def do_animate():
    animate("card", alpha=0.6, rotate=15, duration=180, delay=20, interpolator="linear")
    animate_elevation("card", 8, duration=180)
```

## Example: Sequence + Parallel

```python
@on_click("go")
def do_grouped():
    sequence(
        fade_in("card", duration=120),
        parallel(
            translate("card", x=24, duration=180),
            scale("card", value=1.15, duration=180),
        ),
    )
```

## Navigation Transition Interplay

Screen transitions from `Screen(..., transition=...)` are separate from explicit handler animations.

See also:
- [[10_Events_and_Handler_DSL]]
- [[11_Navigation_State_and_Screens]]
