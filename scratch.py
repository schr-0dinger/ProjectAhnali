from dsl.app import (
    app,
    activity,
    app_config,
    ui,
    on_click,
    on_click_map,
    run,
    Screen,
    Navigate,
    Back,
    Replace,
    state,
    Theme,
    Style,
    presets,
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
    RadioGroup,
    Switch,
    Slider,
    DropdownButton,
    ButtonBar,
    PopupMenuButton,
    Divider,
    Image,
    Container,
    Card,
    Icon,
    ProgressBar,
    View,
    toast,
    # snackbar,  # Material feedback path disabled for native-only scratch.
    simple_dialog,
    dp,
    sp,
    max_width,
)
from dsl.colors import colors
from dsl.widgets import Relative


APP_PACKAGE = "com.anali.widgetzoo"
APP_MIN_SDK = 21
APP_TARGET_SDK = 34
APP_VERSION_CODE = 1
APP_VERSION_NAME = "1.0"
APP_DEBUGGABLE = False
APP_SHOW_ACTION_BAR = False
APP_LABEL = "Anali Widget Zoo"

# APP_PLUGINS = ["material"]  # Disabled: keep scratch.py on native/core widgets only.


NAV_TO_SCREEN = {
    "go_text_icon": "TextIconDemo",
    "go_buttons": "ButtonsDemo",
    "go_inputs": "InputsDemo",
    "go_selectors": "SelectorsDemo",
    "go_layouts": "LayoutsDemo",
    "go_containers": "ContainersDemo",
    "go_images": "ImagesDemo",
    "go_progress": "ProgressDemo",
    "go_dialogs": "DialogsDemo",
    "go_navigation": "NavigationDemo",
}

BACK_TO_HOME = [
    "back_text_icon", "back_buttons", "back_inputs", "back_selectors",
    "back_layouts", "back_containers", "back_images", "back_progress",
    "back_dialogs", "back_navigation",
]

NAV_MISC = {
    "nav_push_btn": [Navigate("NavigationTarget")],
    "nav_replace_btn": [Replace("NavigationTarget")],
    "nav_pop_btn": [Back()],
    "target_home_btn": [Replace("Home")],
    "target_back_btn": [Back()],
}

AUTO_CLICK_SPECS = [
    *on_click_map({btn: [Navigate(screen)] for btn, screen in NAV_TO_SCREEN.items()}),
    *on_click_map({btn: [Replace("Home")] for btn in BACK_TO_HOME}),
    *on_click_map(NAV_MISC),
]


@on_click("state_inc")
def state_inc():
    demo_count += 1
    btn_count_text.text = f"Button taps: {demo_count}"


@on_click("raised_action")
def raised_action():
    toast("RaisedButton clicked")


@on_click("flat_action")
def flat_action():
    toast("FlatButton clicked")


@on_click("icon_action")
def icon_action():
    toast("IconButton clicked")


@on_click("fab_action")
def fab_action():
    # snackbar("FloatingActionButton clicked")  # Disabled (Material path).
    toast("FloatingActionButton clicked")


@on_click("show_toast_btn")
def show_toast_btn():
    toast("Toast from handler")


@on_click("show_snackbar_btn")
def show_snackbar_btn():
    # snackbar("Snackbar from handler")  # Disabled (Material path).
    toast("Snackbar disabled in native mode")


@on_click("show_dialog_btn")
def show_dialog_btn():
    simple_dialog("Dialog Demo", "SimpleDialog is wired and working.")

palette = {
    "bg": colors.zinc_100,
    "card": colors.white,
    "text": colors.slate_900,
    "muted": colors.slate_500,
    "primary": colors.blue_600,
    "on_primary": colors.white,
    "danger": colors.red_500,
    "on_danger": colors.white,
    "divider": colors.zinc_200,
}

preset = presets(palette=palette)
title_style = Style(text_color="text", text_size=sp(20))
section_style = Style(text_color="text", text_size=sp(16))


