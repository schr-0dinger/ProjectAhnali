from dsl.app import *


APP_PACKAGE = "com.schr0dinger.todoapp"
APP_MIN_SDK = 21
APP_TARGET_SDK = 34
APP_LABEL = "Ahnali TODO"


@on_click("pick_template_1")
def _pick_template_1():
    selected_template = 0
    picked_hint.text = "Template: Buy groceries"
    app_status.text = "Template selected"


@on_click("pick_template_2")
def _pick_template_2():
    selected_template = 1
    picked_hint.text = "Template: Ship release build"
    app_status.text = "Template selected"


@on_click("pick_template_3")
def _pick_template_3():
    selected_template = 2
    picked_hint.text = "Template: Read architecture docs"
    app_status.text = "Template selected"


@on_click("add_task")
def _add_task():
    if task1_active == 0:
        task1_active = 1
        task1_done = 0
        task1_status.text = "OPEN"
        if selected_template == 0:
            task1_name.text = "Buy groceries"
        else:
            if selected_template == 1:
                task1_name.text = "Ship release build"
            else:
                task1_name.text = "Read architecture docs"
        app_status.text = "Task added to slot 1"
    else:
        if task2_active == 0:
            task2_active = 1
            task2_done = 0
            task2_status.text = "OPEN"
            if selected_template == 0:
                task2_name.text = "Buy groceries"
            else:
                if selected_template == 1:
                    task2_name.text = "Ship release build"
                else:
                    task2_name.text = "Read architecture docs"
            app_status.text = "Task added to slot 2"
        else:
            if task3_active == 0:
                task3_active = 1
                task3_done = 0
                task3_status.text = "OPEN"
                if selected_template == 0:
                    task3_name.text = "Buy groceries"
                else:
                    if selected_template == 1:
                        task3_name.text = "Ship release build"
                    else:
                        task3_name.text = "Read architecture docs"
                app_status.text = "Task added to slot 3"
            else:
                app_status.text = "All task slots are full. Remove one first."

    done_count = task1_done + task2_done + task3_done
    if done_count == 0:
        summary.text = "Done: 0/3"
    else:
        if done_count == 1:
            summary.text = "Done: 1/3"
        else:
            if done_count == 2:
                summary.text = "Done: 2/3"
            else:
                summary.text = "Done: 3/3"


@on_click("toggle_task_1")
def _toggle_task_1():
    if task1_active == 0:
        app_status.text = "Slot 1 is empty"
    else:
        if task1_done == 0:
            task1_done = 1
            task1_status.text = "DONE"
            app_status.text = "Slot 1 marked done"
        else:
            task1_done = 0
            task1_status.text = "OPEN"
            app_status.text = "Slot 1 marked open"

    done_count = task1_done + task2_done + task3_done
    if done_count == 0:
        summary.text = "Done: 0/3"
    else:
        if done_count == 1:
            summary.text = "Done: 1/3"
        else:
            if done_count == 2:
                summary.text = "Done: 2/3"
            else:
                summary.text = "Done: 3/3"


@on_click("toggle_task_2")
def _toggle_task_2():
    if task2_active == 0:
        app_status.text = "Slot 2 is empty"
    else:
        if task2_done == 0:
            task2_done = 1
            task2_status.text = "DONE"
            app_status.text = "Slot 2 marked done"
        else:
            task2_done = 0
            task2_status.text = "OPEN"
            app_status.text = "Slot 2 marked open"

    done_count = task1_done + task2_done + task3_done
    if done_count == 0:
        summary.text = "Done: 0/3"
    else:
        if done_count == 1:
            summary.text = "Done: 1/3"
        else:
            if done_count == 2:
                summary.text = "Done: 2/3"
            else:
                summary.text = "Done: 3/3"


