import hashlib
import copy
from typing import Any

from ir.expr import Var

from dsl.android.resources import _float_bits, _parse_color
from dsl.ast import (
    _ExprBinary,
    _ExprBoolOp,
    _ExprCompare,
    _ExprConst,
    _ExprFormat,
    _ExprSymbol,
    _ExprUnary,
    _StmtAssign,
    _StmtIf,
    _StmtSetText,
    _StmtSimpleDialog,
    _StmtSnackbar,
    _StmtToast,
    _StmtWhile,
)
from dsl.ir_helpers import (
    add_view,
    assign,
    binary,
    call,
    call_stmt,
    click_handler,
    compare,
    const,
    gravity,
    if_,
    layout_params,
    linear_layout,
    method,
    new,
    on_click_view,
    padding,
    program,
    ret,
    set_content_view,
    set_layout_params,
    set_margins,
    static_field,
    static_get,
    static_set,
    var,
    while_,
)
from dsl.widgets import (
    Style,
    State,
    Theme,
    _UIAppBar,
    _UIButton,
    _UIButtonBar,
    _UICheckbox,
    _UIColumn,
    _UIDropdownButton,
    _UIFlatButton,
    _UIFloatingActionButton,
    _UIIconButton,
    _UIPopupMenuButton,
    _UIRadio,
    _UIRaisedButton,
    _UIRow,
    _UISlider,
    _UISwitch,
    _UIText,
    _UITextField,
)


