from dsl.app import (
    AppBar,
    Back,
    Button,
    Card,
    Checkbox,
    Column,
    Divider,
    DropdownButton,
    FlatButton,
    FloatingActionButton,
    Icon,
    IconButton,
    Image,
    Navigate,
    PopupMenuButton,
    ProgressBar,
    Radio,
    RadioGroup,
    RaisedButton,
    Replace,
    Row,
    Screen,
    Slider,
    Switch,
    Text,
    TextField,
    activity,
    app,
    app_config,
    dp,
    max_width,
    on_click,
    on_click_map,
    run,
    simple_dialog,
    snackbar,
    state,
    toast,
    ui,
)


APP_PACKAGE = "com.anali.materialwidgetzoo"
APP_MIN_SDK = 21
APP_TARGET_SDK = 34
APP_VERSION_CODE = 1
APP_VERSION_NAME = "1.0"
APP_DEBUGGABLE = False
APP_SHOW_ACTION_BAR = False
APP_LABEL = "Anali Material Widget Zoo"

# Material must be explicitly enabled by the app script.
APP_PLUGINS = ["material"]

# TODO(material-demo-pending): Extend this showcase when new Material widgets land.
# Add demo screens for:
# - Badge / Chip / Tooltip / List / Table / Alert / Skeleton
# - BottomNavigation / Drawer / Tabs / Stepper / SpeedDial / Pagination
# - Rating / NumberField / TransferList / ToggleButtonGroup


NAV_TO_SCREEN = {
    "go_buttons": "ButtonsDemo",
    "go_inputs": "InputsDemo",
    "go_indicators": "IndicatorsDemo",
    "go_feedback": "FeedbackDemo",
    "go_navigation": "NavigationDemo",
}

