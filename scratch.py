import dsl.app as A
from apk.toolchain import build_install_run


# Minimal user-facing code:
# - Create one activity
# - Add a text view
# - Add a button
# - On click: update text (stateful increment not supported yet)

app = (
    A.simple_activity()
    .counter(0)
    .button("Tap")
    .on_click_increment("button")
)

if __name__ == "__main__":
    build_install_run(app.build())
