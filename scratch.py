from dsl.app import app, activity, ui, on_click, run
from dsl.widgets import (
    max_width,
    State,
    Text,
    Button,
    Row,
    Column,
    AppBar,
    FloatingActionButton,
    RaisedButton,
    FlatButton,
    IconButton,
    TextField,
    Checkbox,
    Radio,
    Switch,
    Slider,
    DropdownButton,
    ButtonBar,
    PopupMenuButton,
    Theme,
    Style,
    presets,
)
from dsl.colors import colors


@on_click("inc")
def increment():
    count += step
    label.text = f"Count: {count}"


@on_click("dec")
def decrement():
    count = count - 1
    label.text = f"Count: {count}"


@on_click("fab")
def fab_click():
    # toast("FAB clicked!")
    snackbar("hello") # Fallback into toast.. TODO snackbar - needs Material.


@on_click("menu")
def menu_click():
    simple_dialog("Menu", "Popup menu clicked")


app_spec = app(
    activity(
        "MainActivity",
        Theme(
            palette={
                "bg": colors.zinc_100,
                "card": colors.white,
                "primary": colors.blue_600,
                "danger": colors.red_500,
                "text": colors.slate_900,
                "muted": colors.slate_500,
                "on_primary": colors.white,
                "on_danger": colors.white,
            },
            text=Style(text_color="text", text_size=16),
            button=Style(text_color="on_primary", text_size=16, radius=16),
            row=Style(background="card", radius=16),
            column=Style(background="card", radius=12),
        ),
        State(
            count=0,
            step=1,
        ),
        ui(
            # ── AppBar ─────────────────────────────
            AppBar(
                "Anali Widget Zoo",
                id="appbar",
                style=presets().Card(padding=(16, 16, 16, 16)),
            ),

            # ── Text ───────────────────────────────
            Text(
                "Counter demo",
                id="label",
                padding=(16, 16, 16, 16),
                style=presets().MutedText(text_size=30),
            ),

            # ── Buttons Row ────────────────────────
            Row(
                Button("+", id="inc", style=presets().PrimaryButton()), # when max width is given, this button takes entire row - leaving the dec button not visible
                Button("-", id="dec", style=presets().DangerButton(), width = max_width), # When only max_width is given to dec button, both buttons are visible in the row, but dec button spans more than inc button along the row
            
                id="counter_row",
                width=max_width,
                margin=(0, 0, 0, 16),
                style=presets().Card(padding=(8, 8, 8, 8)),
            ),

            # ── Button Variants ────────────────────
            Row(
            Column(
                RaisedButton("Raised", id="raised", style=presets().PrimaryButton(), width=max_width),
                FlatButton("Flat"),
                IconButton("★", width=max_width),
                id="button_variants",
                margin=(0, 0, 0, 16),
                style=presets().Card(padding=(12, 12, 12, 12)),
            )),

            # ── TextField ──────────────────────────
            TextField(
                "",
                id="input",
                hint="Type something",
                margin=(0, 0, 0, 16),
            ),

            # ── Check / Radio / Switch ─────────────
            Row(
            Column(
                Checkbox("Check me", checked=True),
                Radio("Select me", checked=False),
                Switch("Toggle me", checked=True),
                id="toggles",
                margin=(0, 0, 0, 16),
                style=presets().Card(padding=(12, 12, 12, 12)),
            )),

            # ── Slider ─────────────────────────────
            Slider(
                id="slider",
                min=0,
                max=100,
                value=42,
                margin=(0, 0, 0, 16),
            ),

            # ── Dropdown + Popup ───────────────────
            Row(
                DropdownButton(
                    id="dropdown",
                    items=["One", "Two", "Three"],
                ),
                PopupMenuButton(
                    "Menu",
                    id="menu",
                    items=["A", "B", "C"],
                ),
                id="menus",
                margin=(0, 0, 0, 16),
            ),

            # ── ButtonBar ──────────────────────────
            ButtonBar(
                Button("OK"),
                Button("Cancel"),
                id="button_bar",
                margin=(0, 0, 0, 16),
            ),

            # ── Footer Text ────────────────────────
            Text(
                "Snackbar + Toast demo",
                id="footer_text",
                text_color="muted",
                style=presets().MutedText(text_size=14),
            ),

            # ── Floating Action Button ─────────────
            FloatingActionButton(
                "+",
                id="fab",
            ),
        ),
        increment,
        decrement,
        fab_click,
        menu_click,
    )
)


if __name__ == "__main__":
    run(app_spec)
