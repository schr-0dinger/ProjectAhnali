from dsl.app import (
    app,
    activity,
    app_config,
    ui,
    run,
    state,
    Screen,
    Navigate,
    Back,
    Replace,
    Theme,
    Style,
    presets,
    color_state,
    gradient,
    sequence,
    parallel,
    fade_in,
    fade_out,
    translate,
    animate_elevation,
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
    ListView,
    ScrollView,
    HorizontalScrollView,
    toast,
    simple_dialog,
    dp,
    sp,
    max_width,
)
from dsl.colors import colors
from dsl.widgets import Relative


APP_PACKAGE = "com.anali.scratch"
APP_MIN_SDK = 21
APP_TARGET_SDK = 34
APP_VERSION_CODE = 1
APP_VERSION_NAME = "1.0"
APP_SHOW_ACTION_BAR = False
APP_LABEL = "Anali Scratch"


palette = {
    "bg": colors.zinc_100,
    "surface": colors.white,
    "text": colors.slate_900,
    "muted": colors.slate_500,
    "primary": colors.blue_600,
    "on_primary": colors.white,
    "success": colors.emerald_500,
    "danger": colors.red_500,
    "divider": colors.zinc_200,
}

preset = presets(palette=palette)


# Inline-event handlers (callables are parsed to handler DSL)
def tap_once():
    taps += 1
    counter_value.text = f"Taps: {taps}"


def tap_burst():
    loops = step
    while loops > 0:
        taps += 1
        loops -= 1
    if taps > 99:
        taps = 0
    counter_value.text = f"Taps: {taps}"


def text_input_changed():
    changes += 1
    input_status.text = f"Changes: {changes}"


def input_focus_changed():
    input_status.text = "Focus changed"


def selector_changed():
    changes += 1
    input_status.text = f"Selector changed ({changes})"


def popup_item_selected():
    changes += 1
    input_status.text = f"Popup item selected ({changes})"


def show_toast_msg():
    toast("Toast from inline on_click")


def show_dialog_msg():
    simple_dialog("Dialog", "SimpleDialog from inline on_click")


