from dsl.app import app, activity, ui, on_click, run, app_config
from dsl.widgets import (
    State,
    Text,
    Button,
    Row,
    Column,
    Relative,
    Constraint,
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
    toast,
    snackbar,
    exit_app,
    simple_dialog,
)
from dsl.colors import colors
import os

#------------------------------------------

APP_PACKAGE = "com.anali.helloworld"
APP_MIN_SDK = 21
APP_TARGET_SDK = 33
APP_VERSION_CODE = 1
APP_VERSION_NAME = "1.0"
APP_DEBUGGABLE = False
APP_SHOW_ACTION_BAR = False
APP_LABEL = "Anali App"

# Plugin list (core is always loaded)
# APP_PLUGINS = ["material"]

# APP_UNINSTALL_FIRST
# APP_OUTPUT_APK
# APP_KEYSTORE_PATH
# APP_KEYSTORE_ALIAS

#------------------------------------------

@on_click("inc")
def increment():
    count += step
    label.text = f"Count: {count}"
    if count == limit:
        snackbar("Limit reached")


@on_click("dec")
def decrement():
    count = count - 1
    label.text = f"Count: {count}"
    if count == 0:
        toast("At zero")


@on_click("reset")
def reset():
    count = 0
    label.text = f"Count: {count}"
    if count == 0 or limit == 0:
        toast("Reset")


@on_click("boost")
def boost():
    n = 0
    while n < 5:
        count += step
        n += 1
    label.text = f"Count: {count}"


@on_click("fab")
def fab_click():
    toast("FAB clicked!")


@on_click("menu")
def menu_click():
    simple_dialog("Menu", "Popup menu clicked")


@on_click("announce")
def announce_click():
    snackbar("ButtonBar action")


@on_click("exit")
def exit_click():
    exit_app()


palette = {
    "bg": colors.zinc_100,
    "card": colors.white,
    "primary": colors.blue_600,
    "danger": colors.red_500,
    "text": colors.slate_900,
    "muted": colors.slate_500,
    "on_primary": colors.white,
    "on_danger": colors.white,
}

ui_presets = presets(palette=palette)

title_style = Style(text_color="text", text_size=sp(18))

