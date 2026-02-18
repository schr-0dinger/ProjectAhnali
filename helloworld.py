from dsl.app import ui, app, activity, text

APP_PACKAGE = "com.ahnali.helloworld"
APP_MIN_SDK = 21
APP_TARGET_SDK = 34
APP_LABEL = "Ahnali Hello World"

app_spec = app(
    activity(
        "MainActivity",
        ui(
            text("Hello Ahnali", id="title")
        ),
    )
)

app_spec.run()