@on_click("toggle_task_3")
def _toggle_task_3():
    if task3_active == 0:
        app_status.text = "Slot 3 is empty"
    else:
        if task3_done == 0:
            task3_done = 1
            task3_status.text = "DONE"
            app_status.text = "Slot 3 marked done"
        else:
            task3_done = 0
            task3_status.text = "OPEN"
            app_status.text = "Slot 3 marked open"

    done_count = task1_done + task2_done + task3_done
    if done_count == 0:
        summary.text = "Done: 0/3"
    else:
        if done_count == 1:
            summary.text = "Done: 1/3"
        else:
            if done_count == 2:
                summary.text = "Done: 2/3"
            else:
                summary.text = "Done: 3/3"


@on_click("remove_task_1")
def _remove_task_1():
    if task1_active == 0:
        app_status.text = "Slot 1 already empty"
    else:
        task1_active = 0
        task1_done = 0
        task1_name.text = "(empty)"
        task1_status.text = "EMPTY"
        app_status.text = "Removed slot 1 task"

    done_count = task1_done + task2_done + task3_done
    if done_count == 0:
        summary.text = "Done: 0/3"
    else:
        if done_count == 1:
            summary.text = "Done: 1/3"
        else:
            if done_count == 2:
                summary.text = "Done: 2/3"
            else:
                summary.text = "Done: 3/3"


@on_click("remove_task_2")
def _remove_task_2():
    if task2_active == 0:
        app_status.text = "Slot 2 already empty"
    else:
        task2_active = 0
        task2_done = 0
        task2_name.text = "(empty)"
        task2_status.text = "EMPTY"
        app_status.text = "Removed slot 2 task"

    done_count = task1_done + task2_done + task3_done
    if done_count == 0:
        summary.text = "Done: 0/3"
    else:
        if done_count == 1:
            summary.text = "Done: 1/3"
        else:
            if done_count == 2:
                summary.text = "Done: 2/3"
            else:
                summary.text = "Done: 3/3"


@on_click("remove_task_3")
def _remove_task_3():
    if task3_active == 0:
        app_status.text = "Slot 3 already empty"
    else:
        task3_active = 0
        task3_done = 0
        task3_name.text = "(empty)"
        task3_status.text = "EMPTY"
        app_status.text = "Removed slot 3 task"

    done_count = task1_done + task2_done + task3_done
    if done_count == 0:
        summary.text = "Done: 0/3"
    else:
        if done_count == 1:
            summary.text = "Done: 1/3"
        else:
            if done_count == 2:
                summary.text = "Done: 2/3"
            else:
                summary.text = "Done: 3/3"


