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


def gradient(start, end, direction="left_to_right"):
    return Gradient(start=start, end=end, direction=direction)


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


class ColorState:
    def __init__(
        self,
        *,
        default,
        pressed=None,
        disabled=None,
        selected=None,
        focused=None,
    ):
        if default is None:
            raise RuntimeError("ColorState requires a default color.")
        self.default = default
        self.pressed = pressed
        self.disabled = disabled
        self.selected = selected
        self.focused = focused


class Gradient:
    def __init__(self, start, end, direction="left_to_right"):
        self.start = start
        self.end = end
        self.direction = direction


def _resolve_content_description(content_description, accessibility_label):
    if content_description is not None:
        return content_description
    return accessibility_label


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
        font_family=None,
        font_weight=None,
        font_style=None,
        letter_spacing=None,
        line_height=None,
        text_alignment=None,
        all_caps=None,
        max_lines=None,
        ellipsize=None,
        tint=None,
        thumb_tint=None,
        track_tint=None,
        progress_tint=None,
        button_tint=None,
        content_description=None,
        important_for_accessibility=None,
        accessibility_label=None,
        elevation=None,
        pressed_elevation=None,
        text_shadow_color=None,
        text_shadow_radius=None,
        text_shadow_dx=None,
        text_shadow_dy=None,
        opacity=None,
        border_width=None,
        border_color=None,
        border_radius=None,
        ripple_color=None,
        blur_radius=None,
        rotation=None,
        scale_x=None,
        scale_y=None,
        translation_x=None,
        translation_y=None,
        clip_to_outline=None,
        clip_children=None,
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
        self.font_family = font_family
        self.font_weight = font_weight
        self.font_style = font_style
        self.letter_spacing = letter_spacing
        self.line_height = line_height
        self.text_alignment = text_alignment
        self.all_caps = all_caps
        self.max_lines = max_lines
        self.ellipsize = ellipsize
        self.tint = tint
        self.thumb_tint = thumb_tint
        self.track_tint = track_tint
        self.progress_tint = progress_tint
        self.button_tint = button_tint
        self.content_description = _resolve_content_description(content_description, accessibility_label)
        self.important_for_accessibility = important_for_accessibility
        self.accessibility_label = accessibility_label
        self.elevation = elevation
        self.pressed_elevation = pressed_elevation
        self.text_shadow_color = text_shadow_color
        self.text_shadow_radius = text_shadow_radius
        self.text_shadow_dx = text_shadow_dx
        self.text_shadow_dy = text_shadow_dy
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.ripple_color = ripple_color
        self.blur_radius = blur_radius
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.translation_x = translation_x
        self.translation_y = translation_y
        self.clip_to_outline = clip_to_outline
        self.clip_children = clip_children
        self.style = style


class _UIButton:
    def __init__(
        self,
        text,
        *,
        id="button",
        icon=None,
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
        font_family=None,
        font_weight=None,
        font_style=None,
        letter_spacing=None,
        line_height=None,
        text_alignment=None,
        all_caps=None,
        max_lines=None,
        ellipsize=None,
        tint=None,
        thumb_tint=None,
        track_tint=None,
        progress_tint=None,
        button_tint=None,
        content_description=None,
        important_for_accessibility=None,
        accessibility_label=None,
        elevation=None,
        pressed_elevation=None,
        text_shadow_color=None,
        text_shadow_radius=None,
        text_shadow_dx=None,
        text_shadow_dy=None,
        opacity=None,
        border_width=None,
        border_color=None,
        border_radius=None,
        ripple_color=None,
        blur_radius=None,
        rotation=None,
        scale_x=None,
        scale_y=None,
        translation_x=None,
        translation_y=None,
        clip_to_outline=None,
        clip_children=None,
        style=None,
    ):
        self.id = id
        self.text = text
        self.icon = icon
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
        self.font_family = font_family
        self.font_weight = font_weight
        self.font_style = font_style
        self.letter_spacing = letter_spacing
        self.line_height = line_height
        self.text_alignment = text_alignment
        self.all_caps = all_caps
        self.max_lines = max_lines
        self.ellipsize = ellipsize
        self.tint = tint
        self.thumb_tint = thumb_tint
        self.track_tint = track_tint
        self.progress_tint = progress_tint
        self.button_tint = button_tint
        self.content_description = _resolve_content_description(content_description, accessibility_label)
        self.important_for_accessibility = important_for_accessibility
        self.accessibility_label = accessibility_label
        self.elevation = elevation
        self.pressed_elevation = pressed_elevation
        self.text_shadow_color = text_shadow_color
        self.text_shadow_radius = text_shadow_radius
        self.text_shadow_dx = text_shadow_dx
        self.text_shadow_dy = text_shadow_dy
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.ripple_color = ripple_color
        self.blur_radius = blur_radius
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.translation_x = translation_x
        self.translation_y = translation_y
        self.clip_to_outline = clip_to_outline
        self.clip_children = clip_children
        self.style = style


