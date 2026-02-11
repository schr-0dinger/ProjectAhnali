from dsl.app import app, activity, ui, button, on_click, request_permissions


@on_click("ask")
def ask():
    request_permissions("CAMERA")


def test_request_permissions_infers_permission():
    prog = app(
        activity(
            "MainActivity",
            ui(button("Ask", id="ask")),
            ask,
        )
    )
    built = prog.build()
    assert "android.permission.CAMERA" in (built.permissions or [])