app_spec = app(
    activity(
        "MainActivity",
        app_config(
            package=APP_PACKAGE,
            min_sdk=APP_MIN_SDK,
            target_sdk=APP_TARGET_SDK,
            label=APP_LABEL,
        ),
        Theme(
            palette={
                "bg": "#FF000000",
                "surface": "#FF02140E",
                "surface_alt": "#FF05241A",
                "primary": "#FF10B981",
                "on_primary": "#FF00140D",
                "text": "#FFE7FFF6",
                "muted": "#FF7EE5C1",
                "danger": "#FFEF4444",
            },
            text=Style(text_color="text", text_size=sp(14)),
            button=Style(
                background="primary",
                text_color="on_primary",
                radius=dp(12),
                padding=(dp(12), dp(10), dp(12), dp(10)),
            ),
            input=Style(
                background="surface_alt",
                text_color="text",
                hint_color="muted",
                radius=dp(10),
                padding=(dp(10), dp(10), dp(10), dp(10)),
            ),
            container=Style(background="bg"),
            row=Style(background="bg"),
            column=Style(background="bg"),
        ),
        state(
            selected_template=0,
            task1_active=0,
            task1_done=0,
            task2_active=0,
            task2_done=0,
            task3_active=0,
            task3_done=0,
        ),
        ui(
            Column(
                Text("TODO // AMOLED EMERALD", id="title", text_size=sp(22), text_color="primary", padding=(dp(0), dp(0), dp(0), dp(6))),
                Text(
                    "Current static mode supports deterministic TODO slots. Arbitrary typed task capture is not available yet.",
                    id="limit_note",
                    text_color="muted",
                    padding=(dp(0), dp(0), dp(0), dp(10)),
                ),
                TextField(
                    "",
                    id="task_name_input",
                    hint="Task name input (dynamic capture pending)",
                    single_line=True,
                    margin=(dp(0), dp(0), dp(0), dp(8)),
                ),
                Text("Choose task template", id="template_label", text_color="primary", padding=(dp(0), dp(0), dp(0), dp(6))),
                Row(
                    Button("Groceries", id="pick_template_1", background="surface_alt", text_color="text"),
                    Button("Release", id="pick_template_2", background="surface_alt", text_color="text"),
                    Button("Docs", id="pick_template_3", background="surface_alt", text_color="text"),
                    id="template_row",
                    margin=(dp(0), dp(0), dp(0), dp(8)),
                ),
                Text("Template: Buy groceries", id="picked_hint", text_color="muted", padding=(dp(0), dp(0), dp(0), dp(8))),
                Button("Add Task", id="add_task", margin=(dp(0), dp(0), dp(0), dp(8))),
                Text("Done: 0/0", id="summary", text_size=sp(16), text_color="primary", padding=(dp(0), dp(0), dp(0), dp(4))),
                Text("Ready", id="app_status", text_color="muted", padding=(dp(0), dp(0), dp(0), dp(10))),
                Divider(id="sep_1", color="#FF0F3E2D", thickness=dp(1), margin=(dp(0), dp(0), dp(0), dp(10))),
                Text("Slot 1", id="slot1_title", text_color="primary"),
                Text("(empty)", id="task1_name", background="surface", padding=(dp(10), dp(10), dp(10), dp(10)), margin=(dp(0), dp(0), dp(0), dp(4))),
                Text("EMPTY", id="task1_status", text_color="muted", padding=(dp(0), dp(0), dp(0), dp(6))),
                Row(
                    Button("Done / Undo", id="toggle_task_1", background="surface_alt", text_color="text"),
                    Button("Remove", id="remove_task_1", background="danger", text_color="#FFFFFFFF"),
                    id="slot1_actions",
                    margin=(dp(0), dp(0), dp(0), dp(10)),
                ),
                Divider(id="sep_2", color="#FF0F3E2D", thickness=dp(1), margin=(dp(0), dp(0), dp(0), dp(10))),
                Text("Slot 2", id="slot2_title", text_color="primary"),
                Text("(empty)", id="task2_name", background="surface", padding=(dp(10), dp(10), dp(10), dp(10)), margin=(dp(0), dp(0), dp(0), dp(4))),
                Text("EMPTY", id="task2_status", text_color="muted", padding=(dp(0), dp(0), dp(0), dp(6))),
                Row(
                    Button("Done / Undo", id="toggle_task_2", background="surface_alt", text_color="text"),
                    Button("Remove", id="remove_task_2", background="danger", text_color="#FFFFFFFF"),
                    id="slot2_actions",
                    margin=(dp(0), dp(0), dp(0), dp(10)),
                ),
                Divider(id="sep_3", color="#FF0F3E2D", thickness=dp(1), margin=(dp(0), dp(0), dp(0), dp(10))),
                Text("Slot 3", id="slot3_title", text_color="primary"),
                Text("(empty)", id="task3_name", background="surface", padding=(dp(10), dp(10), dp(10), dp(10)), margin=(dp(0), dp(0), dp(0), dp(4))),
                Text("EMPTY", id="task3_status", text_color="muted", padding=(dp(0), dp(0), dp(0), dp(6))),
                Row(
                    Button("Done / Undo", id="toggle_task_3", background="surface_alt", text_color="text"),
                    Button("Remove", id="remove_task_3", background="danger", text_color="#FFFFFFFF"),
                    id="slot3_actions",
                ),
                id="root",
                background="bg",
                padding=(dp(14), dp(14), dp(14), dp(14)),
            )
        ),
        _pick_template_1,
        _pick_template_2,
        _pick_template_3,
        _add_task,
        _toggle_task_1,
        _toggle_task_2,
        _toggle_task_3,
        _remove_task_1,
        _remove_task_2,
        _remove_task_3,
    )
)

run(app_spec)
