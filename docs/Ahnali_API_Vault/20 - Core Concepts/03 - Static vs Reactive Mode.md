---
tags: [ahnali, modes, static, reactive]
---

# Static vs Reactive Mode

> [!abstract] Two modes, one compiler
> Static is the default and the identity of Ahnali. Reactive is opt-in and bounded. Neither mode changes how the other works.

## Static mode (default)

This is what Ahnali is. Everything is resolved at compile time:

- UI structure - which widgets exist, where they are, how they're styled
- Navigation graph - which screens exist, how they connect, what transitions they use
- Event handlers - what happens when you tap a button
- State wiring - which fields exist, how they're read and written
- Capability calls - which platform services are used

The resulting APK has no interpreter, no runtime UI tree builder, no dynamic dispatch. It's just Smali that talks to Android.

```python
app(
    activity("Main",
        ui(text("Hello", id="greeting")),
        # everything above is compiled, nothing is interpreted
    ),
)
```

## Reactive mode (opt-in)

Sometimes you need the UI to respond to state changes without writing explicit `widget.text = ...` assignments. Reactive mode gives you that - but you have to explicitly ask for it.

```python
app(
    activity("Main",
        app_config(mode="reactive"),
        ui(text("Hello", id="greeting")),
        on_click("btn", [
            observable("msg", "hello"),
            bind_text("greeting", "msg"),
            set_observable("msg", "world"),
        ]),
    ),
)
```

What reactive gives you:
- `observable(name, value)` - declare a reactive variable
- `set_observable(name, value)` - update it
- `bind_text(widget_id, observable_name)` - wire a widget's text to an observable
- `derived(name, fn)` - computed values
- `listen(name, handler)` - react to changes

> [!important] What reactive does NOT do
> - No dynamic widget creation or destruction
> - No runtime UI tree diffing
> - No implicit observer graph
> - No hidden mutation layer
> - No change to static mode behavior

## Guardrails

The compiler enforces the boundary between modes:

- If you use a reactive API in static mode, you get `[ReactiveModeError]` at compile time
- Static apps are completely unaffected by reactive mode existing
- The ABI snapshot includes a reactive surface snapshot to catch symbol drift

## When to use which

**Static mode** for the vast majority of apps. If you can describe your UI and its behavior at compile time (and you usually can), use static.

**Reactive mode** when you have UI elements that need to update frequently based on state changes and you don't want to write explicit update code for each one. Think live search results, real-time status displays, that sort of thing.

## Learn more

- How Ahnali works: [[20 - Core Concepts/01 - How Ahnali Works]]
- State management: [[20 - Core Concepts/05 - State Management]]
- Design philosophy: [[20 - Core Concepts/06 - Design Philosophy]]