class _UIView:
    def __init__(
        self,
        *,
        id="view",
        layout=None,
        width=None,
        height=None,
        padding=None,
        margin=None,
        gravity=None,
        weight=None,
        relative=None,
        constraints=None,
        background=None,
        radius=None,
        tint=None,
        thumb_tint=None,
        track_tint=None,
        progress_tint=None,
        button_tint=None,
        content_description=None,
        important_for_accessibility=None,
        accessibility_label=None,
        elevation=None,
        pressed_elevation=None,
        text_shadow_color=None,
        text_shadow_radius=None,
        text_shadow_dx=None,
        text_shadow_dy=None,
        opacity=None,
        border_width=None,
        border_color=None,
        border_radius=None,
        ripple_color=None,
        blur_radius=None,
        rotation=None,
        scale_x=None,
        scale_y=None,
        translation_x=None,
        translation_y=None,
        clip_to_outline=None,
        clip_children=None,
        style=None,
    ):
        self.id = id
        self.width = width
        self.height = height
        self.layout = _layout_with_size(layout, width, height)
        self.padding = padding
        self.margin = margin
        self.gravity = gravity
        self.weight = weight
        self.relative = relative
        self.constraints = constraints
        self.background = background
        self.radius = radius
        self.tint = tint
        self.thumb_tint = thumb_tint
        self.track_tint = track_tint
        self.progress_tint = progress_tint
        self.button_tint = button_tint
        self.content_description = _resolve_content_description(content_description, accessibility_label)
        self.important_for_accessibility = important_for_accessibility
        self.accessibility_label = accessibility_label
        self.elevation = elevation
        self.pressed_elevation = pressed_elevation
        self.text_shadow_color = text_shadow_color
        self.text_shadow_radius = text_shadow_radius
        self.text_shadow_dx = text_shadow_dx
        self.text_shadow_dy = text_shadow_dy
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.ripple_color = ripple_color
        self.blur_radius = blur_radius
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.translation_x = translation_x
        self.translation_y = translation_y
        self.clip_to_outline = clip_to_outline
        self.clip_children = clip_children
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
        content_description=None,
        important_for_accessibility=None,
        accessibility_label=None,
        elevation=None,
        pressed_elevation=None,
        text_shadow_color=None,
        text_shadow_radius=None,
        text_shadow_dx=None,
        text_shadow_dy=None,
        opacity=None,
        border_width=None,
        border_color=None,
        border_radius=None,
        ripple_color=None,
        blur_radius=None,
        rotation=None,
        scale_x=None,
        scale_y=None,
        translation_x=None,
        translation_y=None,
        clip_to_outline=None,
        clip_children=None,
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
        self.content_description = _resolve_content_description(content_description, accessibility_label)
        self.important_for_accessibility = important_for_accessibility
        self.accessibility_label = accessibility_label
        self.elevation = elevation
        self.pressed_elevation = pressed_elevation
        self.text_shadow_color = text_shadow_color
        self.text_shadow_radius = text_shadow_radius
        self.text_shadow_dx = text_shadow_dx
        self.text_shadow_dy = text_shadow_dy
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.ripple_color = ripple_color
        self.blur_radius = blur_radius
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.translation_x = translation_x
        self.translation_y = translation_y
        self.clip_to_outline = clip_to_outline
        self.clip_children = clip_children
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
        content_description=None,
        important_for_accessibility=None,
        accessibility_label=None,
        elevation=None,
        pressed_elevation=None,
        text_shadow_color=None,
        text_shadow_radius=None,
        text_shadow_dx=None,
        text_shadow_dy=None,
        opacity=None,
        border_width=None,
        border_color=None,
        border_radius=None,
        ripple_color=None,
        blur_radius=None,
        rotation=None,
        scale_x=None,
        scale_y=None,
        translation_x=None,
        translation_y=None,
        clip_to_outline=None,
        clip_children=None,
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
        self.content_description = _resolve_content_description(content_description, accessibility_label)
        self.important_for_accessibility = important_for_accessibility
        self.accessibility_label = accessibility_label
        self.elevation = elevation
        self.pressed_elevation = pressed_elevation
        self.text_shadow_color = text_shadow_color
        self.text_shadow_radius = text_shadow_radius
        self.text_shadow_dx = text_shadow_dx
        self.text_shadow_dy = text_shadow_dy
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.ripple_color = ripple_color
        self.blur_radius = blur_radius
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.translation_x = translation_x
        self.translation_y = translation_y
        self.clip_to_outline = clip_to_outline
        self.clip_children = clip_children
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
        content_description=None,
        important_for_accessibility=None,
        accessibility_label=None,
        elevation=None,
        pressed_elevation=None,
        text_shadow_color=None,
        text_shadow_radius=None,
        text_shadow_dx=None,
        text_shadow_dy=None,
        opacity=None,
        border_width=None,
        border_color=None,
        border_radius=None,
        ripple_color=None,
        blur_radius=None,
        rotation=None,
        scale_x=None,
        scale_y=None,
        translation_x=None,
        translation_y=None,
        clip_to_outline=None,
        clip_children=None,
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
        self.content_description = _resolve_content_description(content_description, accessibility_label)
        self.important_for_accessibility = important_for_accessibility
        self.accessibility_label = accessibility_label
        self.elevation = elevation
        self.pressed_elevation = pressed_elevation
        self.text_shadow_color = text_shadow_color
        self.text_shadow_radius = text_shadow_radius
        self.text_shadow_dx = text_shadow_dx
        self.text_shadow_dy = text_shadow_dy
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.ripple_color = ripple_color
        self.blur_radius = blur_radius
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.translation_x = translation_x
        self.translation_y = translation_y
        self.clip_to_outline = clip_to_outline
        self.clip_children = clip_children
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
        content_description=None,
        important_for_accessibility=None,
        accessibility_label=None,
        elevation=None,
        pressed_elevation=None,
        text_shadow_color=None,
        text_shadow_radius=None,
        text_shadow_dx=None,
        text_shadow_dy=None,
        opacity=None,
        border_width=None,
        border_color=None,
        border_radius=None,
        ripple_color=None,
        blur_radius=None,
        rotation=None,
        scale_x=None,
        scale_y=None,
        translation_x=None,
        translation_y=None,
        clip_to_outline=None,
        clip_children=None,
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
        self.content_description = _resolve_content_description(content_description, accessibility_label)
        self.important_for_accessibility = important_for_accessibility
        self.accessibility_label = accessibility_label
        self.elevation = elevation
        self.pressed_elevation = pressed_elevation
        self.text_shadow_color = text_shadow_color
        self.text_shadow_radius = text_shadow_radius
        self.text_shadow_dx = text_shadow_dx
        self.text_shadow_dy = text_shadow_dy
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.ripple_color = ripple_color
        self.blur_radius = blur_radius
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.translation_x = translation_x
        self.translation_y = translation_y
        self.clip_to_outline = clip_to_outline
        self.clip_children = clip_children
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
    def __init__(
        self,
        text="",
        *,
        id="input",
        hint=None,
        input_type=None,
        ime_options=None,
        max_length=None,
        single_line=None,
        password=False,
        auto_capitalize=None,
        numeric_only=False,
        **kwargs,
    ):
        kwargs.setdefault("id", id)
        super().__init__(text, **kwargs)
        self.hint = hint
        self.input_type = input_type
        self.ime_options = ime_options
        self.max_length = max_length
        self.single_line = single_line
        self.password = password
        self.auto_capitalize = auto_capitalize
        self.numeric_only = numeric_only


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