BACK_TO_HOME = [
    "back_buttons",
    "back_inputs",
    "back_indicators",
    "back_feedback",
    "back_navigation",
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
    btn_count_text.text = f"Material button taps: {demo_count}"


@on_click("raised_action")
def raised_action():
    toast("Material raised button clicked")


@on_click("flat_action")
def flat_action():
    toast("Material flat button clicked")


@on_click("icon_action")
def icon_action():
    toast("Material icon button clicked")


@on_click("fab_action")
def fab_action():
    snackbar("Material FAB clicked")


@on_click("show_toast_btn")
def show_toast_btn():
    toast("Toast from material screen")


@on_click("show_snackbar_btn")
def show_snackbar_btn():
    snackbar("Material Snackbar from handler")


@on_click("show_dialog_btn")
def show_dialog_btn():
    simple_dialog("Material Dialog", "SimpleDialog is wired and working.")


items = [
    Screen(
        "Home",
        AppBar("Anali Material Widget Zoo", id="home_appbar", inline=True),
        Text("Material-only widget showcase", id="home_title", padding=(dp(16), dp(12), dp(16), dp(8))),
        Row(
            Icon("★", id="home_icon", margin=(dp(16), dp(0), dp(8), dp(8))),
            Image(
                id="home_image",
                src=17301651,
                content_description="Material sample icon",
                width=dp(40),
                height=dp(40),
                margin=(dp(0), dp(0), dp(16), dp(8)),
            ),
            id="home_visuals",
        ),
        Divider(id="home_divider", margin=(dp(16), dp(0), dp(16), dp(12))),
        Column(
            Button("Buttons", id="go_buttons"),
            Button("Inputs", id="go_inputs"),
            Button("Indicators", id="go_indicators"),
            Button("Feedback", id="go_feedback"),
            Button("Navigation", id="go_navigation"),
            id="home_menu",
            margin=(dp(16), dp(0), dp(16), dp(16)),
            width=max_width,
        ),
    ),
    Screen(
        "ButtonsDemo",
        Row(Button("Back", id="back_buttons"), id="buttons_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Material Buttons", id="buttons_title", padding=(dp(16), dp(0), dp(16), dp(8))),
        Text("Material button taps: 0", id="btn_count_text", padding=(dp(16), dp(0), dp(16), dp(8))),
        Card(
            Button("Material Button", id="state_inc", margin=(dp(0), dp(0), dp(0), dp(8))),
            RaisedButton("Material Raised", id="raised_action", margin=(dp(0), dp(0), dp(0), dp(8))),
            FlatButton("Material Flat", id="flat_action", margin=(dp(0), dp(0), dp(0), dp(8))),
            IconButton("★", id="icon_action", margin=(dp(0), dp(0), dp(0), dp(8))),
            PopupMenuButton(
                "Material Popup",
                id="popup_action",
                items=["Popup One", "Popup Two", "Popup Three"],
                margin=(dp(0), dp(0), dp(0), dp(8)),
            ),
            id="buttons_card",
            margin=(dp(16), dp(0), dp(16), dp(8)),
            background=None,
            radius=None,
        ),
        Divider(id="buttons_divider", margin=(dp(16), dp(8), dp(16), dp(8))),
    ),
    Screen(
        "InputsDemo",
        Row(Button("Back", id="back_inputs"), id="inputs_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Material Inputs", id="inputs_title", padding=(dp(16), dp(0), dp(16), dp(8))),
        TextField("", id="input_name", hint="Type text here", margin=(dp(16), dp(0), dp(16), dp(12))),
        DropdownButton(
            id="input_dropdown",
            items=["Inbox", "Personal", "Shopping"],
            margin=(dp(16), dp(0), dp(16), dp(12)),
        ),
        Checkbox("Material Checkbox", id="input_checkbox", checked=True, margin=(dp(16), dp(0), dp(16), dp(8))),
        RadioGroup(
            Radio("Material Radio A", id="input_radio_a", checked=True),
            Radio("Material Radio B", id="input_radio_b", checked=False),
            id="input_radio_group",
            orientation="vertical",
            margin=(dp(16), dp(0), dp(16), dp(8)),
        ),
        Switch("Material Switch", id="input_switch", checked=True, margin=(dp(16), dp(0), dp(16), dp(8))),
        Slider(id="input_slider", min=0, max=100, value=42, margin=(dp(16), dp(0), dp(16), dp(12))),
        Divider(id="inputs_divider", margin=(dp(16), dp(0), dp(16), dp(8))),
    ),
    Screen(
        "IndicatorsDemo",
        Row(Button("Back", id="back_indicators"), id="indicators_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Material Progress Indicators", id="indicators_title", padding=(dp(16), dp(0), dp(16), dp(8))),
        Text("Determinate 65%", id="progress_label_det", padding=(dp(16), dp(0), dp(16), dp(4))),
        ProgressBar(id="progress_det", min=0, max=100, value=65, margin=(dp(16), dp(0), dp(16), dp(12))),
        Text("Indeterminate", id="progress_label_ind", padding=(dp(16), dp(0), dp(16), dp(4))),
        ProgressBar(id="progress_ind", indeterminate=True, margin=(dp(16), dp(0), dp(16), dp(12))),
    ),
    Screen(
        "FeedbackDemo",
        Row(Button("Back", id="back_feedback"), id="feedback_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Material Feedback", id="feedback_title", padding=(dp(16), dp(0), dp(16), dp(8))),
        Button("Show Toast", id="show_toast_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Show Material Snackbar", id="show_snackbar_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Show Dialog", id="show_dialog_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        FloatingActionButton("Material FAB", id="fab_action", width=dp(56), height=dp(56), margin=(dp(16), dp(8), dp(16), dp(12))),
    ),
    Screen(
        "NavigationDemo",
        Row(Button("Back", id="back_navigation"), id="navigation_back_row", margin=(dp(16), dp(12), dp(16), dp(12))),
        Text("Navigation", id="navigation_title", padding=(dp(16), dp(0), dp(16), dp(8))),
        Button("Navigate -> Target", id="nav_push_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Replace -> Target", id="nav_replace_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
        Button("Back()", id="nav_pop_btn", margin=(dp(16), dp(0), dp(16), dp(8))),
    ),
    Screen(
        "NavigationTarget",
        Text("Material Navigation Target", id="target_title", padding=(dp(16), dp(24), dp(16), dp(8))),
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
