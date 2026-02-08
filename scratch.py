from dsl.app import app, activity, ui, on_click, run
from dsl.widgets import (
    max_width,
    max_height,
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
    dp,
    toast,
    snackbar,
)
from dsl.colors import colors
import os
import re


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
    toast("FAB clicked!")


@on_click("menu")
def menu_click():
    simple_dialog("Menu", "Popup menu clicked")


USE_MATERIAL = os.getenv("ANALI_USE_MATERIAL") == 1

items = [
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
        Button("+", id="inc", style=presets().PrimaryButton(), weight=1),
        Button("-", id="dec", style=presets().DangerButton(), weight=1),

        id="counter_row",
        width=max_width,
        margin=(0, 0, 0, 16),
        style=presets().Card(padding=(8, 8, 8, 8)),
        weight_sum=2
    ),

    # ── Button Variants ────────────────────
    Row(
        Column(
            RaisedButton("Raised", id="raised", style=presets().PrimaryButton()),
            FlatButton("Flat", style=Style(background=colors.emerald_500, text_color="primary"), weight=1),
            IconButton("★", width=max_width, style=Style(background="card", radius=999, text_color="primary"), weight=1),
            id="button_variants",
            margin=(0, 0, 0, 16),
            style=presets().Card(padding=(12, 12, 12, 12)),
            weight_sum=3
        )
    ),

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
        )
    ),

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

    # ── RelativeLayout demo ────────────────
    Relative(
        Text(
            "Relative Title",
            id="rel_title",
            relative=[("align_parent_top", "parent"), ("center_horizontal", "parent")],
            margin=(0, 0, 0, 8),
        ),
        Button(
            "Below Title",
            id="rel_btn",
            relative=[("below", "rel_title"), ("center_horizontal", "parent")],
        ),
        id="relative_demo",
        margin=(0, 0, 0, 16),
        style=presets().Card(padding=(12, 12, 12, 12)),
    ),
]

if USE_MATERIAL:
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
            margin=(0, 0, 0, 16),
            style=presets().Card(padding=(12, 12, 12, 12)),
        )
    )

items.extend(
    [
        Text(
            "Toast demo",
            id="footer_text",
            text_color="muted",
            style=presets().MutedText(text_size=14),
        ),
        FloatingActionButton(
            "+",
            id="fab",
            width=dp(200),
            height=dp(200),
            style=Style(background="primary", text_color="on_primary", radius=dp(100), padding=(0, 0, 0, 0)),
        ),
    ]
)

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
        ui(*items),
        increment,
        decrement,
        fab_click,
        menu_click,
    )
)


if __name__ == "__main__":
    from pathlib import Path
    import subprocess
    import sys

    def _find_aar(artifact: str) -> Path | None:
        libs_dir = Path("libs")
        if not libs_dir.exists():
            return None
        pattern = rf"^{artifact}-(\\d.*)\\.aar$"
        matches = sorted([p for p in libs_dir.glob(f"{artifact}-*.aar") if re.match(pattern, p.name)])
        return matches[-1] if matches else None

    required_artifacts = [
        "constraintlayout",
        "material",
        "appcompat",
        "core",
        "coordinatorlayout",
        "recyclerview",
        "cardview",
        "drawerlayout",
        "customview",
        "vectordrawable",
        "transition",
        "viewpager",
        "viewpager2",
        "fragment",
        "activity",
    ]
    extra_aars = []
    if USE_MATERIAL:
        missing = []
        for artifact in required_artifacts:
            found = _find_aar(artifact)
            if found is None:
                missing.append(f"{artifact}-*.aar")
            else:
                extra_aars.append(found)
        if missing:
            subprocess.run(
                [sys.executable, "tools/download_aars.py", "--out", "libs"],
                check=True,
            )
            extra_aars = []
            missing = []
            for artifact in required_artifacts:
                found = _find_aar(artifact)
                if found is None:
                    missing.append(f"{artifact}-*.aar")
                else:
                    extra_aars.append(found)
            if missing:
                missing_list = ", ".join(missing)
                raise RuntimeError(
                    f"Missing required AARs in ./libs: {missing_list}. "
                    "Download the missing AARs from Maven and place them under ./libs."
                )
        run(
            app_spec,
            extra_aars=[str(p) for p in extra_aars],
        )
    else:
        run(app_spec)
