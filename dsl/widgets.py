# dsl/widgets.py

max_width = "max_width"
max_height = "max_height"
wrap_width = "wrap"
wrap_height = "wrap"


class Dp:
    def __init__(self, value):
        self.value = float(value)

    def __repr__(self):
        return f"dp({self.value})"


class Sp:
    def __init__(self, value):
        self.value = float(value)

    def __repr__(self):
        return f"sp({self.value})"


class Px:
    def __init__(self, value):
        self.value = float(value)

    def __repr__(self):
        return f"px({self.value})"


class Percent:
    def __init__(self, value):
        self.value = float(value)

    def __repr__(self):
        return f"percent({self.value})"


def fill():
    return "match_parent"


def wrap():
    return "wrap"


def size(width, height):
    return (width, height)


class _Unit:
    def __init__(self, name, cls):
        self.name = name
        self.cls = cls

    def __call__(self, value):
        return self.cls(value)

    def __rmul__(self, value):
        return self.cls(value)

    def __repr__(self):
        return self.name


dp = _Unit("dp", Dp)
sp = _Unit("sp", Sp)
px = _Unit("px", Px)
percent = _Unit("percent", Percent)


class _UIText:
    def __init__(
        self,
        text,
        *,
        id="label",
        layout=None,
        width=None,
        height=None,
        padding=None,
        margin=None,
        gravity=None,
        weight=None,
        relative=None,
        constraints=None,
        text_color=None,
        background=None,
        text_size=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.text = text
        self.width = width
        self.height = height
        self.layout = _layout_with_size(layout, width, height)
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.weight = weight
        self.relative = relative
        self.constraints = constraints
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
        width=None,
        height=None,
        padding=None,
        margin=None,
        gravity=None,
        weight=None,
        relative=None,
        constraints=None,
        text_color=None,
        background=None,
        text_size=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.text = text
        self.width = width
        self.height = height
        self.layout = _layout_with_size(layout, width, height)
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.weight = weight
        self.relative = relative
        self.constraints = constraints
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
        width=None,
        height=None,
        padding=None,
        margin=None,
        gravity=None,
        align=None,
        arrangement=None,
        weight_sum=None,
        relative=None,
        constraints=None,
        background=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.items = items
        self.width = width
        self.height = height
        self.layout = _layout_with_size(layout, width, height, default=("match_parent", "wrap"))
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.align = align
        self.arrangement = arrangement
        self.weight_sum = weight_sum
        self.relative = relative
        self.constraints = constraints
        self.background = background
        self.radius = radius
        self.style = style


class _UIColumn:
    def __init__(
        self,
        *items,
        id="column",
        layout=None,
        width=None,
        height=None,
        padding=None,
        margin=None,
        gravity=None,
        align=None,
        arrangement=None,
        weight_sum=None,
        relative=None,
        constraints=None,
        background=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.items = items
        self.width = width
        self.height = height
        self.layout = _layout_with_size(layout, width, height)
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.align = align
        self.arrangement = arrangement
        self.weight_sum = weight_sum
        self.relative = relative
        self.constraints = constraints
        self.background = background
        self.radius = radius
        self.style = style


class _UIRelative:
    def __init__(
        self,
        *items,
        id="relative",
        layout=None,
        width=None,
        height=None,
        padding=None,
        margin=None,
        gravity=None,
        background=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.items = items
        self.width = width
        self.height = height
        self.layout = _layout_with_size(layout, width, height)
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.background = background
        self.radius = radius
        self.style = style


class _UIConstraint:
    def __init__(
        self,
        *items,
        id="constraint",
        layout=None,
        width=None,
        height=None,
        padding=None,
        margin=None,
        gravity=None,
        background=None,
        radius=None,
        style=None,
    ):
        self.id = id
        self.items = items
        self.width = width
        self.height = height
        self.layout = _layout_with_size(layout, width, height)
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.background = background
        self.radius = radius
        self.style = style


class _UIAppBar(_UIText):
    def __init__(self, text, *, id="appbar", inline=False, **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)
        self.inline = inline


class _UIFloatingActionButton(_UIButton):
    def __init__(self, text="+", *, id="fab", **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)
        self.floating = True


class _UIRaisedButton(_UIButton):
    def __init__(self, text, *, id="raised_btn", **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)


class _UIFlatButton(_UIButton):
    def __init__(self, text, *, id="flat_btn", **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)


class _UIIconButton(_UIButton):
    def __init__(self, text="*", *, id="icon_btn", **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)


class _UITextField(_UIText):
    def __init__(self, text="", *, id="input", hint=None, **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)
        self.hint = hint


class _UICheckbox(_UIText):
    def __init__(self, text="", *, id="checkbox", checked=False, **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)
        self.checked = checked


class _UIRadio(_UIText):
    def __init__(self, text="", *, id="radio", checked=False, **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)
        self.checked = checked


class _UISwitch(_UIText):
    def __init__(self, text="", *, id="switch", checked=False, **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)
        self.checked = checked


class _UISlider(_UIButton):
    def __init__(self, *, id="slider", value=0, min=0, max=100, **kwargs):
        kwargs.setdefault("id", id)
        super().__init__("", **kwargs)
        self.value = value
        self.min = min
        self.max = max


class _UIDropdownButton(_UIButton):
    def __init__(self, *, id="dropdown", items=None, **kwargs):
        kwargs.setdefault("id", id)
        super().__init__("", **kwargs)
        self.items = items or []


class _UIButtonBar(_UIRow):
    def __init__(self, *items, id="button_bar", **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(*items, **kwargs)


class _UIPopupMenuButton(_UIButton):
    def __init__(self, text="Menu", *, id="popup", items=None, **kwargs):
        kwargs.setdefault("id", id)
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
        width=None,
        height=None,
        padding=None,
        margin=None,
        gravity=None,
        weight=None,
        align=None,
        arrangement=None,
        weight_sum=None,
        relative=None,
        constraints=None,
        text_color=None,
        background=None,
        text_size=None,
        radius=None,
    ):
        self.layout = layout
        self.width = width
        self.height = height
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.weight = weight
        self.align = align
        self.arrangement = arrangement
        self.weight_sum = weight_sum
        self.relative = relative
        self.constraints = constraints
        self.text_color = text_color
        self.background = background
        self.text_size = text_size
        self.radius = radius

    def merged(self, override):
        if override is None:
            return self
        return Style(
            layout=override.layout if override.layout is not None else self.layout,
            width=override.width if override.width is not None else self.width,
            height=override.height if override.height is not None else self.height,
            padding=override.padding if override.padding is not None else self.padding,
            margin=override.margin if override.margin is not None else self.margin,
            gravity=override.gravity if override.gravity is not None else self.gravity,
            weight=override.weight if override.weight is not None else self.weight,
            align=override.align if override.align is not None else self.align,
            arrangement=override.arrangement if override.arrangement is not None else self.arrangement,
            weight_sum=override.weight_sum if override.weight_sum is not None else self.weight_sum,
            relative=override.relative if override.relative is not None else self.relative,
            constraints=override.constraints if override.constraints is not None else self.constraints,
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
            text_size=sp(16),
            radius=dp(16),
            padding=(dp(12), dp(12), dp(12), dp(12)),
        ).merged(Style(**overrides))

    def DangerButton(self, **overrides):
        return Style(
            background=self.palette.get("danger", "#EF4444"),
            text_color=self.palette.get("on_danger", "#FFFFFF"),
            text_size=sp(16),
            radius=dp(16),
            padding=(dp(12), dp(12), dp(12), dp(12)),
        ).merged(Style(**overrides))

    def MutedText(self, **overrides):
        return Style(
            text_color=self.palette.get("muted", "#6B7280"),
            text_size=sp(14),
        ).merged(Style(**overrides))

    def Card(self, **overrides):
        return Style(
            background=self.palette.get("card", "#FFFFFF"),
            radius=dp(16),
            padding=(dp(12), dp(12), dp(12), dp(12)),
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


class Relative(_UIRelative):
    pass


class Constraint(_UIConstraint):
    pass


def _layout_with_size(layout, width, height, default=None):
    if layout is None:
        layout = default
    if width is None and height is None:
        return layout
    if layout is None:
        base = ("wrap", "wrap")
    elif isinstance(layout, str):
        base = (layout, layout)
    else:
        base = (layout[0], layout[1])
    return (
        width if width is not None else base[0],
        height if height is not None else base[1],
    )


def text(
    text,
    *,
    id="label",
    layout=None,
    width=None,
    height=None,
    padding=None,
    margin=None,
    gravity=None,
    weight=None,
    relative=None,
    constraints=None,
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
        width=width,
        height=height,
        padding=padding,
        margin=margin,
        gravity=gravity,
        weight=weight,
        relative=relative,
        constraints=constraints,
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
    width=None,
    height=None,
    padding=None,
    margin=None,
    gravity=None,
    weight=None,
    relative=None,
    constraints=None,
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
        width=width,
        height=height,
        padding=padding,
        margin=margin,
        gravity=gravity,
        weight=weight,
        relative=relative,
        constraints=constraints,
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
    width=None,
    height=None,
    padding=None,
    margin=None,
    gravity=None,
    align=None,
    arrangement=None,
    weight_sum=None,
    relative=None,
    constraints=None,
    background=None,
    radius=None,
    style=None,
):
    return _UIRow(
        *items,
        id=id,
        layout=layout,
        width=width,
        height=height,
        padding=padding,
        margin=margin,
        gravity=gravity,
        align=align,
        arrangement=arrangement,
        weight_sum=weight_sum,
        relative=relative,
        constraints=constraints,
        background=background,
        radius=radius,
        style=style,
    )


def column(
    *items,
    id="column",
    layout=None,
    width=None,
    height=None,
    padding=None,
    margin=None,
    gravity=None,
    align=None,
    arrangement=None,
    weight_sum=None,
    relative=None,
    constraints=None,
    background=None,
    radius=None,
    style=None,
):
    return _UIColumn(
        *items,
        id=id,
        layout=layout,
        width=width,
        height=height,
        padding=padding,
        margin=margin,
        gravity=gravity,
        align=align,
        arrangement=arrangement,
        weight_sum=weight_sum,
        relative=relative,
        constraints=constraints,
        background=background,
        radius=radius,
        style=style,
    )


def relative(
    *items,
    id="relative",
    layout=None,
    width=None,
    height=None,
    padding=None,
    margin=None,
    gravity=None,
    background=None,
    radius=None,
    style=None,
):
    return _UIRelative(
        *items,
        id=id,
        layout=layout,
        width=width,
        height=height,
        padding=padding,
        margin=margin,
        gravity=gravity,
        background=background,
        radius=radius,
        style=style,
    )


def constraint(
    *items,
    id="constraint",
    layout=None,
    width=None,
    height=None,
    padding=None,
    margin=None,
    gravity=None,
    background=None,
    radius=None,
    style=None,
):
    return _UIConstraint(
        *items,
        id=id,
        layout=layout,
        width=width,
        height=height,
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


def exit_app():
    from .ast import _StmtExitApp

    return _StmtExitApp()


def core(widget):
    setattr(widget, "_plugin_override", "core")
    return widget


def style(**kwargs):
    return Style(**kwargs)


def theme(**kwargs):
    return Theme(**kwargs)


def presets(palette=None):
    return Presets(palette=palette)


def state(**kwargs):
    return State(**kwargs)
