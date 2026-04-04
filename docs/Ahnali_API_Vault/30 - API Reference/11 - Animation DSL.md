---
tags: [ahnali, api, animation]
---

# Animation DSL

> [!abstract] Explicit and imperative
> All animations in Ahnali are explicit — you say what animates, how, and when. No state-bound implicit animations, no diff-based recomposition.

## Basic animations

```python
animate("my_button", rotate=360, duration=500)
animate("my_image", alpha=0.0, duration=300, delay=100)
```

The first argument is always the widget ID. The compiler validates that the target exists.

## Animation helpers

Shorthand helpers for common patterns:

```python
fade_in("label", duration=400)
fade_out("label", duration=400)
rotate("icon", degrees=360, duration=500)
scale("card", x=1.2, y=1.2, duration=200)
translate("fab", x=0, y=-100, duration=300)
animate_elevation("card", elevation=8, duration=200)
```

## Composition

Chain animations with `sequence` (one after another) or `parallel` (all at once):

```python
sequence([
    fade_in("title", duration=300),
    parallel([
        translate("subtitle", y=20, duration=400),
        fade_in("subtitle", duration=400),
    ]),
])
```

## Properties

| Property | Range | Notes |
|---|---|---|
| `rotate` | degrees | Full rotation supported |
| `scale` | float | Uniform scale |
| `scale_x` | float | Horizontal only |
| `scale_y` | float | Vertical only |
| `translate_x` | px | Horizontal translation |
| `translate_y` | px | Vertical translation |
| `alpha` | 0.0–1.0 | Opacity |
| `elevation` | px | Shadow depth |

## Common params

Every animation accepts:

- `duration` — milliseconds
- `delay` — milliseconds before starting
- `interpolator` — easing curve (`linear`, `accelerate`, `decelerate`, `accelerate_decelerate`, `bounce`, `overshoot`, `anticipate`, `anticipate_overshoot`)

## Navigation transitions

Screens support a `transition` parameter that animates the screen enter/exit:

```python
Screen("Details",
    text("Details", id="details_title"),
    transition="slide_left",
)
```

Supported transitions: `fade`, `slide_left`, `slide_right`, `slide_up`, `slide_down`.

## How it lowers

Animations compile to:

- **`ViewPropertyAnimator`** — simple single-property animations
- **`ObjectAnimator`** — multi-property and custom property animations
- **`AnimatorSet`** — composition (sequence/parallel)

Everything is imperative. The compiler generates the animator setup code, wires it to the right widget by ID, and emits it into the handler.

> [!important] What animations don't do
> - No state-bound implicit animations (changing a value doesn't automatically animate)
> - No diff-based recomposition (there's no runtime comparing old vs new state)
> - No reactive animation runtime (animations don't observe anything)
>
> If you want something to animate, you call the animation function. Period.

## Learn more

- Events and handlers: [[30 - API Reference/09 - Events and Handlers]]
- Navigation and screens: [[30 - API Reference/10 - Navigation and Screens]]
- Validation checks: [[30 - API Reference/12 - Validation and Diagnostics]]
