---
tags: [ahnali, getting-started]
---

	# Getting Started

Back to: [[00_Home]]

## 1. Minimal App

```python
from dsl.app import app, activity, ui, text

app_spec = app(
    activity(
        "MainActivity",
        ui(
            text("Hello Ahnali", id="title"),
        ),
    )
)

app_spec.run()
```

## 2. Add State + Event

```python
from dsl.app import app, activity, ui, state, text, button, on_click

@on_click("inc")
def handle_inc():
    counter = counter + 1
    label.text = f"Count: {counter}"

app_spec = app(
    activity(
        "MainActivity",
        state(counter=0),
        ui(
            text("Count: 0", id="label"),
            button("+", id="inc"),
        ),
        handle_inc,
    )
)
```

## 3. Add Screens + Navigation

```python
from dsl.app import app, activity, ui, Screen, button, text, on_click, Navigate, Back

@on_click("go_details")
def go_details():
    Navigate("Details")

@on_click("go_back")
def go_back():
    Back()

app_spec = app(
    activity(
        "MainActivity",
        ui(
            Screen("Home", text("Home", id="home_title"), button("Open Details", id="go_details")),
            Screen("Details", text("Details", id="details_title"), button("Back", id="go_back"), transition="slide_left"),
        ),
        go_details,
        go_back,
    )
)
```

## 4. Add AppConfig (Including Mode)

```python
from dsl.app import app, activity, app_config, ui, text

app_spec = app(
    activity(
        "MainActivity",
        app_config(
            package="com.example.todo",
            min_sdk=21,
            target_sdk=33,
            version_code=1,
            version_name="1.0.0",
            debuggable=True,
            mode="static",  # or "reactive"
            auto_deps=False,
        ),
        ui(text("Configured", id="title")),
    )
)
```

## 5. Enable Reactive APIs (Optional)

Reactive statements/expressions require `app_config(mode="reactive")`.

```python
from dsl.app import app, activity, app_config, ui, text, button, on_click, observable, bind_text, set_observable

@on_click("run")
def run_handler():
    observable("greeting", "hello")
    bind_text("status", "greeting")
    set_observable("greeting", "world")

app_spec = app(
    activity(
        "MainActivity",
        app_config(mode="reactive"),
        ui(text("Status", id="status"), button("Run", id="run")),
        run_handler,
    )
)
```

## 6. Where to Go Next

- App model/build: [[02_App_Model_and_Build_Run]]
- Values/units/colors: [[03_Value_Types_and_Units]]
- Components: [[14_Component_Attribute_Matrix]]