app_spec = app(
    activity(
        "MainActivity",
        app_config(
            package=APP_PACKAGE,
            min_sdk=APP_MIN_SDK,
            target_sdk=APP_TARGET_SDK,
            version_code=APP_VERSION_CODE,
            version_name=APP_VERSION_NAME,
            show_action_bar=APP_SHOW_ACTION_BAR,
            label=APP_LABEL,
        ),
        Theme(
            palette=palette,
            text=Style(),
            button=Style(),
            input=Style(),
            selector=Style(),
            progress=Style(),
            icon=Style(),
            container=Style(background="surface", radius=dp(14), padding=(dp(12), dp(12), dp(12), dp(12))),
            appbar=Style(),
        ),
        state(taps=0, step=3, changes=0),
        ui(
            Screen(
                "Home",
                AppBar("Anali Native Scratch", id="home_appbar", inline=True),
                Text("Getting Started + API Reality Demo", id="home_title", style=Style(text_size=sp(18)), padding=(dp(16), dp(10), dp(16), dp(6))),
                Text(
                    "Every button below uses inline on_click event attributes.",
                    id="home_subtitle",
                    style=Style(text_color="muted", text_size=sp(13)),
                    padding=(dp(16), dp(0), dp(16), dp(10)),
                ),
                Card(
                    Column(
                        Button("Typography + Visuals", id="go_typography", on_click=[Navigate("Typography")]),
                        Divider(id="home_d1", color="divider"),
                        Button("Buttons + Animation", id="go_buttons", on_click=[Navigate("Buttons")]),
                        Divider(id="home_d2", color="divider"),
                        Button("Inputs + Events", id="go_inputs", on_click=[Navigate("Inputs")]),
                        Divider(id="home_d3", color="divider"),
                        Button("Layouts + Data", id="go_layouts", on_click=[Navigate("Layouts")]),
                        Divider(id="home_d4", color="divider"),
                        Button("Feedback + Navigation", id="go_feedback", on_click=[Navigate("Feedback")]),
                        id="home_menu",
                        width=max_width,
                    ),
                    id="home_card",
                    margin=(dp(16), dp(0), dp(16), dp(16)),
                    width=max_width,
                    style=preset.Card(),
                ),
            ),
            Screen(
                "Typography",
                Button("Back", id="back_typography", on_click=[Replace("Home")], margin=(dp(16), dp(12), dp(16), dp(8))),
                Text("Text, Icon, Style, ColorState, Gradient", id="typo_title", style=Style(text_size=sp(18)), padding=(dp(16), dp(0), dp(16), dp(8))),
                Card(
                    Column(
                        Icon("STAR", id="hero_icon", style=Style(text_size=sp(28), text_color="primary")),
                        Text("Hero Text", id="hero_text", style=Style(text_size=sp(20), letter_spacing=0.04), margin=(dp(0), dp(6), dp(0), dp(6))),
                        View(
                            id="hero_bar",
                            width=max_width,
                            height=dp(10),
                            background=gradient("#FFDBEAFE", "#FFBFDBFE", "left_to_right"),
                            border_width=dp(1),
                            border_color="#FF93C5FD",
                            border_radius=(dp(8), dp(8), dp(8), dp(8)),
                            opacity=0.95,
                        ),
                        Button(
                            "Animate Header",
                            id="animate_header",
                            on_click=[
                                parallel(
                                    fade_in("hero_text", duration=220),
                                    animate_elevation("hero_card", 12, duration=220),
                                ),
                                sequence(
                                    translate("hero_text", y=-10, duration=120),
                                    translate("hero_text", y=0, duration=120),
                                    fade_out("hero_bar", duration=100),
                                    fade_in("hero_bar", duration=120),
                                ),
                            ],
                            margin=(dp(0), dp(10), dp(0), dp(0)),
                        ),
                        id="hero_column",
                    ),
                    id="hero_card",
                    margin=(dp(16), dp(0), dp(16), dp(12)),
                    width=max_width,
                    background=color_state(
                        default="#FFFFFFFF",
                        pressed="#FFF8FAFC",
                        disabled="#FFE2E8F0",
                    ),
                ),
                transition="slide_left",
            ),
            Screen(
                "Buttons",
                Row(
                    Button("Back", id="back_buttons", on_click=[Replace("Home")]),
                    Button("Target", id="go_target", on_click=[Navigate("Target")]),
                    id="buttons_top",
                    margin=(dp(16), dp(12), dp(16), dp(10)),
                ),
                Text("Buttons + Grammar", id="buttons_title", style=Style(text_size=sp(18)), padding=(dp(16), dp(0), dp(16), dp(8))),
                Text("Taps: 0", id="counter_value", padding=(dp(16), dp(0), dp(16), dp(8))),
                Button("Tap +1", id="tap_once", on_click=tap_once, margin=(dp(16), dp(0), dp(16), dp(8))),
                RaisedButton("Burst +step", id="tap_burst", on_click=tap_burst, margin=(dp(16), dp(0), dp(16), dp(8))),
                FlatButton("Toast", id="flat_toast", on_click=show_toast_msg, margin=(dp(16), dp(0), dp(16), dp(8))),
                IconButton("*", id="icon_dialog", on_click=show_dialog_msg, margin=(dp(16), dp(0), dp(16), dp(8))),
                ButtonBar(
                    Button("A", id="bar_a", on_click=show_toast_msg, width=dp(96)),
                    Button("B", id="bar_b", on_click=show_toast_msg, width=dp(96)),
                    Button("C", id="bar_c", on_click=show_toast_msg, width=dp(96)),
                    id="btn_bar",
                    margin=(dp(16), dp(0), dp(16), dp(8)),
                    width=max_width,
                ),
                FloatingActionButton("+", id="fab_add", on_click=tap_once, width=dp(64), height=dp(64), margin=(dp(16), dp(6), dp(16), dp(12))),
                transition="slide_left",
            ),
            Screen(
                "Inputs",
                Button("Back", id="back_inputs", on_click=[Replace("Home")], margin=(dp(16), dp(12), dp(16), dp(10))),
                Text("Input Configuration + Inline Events", id="inputs_title", style=Style(text_size=sp(18)), padding=(dp(16), dp(0), dp(16), dp(8))),
                TextField(
                    "",
                    id="name_input",
                    hint="Type your name",
                    input_type="text",
                    ime_options="done|no_fullscreen",
                    max_length=40,
                    single_line=True,
                    auto_capitalize="words",
                    on_text_change=text_input_changed,
                    on_focus_change=input_focus_changed,
                    margin=(dp(16), dp(0), dp(16), dp(8)),
                ),
                TextField(
                    "",
                    id="pin_input",
                    hint="Numeric PIN",
                    input_type="number_password",
                    numeric_only=True,
                    password=True,
                    max_length=6,
                    single_line=True,
                    on_text_change=text_input_changed,
                    margin=(dp(16), dp(0), dp(16), dp(10)),
                ),
                Checkbox("Checkbox", id="check_demo", checked=True, on_change=selector_changed, margin=(dp(16), dp(0), dp(16), dp(6))),
                Switch("Switch", id="switch_demo", checked=False, on_change=selector_changed, margin=(dp(16), dp(0), dp(16), dp(6))),
                Slider(id="slider_demo", min=0, max=100, value=35, on_change=selector_changed, margin=(dp(16), dp(0), dp(16), dp(8))),
                RadioGroup(
                    Radio("Choice A", id="radio_a", checked=True, on_change=selector_changed),
                    Radio("Choice B", id="radio_b", checked=False, on_change=selector_changed),
                    id="radio_group_demo",
                    margin=(dp(16), dp(0), dp(16), dp(8)),
                ),
                DropdownButton(id="dropdown_demo", items=["One", "Two", "Three"], on_item_selected=selector_changed, margin=(dp(16), dp(0), dp(16), dp(8))),
                PopupMenuButton("Popup Menu", id="popup_demo", items=["Alpha", "Beta", "Gamma"], on_menu_item_selected=popup_item_selected, margin=(dp(16), dp(0), dp(16), dp(8))),
                Text("Changes: 0", id="input_status", style=Style(text_color="muted"), padding=(dp(16), dp(0), dp(16), dp(8))),
                transition="slide_left",
            ),
            Screen(
                "Layouts",
                Button("Back", id="back_layouts", on_click=[Replace("Home")], margin=(dp(16), dp(12), dp(16), dp(10))),
                Text("Row / Column / Relative / Scroll / ListView", id="layouts_title", style=Style(text_size=sp(18)), padding=(dp(16), dp(0), dp(16), dp(8))),
                Row(
                    Button("Left", id="row_left", width=dp(0), weight=1, on_click=show_toast_msg),
                    Button("Right", id="row_right", width=dp(0), weight=1, on_click=show_toast_msg),
                    id="layout_row",
                    weight_sum=2,
                    margin=(dp(16), dp(0), dp(16), dp(8)),
                ),
                Relative(
                    Text("Top", id="rel_top", relative=[("align_parent_top", "parent"), ("center_horizontal", "parent")]),
                    Button("Below", id="rel_btn", relative=[("below", "rel_top"), ("center_horizontal", "parent")], on_click=show_toast_msg),
                    id="layout_relative",
                    margin=(dp(16), dp(0), dp(16), dp(8)),
                    width=max_width,
                    style=preset.Card(),
                ),
                Container(
                    Card(
                        Text("Container + Card", id="container_title", style=Style(text_size=sp(16))),
                        Divider(id="container_div", color="divider", margin=(dp(0), dp(6), dp(0), dp(6))),
                        View(id="container_bar", width=max_width, height=dp(8), background="primary"),
                        id="container_card",
                        width=max_width,
                    ),
                    id="container_root",
                    margin=(dp(16), dp(0), dp(16), dp(8)),
                    width=max_width,
                ),
                HorizontalScrollView(
                    Row(
                        Button("Chip 1", id="chip_1", on_click=show_toast_msg),
                        Button("Chip 2", id="chip_2", on_click=show_toast_msg),
                        Button("Chip 3", id="chip_3", on_click=show_toast_msg),
                        Button("Chip 4", id="chip_4", on_click=show_toast_msg),
                        id="chip_row",
                    ),
                    id="horizontal_demo",
                    margin=(dp(16), dp(0), dp(16), dp(8)),
                ),
                ScrollView(
                    Column(
                        Text("ScrollView child (single direct child rule)", id="scroll_note", style=Style(text_color="muted")),
                        ListView(
                            id="static_list",
                            items=["Alpha", "Beta", "Gamma", "Delta"],
                            item_layout="simple_list_item_1",
                            margin=(dp(0), dp(6), dp(0), dp(0)),
                        ),
                        id="scroll_col",
                    ),
                    id="scroll_demo",
                    margin=(dp(16), dp(0), dp(16), dp(10)),
                ),
                transition="slide_left",
            ),
            Screen(
                "Feedback",
                Button("Back", id="back_feedback", on_click=[Replace("Home")], margin=(dp(16), dp(12), dp(16), dp(10))),
                Text("Feedback + Navigation", id="feedback_title", style=Style(text_size=sp(18)), padding=(dp(16), dp(0), dp(16), dp(8))),
                Text("Determinate", id="pb_label_1", padding=(dp(16), dp(0), dp(16), dp(4))),
                ProgressBar(id="pb_det", min=0, max=100, value=72, progress_tint="success", margin=(dp(16), dp(0), dp(16), dp(8))),
                Text("Indeterminate", id="pb_label_2", padding=(dp(16), dp(0), dp(16), dp(4))),
                ProgressBar(id="pb_ind", indeterminate=True, progress_tint="primary", margin=(dp(16), dp(0), dp(16), dp(10))),
                Image(id="img_logo", src="ic_launcher", content_description="Launcher", width=dp(72), height=dp(72), margin=(dp(16), dp(0), dp(16), dp(10))),
                Button("Toast", id="fb_toast", on_click=show_toast_msg, margin=(dp(16), dp(0), dp(16), dp(6))),
                Button("Dialog", id="fb_dialog", on_click=show_dialog_msg, margin=(dp(16), dp(0), dp(16), dp(6))),
                Button("Navigate Target", id="fb_nav", on_click=[Navigate("Target")], margin=(dp(16), dp(0), dp(16), dp(6))),
                Button("Replace Target", id="fb_replace", on_click=[Replace("Target")], margin=(dp(16), dp(0), dp(16), dp(6))),
                Button("Back()", id="fb_back", on_click=[Back()], margin=(dp(16), dp(0), dp(16), dp(10))),
                transition="slide_left",
            ),
            Screen(
                "Target",
                Text("Navigation Target", id="target_title", style=Style(text_size=sp(20)), padding=(dp(16), dp(24), dp(16), dp(8))),
                Text("Opened via Navigate/Replace.", id="target_note", style=Style(text_color="muted"), padding=(dp(16), dp(0), dp(16), dp(8))),
                Button("Replace Home", id="target_home", on_click=[Replace("Home")], margin=(dp(16), dp(0), dp(16), dp(8))),
                Button("Back", id="target_back", on_click=[Back()], margin=(dp(16), dp(0), dp(16), dp(8))),
                transition="slide_left",
            ),
        ),
    )
)


if __name__ == "__main__":
    run(app_spec)
