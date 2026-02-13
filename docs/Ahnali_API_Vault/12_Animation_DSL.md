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

Supported normalized keys:
- `rotate`
- `scale` (expands to `scale_x` + `scale_y`)
- `scale_x`
- `scale_y`
- `translate_x`
- `translate_y`
- `alpha`
- `elevation`

Property aliases are normalized from user-friendly names.

## Timing Fields

- `duration`: numeric (cast to integer milliseconds)
- `delay`: numeric (cast to integer milliseconds)
- `interpolator`: string

Interpolators:
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
    animate(
        "card",
        alpha=0.6,
        rotate=15,
        duration=180,
        delay=20,
        interpolator="linear",
    )
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

Screen transitions are independent from handler animation calls.
Both are explicit and deterministic.

See also:
- [[10_Events_and_Handler_DSL]]
- [[11_Navigation_State_and_Screens]]
