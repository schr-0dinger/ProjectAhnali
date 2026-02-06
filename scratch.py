from dsl.app import app, activity, state, ui, text, button, on_click, run

app_spec = app(
    activity(
        "MainActivity",
        state(count=0),
        ui(
            text("Count: 0", id="label"),
            button("+", id="inc"),
            button("-", id="dec"),
        ),
        on_click("inc", [
            "count += 1",
            "label.text = f'Count: {count}'",
        ]),
        on_click("dec", [
            "count -= 1",
            "label.text = f'Count: {count}'",
        ]),
    )
)

if __name__ == "__main__":
    run(app_spec)