class _PythonicContext:
    def __init__(self, state_spec: State, ui_spec: Any, theme_spec: Theme):
        self.state_spec = state_spec
        self.ui_spec = ui_spec
        self.theme_spec = theme_spec
        self.view_types = {}
        self.view_fields = {}
        self.root_id = "root"
        self._tmp_counter = 0
        self._resources = {}
        self._resource_ids = {}
        self._local_vars = set()

    def _view_desc(self, kind):
        if kind == "text":
            return "Landroid/widget/TextView;"
        if kind == "button":
            return "Landroid/widget/Button;"
        if kind == "app_bar":
            return "Landroid/widget/Toolbar;"
        if kind == "fab":
            return "Landroid/widget/ImageButton;"
        if kind == "raised_button":
            return "Landroid/widget/Button;"
        if kind == "flat_button":
            return "Landroid/widget/Button;"
        if kind == "icon_button":
            return "Landroid/widget/Button;"
        if kind == "text_field":
            return "Landroid/widget/EditText;"
        if kind == "checkbox":
            return "Landroid/widget/CheckBox;"
        if kind == "radio":
            return "Landroid/widget/RadioButton;"
        if kind == "switch":
            return "Landroid/widget/Switch;"
        if kind == "slider":
            return "Landroid/widget/SeekBar;"
        if kind == "dropdown":
            return "Landroid/widget/Spinner;"
        if kind == "popup_button":
            return "Landroid/widget/Button;"
        return "Landroid/view/View;"

    def build_program(self, click_specs, resources=None):
        body = []
        fields = []
        self._resources = dict(resources or {})
        self._resource_ids = {}

        body.extend(linear_layout(self.root_id, var("ctx"), "vertical"))

        # UI creation (recursive)
        body.extend(self._build_ui_items(self.root_id, self.ui_spec.items))

        # Store static refs for views
        for vid, field_name in self.view_fields.items():
            desc = self._view_desc(self.view_types[vid])
            fields.append(static_field(field_name, desc, access="private static"))
            body.append(static_set(field_name, desc, var(vid)))

        fields.append(static_field("app_ctx", "Landroid/app/Activity;", access="private static"))
        body.append(static_set("app_ctx", "Landroid/app/Activity;", var("ctx")))

        # State fields
        for name, value in self.state_spec.values.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise RuntimeError(
                    f"State '{name}' must be an integer literal, got {value!r} ({type(value).__name__})"
                )
            fields.append(static_field(name, "I", access="private static"))
            body.append(static_set(name, "I", const(value)))

        # Wire click handlers
        handler_methods = []
        support_classes = []
        for spec in click_specs:
            if spec.button_id not in self.view_types:
                known = ", ".join(sorted(self.view_types.keys()))
                raise RuntimeError(
                    f"on_click target '{spec.button_id}' not found in ui() ids. "
                    f"Known ids: [{known}]"
                )
            clickable_kinds = {
                "button",
                "raised_button",
                "flat_button",
                "icon_button",
                "fab",
                "popup_button",
            }
            if self.view_types.get(spec.button_id) not in clickable_kinds:
                raise RuntimeError(
                    f"on_click target '{spec.button_id}' is not a button (kind={self.view_types.get(spec.button_id)})."
                )
            handler_name = f"onClick_{spec.button_id}"
            listener_desc = f"Lcom/anali/preview/AnaliClickListener_{spec.button_id};"
            body.extend(on_click_view(var(spec.button_id), handler_name=handler_name, listener_class_desc=listener_desc))
            support_classes.append((listener_desc, handler_name))
            handler_methods.append((handler_name, self._compile_stmts(spec.stmts)))

        # Main method
        methods = [
            method(
                "main",
                params=["ctx"],
                param_types=["Landroid/app/Activity;"],
                return_type=None,
                body=[
                    *body,
                    set_content_view(var("ctx"), var(self.root_id)),
                    ret(),
                ],
            )
        ]

        for name, hbody in handler_methods:
            methods.append(click_handler(name, hbody))

        return program(
            methods,
            fields=fields,
            support_classes=support_classes,
            resources=self._resources,
            resource_ids=self._resource_ids,
        )

    def _resource_key(self, base: str, value: str = "") -> str:
        key = []
        for ch in base:
            if ch.isalnum() or ch == "_":
                key.append(ch.lower())
            else:
                key.append("_")
        out = "".join(key).strip("_") or "value"
        if out[0].isdigit():
            out = f"v_{out}"
        if out not in self._resources:
            return out
        if self._resources[out] == str(value):
            return out
        suffix = hashlib.sha1(str(value).encode("utf-8")).hexdigest()[:6]
        candidate = f"{out}_{suffix}"
        if candidate not in self._resources or self._resources[candidate] == str(value):
            return candidate
        i = 2
        while True:
            cand = f"{candidate}_{i}"
            if cand not in self._resources or self._resources[cand] == str(value):
                return cand
            i += 1

    def _add_string_resource(self, name_hint: str, value: str) -> str:
        if value is None:
            value = ""
        key = self._resource_key(name_hint, value)
        self._resources[key] = str(value)
        if key not in self._resource_ids:
            self._resource_ids[key] = 0x7F010000 + len(self._resource_ids)
        return key

    def _load_string_expr(self, res_name: str, *, ctx_expr=None, prefix="str"):
        p = self._next_tmp(prefix)
        ctx_name = f"{p}_ctx"
        res_obj = f"{p}_res"
        sval = f"{p}_val"
        stmts = []
        if ctx_expr is None:
            ctx_expr = static_get("app_ctx", "Landroid/app/Activity;")
        # Normalize context into an SSA variable for verifier cleanliness.
        if not isinstance(ctx_expr, Var):
            stmts.append(assign(ctx_name, ctx_expr))
            ctx_expr = var(ctx_name)
        rid_value = self._resource_ids.get(res_name)
        if rid_value is None:
            raise RuntimeError(f"Missing resource id for string '{res_name}'")
        stmts.extend(
            [
                assign(
                    res_obj,
                    call(
                        "getResources",
                        args=[ctx_expr],
                        invoke_kind="virtual",
                        owner="Landroid/content/Context;",
                    ),
                ),
                assign(
                    sval,
                    call(
                        "getString",
                        args=[var(res_obj), const(rid_value)],
                        invoke_kind="virtual",
                        owner="Landroid/content/res/Resources;",
                    ),
                ),
            ]
        )
        return stmts, var(sval)

    def _set_text_from_resource(
        self,
        view_name: str,
        value: str,
        owner: str,
        hint: str,
        *,
        ctx_expr=None,
        method_name: str = "setText",
    ):
        res_name = self._add_string_resource(hint, value)
        stmts, sval = self._load_string_expr(res_name, ctx_expr=ctx_expr, prefix=hint)
        stmts.append(
            call_stmt(
                method_name,
                args=[var(view_name), sval],
                return_type=None,
                invoke_kind="virtual",
                owner=owner,
            )
        )
        return stmts

    def _build_ui_items(self, parent_id, items):
        body = []
        for item in items:
            if isinstance(item, _UIAppBar):
                self.view_types[item.id] = "app_bar"
                title_key = self._add_string_resource("app_name", item.text)
                title_load, title_expr = self._load_string_expr(title_key, ctx_expr=var("ctx"), prefix="app_name")
                body.extend(title_load)
                body.append(
                    call_stmt(
                        "setTitle",
                        args=[var("ctx"), title_expr],
                        return_type=None,
                        invoke_kind="virtual",
                        owner="Landroid/app/Activity;",
                    )
                )
                # Default behavior is title-only to avoid duplicated bars.
                if item.inline:
                    self.view_fields[item.id] = f"view_{item.id}"
                    body.extend(
                        [
                            assign(item.id, new("Landroid/widget/Toolbar;", args=[var("ctx")])),
                        ]
                    )
                    body.extend(
                        self._set_text_from_resource(
                            item.id,
                            item.text,
                            "Landroid/widget/Toolbar;",
                            f"{item.id}_title",
                            ctx_expr=var("ctx"),
                            method_name="setTitle",
                        )
                    )
                    body.extend(self._apply_view_layout(item))
                    body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIFloatingActionButton):
                self.view_types[item.id] = "fab"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/ImageButton;", args=[var("ctx")])),
                        call_stmt(
                            "setContentDescription",
                            args=[var(item.id), const(item.text)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/view/View;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIRaisedButton):
                self.view_types[item.id] = "raised_button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
                body.extend(self._set_text_from_resource(item.id, item.text, "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIFlatButton):
                self.view_types[item.id] = "flat_button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
                body.extend(self._set_text_from_resource(item.id, item.text, "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIIconButton):
                self.view_types[item.id] = "icon_button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
                body.extend(self._set_text_from_resource(item.id, item.text, "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UITextField):
                self.view_types[item.id] = "text_field"
                self.view_fields[item.id] = f"view_{item.id}"
                if item.layout is None:
                    item.layout = ("match_parent", "wrap")
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/EditText;", args=[var("ctx")])),
                    ]
                )
                body.extend(self._set_text_from_resource(item.id, item.text or "", "Landroid/widget/EditText;", f"{item.id}_text", ctx_expr=var("ctx")))
                if item.hint:
                    hint_key = self._add_string_resource(f"{item.id}_hint", item.hint)
                    hint_load, hint_expr = self._load_string_expr(hint_key, ctx_expr=var("ctx"), prefix=f"{item.id}_hint")
                    body.extend(hint_load)
                    body.append(
                        call_stmt(
                            "setHint",
                            args=[var(item.id), hint_expr],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/EditText;",
                        )
                    )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UICheckbox):
                self.view_types[item.id] = "checkbox"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/CheckBox;", args=[var("ctx")])),
                        call_stmt(
                            "setChecked",
                            args=[var(item.id), const(1 if item.checked else 0)],
                            return_type=None,
                            arg_types=["Z"],
                            invoke_kind="virtual",
                            owner="Landroid/widget/CheckBox;",
                        ),
                    ]
                )
                body.extend(self._set_text_from_resource(item.id, item.text or "", "Landroid/widget/CheckBox;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIRadio):
                self.view_types[item.id] = "radio"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/RadioButton;", args=[var("ctx")])),
                        call_stmt(
                            "setChecked",
                            args=[var(item.id), const(1 if item.checked else 0)],
                            return_type=None,
                            arg_types=["Z"],
                            invoke_kind="virtual",
                            owner="Landroid/widget/RadioButton;",
                        ),
                    ]
                )
                body.extend(self._set_text_from_resource(item.id, item.text or "", "Landroid/widget/RadioButton;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UISwitch):
                self.view_types[item.id] = "switch"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/Switch;", args=[var("ctx")])),
                        call_stmt(
                            "setChecked",
                            args=[var(item.id), const(1 if item.checked else 0)],
                            return_type=None,
                            arg_types=["Z"],
                            invoke_kind="virtual",
                            owner="Landroid/widget/Switch;",
                        ),
                    ]
                )
                body.extend(self._set_text_from_resource(item.id, item.text or "", "Landroid/widget/Switch;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UISlider):
                self.view_types[item.id] = "slider"
                self.view_fields[item.id] = f"view_{item.id}"
                if item.layout is None:
                    item.layout = ("match_parent", "wrap")
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/SeekBar;", args=[var("ctx")])),
                        call_stmt(
                            "setMax",
                            args=[var(item.id), const(int(item.max) - int(item.min))],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/SeekBar;",
                        ),
                        call_stmt(
                            "setProgress",
                            args=[var(item.id), const(int(item.value) - int(item.min))],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/SeekBar;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIDropdownButton):
                self.view_types[item.id] = "dropdown"
                self.view_fields[item.id] = f"view_{item.id}"
                if item.layout is None:
                    item.layout = ("wrap", "wrap")
                body.extend(
                    [
                        assign(item.id, new("Landroid/widget/Spinner;", args=[var("ctx")])),
                        assign(
                            f"adapter_{item.id}",
                            new(
                                "Landroid/widget/ArrayAdapter;",
                                args=[var("ctx"), const(17367048)],
                            ),
                        ),
                    ]
                )
                for val in item.items:
                    item_key = self._add_string_resource(f"{item.id}_item", str(val))
                    item_load, item_expr = self._load_string_expr(item_key, ctx_expr=var("ctx"), prefix=f"{item.id}_item")
                    body.extend(item_load)
                    body.append(
                        call_stmt(
                            "add",
                            args=[var(f"adapter_{item.id}"), item_expr],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/ArrayAdapter;",
                        )
                    )
                body.extend(
                    [
                        call_stmt(
                            "setDropDownViewResource",
                            args=[var(f"adapter_{item.id}"), const(17367049)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/ArrayAdapter;",
                        ),
                        call_stmt(
                            "setAdapter",
                            args=[var(item.id), var(f"adapter_{item.id}")],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/Spinner;",
                        ),
                    ]
                )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIButtonBar):
                self.view_types[item.id] = "row"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(linear_layout(item.id, var("ctx"), "horizontal"))
                if item.gravity is None:
                    body.append(
                        call_stmt(
                            "setGravity",
                            args=[var(item.id), const(1)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/LinearLayout;",
                        )
                    )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
                body.extend(self._build_ui_items(item.id, item.items))
            elif isinstance(item, _UIPopupMenuButton):
                self.view_types[item.id] = "popup_button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
                body.extend(self._set_text_from_resource(item.id, item.text, "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIRow):
                self.view_types[item.id] = "row"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(linear_layout(item.id, var("ctx"), "horizontal"))
                if item.gravity is None:
                    body.append(
                        call_stmt(
                            "setGravity",
                            args=[var(item.id), const(1)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/LinearLayout;",
                        )
                    )
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
                body.extend(self._build_ui_items(item.id, item.items))
            elif isinstance(item, _UIColumn):
                self.view_types[item.id] = "column"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend(linear_layout(item.id, var("ctx"), "vertical"))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
                body.extend(self._build_ui_items(item.id, item.items))
            elif isinstance(item, _UIText):
                self.view_types[item.id] = "text"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend([assign(item.id, new("Landroid/widget/TextView;", args=[var("ctx")]))])
                body.extend(self._set_text_from_resource(item.id, item.text, "Landroid/widget/TextView;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            elif isinstance(item, _UIButton):
                self.view_types[item.id] = "button"
                self.view_fields[item.id] = f"view_{item.id}"
                body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
                body.extend(self._set_text_from_resource(item.id, item.text, "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
                body.extend(self._apply_view_layout(item))
                body.append(add_view(var(parent_id), var(item.id)))
            else:
                raise RuntimeError(f"Unsupported UI item: {item}")
        return body

    def _compile_stmts(self, stmts):
        prev_locals = self._local_vars
        try:
            self._local_vars = set()
            out = self._compile_stmt_block(stmts)
            out.append(ret())
            return out
        finally:
            self._local_vars = prev_locals

    def _compile_stmt_block(self, stmts):
        out = []
        for stmt in stmts:
            out.extend(self.lower_stmt(stmt))
        return out

    def lower_stmt(self, stmt):
        if isinstance(stmt, str):
            raise RuntimeError("String statements are deprecated; use AST builder objects.")
        if isinstance(stmt, _StmtAssign):
            return self._compile_assign_stmt(stmt)
        if isinstance(stmt, _StmtSetText):
            return self._compile_set_text_stmt(stmt)
        if isinstance(stmt, _StmtIf):
            return self._compile_if_stmt(stmt)
        if isinstance(stmt, _StmtWhile):
            return self._compile_while_stmt(stmt)
        if isinstance(stmt, _StmtToast):
            return self._compile_toast_stmt(stmt)
        if isinstance(stmt, _StmtSnackbar):
            return self._compile_snackbar_stmt(stmt)
        if isinstance(stmt, _StmtSimpleDialog):
            return self._compile_dialog_stmt(stmt)
        raise RuntimeError(f"Unsupported statement: {stmt}")

    def _apply_view_layout(self, item):
        out = []
        theme_style = Style()
        if isinstance(item, _UIText):
            theme_style = self.theme_spec.text
        elif isinstance(item, _UIButton):
            theme_style = self.theme_spec.button
        elif isinstance(item, _UIRow):
            theme_style = self.theme_spec.row
        elif isinstance(item, _UIColumn):
            theme_style = self.theme_spec.column

        item_style = item.style if getattr(item, "style", None) else None
        style = theme_style.merged(item_style)

        padding_value = item.padding if item.padding is not None else style.padding
        gravity_value = item.gravity if item.gravity is not None else style.gravity
        layout_value = item.layout if item.layout is not None else style.layout
        margin_value = item.margin if item.margin is not None else style.margin
        text_color_value = item.text_color if getattr(item, "text_color", None) is not None else style.text_color
        background_value = item.background if getattr(item, "background", None) is not None else style.background
        radius_value = item.radius if getattr(item, "radius", None) is not None else style.radius
        text_size_value = item.text_size if getattr(item, "text_size", None) is not None else style.text_size

        padding_value = self._normalize_box_spacing(padding_value, "padding")
        margin_value = self._normalize_box_spacing(margin_value, "margin")
        layout_value = self._normalize_layout_value(layout_value)

        if padding_value is not None:
            left, top, right, bottom = padding_value
            out.append(padding(var(item.id), left, top, right, bottom))
        if gravity_value is not None:
            out.append(gravity(var(item.id), gravity_value))

        palette = self.theme_spec.palette
        bg_color = _parse_color(background_value, palette)
        txt_color = _parse_color(text_color_value, palette)
        kind = self.view_types.get(item.id)

        if bg_color is not None and radius_value is not None:
            bg_name = f"bg_{item.id}"
            out.append(assign(bg_name, new("Landroid/graphics/drawable/GradientDrawable;", args=[])))
            out.append(
                call_stmt(
                    "setColor",
                    args=[var(bg_name), const(bg_color)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/graphics/drawable/GradientDrawable;",
                )
            )
            out.append(
                call_stmt(
                    "setCornerRadius",
                    args=[var(bg_name), const(_float_bits(radius_value))],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/graphics/drawable/GradientDrawable;",
                )
            )
            out.append(
                call_stmt(
                    "setBackground",
                    args=[var(item.id), var(bg_name)],
                    return_type=None,
                    arg_types=["Landroid/graphics/drawable/Drawable;"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
        elif bg_color is not None:
            out.append(
                call_stmt(
                    "setBackgroundColor",
                    args=[var(item.id), const(bg_color)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )

        text_like_kinds = {
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
        }
        if txt_color is not None:
            if kind == "app_bar":
                out.append(
                    call_stmt(
                        "setTitleTextColor",
                        args=[var(item.id), const(txt_color)],
                        return_type=None,
                        arg_types=["I"],
                        invoke_kind="virtual",
                        owner="Landroid/widget/Toolbar;",
                    )
                )
            elif kind in text_like_kinds:
                out.append(
                    call_stmt(
                        "setTextColor",
                        args=[var(item.id), const(txt_color)],
                        return_type=None,
                        arg_types=["I"],
                        invoke_kind="virtual",
                        owner="Landroid/widget/TextView;",
                    )
                )

        if text_size_value is not None and kind in text_like_kinds:
            out.append(
                call_stmt(
                    "setTextSize",
                    args=[var(item.id), const(_float_bits(text_size_value))],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/TextView;",
                )
            )

        if layout_value or margin_value:
            width, height = layout_value if layout_value else ("wrap", "wrap")
            lp_name = f"lp_{item.id}"
            out.append(assign(lp_name, layout_params(width, height, parent="LinearLayout")))
            if margin_value:
                ml, mt, mr, mb = margin_value
                out.append(set_margins(var(lp_name), ml, mt, mr, mb))
            out.append(set_layout_params(var(item.id), var(lp_name)))
        return out

    def _normalize_box_spacing(self, value, attr_name):
        if value is None:
            return None
        if isinstance(value, int):
            return (value, value, value, value)
        if isinstance(value, (tuple, list)):
            if len(value) == 2:
                h, v = value
                return (int(h), int(v), int(h), int(v))
            if len(value) == 4:
                l, t, r, b = value
                return (int(l), int(t), int(r), int(b))
        raise RuntimeError(
            f"Invalid {attr_name} value {value!r}. Expected int, (h, v), or (l, t, r, b)."
        )

    def _normalize_layout_value(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            # Allow shorthand: layout=\"match\" or layout=\"wrap\".
            return (value, value)
        if isinstance(value, (tuple, list)) and len(value) == 2:
            return (value[0], value[1])
        raise RuntimeError(
            f"Invalid layout value {value!r}. Expected \"match\"/\"wrap\" or (width, height)."
        )

    def _compile_assign_stmt(self, stmt):
        if not isinstance(stmt.target, _ExprSymbol):
            raise RuntimeError("Assignment target must be a symbol")
        name = stmt.target.name

        if isinstance(stmt.value, (_ExprConst, _ExprSymbol, _ExprBinary)):
            prefix, result = self._compile_int_expr(stmt.value)
        else:
            raise RuntimeError(
                f"Unsupported assignment expression for '{name}': {type(stmt.value).__name__}. "
                "Expected int const/symbol/arithmetic expression."
            )

        if name in self.state_spec.values:
            return [*prefix, static_set(name, "I", result)]

        self._local_vars.add(name)
        local_expr = result.name if isinstance(result, Var) else result
        return [*prefix, assign(name, local_expr)]

    def _next_tmp(self, prefix="tmp"):
        self._tmp_counter += 1
        return f"{prefix}_{self._tmp_counter}"

    def _compile_int_expr(self, expr):
        if isinstance(expr, _ExprConst):
            if not isinstance(expr.value, int) or isinstance(expr.value, bool):
                raise RuntimeError(
                    f"Integer expression expected an int constant, got {expr.value!r} ({type(expr.value).__name__})"
                )
            return [], const(expr.value)
        if isinstance(expr, _ExprSymbol):
            if expr.name in self.state_spec.values:
                t = self._next_tmp("s")
                return [assign(t, static_get(expr.name, "I"))], var(t)
            if expr.name in self._local_vars:
                return [], var(expr.name)
            raise RuntimeError(
                f"Undefined variable '{expr.name}' in arithmetic expression. "
                "Declare it earlier in the handler or add it to state(...)."
            )
        if isinstance(expr, _ExprBinary):
            left_stmts, left_expr = self._compile_int_expr(expr.lhs)
            right_stmts, right_expr = self._compile_int_expr(expr.rhs)
            t = self._next_tmp("b")
            return [
                *left_stmts,
                *right_stmts,
                assign(t, binary(expr.op, left_expr, right_expr)),
            ], var(t)
        raise RuntimeError(f"Unsupported expression in assignment: {expr}")

    def _compile_set_text_stmt(self, stmt):
        view_id = stmt.view.name
        view_desc = self._view_desc(self.view_types.get(view_id, "text"))
        view_field = self.view_fields.get(view_id)
        if view_field is None:
            raise RuntimeError(f"Unknown view id: {view_id}")
        if isinstance(stmt.value, _ExprConst):
            if not isinstance(stmt.value.value, str):
                raise RuntimeError(
                    f"{view_id}.text expects a string or f-string, got {stmt.value.value!r} ({type(stmt.value.value).__name__})"
                )
            return [
                assign("v", static_get(view_field, view_desc)),
                call_stmt(
                    "setText",
                    args=[var("v"), const(stmt.value.value)],
                    return_type=None,
                    invoke_kind="virtual",
                    owner=view_desc,
                ),
            ]
        if isinstance(stmt.value, _ExprFormat):
            return self._compile_format_set_text(view_desc, view_field, stmt.value)
        raise RuntimeError("Unsupported set_text value")

    def _compile_if_stmt(self, stmt):
        then_ir = self._compile_stmt_block(stmt.then)
        else_ir = self._compile_stmt_block(stmt.else_)
        return self._lower_condition_branch(stmt.cond, then_ir, else_ir)

    def _compile_while_stmt(self, stmt):
        body_ir = self._compile_stmt_block(stmt.body)
        if isinstance(stmt.cond, _ExprBoolOp):
            guard = self._next_tmp("cond")
            pre = self._compile_bool_to_guard(stmt.cond, guard)
            tail = self._compile_bool_to_guard(stmt.cond, guard)
            self._local_vars.add(guard)
            return [*pre, while_(guard, [*body_ir, *tail])]
        prefix, cond = self._compile_condition(stmt.cond)
        return [*prefix, while_(cond, body_ir)]

    def _compile_bool_to_guard(self, expr, guard_name):
        return self._lower_condition_branch(
            expr,
            [assign(guard_name, const(1))],
            [assign(guard_name, const(0))],
        )

    def _lower_condition_branch(self, cond_expr, then_ir, else_ir):
        if isinstance(cond_expr, _ExprBoolOp):
            if cond_expr.op == "and":
                rhs_ir = self._lower_condition_branch(
                    cond_expr.rhs,
                    self._clone_ir_block(then_ir),
                    self._clone_ir_block(else_ir),
                )
                return self._lower_condition_branch(cond_expr.lhs, rhs_ir, self._clone_ir_block(else_ir))
            if cond_expr.op == "or":
                rhs_ir = self._lower_condition_branch(
                    cond_expr.rhs,
                    self._clone_ir_block(then_ir),
                    self._clone_ir_block(else_ir),
                )
                return self._lower_condition_branch(cond_expr.lhs, self._clone_ir_block(then_ir), rhs_ir)
            raise RuntimeError(f"Unsupported boolean operator: {cond_expr.op}")
        if isinstance(cond_expr, _ExprUnary):
            if cond_expr.op != "not":
                raise RuntimeError(f"Unsupported unary condition operator: {cond_expr.op}")
            return self._lower_condition_branch(cond_expr.value, else_ir, then_ir)

        prefix, cond = self._compile_condition(cond_expr)
        return [*prefix, if_(cond, then_ir, else_ir)]

    def _clone_ir_block(self, stmts):
        return copy.deepcopy(stmts)

    def _compile_condition(self, expr):
        if isinstance(expr, _ExprCompare):
            left_stmts, left_expr = self._compile_int_expr(expr.lhs)
            right_stmts, right_expr = self._compile_int_expr(expr.rhs)
            return [
                *left_stmts,
                *right_stmts,
            ], compare(expr.op, left_expr, right_expr)
        if isinstance(expr, _ExprSymbol):
            if expr.name in self.state_spec.values or expr.name in self._local_vars:
                return [], expr.name
            raise RuntimeError(
                f"Undefined variable '{expr.name}' in condition. "
                "Declare it earlier in the handler or add it to state(...)."
            )
        if isinstance(expr, _ExprConst):
            if isinstance(expr.value, bool):
                v = 1 if expr.value else 0
            elif isinstance(expr.value, int):
                v = expr.value
            else:
                raise RuntimeError(
                    f"Condition constants must be bool/int, got {expr.value!r} ({type(expr.value).__name__})"
                )
            return [], compare("!=", const(v), const(0))
        if isinstance(expr, _ExprUnary):
            if expr.op != "not":
                raise RuntimeError(f"Unsupported unary condition operator: {expr.op}")
            prefix, cond = self._compile_condition(expr.value)
            return prefix, self._negate_condition(cond)
        if isinstance(expr, _ExprBoolOp):
            raise RuntimeError("Boolean conditions must be lowered through branch builder")
        raise RuntimeError(f"Unsupported condition expression: {type(expr).__name__}")

    def _negate_condition(self, cond):
        if isinstance(cond, str):
            return compare("==", var(cond), const(0))
        if hasattr(cond, "op") and hasattr(cond, "left") and hasattr(cond, "right"):
            flip = {
                "==": "!=",
                "!=": "==",
                "<": ">=",
                "<=": ">",
                ">": "<=",
                ">=": "<",
            }
            if cond.op not in flip:
                raise RuntimeError(f"Cannot negate condition operator: {cond.op}")
            return compare(flip[cond.op], cond.left, cond.right)
        raise RuntimeError(f"Cannot negate condition of type: {type(cond).__name__}")

    def _compile_toast_stmt(self, stmt):
        msg_key = self._add_string_resource("toast_msg", stmt.message)
        msg_load, msg_expr = self._load_string_expr(msg_key, prefix="toast_msg")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            *msg_load,
            assign(
                "toast_obj",
                call(
                    "makeText",
                    args=[var("ctx"), msg_expr, const(stmt.duration)],
                    invoke_kind="static",
                    owner="Landroid/widget/Toast;",
                ),
            ),
            call_stmt(
                "show",
                args=[var("toast_obj")],
                return_type=None,
                invoke_kind="virtual",
                owner="Landroid/widget/Toast;",
            ),
        ]

    def _compile_snackbar_stmt(self, stmt):
        # Framework fallback until Material dependency is bundled.
        return self._compile_toast_stmt(_StmtToast(stmt.message, stmt.duration))

    def _compile_dialog_stmt(self, stmt):
        title_key = self._add_string_resource("dialog_title", stmt.title)
        msg_key = self._add_string_resource("dialog_msg", stmt.message)
        title_load, title_expr = self._load_string_expr(title_key, prefix="dialog_title")
        msg_load, msg_expr = self._load_string_expr(msg_key, prefix="dialog_msg")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            *title_load,
            *msg_load,
            assign("dlg", new("Landroid/app/AlertDialog$Builder;", args=[var("ctx")])),
            assign(
                "dlg",
                call(
                    "setTitle",
                    args=[var("dlg"), title_expr],
                    invoke_kind="virtual",
                    owner="Landroid/app/AlertDialog$Builder;",
                ),
            ),
            assign(
                "dlg",
                call(
                    "setMessage",
                    args=[var("dlg"), msg_expr],
                    invoke_kind="virtual",
                    owner="Landroid/app/AlertDialog$Builder;",
                ),
            ),
            assign(
                "_dlg_obj",
                call(
                    "show",
                    args=[var("dlg")],
                    invoke_kind="virtual",
                    owner="Landroid/app/AlertDialog$Builder;",
                ),
            ),
        ]

    def _compile_format_set_text(self, view_desc, view_field, fmt):
        stmts = [
            assign(
                "sb",
                new("Ljava/lang/StringBuilder;", args=[], arg_types=[]),
            )
        ]
        frag_i = 0
        for part in fmt.parts:
            if isinstance(part, _ExprConst):
                if part.value:
                    frag_i += 1
                    frag_key = self._add_string_resource(f"fmt_frag_{frag_i}", str(part.value))
                    frag_load, frag_expr = self._load_string_expr(frag_key, prefix=f"fmt_frag_{frag_i}")
                    stmts.extend(frag_load)
                    stmts.append(
                        assign(
                            "sb",
                            call(
                                "append",
                                args=[var("sb"), frag_expr],
                                return_type="Ljava/lang/StringBuilder;",
                                arg_types=["Ljava/lang/String;"],
                                invoke_kind="virtual",
                                owner="Ljava/lang/StringBuilder;",
                            ),
                        )
                    )
            elif isinstance(part, _ExprSymbol):
                if part.name in self.state_spec.values:
                    stmts.append(assign("x", static_get(part.name, "I")))
                elif part.name in self._local_vars:
                    stmts.append(assign("x", var(part.name)))
                else:
                    raise RuntimeError(
                        f"Undefined variable '{part.name}' in f-string. "
                        "Declare it earlier in the handler or add it to state(...)."
                    )
                stmts.append(
                    assign(
                        "sb",
                        call(
                            "append",
                            args=[var("sb"), var("x")],
                            return_type="Ljava/lang/StringBuilder;",
                            arg_types=["I"],
                            invoke_kind="virtual",
                            owner="Ljava/lang/StringBuilder;",
                        ),
                    )
                )
        stmts.append(
            assign(
                "s",
                call(
                    "toString",
                    args=[var("sb")],
                    return_type="Ljava/lang/String;",
                    arg_types=[],
                    invoke_kind="virtual",
                    owner="Ljava/lang/StringBuilder;",
                ),
            )
        )
        stmts.append(assign("v", static_get(view_field, view_desc)))
        stmts.append(
            call_stmt(
                "setText",
                args=[var("v"), var("s")],
                return_type=None,
                invoke_kind="virtual",
                owner=view_desc,
            )
        )
        return stmts


# -------------------------------
# AST-based expression builder