items = [
    Screen(
        "Home",
        AppBar(
            "Anali Widget Zoo",
            id="home_appbar",
            inline=True,
            style=preset.Card(padding=(dp(14), dp(14), dp(14), dp(14))),
        ),
        Text("Home Menu", id="home_title", style=title_style, padding=(dp(16), dp(12), dp(16), dp(4))),
        Text(
            "ListView-style static menu (compiled as a Column). Tap any entry.",
            id="home_subtitle",
            style=Style(text_color="muted", text_size=sp(13)),
            padding=(dp(16), dp(0), dp(16), dp(10)),
        ),
        Card(
            Column(
                Button("Text + Icon", id="go_text_icon", icon="T"),
                Divider(id="home_div_1", color="divider"),
                Button("Buttons + FAB + ButtonBar", id="go_buttons", icon="B"),
                Divider(id="home_div_2", color="divider"),
                Button("Inputs (TextField / Checkbox / Radio / Switch)", id="go_inputs", icon="I"),
                Divider(id="home_div_3", color="divider"),
                Button("Selectors (Slider / Dropdown / Popup / RadioGroup)", id="go_selectors", icon="S"),
                Divider(id="home_div_4", color="divider"),
                Button("Layouts (Row / Column / Relative)", id="go_layouts", icon="L"),
                Divider(id="home_div_5", color="divider"),
                Button("Containers (Container / Card / View / Divider)", id="go_containers", icon="C"),
                Divider(id="home_div_6", color="divider"),
                Button("Images", id="go_images", icon="IMG"),
                Divider(id="home_div_7", color="divider"),
                Button("ProgressBar", id="go_progress", icon="P"),
                Divider(id="home_div_8", color="divider"),
                Button("Dialogs + Toast + Snackbar", id="go_dialogs", icon="D"),
                Divider(id="home_div_9", color="divider"),
                Button("Navigation (Navigate / Replace / Back)", id="go_navigation", icon="N"),
                id="home_list",
                width=max_width,
            ),
            id="home_card",
            margin=(dp(16), dp(0), dp(16), dp(16)),
            width=max_width,
            style=preset.Card(padding=(dp(10), dp(10), dp(10), dp(10))),
        ),
    ),
    Screen(
        "TextIconDemo",
        Row(Button("Back", id="back_text_icon"), id="text_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Text + Icon", id="text_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Icon("STAR", id="text_icon", style=Style(text_size=sp(22), text_color="primary"), padding=(dp(16), dp(0), dp(16), dp(8))),
        Text("Regular Text widget", id="text_normal", padding=(dp(16), dp(0), dp(16), dp(8))),
        Divider(id="text_divider", color="divider", margin=(dp(16), dp(8), dp(16), dp(8))),
        Text("Styled Text with preset-muted color", id="text_muted", style=preset.MutedText(), padding=(dp(16), dp(0), dp(16), dp(8))),
    ),
    Screen(
        "ButtonsDemo",
        Row(Button("Back", id="back_buttons"), id="buttons_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Buttons", id="buttons_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Text("Button taps: 0", id="btn_count_text", padding=(dp(16), dp(0), dp(16), dp(8))),
        Button("Primary Button", id="state_inc", icon="+", margin=(dp(16), dp(0), dp(16), dp(10)), style=preset.PrimaryButton()),
        RaisedButton("Raised", id="raised_action", margin=(dp(16), dp(0), dp(16), dp(8)), style=preset.PrimaryButton()),
        FlatButton("Flat", id="flat_action", margin=(dp(16), dp(0), dp(16), dp(8))),
        IconButton("*", id="icon_action", margin=(dp(16), dp(0), dp(16), dp(8))),
        ButtonBar(
            Button("One", id="bar_one_btn", width=dp(100)),
            Button("Two", id="bar_two_btn", width=dp(120), background=colors.red_500),
            Button("Three", id="bar_three_btn", width=dp(100)),
            id="buttons_bar",
            margin=(dp(16), dp(0), dp(16), dp(10)),
            width=max_width,
            weight_sum=3,
        ),
        FloatingActionButton("+", id="fab_action", width=dp(64), height=dp(64), margin=(dp(16), dp(4), dp(16), dp(12))),
    ),
    Screen(
        "InputsDemo",
        Row(Button("Back", id="back_inputs"), id="inputs_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Inputs", id="inputs_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        TextField("", id="input_name", hint="Type text here", margin=(dp(16), dp(0), dp(16), dp(12))),
        Checkbox("Checkbox", id="input_checkbox", checked=True, margin=(dp(16), dp(0), dp(16), dp(8))),
        Radio("Single Radio", id="input_radio", checked=False, margin=(dp(16), dp(0), dp(16), dp(8))),
        Switch("Switch", id="input_switch", checked=True, margin=(dp(16), dp(0), dp(16), dp(8))),
    ),
    Screen(
        "SelectorsDemo",
        Row(Button("Back", id="back_selectors"), id="selectors_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Selectors", id="selectors_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Slider(id="selectors_slider", min=0, max=100, value=35, margin=(dp(16), dp(0), dp(16), dp(10))),
        DropdownButton(id="selectors_dropdown", items=["One", "Two", "Three"], margin=(dp(16), dp(0), dp(16), dp(10))),
        PopupMenuButton("Popup Menu", id="selectors_popup", items=["A", "B", "C"], margin=(dp(16), dp(0), dp(16), dp(10))),
        RadioGroup(
            Radio("Choice A", id="selectors_radio_a", checked=True),
            Radio("Choice B", id="selectors_radio_b", checked=True),
            id="selectors_radio_group",
            orientation="vertical",
            margin=(dp(16), dp(0), dp(16), dp(10)),
        ),
    ),
    Screen(
        "LayoutsDemo",
        Row(Button("Back", id="back_layouts"), id="layouts_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Layouts", id="layouts_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Row(
            Button("Left", id="layouts_row_left", weight=1, width=dp(0)),
            Button("Right", id="layouts_row_right", weight=1, width=dp(0)),
            id="layouts_row_demo",
            margin=(dp(16), dp(0), dp(16), dp(12)),
            weight_sum=2,
        ),
        Column(
            Text("Column item A", id="layouts_col_a"),
            Text("Column item B", id="layouts_col_b"),
            id="layouts_col_demo",
            margin=(dp(16), dp(0), dp(16), dp(12)),
            style=preset.Card(),
            width=max_width,
        ),
        Relative(
            Text("Relative Top", id="layouts_rel_top", relative=[("align_parent_top", "parent"), ("center_horizontal", "parent")]),
            Button("Below", id="layouts_rel_btn", relative=[("below", "layouts_rel_top"), ("center_horizontal", "parent")]),
            id="layouts_relative_demo",
            margin=(dp(16), dp(0), dp(16), dp(12)),
            style=preset.Card(padding=(dp(12), dp(12), dp(12), dp(12))),
            width=max_width,
        ),
        # ConstraintLayout demo intentionally disabled to keep scratch.py native-only.
    ),
    Screen(
        "ContainersDemo",
        Row(Button("Back", id="back_containers"), id="containers_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Container / Card / View / Divider", id="containers_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Container(
            Card(
                Text("Card title", id="containers_card_title", style=section_style),
                Divider(id="containers_divider", color="divider", margin=(dp(0), dp(8), dp(0), dp(8))),
                Text("A raw View below draws a simple bar.", id="containers_desc", style=preset.MutedText()),
                View(id="containers_bar", width=max_width, height=dp(8), background="primary", margin=(dp(0), dp(8), dp(0), dp(0))),
                id="containers_card",
                width=max_width,
            ),
            id="containers_root",
            margin=(dp(16), dp(0), dp(16), dp(12)),
            width=max_width,
        ),
    ),
    Screen(
        "ImagesDemo",
        Row(Button("Back", id="back_images"), id="images_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Image", id="images_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Text(
            "Image src expects drawable resource name. Use src='image' for res/drawable/image.jpg.",
            id="images_note",
            style=preset.MutedText(),
            padding=(dp(16), dp(0), dp(16), dp(8)),
        ),
        Image(id="images_local", src="image", content_description="project image", width=dp(180), height=dp(120), margin=(dp(16), dp(0), dp(16), dp(10))),
        Image(id="images_launcher", src="ic_launcher", content_description="launcher icon", width=dp(96), height=dp(96), margin=(dp(16), dp(0), dp(16), dp(12))),
    ),
    Screen(
        "ProgressDemo",
        Row(Button("Back", id="back_progress"), id="progress_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("ProgressBar", id="progress_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Text("Determinate 65%", id="progress_label_det", padding=(dp(16), dp(0), dp(16), dp(4))),
        ProgressBar(id="progress_det", min=0, max=100, value=65, margin=(dp(16), dp(0), dp(16), dp(12))),
        Text("Indeterminate", id="progress_label_ind", padding=(dp(16), dp(0), dp(16), dp(4))),
        ProgressBar(id="progress_ind", indeterminate=True, margin=(dp(16), dp(0), dp(16), dp(12))),
    ),
    Screen(
        "DialogsDemo",
        Row(Button("Back", id="back_dialogs"), id="dialogs_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Dialogs / Toast / Snackbar", id="dialogs_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Button("Show Toast", id="show_toast_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Show Snackbar (native fallback)", id="show_snackbar_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Show SimpleDialog", id="show_dialog_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
    ),
    Screen(
        "NavigationDemo",
        Row(Button("Back", id="back_navigation"), id="navigation_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Navigation", id="navigation_title", style=title_style, padding=(dp(16), dp(0), dp(16), dp(8))),
        Text("Navigate pushes stack, Replace swaps current, Back pops.", id="navigation_note", style=preset.MutedText(), padding=(dp(16), dp(0), dp(16), dp(8))),
        Button("Navigate -> Target", id="nav_push_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Replace -> Target", id="nav_replace_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Back()", id="nav_pop_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
    ),
    Screen(
        "NavigationTarget",
        Text("Navigation Target", id="target_title", style=title_style, padding=(dp(16), dp(24), dp(16), dp(8))),
        Text("Opened via Navigate/Replace", id="target_note", style=preset.MutedText(), padding=(dp(16), dp(0), dp(16), dp(10))),
        Button("Replace Home", id="target_home_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Back()", id="target_back_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
    ),
]


app_spec = app(
    activity(
        "MainActivity",
        app_config(
            package=APP_PACKAGE,
            min_sdk=APP_MIN_SDK,
            target_sdk=APP_TARGET_SDK,
            version_code=APP_VERSION_CODE,
            version_name=APP_VERSION_NAME,
            debuggable=APP_DEBUGGABLE,
            show_action_bar=APP_SHOW_ACTION_BAR,
            label=APP_LABEL,
        ),
        Theme(
            palette=palette,
            text=Style(text_color="text", text_size=sp(15)),
            button=Style(
                text_color="on_primary",
                background=colors.blue_500,
                text_size=sp(15),
                radius=dp(12),
                margin=(dp(12)),
                width=max_width
                ),
            row=Style(background="card", radius=dp(12)),
            column=Style(background="card", radius=dp(12)),
        ),
        state(demo_count=0),
        ui(*items),
        *AUTO_CLICK_SPECS,
        state_inc,
        raised_action,
        flat_action,
        icon_action,
        fab_action,
        show_toast_btn,
        show_snackbar_btn,
        show_dialog_btn,
    )
)


if __name__ == "__main__":
    run(app_spec)
