# dsl/widgets.py


class _UIText:
    def __init__(
        self,
        text,
        *,
        id="label",
        layout=None,
        padding=None,
        margin=None,
        gravity=None,
        text_color=None,
        background=None,
        text_size=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.text = text
        self.layout = layout
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.text_color = text_color
        self.background = background
        self.text_size = text_size
        self.radius = radius
        self.style = style


class _UIButton:
    def __init__(
        self,
        text,
        *,
        id="button",
        layout=None,
        padding=None,
        margin=None,
        gravity=None,
        text_color=None,
        background=None,
        text_size=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.text = text
        self.layout = layout
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.text_color = text_color
        self.background = background
        self.text_size = text_size
        self.radius = radius
        self.style = style


class _UIRow:
    def __init__(
        self,
        *items,
        id="row",
        layout=None,
        padding=None,
        margin=None,
        gravity=None,
        background=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.items = items
        self.layout = layout
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.background = background
        self.radius = radius
        self.style = style


class _UIColumn:
    def __init__(
        self,
        *items,
        id="column",
        layout=None,
        padding=None,
        margin=None,
        gravity=None,
        background=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.items = items
        self.layout = layout
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.background = background
        self.radius = radius
        self.style = style


class _UIAppBar(_UIText):
    pass


class _UIFloatingActionButton(_UIButton):
    pass


class _UIRaisedButton(_UIButton):
    pass


class _UIFlatButton(_UIButton):
    pass


class _UIIconButton(_UIButton):
    pass


class _UITextField(_UIText):
    def __init__(self, text="", *, hint=None, **kwargs):
        super().__init__(text, **kwargs)
        self.hint = hint


class _UICheckbox(_UIText):
    def __init__(self, text="", *, checked=False, **kwargs):
        super().__init__(text, **kwargs)
        self.checked = checked


class _UIRadio(_UIText):
    def __init__(self, text="", *, checked=False, **kwargs):
        super().__init__(text, **kwargs)
        self.checked = checked


class _UISwitch(_UIText):
    def __init__(self, text="", *, checked=False, **kwargs):
        super().__init__(text, **kwargs)
        self.checked = checked


class _UISlider(_UIButton):
    def __init__(self, *, value=0, min=0, max=100, **kwargs):
        super().__init__("", **kwargs)
        self.value = value
        self.min = min
        self.max = max


class _UIDropdownButton(_UIButton):
    def __init__(self, *, items=None, **kwargs):
        super().__init__("", **kwargs)
        self.items = items or []


class _UIButtonBar(_UIRow):
    pass


class _UIPopupMenuButton(_UIButton):
    def __init__(self, text="Menu", *, items=None, **kwargs):
        super().__init__(text, **kwargs)
        self.items = items or []


class _UISimpleDialog:
    def __init__(self, title, message):
        self.title = title
        self.message = message


class _UIToast:
    def __init__(self, message, duration=0):
        self.message = message
        self.duration = duration


class _UISnackbar:
    def __init__(self, message, duration=0):
        self.message = message
        self.duration = duration


class State:
    def __init__(self, **kwargs):
        self.values = kwargs


class Style:
    def __init__(
        self,
        *,
        layout=None,
        padding=None,
        margin=None,
        gravity=None,
        text_color=None,
        background=None,
        text_size=None,
        radius=None,
    ):
        self.layout = layout
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.text_color = text_color
        self.background = background
        self.text_size = text_size
        self.radius = radius

    def merged(self, override):
        if override is None:
            return self
        return Style(
            layout=override.layout if override.layout is not None else self.layout,
            padding=override.padding if override.padding is not None else self.padding,
            margin=override.margin if override.margin is not None else self.margin,
            gravity=override.gravity if override.gravity is not None else self.gravity,
            text_color=override.text_color if override.text_color is not None else self.text_color,
            background=override.background if override.background is not None else self.background,
            text_size=override.text_size if override.text_size is not None else self.text_size,
            radius=override.radius if override.radius is not None else self.radius,
        )


class Theme:
    def __init__(
        self,
        *,
        palette=None,
        text=None,
        button=None,
        row=None,
        column=None,
    ):
        self.palette = palette or {}
        self.text = text or Style()
        self.button = button or Style()
        self.row = row or Style()
        self.column = column or Style()


class Presets:
    def __init__(self, *, palette=None):
        palette = palette or {}
        self.palette = palette

    def PrimaryButton(self, **overrides):
        return Style(
            background=self.palette.get("primary", "#2563EB"),
            text_color=self.palette.get("on_primary", "#FFFFFF"),
            text_size=16,
            radius=16,
            padding=(12, 12, 12, 12),
        ).merged(Style(**overrides))

    def DangerButton(self, **overrides):
        return Style(
            background=self.palette.get("danger", "#EF4444"),
            text_color=self.palette.get("on_danger", "#FFFFFF"),
            text_size=16,
            radius=16,
            padding=(12, 12, 12, 12),
        ).merged(Style(**overrides))

    def MutedText(self, **overrides):
        return Style(
            text_color=self.palette.get("muted", "#6B7280"),
            text_size=14,
        ).merged(Style(**overrides))

    def Card(self, **overrides):
        return Style(
            background=self.palette.get("card", "#FFFFFF"),
            radius=16,
            padding=(12, 12, 12, 12),
        ).merged(Style(**overrides))


class Text(_UIText):
    pass


class Button(_UIButton):
    pass


class Row(_UIRow):
    pass


class Column(_UIColumn):
    pass


class AppBar(_UIAppBar):
    pass


class FloatingActionButton(_UIFloatingActionButton):
    pass


class RaisedButton(_UIRaisedButton):
    pass


class FlatButton(_UIFlatButton):
    pass


class IconButton(_UIIconButton):
    pass


class TextField(_UITextField):
    pass


class Checkbox(_UICheckbox):
    pass


class Radio(_UIRadio):
    pass


class Switch(_UISwitch):
    pass


class Slider(_UISlider):
    pass


class DropdownButton(_UIDropdownButton):
    pass


class ButtonBar(_UIButtonBar):
    pass


class PopupMenuButton(_UIPopupMenuButton):
    pass


def text(
    text,
    *,
    id="label",
    layout=None,
    padding=None,
    margin=None,
    gravity=None,
    text_color=None,
    background=None,
    text_size=None,
    radius=None,
    style=None,
):
    return _UIText(
        text,
        id=id,
        layout=layout,
        padding=padding,
        margin=margin,
        gravity=gravity,
        text_color=text_color,
        background=background,
        text_size=text_size,
        radius=radius,
        style=style,
    )


def button(
    text,
    *,
    id="button",
    layout=None,
    padding=None,
    margin=None,
    gravity=None,
    text_color=None,
    background=None,
    text_size=None,
    radius=None,
    style=None,
):
    return _UIButton(
        text,
        id=id,
        layout=layout,
        padding=padding,
        margin=margin,
        gravity=gravity,
        text_color=text_color,
        background=background,
        text_size=text_size,
        radius=radius,
        style=style,
    )


def row(
    *items,
    id="row",
    layout=None,
    padding=None,
    margin=None,
    gravity=None,
    background=None,
    radius=None,
    style=None,
):
    return _UIRow(
        *items,
        id=id,
        layout=layout,
        padding=padding,
        margin=margin,
        gravity=gravity,
        background=background,
        radius=radius,
        style=style,
    )


def column(
    *items,
    id="column",
    layout=None,
    padding=None,
    margin=None,
    gravity=None,
    background=None,
    radius=None,
    style=None,
):
    return _UIColumn(
        *items,
        id=id,
        layout=layout,
        padding=padding,
        margin=margin,
        gravity=gravity,
        background=background,
        radius=radius,
        style=style,
    )


def app_bar(title, *, id="appbar", **kwargs):
    return _UIAppBar(title, id=id, **kwargs)


def floating_action_button(text="+", *, id="fab", **kwargs):
    return _UIFloatingActionButton(text, id=id, **kwargs)


def raised_button(text, *, id="raised_btn", **kwargs):
    return _UIRaisedButton(text, id=id, **kwargs)


def flat_button(text, *, id="flat_btn", **kwargs):
    return _UIFlatButton(text, id=id, **kwargs)


def icon_button(icon_text="*", *, id="icon_btn", **kwargs):
    return _UIIconButton(icon_text, id=id, **kwargs)


def text_field(text="", *, id="input", hint=None, **kwargs):
    return _UITextField(text, id=id, hint=hint, **kwargs)


def checkbox(text="", *, id="checkbox", checked=False, **kwargs):
    return _UICheckbox(text, id=id, checked=checked, **kwargs)


def radio(text="", *, id="radio", checked=False, **kwargs):
    return _UIRadio(text, id=id, checked=checked, **kwargs)


def switch(text="", *, id="switch", checked=False, **kwargs):
    return _UISwitch(text, id=id, checked=checked, **kwargs)


def slider(*, id="slider", value=0, min=0, max=100, **kwargs):
    return _UISlider(id=id, value=value, min=min, max=max, **kwargs)


def dropdown_button(*, id="dropdown", items=None, **kwargs):
    return _UIDropdownButton(id=id, items=items or [], **kwargs)


def button_bar(*items, id="button_bar", **kwargs):
    return _UIButtonBar(*items, id=id, **kwargs)


def popup_menu_button(text="Menu", *, id="popup", items=None, **kwargs):
    return _UIPopupMenuButton(text, id=id, items=items or [], **kwargs)


def simple_dialog(title, message):
    return _UISimpleDialog(title, message)


def toast(message, duration=0):
    return _UIToast(message, duration=duration)


def snackbar(message, duration=0):
    return _UISnackbar(message, duration=duration)


def style(**kwargs):
    return Style(**kwargs)


def theme(**kwargs):
    return Theme(**kwargs)


def presets(palette=None):
    return Presets(palette=palette)


def state(**kwargs):
    return State(**kwargs)