items = [
    # AppBar (inline toolbar) + title resource
    # AppBar(
    #     "Anali Widget Zoo",
    #     id="appbar",
    #     inline=True,
    #     # text_color="on_primary",
    #     # background="danger",
    #     style=ui_presets.Card(padding=(dp(16), dp(16), dp(16), dp(16))),
    # ),

    # Hero
    Text(
        "User-facing DSL",
        id="hero_title",
        padding=(dp(16), dp(12), dp(16), dp(8)),
        style=Style(text_color="text", text_size=sp(22)),
    ),
    Text(
        "Layout + widgets + state + handlers",
        id="hero_subtitle",
        padding=(dp(16), dp(0), dp(16), dp(16)),
        style=ui_presets.MutedText(text_size=sp(14)),
    ),

    # Counter card
    Column(
        Text(
            "Counter",
            id="counter_title",
            style=title_style,
        ),
        Text(
            "Count: 0",
            id="label",
            padding=(dp(0), dp(8), dp(0), dp(8)),
            style=Style(text_color="text", text_size=sp(20)),
        ),
        Row(
            Button("+", id="inc", style=ui_presets.PrimaryButton(), weight=1, width=dp(0)),
            Button("-", id="dec", style=ui_presets.DangerButton(), weight=1, width=dp(0)),
            Button("Reset", id="reset", style=ui_presets.PrimaryButton(), weight=1, width=dp(0)),
            id="counter_row",
            width=max_width,
            margin=(dp(0), dp(8), dp(0), dp(0)),
            weight_sum=3,
        ),
        Row(
            Button("Boost x5", id="boost", weight=1, width=dp(0), style=ui_presets.PrimaryButton()),
            Button("Announce", id="announce", weight=1, width=dp(0)),
            id="counter_actions",
            margin=(dp(0), dp(8), dp(0), dp(0)),
            weight_sum=2,
        ),
        id="counter_card",
        margin=(dp(16), dp(0), dp(16), dp(16)),
        style=ui_presets.Card(padding=(dp(16), dp(16), dp(16), dp(16))),
        width=max_width
    ),

    # Button variants
    Column(
        Text("Button variants", id="btn_title", style=title_style),
        RaisedButton("Raised", id="raised", style=ui_presets.PrimaryButton()),
        FlatButton("Flat", style=Style(text_color="on_primary")),
        IconButton("*", width=max_width, style=Style(background="card", radius=dp(36), text_color="text")),
        id="button_variants",
        margin=(dp(16), dp(0), dp(16), dp(16)),
        style=ui_presets.Card(padding=(dp(30), dp(30), dp(30), dp(30))),
        width=max_width
    ),

    # TextField + toggles
    TextField(
        "",
        id="input",
        hint="Type something",
        margin=(dp(16), dp(0), dp(16), dp(12)),
    ),
    Row(
        Column(
            Checkbox("Check me", checked=True),
            Radio("Select me", checked=False),
            Switch("Toggle me", checked=True),
            id="toggles",
            style=ui_presets.Card(padding=(dp(12), dp(12), dp(12), dp(12))),
        ),
        id="toggle_row",
        margin=(dp(16), dp(0), dp(16), dp(16)),
    ),

    # Slider
    Row(
        Text("Slider", id="slider_title", style=title_style),
        Slider(
            id="slider",
            min=0,
            max=100,
            value=42,
        ),
        id="slider_card",
        margin=(dp(16), dp(0), dp(16), dp(16)),
        style=ui_presets.Card(padding=(dp(30), dp(30), dp(30), dp(30))),
    ),

    # Dropdown + Popup
    Row(
        DropdownButton(
            id="dropdown",
            items=["One", "Two", "Three"],
            width=percent(50),
        ),
        PopupMenuButton(
            "Menu",
            id="menu",
            items=["A", "B", "C"],
            width=percent(50),
        ),
        id="menus",
        margin=(dp(16), dp(0), dp(16), dp(16)),
    ),

    # ButtonBar
    ButtonBar(
        Button("OK"),
        Button("Cancel"),
        Button("Exit", id="exit", style=ui_presets.DangerButton()),
        id="button_bar",
        margin=(dp(16), dp(0), dp(16), dp(16)),
    ),

    # Relative layout demo
    Relative(
        Text(
            "Relative Title",
            id="rel_title",
            relative=[("align_parent_top", "parent"), ("center_horizontal", "parent")],
            margin=(dp(0), dp(0), dp(0), dp(8)),
        ),
        Button(
            "Below Title",
            id="rel_btn",
            relative=[("below", "rel_title"), ("center_horizontal", "parent")],
        ),
        id="relative_demo",
        margin=(dp(16), dp(0), dp(16), dp(16)),
        style=ui_presets.Card(padding=(dp(12), dp(12), dp(12), dp(12))),
    ),
]

items.append(
    Constraint(
        Text(
            "Constraint Title",
            id="con_title",
            constraints={
                "top_to_top": "parent",
                "left_to_left": "parent",
                "right_to_right": "parent",
                "horizontal_bias": 0.5,
            },
        ),
        Button(
            "Under Title",
            id="con_btn",
            constraints={
                "top_to_bottom": "con_title",
                "left_to_left": "parent",
                "right_to_right": "parent",
                "horizontal_bias": 0.5,
            },
        ),
        id="constraint_demo",
        margin=(dp(16), dp(0), dp(16), dp(16)),
        style=ui_presets.Card(padding=(dp(12), dp(12), dp(12), dp(12))),
    )
)

items.extend(
    [
        Text(
            "Toast/Snackbar demo",
            id="footer_text",
            text_color="muted",
            style=ui_presets.MutedText(text_size=sp(14)),
            padding=(dp(16), dp(0), dp(16), dp(8)),
        ),
        FloatingActionButton(
            "+",
            id="fab",
            width=dp(72),
            height=dp(72),
            style=Style(background=colors.zinc_200, text_color="on_primary", radius=dp(36), padding=(dp(0), dp(0), dp(0), dp(0))),
        ),
    ]
)

app_spec = app(
    activity(
        "MainActivity",
        Theme(
            palette=palette,
            text=Style(text_color="text", text_size=sp(16)),
            button=Style(text_color="on_primary", text_size=sp(16), radius=dp(16)),
            row=Style(background="card", radius=dp(16)),
            column=Style(background="card", radius=dp(12)),
        ),
        State(
            count=0,
            step=1,
            limit=10,
        ),
        ui(*items),
        increment,
        decrement,
        reset,
        boost,
        fab_click,
        menu_click,
        announce_click,
        exit_click,
    )
)


if __name__ == "__main__":
    run(app_spec)