class _UIDivider(_UIView):
    def __init__(self, *, id="divider", color="#FFD1D5DB", thickness=dp(1), **kwargs):
        kwargs.setdefault("id", id)
        kwargs.setdefault("layout", ("match_parent", thickness))
        kwargs.setdefault("background", color)
        super().__init__(**kwargs)


class _UIImage(_UIView):
    def __init__(
        self,
        *,
        id="image",
        src=None,
        content_description=None,
        accessibility_label=None,
        **kwargs,
    ):
        kwargs.setdefault("id", id)
        super().__init__(
            content_description=content_description,
            accessibility_label=accessibility_label,
            **kwargs,
        )
        self.src = src


class _UIContainer(_UIColumn):
    def __init__(self, *items, id="container", **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(*items, **kwargs)


class _UICard(_UIColumn):
    def __init__(self, *items, id="card", **kwargs):
        kwargs.setdefault("id", id)
        kwargs.setdefault("background", "#FFFFFFFF")
        kwargs.setdefault("radius", dp(12))
        kwargs.setdefault("padding", dp(12))
        super().__init__(*items, **kwargs)


class _UIIcon(_UIText):
    def __init__(self, name, *, id="icon", **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(name, **kwargs)


class _UIRadioGroup(_UIColumn):
    def __init__(self, *items, id="radio_group", orientation="vertical", **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(*items, **kwargs)
        self.orientation = str(orientation or "vertical").lower()


class _UIProgressBar(_UIView):
    def __init__(self, *, id="progress", value=0, min=0, max=100, indeterminate=False, **kwargs):
        kwargs.setdefault("id", id)
        super().__init__(**kwargs)
        self.value = value
        self.min = min
        self.max = max
        self.indeterminate = bool(indeterminate)


# TODO(material-pending): Add DSL primitives for pending Material components.
# Planned additions:
# - NumberField, Rating, TransferList, ToggleButtonGroup
# - Avatar, Badge, Chip, List, Table, Tooltip, Typography helpers
# - Alert, Backdrop, Skeleton
# - Accordion, Paper
# - BottomNavigation, Breadcrumbs, Drawer, Link, Pagination, SpeedDial, Stepper, Tabs


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
        font_family=None,
        font_weight=None,
        font_style=None,
        letter_spacing=None,
        line_height=None,
        text_alignment=None,
        all_caps=None,
        max_lines=None,
        ellipsize=None,
        tint=None,
        thumb_tint=None,
        track_tint=None,
        progress_tint=None,
        button_tint=None,
        elevation=None,
        pressed_elevation=None,
        text_shadow_color=None,
        text_shadow_radius=None,
        text_shadow_dx=None,
        text_shadow_dy=None,
        opacity=None,
        border_width=None,
        border_color=None,
        border_radius=None,
        ripple_color=None,
        blur_radius=None,
        rotation=None,
        scale_x=None,
        scale_y=None,
        translation_x=None,
        translation_y=None,
        clip_to_outline=None,
        clip_children=None,
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
        self.font_family = font_family
        self.font_weight = font_weight
        self.font_style = font_style
        self.letter_spacing = letter_spacing
        self.line_height = line_height
        self.text_alignment = text_alignment
        self.all_caps = all_caps
        self.max_lines = max_lines
        self.ellipsize = ellipsize
        self.tint = tint
        self.thumb_tint = thumb_tint
        self.track_tint = track_tint
        self.progress_tint = progress_tint
        self.button_tint = button_tint
        self.elevation = elevation
        self.pressed_elevation = pressed_elevation
        self.text_shadow_color = text_shadow_color
        self.text_shadow_radius = text_shadow_radius
        self.text_shadow_dx = text_shadow_dx
        self.text_shadow_dy = text_shadow_dy
        self.opacity = opacity
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.ripple_color = ripple_color
        self.blur_radius = blur_radius
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.translation_x = translation_x
        self.translation_y = translation_y
        self.clip_to_outline = clip_to_outline
        self.clip_children = clip_children

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
            font_family=override.font_family if override.font_family is not None else self.font_family,
            font_weight=override.font_weight if override.font_weight is not None else self.font_weight,
            font_style=override.font_style if override.font_style is not None else self.font_style,
            letter_spacing=override.letter_spacing if override.letter_spacing is not None else self.letter_spacing,
            line_height=override.line_height if override.line_height is not None else self.line_height,
            text_alignment=override.text_alignment if override.text_alignment is not None else self.text_alignment,
            all_caps=override.all_caps if override.all_caps is not None else self.all_caps,
            max_lines=override.max_lines if override.max_lines is not None else self.max_lines,
            ellipsize=override.ellipsize if override.ellipsize is not None else self.ellipsize,
            tint=override.tint if override.tint is not None else self.tint,
            thumb_tint=override.thumb_tint if override.thumb_tint is not None else self.thumb_tint,
            track_tint=override.track_tint if override.track_tint is not None else self.track_tint,
            progress_tint=override.progress_tint if override.progress_tint is not None else self.progress_tint,
            button_tint=override.button_tint if override.button_tint is not None else self.button_tint,
            elevation=override.elevation if override.elevation is not None else self.elevation,
            pressed_elevation=(
                override.pressed_elevation
                if override.pressed_elevation is not None
                else self.pressed_elevation
            ),
            text_shadow_color=(
                override.text_shadow_color
                if override.text_shadow_color is not None
                else self.text_shadow_color
            ),
            text_shadow_radius=(
                override.text_shadow_radius
                if override.text_shadow_radius is not None
                else self.text_shadow_radius
            ),
            text_shadow_dx=(
                override.text_shadow_dx if override.text_shadow_dx is not None else self.text_shadow_dx
            ),
            text_shadow_dy=(
                override.text_shadow_dy if override.text_shadow_dy is not None else self.text_shadow_dy
            ),
            opacity=override.opacity if override.opacity is not None else self.opacity,
            border_width=override.border_width if override.border_width is not None else self.border_width,
            border_color=override.border_color if override.border_color is not None else self.border_color,
            border_radius=override.border_radius if override.border_radius is not None else self.border_radius,
            ripple_color=override.ripple_color if override.ripple_color is not None else self.ripple_color,
            blur_radius=override.blur_radius if override.blur_radius is not None else self.blur_radius,
            rotation=override.rotation if override.rotation is not None else self.rotation,
            scale_x=override.scale_x if override.scale_x is not None else self.scale_x,
            scale_y=override.scale_y if override.scale_y is not None else self.scale_y,
            translation_x=override.translation_x if override.translation_x is not None else self.translation_x,
            translation_y=override.translation_y if override.translation_y is not None else self.translation_y,
            clip_to_outline=(
                override.clip_to_outline
                if override.clip_to_outline is not None
                else self.clip_to_outline
            ),
            clip_children=(
                override.clip_children if override.clip_children is not None else self.clip_children
            ),
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


class View(_UIView):
    pass


class Button(_UIButton):
    pass


class Divider(_UIDivider):
    pass


class Image(_UIImage):
    pass


class Container(_UIContainer):
    pass


class Card(_UICard):
    pass


class Icon(_UIIcon):
    pass


class RadioGroup(_UIRadioGroup):
    pass


class ProgressBar(_UIProgressBar):
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


class SimpleDialog(_UISimpleDialog):
    pass


class Toast(_UIToast):
    pass


class Snackbar(_UISnackbar):
    pass


class _UIScreen:
    def __init__(self, name, *items, id=None, transition=None):
        self.name = str(name)
        if id is None:
            base = self.name.strip().lower().replace(" ", "_")
            base = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in base)
            id = f"screen_{base or 'screen'}"
        self.id = id
        self.transition = transition
        self.items = items
        self.layout = ("match_parent", "match_parent")
        self.padding = None
        self.margin = None
        self.gravity = None
        self.background = None
        self.radius = None
        self.style = None


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
    font_family=None,
    font_weight=None,
    font_style=None,
    letter_spacing=None,
    line_height=None,
    text_alignment=None,
    all_caps=None,
    max_lines=None,
    ellipsize=None,
    tint=None,
    thumb_tint=None,
    track_tint=None,
    progress_tint=None,
    button_tint=None,
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    elevation=None,
    pressed_elevation=None,
    text_shadow_color=None,
    text_shadow_radius=None,
    text_shadow_dx=None,
    text_shadow_dy=None,
    opacity=None,
    border_width=None,
    border_color=None,
    border_radius=None,
    ripple_color=None,
    blur_radius=None,
    rotation=None,
    scale_x=None,
    scale_y=None,
    translation_x=None,
    translation_y=None,
    clip_to_outline=None,
    clip_children=None,
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
        font_family=font_family,
        font_weight=font_weight,
        font_style=font_style,
        letter_spacing=letter_spacing,
        line_height=line_height,
        text_alignment=text_alignment,
        all_caps=all_caps,
        max_lines=max_lines,
        ellipsize=ellipsize,
        tint=tint,
        thumb_tint=thumb_tint,
        track_tint=track_tint,
        progress_tint=progress_tint,
        button_tint=button_tint,
        content_description=content_description,
        important_for_accessibility=important_for_accessibility,
        accessibility_label=accessibility_label,
        elevation=elevation,
        pressed_elevation=pressed_elevation,
        text_shadow_color=text_shadow_color,
        text_shadow_radius=text_shadow_radius,
        text_shadow_dx=text_shadow_dx,
        text_shadow_dy=text_shadow_dy,
        opacity=opacity,
        border_width=border_width,
        border_color=border_color,
        border_radius=border_radius,
        ripple_color=ripple_color,
        blur_radius=blur_radius,
        rotation=rotation,
        scale_x=scale_x,
        scale_y=scale_y,
        translation_x=translation_x,
        translation_y=translation_y,
        clip_to_outline=clip_to_outline,
        clip_children=clip_children,
        style=style,
    )


def button(
    text,
    *,
    id="button",
    icon=None,
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
    font_family=None,
    font_weight=None,
    font_style=None,
    letter_spacing=None,
    line_height=None,
    text_alignment=None,
    all_caps=None,
    max_lines=None,
    ellipsize=None,
    tint=None,
    thumb_tint=None,
    track_tint=None,
    progress_tint=None,
    button_tint=None,
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    elevation=None,
    pressed_elevation=None,
    text_shadow_color=None,
    text_shadow_radius=None,
    text_shadow_dx=None,
    text_shadow_dy=None,
    opacity=None,
    border_width=None,
    border_color=None,
    border_radius=None,
    ripple_color=None,
    blur_radius=None,
    rotation=None,
    scale_x=None,
    scale_y=None,
    translation_x=None,
    translation_y=None,
    clip_to_outline=None,
    clip_children=None,
    style=None,
):
    return _UIButton(
        text,
        id=id,
        icon=icon,
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
        font_family=font_family,
        font_weight=font_weight,
        font_style=font_style,
        letter_spacing=letter_spacing,
        line_height=line_height,
        text_alignment=text_alignment,
        all_caps=all_caps,
        max_lines=max_lines,
        ellipsize=ellipsize,
        tint=tint,
        thumb_tint=thumb_tint,
        track_tint=track_tint,
        progress_tint=progress_tint,
        button_tint=button_tint,
        content_description=content_description,
        important_for_accessibility=important_for_accessibility,
        accessibility_label=accessibility_label,
        elevation=elevation,
        pressed_elevation=pressed_elevation,
        text_shadow_color=text_shadow_color,
        text_shadow_radius=text_shadow_radius,
        text_shadow_dx=text_shadow_dx,
        text_shadow_dy=text_shadow_dy,
        opacity=opacity,
        border_width=border_width,
        border_color=border_color,
        border_radius=border_radius,
        ripple_color=ripple_color,
        blur_radius=blur_radius,
        rotation=rotation,
        scale_x=scale_x,
        scale_y=scale_y,
        translation_x=translation_x,
        translation_y=translation_y,
        clip_to_outline=clip_to_outline,
        clip_children=clip_children,
        style=style,
    )


def view(
    *,
    id="view",
    layout=None,
    width=None,
    height=None,
    padding=None,
    margin=None,
    gravity=None,
    weight=None,
    relative=None,
    constraints=None,
    background=None,
    radius=None,
    tint=None,
    thumb_tint=None,
    track_tint=None,
    progress_tint=None,
    button_tint=None,
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    elevation=None,
    pressed_elevation=None,
    text_shadow_color=None,
    text_shadow_radius=None,
    text_shadow_dx=None,
    text_shadow_dy=None,
    opacity=None,
    border_width=None,
    border_color=None,
    border_radius=None,
    ripple_color=None,
    blur_radius=None,
    rotation=None,
    scale_x=None,
    scale_y=None,
    translation_x=None,
    translation_y=None,
    clip_to_outline=None,
    clip_children=None,
    style=None,
):
    return _UIView(
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
        background=background,
        radius=radius,
        tint=tint,
        thumb_tint=thumb_tint,
        track_tint=track_tint,
        progress_tint=progress_tint,
        button_tint=button_tint,
        content_description=content_description,
        important_for_accessibility=important_for_accessibility,
        accessibility_label=accessibility_label,
        elevation=elevation,
        pressed_elevation=pressed_elevation,
        text_shadow_color=text_shadow_color,
        text_shadow_radius=text_shadow_radius,
        text_shadow_dx=text_shadow_dx,
        text_shadow_dy=text_shadow_dy,
        opacity=opacity,
        border_width=border_width,
        border_color=border_color,
        border_radius=border_radius,
        ripple_color=ripple_color,
        blur_radius=blur_radius,
        rotation=rotation,
        scale_x=scale_x,
        scale_y=scale_y,
        translation_x=translation_x,
        translation_y=translation_y,
        clip_to_outline=clip_to_outline,
        clip_children=clip_children,
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
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    elevation=None,
    pressed_elevation=None,
    text_shadow_color=None,
    text_shadow_radius=None,
    text_shadow_dx=None,
    text_shadow_dy=None,
    opacity=None,
    border_width=None,
    border_color=None,
    border_radius=None,
    ripple_color=None,
    blur_radius=None,
    rotation=None,
    scale_x=None,
    scale_y=None,
    translation_x=None,
    translation_y=None,
    clip_to_outline=None,
    clip_children=None,
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
        content_description=content_description,
        important_for_accessibility=important_for_accessibility,
        accessibility_label=accessibility_label,
        elevation=elevation,
        pressed_elevation=pressed_elevation,
        text_shadow_color=text_shadow_color,
        text_shadow_radius=text_shadow_radius,
        text_shadow_dx=text_shadow_dx,
        text_shadow_dy=text_shadow_dy,
        opacity=opacity,
        border_width=border_width,
        border_color=border_color,
        border_radius=border_radius,
        ripple_color=ripple_color,
        blur_radius=blur_radius,
        rotation=rotation,
        scale_x=scale_x,
        scale_y=scale_y,
        translation_x=translation_x,
        translation_y=translation_y,
        clip_to_outline=clip_to_outline,
        clip_children=clip_children,
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
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    elevation=None,
    pressed_elevation=None,
    text_shadow_color=None,
    text_shadow_radius=None,
    text_shadow_dx=None,
    text_shadow_dy=None,
    opacity=None,
    border_width=None,
    border_color=None,
    border_radius=None,
    ripple_color=None,
    blur_radius=None,
    rotation=None,
    scale_x=None,
    scale_y=None,
    translation_x=None,
    translation_y=None,
    clip_to_outline=None,
    clip_children=None,
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
        content_description=content_description,
        important_for_accessibility=important_for_accessibility,
        accessibility_label=accessibility_label,
        elevation=elevation,
        pressed_elevation=pressed_elevation,
        text_shadow_color=text_shadow_color,
        text_shadow_radius=text_shadow_radius,
        text_shadow_dx=text_shadow_dx,
        text_shadow_dy=text_shadow_dy,
        opacity=opacity,
        border_width=border_width,
        border_color=border_color,
        border_radius=border_radius,
        ripple_color=ripple_color,
        blur_radius=blur_radius,
        rotation=rotation,
        scale_x=scale_x,
        scale_y=scale_y,
        translation_x=translation_x,
        translation_y=translation_y,
        clip_to_outline=clip_to_outline,
        clip_children=clip_children,
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
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    elevation=None,
    pressed_elevation=None,
    text_shadow_color=None,
    text_shadow_radius=None,
    text_shadow_dx=None,
    text_shadow_dy=None,
    opacity=None,
    border_width=None,
    border_color=None,
    border_radius=None,
    ripple_color=None,
    blur_radius=None,
    rotation=None,
    scale_x=None,
    scale_y=None,
    translation_x=None,
    translation_y=None,
    clip_to_outline=None,
    clip_children=None,
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
        content_description=content_description,
        important_for_accessibility=important_for_accessibility,
        accessibility_label=accessibility_label,
        elevation=elevation,
        pressed_elevation=pressed_elevation,
        text_shadow_color=text_shadow_color,
        text_shadow_radius=text_shadow_radius,
        text_shadow_dx=text_shadow_dx,
        text_shadow_dy=text_shadow_dy,
        opacity=opacity,
        border_width=border_width,
        border_color=border_color,
        border_radius=border_radius,
        ripple_color=ripple_color,
        blur_radius=blur_radius,
        rotation=rotation,
        scale_x=scale_x,
        scale_y=scale_y,
        translation_x=translation_x,
        translation_y=translation_y,
        clip_to_outline=clip_to_outline,
        clip_children=clip_children,
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
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    elevation=None,
    pressed_elevation=None,
    text_shadow_color=None,
    text_shadow_radius=None,
    text_shadow_dx=None,
    text_shadow_dy=None,
    opacity=None,
    border_width=None,
    border_color=None,
    border_radius=None,
    ripple_color=None,
    blur_radius=None,
    rotation=None,
    scale_x=None,
    scale_y=None,
    translation_x=None,
    translation_y=None,
    clip_to_outline=None,
    clip_children=None,
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
        content_description=content_description,
        important_for_accessibility=important_for_accessibility,
        accessibility_label=accessibility_label,
        elevation=elevation,
        pressed_elevation=pressed_elevation,
        text_shadow_color=text_shadow_color,
        text_shadow_radius=text_shadow_radius,
        text_shadow_dx=text_shadow_dx,
        text_shadow_dy=text_shadow_dy,
        opacity=opacity,
        border_width=border_width,
        border_color=border_color,
        border_radius=border_radius,
        ripple_color=ripple_color,
        blur_radius=blur_radius,
        rotation=rotation,
        scale_x=scale_x,
        scale_y=scale_y,
        translation_x=translation_x,
        translation_y=translation_y,
        clip_to_outline=clip_to_outline,
        clip_children=clip_children,
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


def text_field(
    text="",
    *,
    id="input",
    hint=None,
    input_type=None,
    ime_options=None,
    max_length=None,
    single_line=None,
    password=False,
    auto_capitalize=None,
    numeric_only=False,
    **kwargs,
):
    return _UITextField(
        text,
        id=id,
        hint=hint,
        input_type=input_type,
        ime_options=ime_options,
        max_length=max_length,
        single_line=single_line,
        password=password,
        auto_capitalize=auto_capitalize,
        numeric_only=numeric_only,
        **kwargs,
    )


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


def divider(*, id="divider", color="#FFD1D5DB", thickness=dp(1), **kwargs):
    return _UIDivider(id=id, color=color, thickness=thickness, **kwargs)


def image(
    *,
    id="image",
    src=None,
    content_description=None,
    important_for_accessibility=None,
    accessibility_label=None,
    **kwargs,
):
    return _UIImage(
        id=id,
        src=src,
        content_description=content_description,
        important_for_accessibility=important_for_accessibility,
        accessibility_label=accessibility_label,
        **kwargs,
    )


def container(*items, id="container", **kwargs):
    return _UIContainer(*items, id=id, **kwargs)


def card(*items, id="card", **kwargs):
    return _UICard(*items, id=id, **kwargs)


def icon(name, *, id="icon", **kwargs):
    return _UIIcon(name, id=id, **kwargs)


def radio_group(*items, id="radio_group", orientation="vertical", **kwargs):
    return _UIRadioGroup(*items, id=id, orientation=orientation, **kwargs)


def progress_bar(*, id="progress", value=0, min=0, max=100, indeterminate=False, **kwargs):
    return _UIProgressBar(id=id, value=value, min=min, max=max, indeterminate=indeterminate, **kwargs)


def simple_dialog(title, message):
    return _UISimpleDialog(title, message)


def toast(message, duration=0):
    return _UIToast(message, duration=duration)


def snackbar(message, duration=0):
    return _UISnackbar(message, duration=duration)


def SimpleDialog(title, message):
    return simple_dialog(title, message)


def Toast(message, duration=0):
    return toast(message, duration=duration)


def Snackbar(message, duration=0):
    return snackbar(message, duration=duration)


def screen(name, *items, id=None, transition=None):
    return _UIScreen(name, *items, id=id, transition=transition)


def Screen(name, *items, id=None, transition=None):
    return screen(name, *items, id=id, transition=transition)


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


def color_state(
    *,
    default,
    pressed=None,
    disabled=None,
    selected=None,
    focused=None,
):
    return ColorState(
        default=default,
        pressed=pressed,
        disabled=disabled,
        selected=selected,
        focused=focused,
    )


def presets(palette=None):
    return Presets(palette=palette)


def state(**kwargs):
    return State(**kwargs)
