import hashlib
import copy
from typing import Any

from ir.expr import Var

from dsl.android.resources import _parse_color
from dsl.ast import (
    _ExprBinary,
    _ExprBoolOp,
    _ExprCompare,
    _ExprConst,
    _ExprFormat,
    _ExprSymbol,
    _ExprUnary,
    _StmtAssign,
    _StmtExitApp,
    _StmtIf,
    _StmtBack,
    _StmtReplace,
    _StmtRequestPermissions,
    _StmtSetText,
    _StmtSimpleDialog,
    _StmtSnackbar,
    _StmtToast,
    _StmtLog,
    _StmtNavigate,
    _StmtWhile,
)
from dsl.ir_helpers import (
    add_view,
    assign,
    array_get,
    array_set,
    binary,
    call,
    call_stmt,
    event_handler,
    compare,
    const,
    constraint_layout,
    field_set,
    if_,
    layout_params,
    linear_layout,
    method,
    new,
    new_array,
    on_change_view,
    on_click_view,
    on_focus_change_view,
    on_item_selected_view,
    on_text_change_view,
    program,
    primitive_cast,
    relative_layout,
    ret,
    set_content_view,
    set_layout_params,
    static_field,
    static_get,
    static_set,
    var,
    while_,
)
from dsl.widgets import (
    ColorState,
    Dp,
    Px,
    Sp,
    Percent,
    Style,
    State,
    Theme,
    _UIAppBar,
    _UIButton,
    _UIButtonBar,
    _UICard,
    _UICheckbox,
    _UIColumn,
    _UIContainer,
    _UIConstraint,
    _UIDivider,
    _UIDropdownButton,
    _UIFlatButton,
    _UIFloatingActionButton,
    _UIIcon,
    _UIIconButton,
    _UIImage,
    _UIPopupMenuButton,
    _UIProgressBar,
    _UIRadio,
    _UIRadioGroup,
    _UIRelative,
    _UIRaisedButton,
    _UIRow,
    _UIScreen,
    _UISlider,
    _UISwitch,
    _UIText,
    _UITextField,
    _UIView,
)
from dsl.lowering.attr_registry import ATTR_METHODS


class _PythonicContext:
    def __init__(self, state_spec: State, ui_spec: Any, theme_spec: Theme, *, registry=None):
        self.state_spec = state_spec
        self.ui_spec = ui_spec
        self.theme_spec = theme_spec
        self.registry = registry
        self.view_types = {}
        self.view_fields = {}
        self.root_id = "root"
        self._tmp_counter = 0
        self._resources = {}
        self._resource_ids = {}
        self._resource_colors = {}
        self._resource_color_ids = {}
        self._resource_dimens = {}
        self._resource_dimen_ids = {}
        self._resource_styles = {}
        self._resource_style_ids = {}
        self._local_vars = set()
        self._container_orientation = {self.root_id: "vertical"}
        self._lint_warnings = []
        self._screens = []
        self._screen_map = {}
        self._current_screen = None
        self._view_screen = {}
        self._nav_stack_limit = 0
        self._popup_button_items = {}

    def _view_desc(self, kind):
        if kind == "text":
            return "Landroid/widget/TextView;"
        if kind == "icon":
            return "Landroid/widget/TextView;"
        if kind == "button":
            return "Landroid/widget/Button;"
        if kind == "app_bar":
            return "Landroid/widget/Toolbar;"
        if kind == "fab":
            return "Landroid/view/View;"
        if kind == "raised_button":
            return "Landroid/widget/Button;"
        if kind == "flat_button":
            return "Landroid/widget/Button;"
        if kind == "icon_button":
            return "Landroid/widget/Button;"
        if kind == "relative":
            return "Landroid/widget/RelativeLayout;"
        if kind == "constraint":
            return "Landroidx/constraintlayout/widget/ConstraintLayout;"
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
        if kind == "image":
            return "Landroid/widget/ImageView;"
        if kind == "progress_bar":
            return "Landroid/widget/ProgressBar;"
        if kind == "radio_group":
            return "Landroid/widget/RadioGroup;"
        if kind == "container":
            return "Landroid/widget/LinearLayout;"
        if kind == "card":
            return "Landroid/widget/LinearLayout;"
        if kind == "divider":
            return "Landroid/view/View;"
        if kind == "view":
            return "Landroid/view/View;"
        if kind == "screen":
            return "Landroid/widget/RelativeLayout;"
        return "Landroid/view/View;"

    def _register_view(self, item_id: str, kind: str):
        default_like_ids = {
            "label",
            "button",
            "row",
            "column",
            "relative",
            "constraint",
            "appbar",
            "fab",
            "raised_btn",
            "flat_btn",
            "icon_btn",
            "input",
            "checkbox",
            "radio",
            "switch",
            "slider",
            "dropdown",
            "button_bar",
            "popup",
            "view",
            "divider",
            "image",
            "container",
            "card",
            "icon",
            "radio_group",
            "progress",
            "screen",
        }
        resolved_id = item_id
        if resolved_id in self.view_types:
            if resolved_id in default_like_ids:
                i = 2
                while f"{resolved_id}_{i}" in self.view_types:
                    i += 1
                resolved_id = f"{resolved_id}_{i}"
                self._lint_warnings.append(
                    f"Auto-suffixed duplicate default id '{item_id}' to '{resolved_id}'. "
                    "Provide explicit unique ids to avoid this."
                )
            else:
                raise RuntimeError(
                    f"Duplicate widget id '{item_id}'. "
                    "Widget ids must be unique; provide explicit id=... for repeated widget types."
                )
        self.view_types[resolved_id] = kind
        self.view_fields[resolved_id] = f"view_{resolved_id}"
        self._record_view_screen(resolved_id)
        return resolved_id

    def _record_view_screen(self, view_id: str):
        if not self._current_screen:
            return
        existing = self._view_screen.get(view_id)
        if existing and existing != self._current_screen:
            raise RuntimeError(
                f"Widget id '{view_id}' is declared in multiple Screens "
                f"('{existing}' and '{self._current_screen}'). "
                "Widget ids must be unique across Screens."
            )
        self._view_screen[view_id] = self._current_screen

    def _nav_limit(self) -> int:
        if self._nav_stack_limit:
            return self._nav_stack_limit
        # Allow repeated navigation without overflowing.
        self._nav_stack_limit = max(8, len(self._screens) * 4)
        return self._nav_stack_limit

    def _nav_screen_index(self, target: str) -> int:
        for idx, (name, _) in enumerate(self._screens):
            if name == target:
                return idx
        known = ", ".join(sorted(self._screen_map.keys()))
        raise RuntimeError(f"Unknown screen '{target}'. Known: [{known}]")

    def _nav_set_visibility_for_index(self, idx_expr, vis):
        out = []
        desc = self._view_desc("screen")
        for idx, (_, screen_id) in enumerate(self._screens):
            field_name = self.view_fields.get(screen_id)
            if not field_name:
                raise RuntimeError(f"Missing view field for screen '{screen_id}'")
            tmp = self._next_tmp(f"screen_ref_{idx}")
            then = [
                assign(tmp, static_get(field_name, desc)),
                call_stmt(
                    "setVisibility",
                    args=[var(tmp), const(vis)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                ),
            ]
            out.append(if_(compare("==", idx_expr, const(idx)), then, []))
        return out

    def _resolve_color_state_entries(self, color_value, palette):
        if isinstance(color_value, ColorState):
            entries = []
            state_keys = ("pressed", "disabled", "selected", "focused", "default")
            for key in state_keys:
                raw = getattr(color_value, key)
                if raw is None:
                    continue
                argb = _parse_color(raw, palette)
                if argb is None:
                    continue
                entries.append((key, argb))
            if not entries:
                raise RuntimeError("ColorState resolved to no concrete colors.")
            if not any(k == "default" for k, _ in entries):
                raise RuntimeError("ColorState requires a default color.")
            return entries
        argb = _parse_color(color_value, palette)
        if argb is None:
            return []
        return [("default", argb)]

    def _build_color_state_list_expr(self, view_id: str, attr_name: str, color_value, palette):
        entries = self._resolve_color_state_entries(color_value, palette)
        if not entries:
            return [], None
        states_var = self._next_tmp(f"{view_id}_{attr_name}_states")
        colors_var = self._next_tmp(f"{view_id}_{attr_name}_colors")
        csl_var = self._next_tmp(f"{view_id}_{attr_name}_csl")
        stmts = [
            assign(states_var, new_array(const(len(entries)), "[I", array_desc="[[I")),
            assign(colors_var, new_array(const(len(entries)), "I")),
        ]
        state_ids = {
            "pressed": 16842919,
            "disabled": -16842910,
            "selected": 16842913,
            "focused": 16842908,
        }
        for idx, (state_key, argb) in enumerate(entries):
            state_arr = self._next_tmp(f"{view_id}_{attr_name}_st_{idx}")
            if state_key == "default":
                stmts.append(assign(state_arr, new_array(const(0), "I")))
            else:
                stmts.append(assign(state_arr, new_array(const(1), "I")))
                stmts.append(
                    array_set(
                        var(state_arr),
                        const(0),
                        "I",
                        const(state_ids[state_key]),
                    )
                )
            stmts.append(array_set(var(states_var), const(idx), "[I", var(state_arr)))
            stmts.append(array_set(var(colors_var), const(idx), "I", const(argb)))
        stmts.append(
            assign(
                csl_var,
                new(
                    "Landroid/content/res/ColorStateList;",
                    args=[var(states_var), var(colors_var)],
                    arg_types=["[[I", "[I"],
                ),
            )
        )
        return stmts, var(csl_var)

    def _resolve_text_alignment_value(self, raw_value):
        if isinstance(raw_value, bool):
            raise RuntimeError("text_alignment must be string or int, not bool.")
        if isinstance(raw_value, int):
            return int(raw_value)
        if not isinstance(raw_value, str):
            raise RuntimeError("text_alignment must be one of: inherit, gravity, text_start, text_end, center, view_start, view_end.")
        key = raw_value.strip().lower()
        mapping = {
            "inherit": 0,
            "gravity": 1,
            "text_start": 2,
            "text_end": 3,
            "center": 4,
            "view_start": 5,
            "view_end": 6,
        }
        if key not in mapping:
            raise RuntimeError(
                "Unsupported text_alignment. Expected one of: inherit, gravity, text_start, text_end, center, view_start, view_end."
            )
        return mapping[key]

    def _resolve_typeface_style(self, font_weight, font_style):
        italic = False
        bold = False
        if font_weight is not None:
            if isinstance(font_weight, bool):
                raise RuntimeError("font_weight must be int-like, not bool.")
            weight_int = int(font_weight)
            bold = weight_int >= 600
        if font_style is not None:
            key = str(font_style).strip().lower()
            if key in ("italic", "oblique"):
                italic = True
            elif key == "normal":
                italic = False
            else:
                raise RuntimeError("font_style must be one of: normal, italic, oblique.")
        if bold and italic:
            return 3
        if bold:
            return 1
        if italic:
            return 2
        return 0

    def _emit_attr_call(self, *, view_id, attr_name, raw_value):
        meta = ATTR_METHODS.get(attr_name)
        if meta is None:
            return []
        if raw_value is None:
            return []
        if meta.supported_kinds is not None:
            kind = self.view_types.get(view_id)
            if kind not in meta.supported_kinds:
                return []

        stmts = []

        # ---- value resolution ----
        if meta.value_loader == "color":
            key = self._add_color_resource(f"{view_id}_{attr_name}", raw_value)
            load, value_expr = self._load_color_expr(key, ctx_expr=var("ctx"))
            stmts.extend(load)
            args = [var(view_id), value_expr]

        elif meta.value_loader == "dimen_px_4":
            l, t, r, b = raw_value
            args = [var(view_id)]
            for side, v in zip(("l", "t", "r", "b"), (l, t, r, b)):
                key = self._add_dimen_resource(f"{view_id}_{attr_name}_{side}", v)
                load, expr = self._load_dimen_px_expr(
                    key,
                    ctx_expr=var("ctx"),
                    prefix=f"{view_id}_{attr_name}_{side}")
                stmts.extend(load)
                args.append(expr)
        elif meta.value_loader == "margin_px_4":
            if not (isinstance(raw_value, tuple) and len(raw_value) == 2):
                raise RuntimeError("margin loader expects (layout_params_var, (l,t,r,b))")
            lp_var, margin_tuple = raw_value
            l, t, r, b = margin_tuple
            args = [lp_var]
            for side, v in zip(("l", "t", "r", "b"), (l, t, r, b)):
                key = self._add_dimen_resource(f"{view_id}_{attr_name}_{side}", v)
                load, expr = self._load_dimen_px_expr(
                    key,
                    ctx_expr=var("ctx"),
                    prefix=f"{view_id}_{attr_name}_{side}")
                stmts.extend(load)
                args.append(expr)
        elif meta.value_loader == "dimen_sp_float":
            if not isinstance(raw_value, Sp):
                raise RuntimeError("text_size must use sp(...) units.")
            key = self._add_dimen_resource(f"{view_id}_{attr_name}", raw_value)
            load, value_expr = self._load_dimen_float_expr(key, ctx_expr=var("ctx"), prefix=f"{view_id}_{attr_name}")
            stmts.extend(load)
            args = [var(view_id), value_expr]
        elif meta.value_loader == "line_spacing":
            if isinstance(raw_value, bool):
                raise RuntimeError("line_height must be a number or unit value, not bool.")
            key = self._add_dimen_resource(f"{view_id}_{attr_name}", raw_value)
            load, value_expr = self._load_dimen_float_expr(key, ctx_expr=var("ctx"), prefix=f"{view_id}_{attr_name}")
            stmts.extend(load)
            mult_setup, mult_expr = self._float_const_expr(1.0, prefix=f"{view_id}_{attr_name}_mult")
            stmts.extend(mult_setup)
            args = [var(view_id), value_expr, mult_expr]
        elif meta.value_loader == "text_alignment":
            args = [var(view_id), const(self._resolve_text_alignment_value(raw_value))]
        elif meta.value_loader == "ellipsize":
            if isinstance(raw_value, str):
                key = raw_value.strip().lower()
            else:
                raise RuntimeError("ellipsize must be one of: start, middle, end, marquee, none.")
            if key == "none":
                ellipsize_expr = const(None)
            else:
                truncate_map = {
                    "start": "START",
                    "middle": "MIDDLE",
                    "end": "END",
                    "marquee": "MARQUEE",
                }
                if key not in truncate_map:
                    raise RuntimeError("ellipsize must be one of: start, middle, end, marquee, none.")
                ellipsize_var = self._next_tmp(f"{view_id}_ellipsize")
                stmts.append(
                    assign(
                        ellipsize_var,
                        static_get(
                            truncate_map[key],
                            "Landroid/text/TextUtils$TruncateAt;",
                            owner="Landroid/text/TextUtils$TruncateAt;",
                        ),
                    )
                )
                ellipsize_expr = var(ellipsize_var)
            args = [var(view_id), ellipsize_expr]
        elif meta.value_loader == "typeface":
            if not (isinstance(raw_value, tuple) and len(raw_value) == 3):
                raise RuntimeError("typeface loader expects (font_family, font_weight, font_style)")
            family, weight, font_style = raw_value
            style_value = self._resolve_typeface_style(weight, font_style)
            family_name = "sans-serif" if family is None else str(family)
            tf_var = self._next_tmp(f"{view_id}_typeface")
            stmts.append(
                assign(
                    tf_var,
                    call(
                        "create",
                        args=[const(family_name), const(style_value)],
                        return_type="Landroid/graphics/Typeface;",
                        arg_types=["Ljava/lang/String;", "I"],
                        invoke_kind="static",
                        owner="Landroid/graphics/Typeface;",
                    ),
                )
            )
            args = [var(view_id), var(tf_var)]
        elif meta.value_loader == "color_state_list":
            csl_stmts, csl_expr = self._build_color_state_list_expr(
                view_id,
                attr_name,
                raw_value,
                self.theme_spec.palette,
            )
            stmts.extend(csl_stmts)
            if csl_expr is None:
                return []
            args = [var(view_id), csl_expr]
        elif meta.value_loader == "float":
            setup, value_expr = self._float_const_expr(raw_value, prefix=f"{view_id}_{attr_name}")
            stmts.extend(setup)
            args = [var(view_id), value_expr]
        elif meta.value_loader == "layout_params":
            args = [var(view_id), raw_value]
        elif meta.value_loader == "layout_weight":
            if not (isinstance(raw_value, tuple) and len(raw_value) == 2):
                raise RuntimeError("weight loader expects (layout_params_var, weight_value)")
            lp_var, weight_value = raw_value
            setup, value_expr = self._float_const_expr(weight_value, prefix=f"{view_id}_{attr_name}")
            stmts.extend(setup)
            args = [lp_var, value_expr]
        elif meta.value_loader == "relative_rules":
            lp_var, rules = raw_value
            if not isinstance(rules, (list, tuple)):
                raise RuntimeError("relative rules must be list of (verb, anchor) pairs")
            for verb, anchor in rules:
                stmts.append(
                    call_stmt(
                        "addRule",
                        args=[lp_var, const(int(verb)), const(int(anchor))],
                        return_type=None,
                        arg_types=["I", "I"],
                        invoke_kind="virtual",
                        owner="Landroid/widget/RelativeLayout$LayoutParams;",
                    )
                )
            return stmts
        elif meta.value_loader == "constraint_fields":
            lp_var, field_pairs = raw_value
            if not isinstance(field_pairs, (list, tuple)):
                raise RuntimeError("constraint fields must be list of (field, type, value)")
            for field_name, field_type, value_expr in field_pairs:
                stmts.append(
                    field_set(
                        lp_var,
                        "Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;",
                        field_name,
                        field_type,
                        value_expr,
                    )
                )
            return stmts
        elif meta.value_loader == "background":
            if not (isinstance(raw_value, tuple) and len(raw_value) == 2):
                raise RuntimeError("background loader expects (bg_color, radius_value)")
            bg_color, radius_value = raw_value
            if bg_color is None:
                return []
            if radius_value is not None and not isinstance(radius_value, (Dp, Px)):
                raise RuntimeError("background radius must use dp()/px() units.")
            if radius_value is None:
                out = []
                out.extend(
                    self._emit_attr_call(
                        view_id=view_id,
                        attr_name="background_color",
                        raw_value=bg_color,
                    )
                )
                return out
            bg_name = f"bg_{view_id}"
            color_key = self._add_color_resource(f"{view_id}_bg", bg_color)
            color_load, color_expr = self._load_color_expr(color_key, ctx_expr=var("ctx"), prefix=f"{view_id}_bg")
            radius_key = self._add_dimen_resource(f"{view_id}_radius", radius_value, unit="px")
            radius_load, radius_expr = self._load_dimen_float_expr(radius_key, ctx_expr=var("ctx"), prefix=f"{view_id}_radius")
            stmts.extend(color_load)
            stmts.extend(radius_load)
            stmts.append(assign(bg_name, new("Landroid/graphics/drawable/GradientDrawable;", args=[])))
            stmts.append(
                call_stmt(
                    "setColor",
                    args=[var(bg_name), color_expr],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/graphics/drawable/GradientDrawable;",
                )
            )
            stmts.append(
                call_stmt(
                    "setCornerRadius",
                    args=[var(bg_name), radius_expr],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/graphics/drawable/GradientDrawable;",
                )
            )
            stmts.append(
                call_stmt(
                    "setBackground",
                    args=[var(view_id), var(bg_name)],
                    return_type=None,
                    arg_types=["Landroid/graphics/drawable/Drawable;"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
            return stmts

        else:
            # simple literal
            args = [var(view_id), const(raw_value)]

        if meta.arg_prefix:
            prefix_args = [const(v) for v in meta.arg_prefix]
            args = [args[0], *prefix_args, *args[1:]]

        owner = meta.owner

        if getattr(meta, "owner_resolver", None) == "gravity_owner":
            view_type = self.view_types.get(view_id)
            if view_type in ("row", "column"):
                owner = "Landroid/widget/LinearLayout;"
            else:
                owner = "Landroid/widget/TextView;"
        elif getattr(meta, "owner_resolver", None) == "thumb_tint_owner":
            view_type = self.view_types.get(view_id)
            if view_type == "switch":
                owner = "Landroid/widget/Switch;"
            else:
                owner = "Landroid/widget/SeekBar;"
        elif getattr(meta, "owner_resolver", None) == "progress_tint_owner":
            view_type = self.view_types.get(view_id)
            if view_type == "progress_bar":
                owner = "Landroid/widget/ProgressBar;"
            else:
                owner = "Landroid/widget/SeekBar;"

        if owner is None:
            return []

        if meta.emit_kind == "field_set":
            stmts.append(
                field_set(
                    args[0],
                    owner,
                    meta.field_name,
                    meta.field_desc,
                    args[1],
                )
            )
        elif meta.emit_kind == "custom" and meta.field_map is not None:
            lp_var, value_map = args
            if not isinstance(value_map, dict):
                raise RuntimeError("custom attr mapping expects dict value")
            for key, value in value_map.items():
                if key not in meta.field_map:
                    continue
                field_name, field_desc = meta.field_map[key]
                if field_desc == "F":
                    setup, expr = self._float_const_expr(value, prefix=f"{view_id}_{key}")
                    stmts.extend(setup)
                    value_expr = expr
                else:
                    value_expr = const(int(value))
                stmts.append(
                    field_set(
                        lp_var,
                        "Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;",
                        field_name,
                        field_desc,
                        value_expr,
                    )
                )
        else:
            stmts.append(
                call_stmt(
                    meta.method,
                    args=args,
                    return_type=None,
                    arg_types=meta.arg_types,
                    invoke_kind=meta.invoke_kind,
                    owner=owner,
                )
            )

        return stmts


    def _capture_view_static(self, item_id: str):
        field_name = self.view_fields[item_id]
        desc = self._view_desc(self.view_types[item_id])
        view_id_value = self._numeric_id(item_id)
        return [
            call_stmt(
                "setId",
                args=[var(item_id), const(view_id_value)],
                return_type=None,
                arg_types=["I"],
                invoke_kind="virtual",
                owner="Landroid/view/View;",
            ),
            static_set(field_name, desc, var(item_id)),
        ]

    def build_program(self, event_specs, resources=None):
        body = []
        fields = []
        methods = []
        self._resources = dict(resources or {})
        self._resource_ids = {}
        self._resource_colors = {}
        self._resource_color_ids = {}
        self._resource_dimens = {}
        self._resource_dimen_ids = {}
        self._resource_styles = {}
        self._resource_style_ids = {}
        self._container_orientation = {self.root_id: "vertical"}
        self._popup_button_items = {}
        self._build_theme_resources()

        # Ensure app_ctx is available for resource helper calls.
        fields.append(static_field("app_ctx", "Landroid/app/Activity;", access="public static"))
        body.append(static_set("app_ctx", "Landroid/app/Activity;", var("ctx")))
        floating_items = [item for item in self.ui_spec.items if getattr(item, "floating", False)]
        scroll_items = [item for item in self.ui_spec.items if not getattr(item, "floating", False)]
        use_overlay_root = bool(floating_items)
        screen_root_id = None
        if use_overlay_root:
            screen_root_id = self._register_view("_screen_root", "relative")
            body.extend(relative_layout(screen_root_id, var("ctx")))
        body.extend(linear_layout(self.root_id, var("ctx"), "vertical"))

        # Resource helper methods (LTestRes)
        res_methods = []
        res_map = {}

        def _res_method(name, ret_type, res_call):
            res_methods.append(
                method(
                    name,
                    params=["res_id"],
                    param_types=["I"],
                    return_type=ret_type,
                    body=[
                        assign("ctx", static_get("app_ctx", "Landroid/app/Activity;", owner="LTest;")),
                        assign(
                            "res",
                            call(
                                "getResources",
                                args=[var("ctx")],
                                invoke_kind="virtual",
                                owner="Landroid/content/Context;",
                            ),
                        ),
                        assign(
                            "out",
                            call(
                                res_call,
                                args=[var("res"), var("res_id")],
                                return_type=ret_type,
                                arg_types=["I"],
                                invoke_kind="virtual",
                                owner="Landroid/content/res/Resources;",
                            ),
                        ),
                        ret(var("out")),
                    ],
                )
            )
            res_map[name] = "LTestRes;"

        _res_method("res_get_string", "Ljava/lang/String;", "getString")
        _res_method("res_get_color", "I", "getColor")
        _res_method("res_get_dimen_px", "I", "getDimensionPixelSize")
        _res_method("res_get_dimen_float", "F", "getDimension")

        methods.extend(res_methods)

        # UI creation (split by statement count)
        max_stmts = 120
        helper_idx = 0
        pending = []
        pending_count = 0

        def _flush_helper(parent_id):
            nonlocal helper_idx, pending, pending_count
            if not pending:
                return
            helper_name = f"buildUi_{helper_idx}"
            helper_idx += 1
            helper_body = [*pending, ret()]
            methods.append(
                method(
                    helper_name,
                    params=["ctx", "parent"],
                    param_types=["Landroid/app/Activity;", "Landroid/view/ViewGroup;"],
                    return_type=None,
                    body=helper_body,
                )
            )
            body.append(
                call_stmt(
                    helper_name,
                    args=[var("ctx"), var(parent_id)],
                    return_type=None,
                    arg_types=["Landroid/app/Activity;", "Landroid/view/ViewGroup;"],
                    invoke_kind="static",
                    owner="LTest;",
                )
            )
            pending = []
            pending_count = 0

        for item in scroll_items:
            item_stmts = self._build_ui_items("parent", [item])
            if pending and pending_count + len(item_stmts) > max_stmts:
                _flush_helper(self.root_id)
            pending.extend(item_stmts)
            pending_count += len(item_stmts)
        _flush_helper(self.root_id)

        if use_overlay_root:
            prev_parent_kind = self.view_types.get("parent")
            self.view_types["parent"] = "relative"
            try:
                for item in floating_items:
                    item_stmts = self._build_ui_items("parent", [item])
                    if pending and pending_count + len(item_stmts) > max_stmts:
                        _flush_helper(screen_root_id)
                    pending.extend(item_stmts)
                    pending_count += len(item_stmts)
                _flush_helper(screen_root_id)
            finally:
                if prev_parent_kind is None:
                    self.view_types.pop("parent", None)
                else:
                    self.view_types["parent"] = prev_parent_kind

        # Declare static refs for views
        for vid, field_name in self.view_fields.items():
            desc = self._view_desc(self.view_types[vid])
            fields.append(static_field(field_name, desc, access="public static"))

        # Navigation stack fields (screen-only)
        if self._screens:
            fields.append(static_field("nav_stack", "[I", access="public static"))
            fields.append(static_field("nav_size", "I", access="public static"))
            fields.append(static_field("nav_current", "I", access="public static"))

        # State fields
        for name, value in self.state_spec.values.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise RuntimeError(
                    f"State '{name}' must be an integer literal, got {value!r} ({type(value).__name__})"
                )
            fields.append(static_field(name, "I"))
            body.append(static_set(name, "I", const(value)))

        # Navigation stack init (after screens are built)
        if self._screens:
            nav_limit = self._nav_limit()
            stack_tmp = self._next_tmp("nav_stack")
            body.extend(
                [
                    assign(stack_tmp, new_array(const(nav_limit), "I")),
                    static_set("nav_stack", "[I", var(stack_tmp)),
                    array_set(var(stack_tmp), const(0), "I", const(0)),
                    static_set("nav_size", "I", const(1)),
                    static_set("nav_current", "I", const(0)),
                ]
            )

        # System back bridge for wrapper activity.
        methods.append(self._compile_system_back_method())

        # Accessors for cross-class handlers (keep fields private)
        handler_owner_desc = "LTestHandlers;"
        self._handler_owner_desc = handler_owner_desc
        self._state_accessors = {}
        if handler_owner_desc != "LTest;" and self.state_spec.values:
            for name in self.state_spec.values.keys():
                getter = f"get_state_{name}"
                setter = f"set_state_{name}"
                self._state_accessors[name] = (getter, setter)
                methods.append(
                    method(
                        getter,
                        params=[],
                        param_types=[],
                        return_type="I",
                        body=[
                            assign("v", static_get(name, "I", owner="LTest;")),
                            ret(var("v")),
                        ],
                    )
                )
                methods.append(
                    method(
                        setter,
                        params=["value"],
                        param_types=["I"],
                        return_type=None,
                        body=[
                            static_set(name, "I", var("value"), owner="LTest;"),
                            ret(),
                        ],
                    )
                )

        # Wire event handlers
        handler_methods = []
        support_classes = []
        method_class_map = {}
        explicit_click_ids = set()
        popup_menu_listener_map = {}

        for spec in event_specs or []:
            event_kind = getattr(spec, "event_kind", "click")
            target_id = getattr(spec, "target_id", getattr(spec, "button_id", None))
            if target_id is None:
                raise RuntimeError(f"Malformed event spec: missing target id for event '{event_kind}'")
            if target_id not in self.view_types:
                known = ", ".join(sorted(self.view_types.keys()))
                raise RuntimeError(
                    f"{event_kind} target '{target_id}' not found in ui() ids. "
                    f"Known ids: [{known}]"
                )
            view_kind = self.view_types.get(target_id)
            view_desc = self._view_desc(view_kind)
            view_field = self.view_fields[target_id]
            compiled_stmts = self._compile_stmts(spec.stmts or [])

            if event_kind == "click":
                explicit_click_ids.add(target_id)
                clickable_kinds = {
                    "button",
                    "raised_button",
                    "flat_button",
                    "icon_button",
                    "fab",
                    "popup_button",
                }
                if view_kind not in clickable_kinds:
                    raise RuntimeError(
                        f"on_click target '{target_id}' is not clickable (kind={view_kind})."
                    )
                handler_name = f"onClick_{target_id}"
                listener_desc = f"Lcom/anali/preview/AnaliClickListener_{target_id};"
                tmp_btn = f"_btn_{target_id}"
                body.append(assign(tmp_btn, static_get(view_field, view_desc)))
                body.extend(on_click_view(var(tmp_btn), handler_name=handler_name, listener_class_desc=listener_desc))
                support_classes.append((listener_desc, handler_name, handler_owner_desc, "click"))
                handler_methods.append(
                    (
                        handler_name,
                        ["view"],
                        ["Landroid/view/View;"],
                        compiled_stmts,
                    )
                )
                method_class_map[handler_name] = handler_owner_desc
            elif event_kind == "change":
                if view_kind not in {"checkbox", "switch", "radio"}:
                    raise RuntimeError(
                        f"on_change target '{target_id}' must be checkbox/switch/radio (kind={view_kind})."
                    )
                handler_name = f"onChange_{target_id}"
                listener_desc = f"Lcom/anali/preview/AnaliChangeListener_{target_id};"
                tmp_btn = f"_chg_{target_id}"
                body.append(assign(tmp_btn, static_get(view_field, view_desc)))
                body.extend(on_change_view(var(tmp_btn), handler_name=handler_name, listener_class_desc=listener_desc))
                support_classes.append((listener_desc, handler_name, handler_owner_desc, "change"))
                handler_methods.append(
                    (
                        handler_name,
                        ["button", "is_checked"],
                        ["Landroid/widget/CompoundButton;", "Z"],
                        compiled_stmts,
                    )
                )
                method_class_map[handler_name] = handler_owner_desc
            elif event_kind == "text_change":
                if view_kind != "text_field":
                    raise RuntimeError(
                        f"on_text_change target '{target_id}' must be text_field (kind={view_kind})."
                    )
                handler_name = f"onTextChange_{target_id}"
                listener_desc = f"Lcom/anali/preview/AnaliTextChangeListener_{target_id};"
                tmp_input = f"_txt_{target_id}"
                body.append(assign(tmp_input, static_get(view_field, view_desc)))
                body.extend(
                    on_text_change_view(
                        var(tmp_input),
                        handler_name=handler_name,
                        listener_class_desc=listener_desc,
                    )
                )
                support_classes.append((listener_desc, handler_name, handler_owner_desc, "text_change"))
                handler_methods.append(
                    (
                        handler_name,
                        ["editable"],
                        ["Landroid/text/Editable;"],
                        compiled_stmts,
                    )
                )
                method_class_map[handler_name] = handler_owner_desc
            elif event_kind == "item_selected":
                if view_kind != "dropdown":
                    raise RuntimeError(
                        f"on_item_selected target '{target_id}' must be dropdown (kind={view_kind})."
                    )
                handler_name = f"onItemSelected_{target_id}"
                listener_desc = f"Lcom/anali/preview/AnaliItemSelectedListener_{target_id};"
                tmp_spinner = f"_item_{target_id}"
                body.append(assign(tmp_spinner, static_get(view_field, view_desc)))
                body.extend(
                    on_item_selected_view(
                        var(tmp_spinner),
                        handler_name=handler_name,
                        listener_class_desc=listener_desc,
                    )
                )
                support_classes.append((listener_desc, handler_name, handler_owner_desc, "item_selected"))
                handler_methods.append(
                    (
                        handler_name,
                        ["parent", "view", "position", "item_id"],
                        ["Landroid/widget/AdapterView;", "Landroid/view/View;", "I", "J"],
                        compiled_stmts,
                    )
                )
                method_class_map[handler_name] = handler_owner_desc
            elif event_kind == "focus_change":
                handler_name = f"onFocusChange_{target_id}"
                listener_desc = f"Lcom/anali/preview/AnaliFocusChangeListener_{target_id};"
                tmp_view = f"_focus_{target_id}"
                body.append(assign(tmp_view, static_get(view_field, view_desc)))
                body.extend(
                    on_focus_change_view(
                        var(tmp_view),
                        handler_name=handler_name,
                        listener_class_desc=listener_desc,
                    )
                )
                support_classes.append((listener_desc, handler_name, handler_owner_desc, "focus_change"))
                handler_methods.append(
                    (
                        handler_name,
                        ["view", "has_focus"],
                        ["Landroid/view/View;", "Z"],
                        compiled_stmts,
                    )
                )
                method_class_map[handler_name] = handler_owner_desc
            elif event_kind == "menu_item_selected":
                if view_kind != "popup_button":
                    raise RuntimeError(
                        f"on_menu_item_selected target '{target_id}' must be popup_button (kind={view_kind})."
                    )
                handler_name = f"onMenuItemSelected_{target_id}"
                listener_desc = f"Lcom/anali/preview/AnaliMenuItemListener_{target_id};"
                support_classes.append((listener_desc, handler_name, handler_owner_desc, "menu_item_selected"))
                handler_methods.append(
                    (
                        handler_name,
                        ["menu_item"],
                        ["Landroid/view/MenuItem;"],
                        compiled_stmts,
                    )
                )
                method_class_map[handler_name] = handler_owner_desc
                popup_menu_listener_map[target_id] = listener_desc
            else:
                raise RuntimeError(f"Unsupported event kind: {event_kind}")

        # Auto-wire popup behavior for PopupMenuButton without explicit on_click.
        for popup_id, popup_items in self._popup_button_items.items():
            if popup_id in explicit_click_ids and popup_id in popup_menu_listener_map:
                raise RuntimeError(
                    f"on_menu_item_selected target '{popup_id}' cannot be combined with explicit on_click on the same PopupMenuButton."
                )
            if popup_id in explicit_click_ids:
                continue
            if not popup_items and popup_id not in popup_menu_listener_map:
                continue
            handler_name = f"onClick_{popup_id}_popup"
            listener_desc = f"Lcom/anali/preview/AnaliClickListener_{popup_id}_popup;"
            view_desc = self._view_desc(self.view_types[popup_id])
            view_field = self.view_fields[popup_id]
            tmp_btn = f"_btn_{popup_id}_popup"
            body.append(assign(tmp_btn, static_get(view_field, view_desc)))
            body.extend(on_click_view(var(tmp_btn), handler_name=handler_name, listener_class_desc=listener_desc))
            support_classes.append((listener_desc, handler_name, handler_owner_desc, "click"))
            handler_methods.append(
                (
                    handler_name,
                    ["view"],
                    ["Landroid/view/View;"],
                    self._compile_popup_menu_handler(
                        popup_id=popup_id,
                        popup_items=popup_items,
                        view_field=view_field,
                        view_desc=view_desc,
                        menu_listener_class_desc=popup_menu_listener_map.get(popup_id),
                    ),
                )
            )
            method_class_map[handler_name] = handler_owner_desc
        method_class_map.update(res_map)

        # Main method
        if use_overlay_root and screen_root_id:
            methods.insert(
                0,
                method(
                    "main",
                    params=["ctx"],
                    param_types=["Landroid/app/Activity;"],
                    return_type=None,
                    body=[
                        *body,
                        assign("_scroll_root", new("Landroid/widget/ScrollView;", args=[var("ctx")])),
                        add_view(var("_scroll_root"), var(self.root_id)),
                        assign(
                            "_scroll_lp",
                            new(
                                "Landroid/widget/RelativeLayout$LayoutParams;",
                                args=[const(-1), const(-1)],
                                arg_types=["I", "I"],
                            ),
                        ),
                        set_layout_params(var("_scroll_root"), var("_scroll_lp")),
                        add_view(var(screen_root_id), var("_scroll_root")),
                        set_content_view(var("ctx"), var(screen_root_id)),
                        ret(),
                    ],
                ),
            )
        else:
            methods.insert(
                0,
                method(
                    "main",
                    params=["ctx"],
                    param_types=["Landroid/app/Activity;"],
                    return_type=None,
                    body=[
                        *body,
                        assign("_scroll_root", new("Landroid/widget/ScrollView;", args=[var("ctx")])),
                        add_view(var("_scroll_root"), var(self.root_id)),
                        set_content_view(var("ctx"), var("_scroll_root")),
                        ret(),
                    ],
                ),
            )

        for name, params, param_types, hbody in handler_methods:
            methods.append(event_handler(name, hbody, params=params, param_types=param_types))

        return program(
            methods,
            fields=fields,
            support_classes=support_classes,
            method_class_map=method_class_map,
            lint_warnings=self._lint_warnings,
            resources=self._resources,
            resource_ids=self._resource_ids,
            resource_colors=self._resource_colors,
            resource_color_ids=self._resource_color_ids,
            resource_dimens=self._resource_dimens,
            resource_dimen_ids=self._resource_dimen_ids,
            resource_styles=self._resource_styles,
            resource_style_ids=self._resource_style_ids,
        )

    def _build_theme_resources(self):
        palette = self.theme_spec.palette or {}
        if not palette:
            return
        style_items = {}
        primary = palette.get("primary")
        on_primary = palette.get("on_primary")
        accent = palette.get("accent", primary)
        if primary is not None:
            argb = _parse_color(primary, {})
            if argb is not None:
                ckey = self._add_color_resource("theme_primary", argb)
                style_items["android:colorPrimary"] = f"@color/{ckey}"
        if on_primary is not None:
            argb = _parse_color(on_primary, {})
            if argb is not None:
                ckey = self._add_color_resource("theme_on_primary", argb)
                style_items["android:textColorPrimary"] = f"@color/{ckey}"
        if accent is not None:
            argb = _parse_color(accent, {})
            if argb is not None:
                ckey = self._add_color_resource("theme_accent", argb)
                style_items["android:colorAccent"] = f"@color/{ckey}"
        if style_items:
            self._add_style_resource("AppTheme", style_items)

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
            # Match aapt2 type IDs (sorted by type name). string -> 0x0e.
            self._resource_ids[key] = 0x7F0E0000 + len(self._resource_ids)
        return key

    def _add_color_resource(self, name_hint: str, argb: int) -> str:
        key = self._resource_key(name_hint, f"{argb:08X}")
        self._resource_colors[key] = f"#{argb & 0xFFFFFFFF:08X}"
        if key not in self._resource_color_ids:
            # color -> 0x05
            self._resource_color_ids[key] = 0x7F050000 + len(self._resource_color_ids)
        return key

    def _add_dimen_resource(self, name_hint: str, value: int | float | Dp | Px | Sp, unit: str = "px") -> str:
        if isinstance(value, Dp):
            unit = "dp"
            value = value.value
        elif isinstance(value, Sp):
            unit = "sp"
            value = value.value
        elif isinstance(value, Px):
            unit = "px"
            value = value.value
        normalized = float(value) if isinstance(value, float) else int(value)
        key = self._resource_key(name_hint, f"{normalized}:{unit}")
        if isinstance(normalized, float):
            dimen_value = f"{normalized:g}{unit}"
        else:
            dimen_value = f"{int(normalized)}{unit}"
        self._resource_dimens[key] = dimen_value
        if key not in self._resource_dimen_ids:
            # dimen -> 0x06
            self._resource_dimen_ids[key] = 0x7F060000 + len(self._resource_dimen_ids)
        return key

    def _add_style_resource(self, name_hint: str, items: dict[str, str]) -> str:
        key = self._resource_key(name_hint, str(sorted(items.items())))
        self._resource_styles[key] = dict(items)
        if key not in self._resource_style_ids:
            # style -> 0x0f
            self._resource_style_ids[key] = 0x7F0F0000 + len(self._resource_style_ids)
        return key

    def _load_string_expr(self, res_name: str, *, ctx_expr=None, prefix="str"):
        p = self._next_tmp(prefix)
        sval = f"{p}_val"
        stmts = []
        rid_value = self._resource_ids.get(res_name)
        if rid_value is None:
            raise RuntimeError(f"Missing resource id for string '{res_name}'")
        stmts.append(
            assign(
                sval,
                call(
                    "res_get_string",
                    args=[const(rid_value)],
                    return_type="Ljava/lang/String;",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner="LTestRes;",
                ),
            )
        )
        return stmts, var(sval)

    def _load_color_expr(self, res_name: str, *, ctx_expr=None, prefix="color"):
        p = self._next_tmp(prefix)
        cval = f"{p}_val"
        stmts = []
        rid_value = self._resource_color_ids.get(res_name)
        if rid_value is None:
            raise RuntimeError(f"Missing color id for '{res_name}'")
        stmts.append(
            assign(
                cval,
                call(
                    "res_get_color",
                    args=[const(rid_value)],
                    return_type="I",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner="LTestRes;",
                ),
            )
        )
        return stmts, var(cval)

    def _load_dimen_px_expr(self, res_name: str, *, ctx_expr=None, prefix="dimen"):
        p = self._next_tmp(prefix)
        dval = f"{p}_val"
        stmts = []
        rid_value = self._resource_dimen_ids.get(res_name)
        if rid_value is None:
            raise RuntimeError(f"Missing dimen id for '{res_name}'")
        stmts.append(
            assign(
                dval,
                call(
                    "res_get_dimen_px",
                    args=[const(rid_value)],
                    return_type="I",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner="LTestRes;",
                ),
            )
        )
        return stmts, var(dval)

    def _load_dimen_float_expr(self, res_name: str, *, ctx_expr=None, prefix="dimenf"):
        p = self._next_tmp(prefix)
        dval = f"{p}_val"
        stmts = []
        rid_value = self._resource_dimen_ids.get(res_name)
        if rid_value is None:
            raise RuntimeError(f"Missing dimen id for '{res_name}'")
        stmts.append(
            assign(
                dval,
                call(
                    "res_get_dimen_float",
                    args=[const(rid_value)],
                    return_type="F",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner="LTestRes;",
                ),
            )
        )
        return stmts, var(dval)

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

    def _button_label(self, item) -> str:
        text = "" if getattr(item, "text", None) is None else str(item.text)
        icon = getattr(item, "icon", None)
        if icon is None:
            return text
        icon_text = str(icon).strip()
        if not icon_text:
            return text
        return f"{icon_text} {text}".strip()

    def _set_image_source(self, view_name: str, source):
        if source is None:
            return []
        if isinstance(source, bool):
            raise RuntimeError("Image source must be int resource id or drawable name string.")
        if isinstance(source, int):
            return [
                call_stmt(
                    "setImageResource",
                    args=[var(view_name), const(int(source))],
                    return_type=None,
                    invoke_kind="virtual",
                    owner="Landroid/widget/ImageView;",
                )
            ]
        if isinstance(source, str):
            rid_var = self._next_tmp(f"{view_name}_rid")
            res_var = self._next_tmp(f"{view_name}_res")
            pkg_var = self._next_tmp(f"{view_name}_pkg")
            return [
                assign(
                    res_var,
                    call(
                        "getResources",
                        args=[var("ctx")],
                        return_type="Landroid/content/res/Resources;",
                        invoke_kind="virtual",
                        owner="Landroid/content/Context;",
                    ),
                ),
                assign(
                    pkg_var,
                    call(
                        "getPackageName",
                        args=[var("ctx")],
                        return_type="Ljava/lang/String;",
                        invoke_kind="virtual",
                        owner="Landroid/content/Context;",
                    ),
                ),
                assign(
                    rid_var,
                    call(
                        "getIdentifier",
                        args=[var(res_var), const(source), const("drawable"), var(pkg_var)],
                        return_type="I",
                        invoke_kind="virtual",
                        owner="Landroid/content/res/Resources;",
                    ),
                ),
                call_stmt(
                    "setImageResource",
                    args=[var(view_name), var(rid_var)],
                    return_type=None,
                    invoke_kind="virtual",
                    owner="Landroid/widget/ImageView;",
                ),
            ]
        raise RuntimeError("Image source must be int resource id or drawable name string.")

    def _build_ui_items(self, parent_id, items):
        body = []
        for item in items:
            if self.registry is not None:
                handled = self.registry.render_ui(self, item, parent_id)
                if handled is not None:
                    body.extend(handled)
                    continue
            body.extend(self._render_ui_core(item, parent_id))
        return body

    def _render_ui_core(self, item, parent_id):
        body = []
        if isinstance(item, _UIAppBar):
            if item.inline:
                item.id = self._register_view(item.id, "app_bar")
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
                palette = self.theme_spec.palette
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
                text_color_value = item.text_color
                if text_color_value is None and getattr(item, "style", None):
                    text_color_value = item.style.text_color
                if isinstance(text_color_value, ColorState):
                    text_color_value = _parse_color(text_color_value.default, palette)
                else:
                    text_color_value = _parse_color(text_color_value, palette)
                if text_color_value is not None:
                    color_key = self._add_color_resource(f"{item.id}_title", text_color_value)
                    color_load, color_expr = self._load_color_expr(color_key, ctx_expr=var("ctx"), prefix=f"{item.id}_title")
                    body.extend(color_load)
                    body.append(
                        call_stmt(
                            "setTitleTextColor",
                            args=[var(item.id), color_expr],
                            return_type=None,
                            arg_types=["I"],
                            invoke_kind="virtual",
                            owner="Landroid/widget/Toolbar;",
                        )
                    )
                body.extend(self._apply_view_layout(item, parent_id))
                body.append(add_view(var(parent_id), var(item.id)))
                body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIDivider):
            item.id = self._register_view(item.id, "divider")
            body.extend([assign(item.id, new("Landroid/view/View;", args=[var("ctx")]))])
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIImage):
            item.id = self._register_view(item.id, "image")
            body.extend([assign(item.id, new("Landroid/widget/ImageView;", args=[var("ctx")]))])
            body.extend(self._set_image_source(item.id, item.src))
            if item.content_description:
                body.extend(
                    self._set_text_from_resource(
                        item.id,
                        item.content_description,
                        "Landroid/view/View;",
                        f"{item.id}_content_desc",
                        ctx_expr=var("ctx"),
                        method_name="setContentDescription",
                    )
                )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIProgressBar):
            item.id = self._register_view(item.id, "progress_bar")
            min_value = int(item.min)
            max_value = int(item.max)
            span = max(max_value - min_value, 0)
            progress = int(item.value) - min_value
            if progress < 0:
                progress = 0
            if progress > span:
                progress = span
            # ProgressBar default style is spinner. Use the horizontal style
            # constructor for determinate bars so value/max are visually shown.
            if item.indeterminate:
                progress_ctor = new("Landroid/widget/ProgressBar;", args=[var("ctx")])
            else:
                progress_ctor = new(
                    "Landroid/widget/ProgressBar;",
                    args=[var("ctx"), const(0), const(0x1010078)],
                    arg_types=[
                        "Landroid/content/Context;",
                        "Landroid/util/AttributeSet;",
                        "I",
                    ],
                )
            body.extend(
                [
                    assign(item.id, progress_ctor),
                    call_stmt(
                        "setIndeterminate",
                        args=[var(item.id), const(1 if item.indeterminate else 0)],
                        return_type=None,
                        arg_types=["Z"],
                        invoke_kind="virtual",
                        owner="Landroid/widget/ProgressBar;",
                    ),
                ]
            )
            if not item.indeterminate:
                body.extend(
                    [
                        call_stmt(
                            "setMax",
                            args=[var(item.id), const(span)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/ProgressBar;",
                        ),
                        call_stmt(
                            "setProgress",
                            args=[var(item.id), const(progress)],
                            return_type=None,
                            invoke_kind="virtual",
                            owner="Landroid/widget/ProgressBar;",
                        ),
                    ]
                )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIFloatingActionButton):
            item.id = self._register_view(item.id, "fab")
            body.extend(
                [
                    assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")])),
                ]
            )
            body.extend(self._set_text_from_resource(item.id, self._button_label(item), "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIRaisedButton):
            item.id = self._register_view(item.id, "raised_button")
            body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
            body.extend(self._set_text_from_resource(item.id, self._button_label(item), "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIFlatButton):
            item.id = self._register_view(item.id, "flat_button")
            body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
            body.extend(self._set_text_from_resource(item.id, self._button_label(item), "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIIconButton):
            item.id = self._register_view(item.id, "icon_button")
            body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
            body.extend(self._set_text_from_resource(item.id, self._button_label(item), "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UITextField):
            item.id = self._register_view(item.id, "text_field")
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
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UICheckbox):
            item.id = self._register_view(item.id, "checkbox")
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
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIRadio):
            item.id = self._register_view(item.id, "radio")
            body.extend(
                [
                    assign(item.id, new("Landroid/widget/RadioButton;", args=[var("ctx")])),
                ]
            )
            # RadioGroup tracks checked ids; id must be assigned before checked state is set.
            body.extend(self._capture_view_static(item.id))
            body.append(
                call_stmt(
                    "setChecked",
                    args=[var(item.id), const(1 if item.checked else 0)],
                    return_type=None,
                    arg_types=["Z"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/RadioButton;",
                )
            )
            body.extend(self._set_text_from_resource(item.id, item.text or "", "Landroid/widget/RadioButton;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
        elif isinstance(item, _UISwitch):
            item.id = self._register_view(item.id, "switch")
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
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UISlider):
            item.id = self._register_view(item.id, "slider")
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
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIDropdownButton):
            item.id = self._register_view(item.id, "dropdown")
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
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIButtonBar):
            item.id = self._register_view(item.id, "row")
            self._container_orientation[item.id] = "horizontal"
            body.extend(linear_layout(item.id, var("ctx"), "horizontal"))
            if item.weight_sum is not None:
                body.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="weight_sum",
                        raw_value=item.weight_sum,
                    )
                )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UIPopupMenuButton):
            item.id = self._register_view(item.id, "popup_button")
            self._popup_button_items[item.id] = [str(v) for v in (item.items or [])]
            body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
            body.extend(self._set_text_from_resource(item.id, self._button_label(item), "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIRadioGroup):
            item.id = self._register_view(item.id, "radio_group")
            orientation = "horizontal" if item.orientation == "horizontal" else "vertical"
            self._container_orientation[item.id] = orientation
            body.extend([assign(item.id, new("Landroid/widget/RadioGroup;", args=[var("ctx")]))])
            body.append(
                call_stmt(
                    "setOrientation",
                    args=[var(item.id), const(0 if orientation == "horizontal" else 1)],
                    return_type=None,
                    invoke_kind="virtual",
                    owner="Landroid/widget/LinearLayout;",
                )
            )
            if item.weight_sum is not None:
                body.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="weight_sum",
                        raw_value=item.weight_sum,
                    )
                )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UIContainer):
            item.id = self._register_view(item.id, "container")
            self._container_orientation[item.id] = "vertical"
            body.extend(linear_layout(item.id, var("ctx"), "vertical"))
            if item.weight_sum is not None:
                body.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="weight_sum",
                        raw_value=item.weight_sum,
                    )
                )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UICard):
            item.id = self._register_view(item.id, "card")
            self._container_orientation[item.id] = "vertical"
            body.extend(linear_layout(item.id, var("ctx"), "vertical"))
            if item.weight_sum is not None:
                body.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="weight_sum",
                        raw_value=item.weight_sum,
                    )
                )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UIRow):
            item.id = self._register_view(item.id, "row")
            self._container_orientation[item.id] = "horizontal"
            body.extend(linear_layout(item.id, var("ctx"), "horizontal"))
            if item.weight_sum is not None:
                body.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="weight_sum",
                        raw_value=item.weight_sum,
                    )
                )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UIColumn):
            item.id = self._register_view(item.id, "column")
            self._container_orientation[item.id] = "vertical"
            body.extend(linear_layout(item.id, var("ctx"), "vertical"))
            if item.weight_sum is not None:
                body.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="weight_sum",
                        raw_value=item.weight_sum,
                    )
                )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UIRelative):
            item.id = self._register_view(item.id, "relative")
            body.extend(relative_layout(item.id, var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UIConstraint):
            item.id = self._register_view(item.id, "constraint")
            body.extend(constraint_layout(item.id, var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UIScreen):
            item.id = self._register_view(item.id, "screen")
            self._screen_map[item.name] = item.id
            self._screens.append((item.name, item.id))
            self._container_orientation[item.id] = "vertical"
            body.extend(relative_layout(item.id, var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            # Default visibility: first screen visible, others gone.
            vis = 0 if len(self._screens) == 1 else 8
            body.append(
                call_stmt(
                    "setVisibility",
                    args=[var(item.id), const(vis)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            prev_screen = self._current_screen
            self._current_screen = item.name
            try:
                screen_root = _UIColumn(
                    *item.items,
                    id=f"{item.id}_root",
                    layout=("match_parent", "match_parent"),
                )
                screen_root.id = self._register_view(screen_root.id, "column")
                self._container_orientation[screen_root.id] = "vertical"
                body.extend(linear_layout(screen_root.id, var("ctx"), "vertical"))
                body.extend(self._apply_view_layout(screen_root, item.id))
                body.append(add_view(var(item.id), var(screen_root.id)))
                body.extend(self._capture_view_static(screen_root.id))
                body.extend(self._build_ui_items(screen_root.id, screen_root.items))
            finally:
                self._current_screen = prev_screen
        elif isinstance(item, _UIIcon):
            item.id = self._register_view(item.id, "icon")
            body.extend([assign(item.id, new("Landroid/widget/TextView;", args=[var("ctx")]))])
            body.extend(self._set_text_from_resource(item.id, item.text, "Landroid/widget/TextView;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIView):
            item.id = self._register_view(item.id, "view")
            body.extend([assign(item.id, new("Landroid/view/View;", args=[var("ctx")]))])
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIText):
            item.id = self._register_view(item.id, "text")
            body.extend([assign(item.id, new("Landroid/widget/TextView;", args=[var("ctx")]))])
            body.extend(self._set_text_from_resource(item.id, item.text, "Landroid/widget/TextView;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
        elif isinstance(item, _UIButton):
            item.id = self._register_view(item.id, "button")
            body.extend([assign(item.id, new("Landroid/widget/Button;", args=[var("ctx")]))])
            body.extend(self._set_text_from_resource(item.id, self._button_label(item), "Landroid/widget/Button;", f"{item.id}_text", ctx_expr=var("ctx")))
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
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
        if self.registry is not None:
            out = self.registry.compile_stmt(self, stmt)
            if out is not None:
                return out
        return self._compile_stmt_core(stmt)

    def _compile_stmt_core(self, stmt):
        if isinstance(stmt, str):
            raise RuntimeError("String statements are deprecated; use AST builder objects.")
        if isinstance(stmt, _StmtAssign):
            return self._compile_assign_stmt(stmt)
        if isinstance(stmt, _StmtSetText):
            return self._compile_set_text_stmt(stmt)
        if isinstance(stmt, _StmtExitApp):
            return self._compile_exit_app_stmt(stmt)
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
        if isinstance(stmt, _StmtLog):
            return self._compile_log_stmt(stmt)
        if isinstance(stmt, _StmtNavigate):
            return self._compile_navigate_stmt(stmt)
        if isinstance(stmt, _StmtBack):
            return self._compile_back_stmt(stmt)
        if isinstance(stmt, _StmtReplace):
            return self._compile_replace_stmt(stmt)
        if isinstance(stmt, _StmtRequestPermissions):
            return self._compile_request_permissions_stmt(stmt)
        raise RuntimeError(f"Unsupported statement: {stmt}")

    def _compile_exit_app_stmt(self, stmt):
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            call_stmt(
                "finish",
                args=[var("ctx")],
                return_type=None,
                invoke_kind="virtual",
                owner="Landroid/app/Activity;",
            )
        ]

    def _float_const_expr(self, value, prefix="f"):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise RuntimeError(f"Expected numeric float value, got {value!r}")
        flt_name = self._next_tmp(prefix)
        return [
            assign(flt_name, const(float(value))),
        ], var(flt_name)

    def _emit_linear_weight_sum(self, view_id, weight_sum):
        setup, weight_expr = self._float_const_expr(weight_sum, prefix=f"{view_id}_wsum")
        return [
            *setup,
            call_stmt(
                "setWeightSum",
                args=[var(view_id), weight_expr],
                return_type=None,
                arg_types=["F"],
                invoke_kind="virtual",
                owner="Landroid/widget/LinearLayout;",
            ),
        ]

    def _container_gravity(self, item, align_value, arrangement_value):
        h_map = {"start": 3, "left": 3, "center": 1, "end": 5, "right": 5}
        v_map = {"top": 48, "center": 16, "bottom": 80}
        is_row = isinstance(item, _UIRow)
        if is_row:
            h = h_map.get(str(arrangement_value).lower(), 3) if arrangement_value is not None else None
            v = v_map.get(str(align_value).lower(), 16) if align_value is not None else None
        else:
            h = h_map.get(str(align_value).lower(), 3) if align_value is not None else None
            v = v_map.get(str(arrangement_value).lower(), 48) if arrangement_value is not None else None
        if h is None and v is None:
            return None
        return (h or 0) | (v or 0)

    def _apply_view_layout(self, item, parent_id):
        out = []
        theme_style = Style()
        if isinstance(item, _UIText):
            theme_style = self.theme_spec.text
        elif isinstance(item, _UIButton) and not isinstance(item, (_UISlider, _UIDropdownButton, _UIPopupMenuButton)):
            theme_style = self.theme_spec.button
        elif isinstance(item, _UIRow):
            theme_style = self.theme_spec.row
        elif isinstance(item, _UIColumn):
            theme_style = self.theme_spec.column

        item_style = item.style if getattr(item, "style", None) else None
        style = theme_style.merged(item_style)

        padding_value = item.padding if item.padding is not None else style.padding
        gravity_value = item.gravity if item.gravity is not None else style.gravity
        align_value = getattr(item, "align", None) if getattr(item, "align", None) is not None else getattr(style, "align", None)
        arrangement_value = (
            getattr(item, "arrangement", None)
            if getattr(item, "arrangement", None) is not None
            else getattr(style, "arrangement", None)
        )
        weight_value = getattr(item, "weight", None) if getattr(item, "weight", None) is not None else getattr(style, "weight", None)
        layout_value = item.layout if item.layout is not None else style.layout
        width_value = getattr(item, "width", None)
        if width_value is None:
            width_value = getattr(style, "width", None)
        height_value = getattr(item, "height", None)
        if height_value is None:
            height_value = getattr(style, "height", None)
        if isinstance(width_value, Percent):
            parent_orientation = self._container_orientation.get(parent_id, "vertical")
            if parent_orientation != "horizontal":
                raise RuntimeError("Percent width is only supported in horizontal rows.")
            weight_value = width_value.value / 100.0 if width_value.value > 1 else width_value.value
            width_value = Dp(0)
        if isinstance(height_value, Percent):
            parent_orientation = self._container_orientation.get(parent_id, "vertical")
            if parent_orientation != "vertical":
                raise RuntimeError("Percent height is only supported in vertical columns.")
            weight_value = height_value.value / 100.0 if height_value.value > 1 else height_value.value
            height_value = Dp(0)
        margin_value = item.margin if item.margin is not None else style.margin
        relative_value = getattr(item, "relative", None) if getattr(item, "relative", None) is not None else getattr(style, "relative", None)
        constraints_value = getattr(item, "constraints", None) if getattr(item, "constraints", None) is not None else getattr(style, "constraints", None)
        text_color_value = item.text_color if getattr(item, "text_color", None) is not None else style.text_color
        background_value = item.background if getattr(item, "background", None) is not None else style.background
        radius_value = item.radius if getattr(item, "radius", None) is not None else style.radius
        text_size_value = item.text_size if getattr(item, "text_size", None) is not None else style.text_size
        font_family_value = getattr(item, "font_family", None) if getattr(item, "font_family", None) is not None else getattr(style, "font_family", None)
        font_weight_value = getattr(item, "font_weight", None) if getattr(item, "font_weight", None) is not None else getattr(style, "font_weight", None)
        font_style_value = getattr(item, "font_style", None) if getattr(item, "font_style", None) is not None else getattr(style, "font_style", None)
        letter_spacing_value = getattr(item, "letter_spacing", None) if getattr(item, "letter_spacing", None) is not None else getattr(style, "letter_spacing", None)
        line_height_value = getattr(item, "line_height", None) if getattr(item, "line_height", None) is not None else getattr(style, "line_height", None)
        text_alignment_value = getattr(item, "text_alignment", None) if getattr(item, "text_alignment", None) is not None else getattr(style, "text_alignment", None)
        all_caps_value = getattr(item, "all_caps", None) if getattr(item, "all_caps", None) is not None else getattr(style, "all_caps", None)
        max_lines_value = getattr(item, "max_lines", None) if getattr(item, "max_lines", None) is not None else getattr(style, "max_lines", None)
        ellipsize_value = getattr(item, "ellipsize", None) if getattr(item, "ellipsize", None) is not None else getattr(style, "ellipsize", None)
        tint_value = getattr(item, "tint", None) if getattr(item, "tint", None) is not None else getattr(style, "tint", None)
        thumb_tint_value = getattr(item, "thumb_tint", None) if getattr(item, "thumb_tint", None) is not None else getattr(style, "thumb_tint", None)
        track_tint_value = getattr(item, "track_tint", None) if getattr(item, "track_tint", None) is not None else getattr(style, "track_tint", None)
        progress_tint_value = getattr(item, "progress_tint", None) if getattr(item, "progress_tint", None) is not None else getattr(style, "progress_tint", None)
        button_tint_value = getattr(item, "button_tint", None) if getattr(item, "button_tint", None) is not None else getattr(style, "button_tint", None)

        if margin_value is None and getattr(item, "floating", False):
            margin_value = Dp(16)
        if isinstance(radius_value, (int, float)) and not isinstance(radius_value, bool):
            radius_value = Dp(radius_value)
        if isinstance(text_size_value, (int, float)) and not isinstance(text_size_value, bool):
            text_size_value = Sp(text_size_value)

        padding_value = self._normalize_box_spacing(padding_value, "padding")
        margin_value = self._normalize_box_spacing(margin_value, "margin")
        layout_value = self._normalize_layout_value(layout_value)
        if gravity_value is None and (align_value is not None or arrangement_value is not None):
            gravity_value = self._container_gravity(item, align_value, arrangement_value)
        if width_value is not None or height_value is not None:
            base_layout = layout_value if layout_value is not None else ("wrap", "wrap")
            layout_value = (
                width_value if width_value is not None else base_layout[0],
                height_value if height_value is not None else base_layout[1],
            )
        if layout_value is None and isinstance(item, _UIRow):
            layout_value = ("match_parent", "wrap")
        if weight_value is not None and layout_value is None:
            parent_orientation = self._container_orientation.get(parent_id, "vertical")
            if parent_orientation == "horizontal":
                layout_value = (Dp(0), "wrap")
            else:
                layout_value = ("match_parent", Dp(0))
        if weight_value is not None and layout_value is not None:
            parent_orientation = self._container_orientation.get(parent_id, "vertical")
            def _is_zero_size(val):
                if val in (0, "0"):
                    return True
                if isinstance(val, (Dp, Px)) and val.value == 0:
                    return True
                return False
            if parent_orientation == "horizontal" and not _is_zero_size(layout_value[0]):
                self._lint_warnings.append(
                    f"weight on '{item.id}' in horizontal container should use width=dp(0) for proper weight."
                )
            if parent_orientation == "vertical" and not _is_zero_size(layout_value[1]):
                self._lint_warnings.append(
                    f"weight on '{item.id}' in vertical container should use height=dp(0) for proper weight."
                )
        gravity_value = self._normalize_gravity(gravity_value)

        if padding_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="padding",
                    raw_value=padding_value,
                )
            )

        if gravity_value is not None and (align_value is not None or arrangement_value is not None):
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="align",
                    raw_value=gravity_value,
                )
            )
        elif gravity_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="gravity",
                    raw_value=gravity_value,
                )
            )


        palette = self.theme_spec.palette
        bg_color = _parse_color(background_value, palette)
        txt_color = None if isinstance(text_color_value, ColorState) else _parse_color(text_color_value, palette)
        if bg_color is not None or radius_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="background",
                    raw_value=(bg_color, radius_value),
                )
            )

        if txt_color is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="text_color",
                    raw_value=txt_color,
                )
            )
        elif isinstance(text_color_value, ColorState):
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="text_color_state",
                    raw_value=text_color_value,
                )
            )


        if text_size_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="text_size",
                    raw_value=text_size_value,
                )
            )

        if font_family_value is not None or font_weight_value is not None or font_style_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="typeface",
                    raw_value=(font_family_value, font_weight_value, font_style_value),
                )
            )

        if letter_spacing_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="letter_spacing",
                    raw_value=letter_spacing_value,
                )
            )

        if line_height_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="line_height",
                    raw_value=line_height_value,
                )
            )

        if text_alignment_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="text_alignment",
                    raw_value=text_alignment_value,
                )
            )

        if all_caps_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="all_caps",
                    raw_value=all_caps_value,
                )
            )

        if max_lines_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="max_lines",
                    raw_value=max_lines_value,
                )
            )

        if ellipsize_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="ellipsize",
                    raw_value=ellipsize_value,
                )
            )

        if tint_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="tint",
                    raw_value=tint_value,
                )
            )

        if thumb_tint_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="thumb_tint",
                    raw_value=thumb_tint_value,
                )
            )

        if track_tint_value is not None:
            if self.view_types.get(item.id) == "slider":
                out.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="slider_track_tint",
                        raw_value=track_tint_value,
                    )
                )
            else:
                out.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="switch_track_tint",
                        raw_value=track_tint_value,
                    )
                )

        if progress_tint_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="progress_tint",
                    raw_value=progress_tint_value,
                )
            )
            if self.view_types.get(item.id) == "progress_bar":
                out.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="indeterminate_tint",
                        raw_value=progress_tint_value,
                    )
                )

        if button_tint_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="button_tint",
                    raw_value=button_tint_value,
                )
            )

        if layout_value or margin_value or weight_value is not None or relative_value is not None or constraints_value is not None:
            if getattr(item, "floating", False) and relative_value is None:
                relative_value = [("align_parent_bottom", "parent"), ("align_parent_end", "parent")]
            if layout_value is None:
                layout_value = ("wrap", "wrap")
            width, height = layout_value if layout_value else ("wrap", "wrap")
            lp_name = f"lp_{item.id}"
            parent_kind = self.view_types.get(parent_id, "column")
            if parent_kind == "relative":
                parent_lp = "RelativeLayout"
            elif parent_kind == "constraint":
                parent_lp = "ConstraintLayout"
            else:
                parent_lp = "LinearLayout"
            if parent_lp == "RelativeLayout":
                lp_desc = "Landroid/widget/RelativeLayout$LayoutParams;"
            elif parent_lp == "ConstraintLayout":
                lp_desc = "Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;"
            else:
                lp_desc = "Landroid/widget/LinearLayout$LayoutParams;"
            w_setup, w_expr = self._layout_size_expr(width, prefix=f"{item.id}_w")
            h_setup, h_expr = self._layout_size_expr(height, prefix=f"{item.id}_h")
            out.extend(w_setup)
            out.extend(h_setup)
            out.append(
                assign(
                    lp_name,
                    new(lp_desc, args=[w_expr, h_expr], arg_types=["I", "I"]),
                )
            )
            if weight_value is not None:
                out.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="weight",
                        raw_value=(var(lp_name), weight_value),
                    )
                )
            if margin_value:
                out.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="margin",
                        raw_value=(var(lp_name), margin_value),
                    )
                )
            if parent_lp == "RelativeLayout" and relative_value is not None:
                rules = self._normalize_relative_rules(relative_value, parent_id=parent_id)
                out.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="relative",
                        raw_value=(var(lp_name), rules),
                    )
                )
            if parent_lp == "ConstraintLayout" and constraints_value is not None:
                constraints = self._normalize_constraints(constraints_value, parent_id=parent_id)
                field_pairs = []
                meta = ATTR_METHODS.get("constraints")
                if meta and meta.field_map:
                    for key, value in constraints.items():
                        if key not in meta.field_map:
                            continue
                        field_name, field_desc = meta.field_map[key]
                        if field_desc == "F":
                            setup, expr = self._float_const_expr(value, prefix=f"{item.id}_{key}")
                            out.extend(setup)
                            value_expr = expr
                        else:
                            value_expr = const(int(value))
                        field_pairs.append((field_name, field_desc, value_expr))
                out.extend(
                    self._emit_attr_call(
                        view_id=item.id,
                        attr_name="constraints",
                        raw_value=(var(lp_name), field_pairs),
                    )
                )
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="layout_params",
                    raw_value=var(lp_name),
                )
            )
        return out

    def _normalize_box_spacing(self, value, attr_name):
        if value is None:
            return None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            value = Dp(value)
        if isinstance(value, (Dp, Px)):
            return (value, value, value, value)
        if isinstance(value, (tuple, list)):
            if len(value) == 2:
                h, v = value
                if isinstance(h, (int, float)) and not isinstance(h, bool):
                    h = Dp(h)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    v = Dp(v)
                for entry in (h, v):
                    if not isinstance(entry, (Dp, Px)):
                        raise RuntimeError(
                            f"Invalid {attr_name} value {value!r}. Use dp()/px() units."
                        )
                return (h, v, h, v)
            if len(value) == 4:
                l, t, r, b = value
                if isinstance(l, (int, float)) and not isinstance(l, bool):
                    l = Dp(l)
                if isinstance(t, (int, float)) and not isinstance(t, bool):
                    t = Dp(t)
                if isinstance(r, (int, float)) and not isinstance(r, bool):
                    r = Dp(r)
                if isinstance(b, (int, float)) and not isinstance(b, bool):
                    b = Dp(b)
                for entry in (l, t, r, b):
                    if not isinstance(entry, (Dp, Px)):
                        raise RuntimeError(
                            f"Invalid {attr_name} value {value!r}. Use dp()/px() units."
                        )
                return (l, t, r, b)
        raise RuntimeError(
            f"Invalid {attr_name} value {value!r}. Use dp()/px() units (e.g., dp(16) or (dp(16), dp(8)))."
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

    def _layout_size_expr(self, value, *, prefix):
        if isinstance(value, str):
            key = value.lower().strip()
            if key in ("match", "match_parent", "fill", "max", "max_width", "max_height"):
                return [], const(-1)
            if key in ("wrap", "wrap_content"):
                return [], const(-2)
            raise RuntimeError(f"Unknown layout size: {value}")
        if isinstance(value, Percent):
            raise RuntimeError("Percent sizes must be handled by layout weight.")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return [], const(int(value))
        if isinstance(value, (Dp, Px)):
            key = self._add_dimen_resource(f"{prefix}_size", value)
            stmts, expr = self._load_dimen_px_expr(key, ctx_expr=var("ctx"), prefix=f"{prefix}_size")
            return stmts, expr
        if isinstance(value, Sp):
            raise RuntimeError("sp units are not valid for layout size.")
        if isinstance(value, int):
            raise RuntimeError("Layout sizes must use dp()/px() or wrap()/fill().")
        raise RuntimeError(f"Unsupported layout size: {value!r}")

    def _normalize_relative_rules(self, value, *, parent_id):
        if value is None:
            return None
        if not isinstance(value, (list, tuple)):
            raise RuntimeError("relative expects a list/tuple of rules")
        verb_map = {
            "align_parent_left": 9,
            "align_parent_right": 11,
            "align_parent_top": 10,
            "align_parent_bottom": 12,
            "align_parent_start": 20,
            "align_parent_end": 21,
            "center_horizontal": 14,
            "center_vertical": 15,
            "center_in_parent": 13,
            "align_left": 5,
            "align_right": 7,
            "align_top": 6,
            "align_bottom": 8,
            "left_of": 0,
            "right_of": 1,
            "above": 2,
            "below": 3,
            "align_baseline": 4,
            "align_start": 17,
            "align_end": 19,
            "start_of": 16,
            "end_of": 18,
        }
        out = []
        for rule in value:
            if not isinstance(rule, (tuple, list)) or len(rule) != 2:
                raise RuntimeError("relative rule must be (verb, target)")
            verb, target = rule
            verb_key = str(verb).lower().strip()
            if verb_key not in verb_map:
                raise RuntimeError(f"Unknown relative rule verb: {verb}")
            if target is None or target == "parent":
                # RelativeLayout.TRUE
                target_id = -1
            else:
                target_id = self._view_id_value(target, parent_id=parent_id)
            out.append((verb_map[verb_key], int(target_id)))
        return out

    def _normalize_constraints(self, value, *, parent_id):
        if value is None:
            return None
        if not isinstance(value, dict):
            raise RuntimeError("constraints expects a dict")
        out = {}
        for key, target in value.items():
            if key in ("horizontal_bias", "vertical_bias", "circle_angle"):
                out[key] = float(target)
                continue
            if key == "circle_radius":
                out[key] = int(target)
                continue
            if target is None or target == "parent":
                out[key] = 0
                continue
            out[key] = self._view_id_value(target, parent_id=parent_id)
        return out

    def _view_id_value(self, view_id, *, parent_id=None):
        if isinstance(view_id, int):
            return view_id
        if view_id == "parent" or view_id is None:
            return 0
        if view_id == parent_id:
            raise RuntimeError("Constraints cannot target the parent by id; use 'parent'.")
        resolved = self.view_fields.get(view_id)
        if resolved is None:
            raise RuntimeError(f"Unknown view id: {view_id}")
        return self._numeric_id(view_id)

    def _numeric_id(self, view_id):
        digest = hashlib.md5(view_id.encode("utf-8")).hexdigest()
        return 0x70000000 | (int(digest[:6], 16) & 0x00FFFFFF)

    def _normalize_gravity(self, value):
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            key = value.lower().strip()
            mapping = {
                "center": 17,
                "center_horizontal": 1,
                "center_vertical": 16,
                "start": 3,
                "left": 3,
                "end": 5,
                "right": 5,
                "top": 48,
                "bottom": 80,
            }
            if key in mapping:
                return mapping[key]
        raise RuntimeError(
            f"Invalid gravity value {value!r}. Expected int or one of center/start/end/top/bottom variants."
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
            accessor = self._state_accessor(name)
            if accessor:
                _, setter = accessor
                return [
                    *prefix,
                    call_stmt(
                        setter,
                        args=[result],
                        return_type=None,
                        arg_types=["I"],
                        invoke_kind="static",
                        owner="LTest;",
                    ),
                ]
            return [*prefix, static_set(name, "I", result)]

        self._local_vars.add(name)
        local_expr = result.name if isinstance(result, Var) else result
        return [*prefix, assign(name, local_expr)]

    def _next_tmp(self, prefix="tmp"):
        self._tmp_counter += 1
        return f"{prefix}_{self._tmp_counter}"

    def _state_accessor(self, name):
        if getattr(self, "_handler_owner_desc", "LTest;") == "LTest;":
            return None
        accessors = getattr(self, "_state_accessors", None) or {}
        return accessors.get(name)

    def _compile_int_expr(self, expr):
        if isinstance(expr, _ExprConst):
            if not isinstance(expr.value, int) or isinstance(expr.value, bool):
                raise RuntimeError(
                    f"Integer expression expected an int constant, got {expr.value!r} ({type(expr.value).__name__})"
                )
            return [], const(expr.value)
        if isinstance(expr, _ExprSymbol):
            if expr.name in self.state_spec.values:
                accessor = self._state_accessor(expr.name)
                t = self._next_tmp("s")
                if accessor:
                    getter, _ = accessor
                    return [
                        assign(
                            t,
                            call(
                                getter,
                                args=[],
                                return_type="I",
                                arg_types=[],
                                invoke_kind="static",
                                owner="LTest;",
                            ),
                        )
                    ], var(t)
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
            if expr.name in self.state_spec.values:
                accessor = self._state_accessor(expr.name)
                if accessor:
                    getter, _ = accessor
                    t = self._next_tmp("s")
                    return [
                        assign(
                            t,
                            call(
                                getter,
                                args=[],
                                return_type="I",
                                arg_types=[],
                                invoke_kind="static",
                                owner="LTest;",
                            ),
                        )
                    ], t
                return [], expr.name
            if expr.name in self._local_vars:
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

    def _compile_popup_menu_handler(
        self,
        *,
        popup_id: str,
        popup_items,
        view_field: str,
        view_desc: str,
        menu_listener_class_desc: str | None = None,
    ):
        out = [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign("anchor", static_get(view_field, view_desc)),
            assign(
                "popup",
                new(
                    "Landroid/widget/PopupMenu;",
                    args=[var("ctx"), var("anchor")],
                    arg_types=["Landroid/content/Context;", "Landroid/view/View;"],
                ),
            ),
            assign(
                "menu",
                call(
                    "getMenu",
                    args=[var("popup")],
                    return_type="Landroid/view/Menu;",
                    arg_types=[],
                    invoke_kind="virtual",
                    owner="Landroid/widget/PopupMenu;",
                ),
            ),
        ]

        if menu_listener_class_desc:
            listener_var = self._next_tmp(f"{popup_id}_menu_listener")
            out.extend(
                [
                    assign(
                        listener_var,
                        new(
                            menu_listener_class_desc,
                            args=[],
                        ),
                    ),
                    call_stmt(
                        "setOnMenuItemClickListener",
                        args=[var("popup"), var(listener_var)],
                        return_type=None,
                        invoke_kind="virtual",
                        owner="Landroid/widget/PopupMenu;",
                    ),
                ]
            )

        for idx, label in enumerate(popup_items):
            label_key = self._add_string_resource(f"{popup_id}_item_{idx}", str(label))
            label_load, label_expr = self._load_string_expr(label_key, prefix=f"{popup_id}_item_{idx}")
            out.extend(label_load)
            out.append(
                assign(
                    self._next_tmp(f"{popup_id}_item_ref"),
                    call(
                        "add",
                        args=[var("menu"), label_expr],
                        return_type="Landroid/view/MenuItem;",
                        arg_types=["Ljava/lang/CharSequence;"],
                        invoke_kind="interface",
                        owner="Landroid/view/Menu;",
                    ),
                )
            )

        out.append(
            call_stmt(
                "show",
                args=[var("popup")],
                return_type=None,
                arg_types=[],
                invoke_kind="virtual",
                owner="Landroid/widget/PopupMenu;",
            )
        )
        out.append(ret())
        return out

    def _compile_snackbar_stmt(self, stmt):
        msg_key = self._add_string_resource("snackbar_msg", stmt.message)
        msg_load, msg_expr = self._load_string_expr(msg_key, prefix="snackbar_msg")
        # DSL duration uses 0/1 (short/long). Snackbar constants are -1/0.
        if stmt.duration == 0:
            snackbar_duration = -1
        elif stmt.duration == 1:
            snackbar_duration = 0
        else:
            snackbar_duration = int(stmt.duration)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            *msg_load,
            assign(
                "snackbar_anchor",
                call(
                    "findViewById",
                    args=[var("ctx"), const(0x01020002)],
                    return_type="Landroid/view/View;",
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/app/Activity;",
                ),
            ),
            assign(
                "snackbar_obj",
                call(
                    "make",
                    args=[var("snackbar_anchor"), msg_expr, const(snackbar_duration)],
                    invoke_kind="static",
                    owner="Lcom/google/android/material/snackbar/Snackbar;",
                ),
            ),
            call_stmt(
                "show",
                args=[var("snackbar_obj")],
                return_type=None,
                invoke_kind="virtual",
                owner="Lcom/google/android/material/snackbar/Snackbar;",
            ),
        ]

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

    def _compile_log_stmt(self, stmt):
        return [
            call_stmt(
                "d",
                args=[const(stmt.tag), const(stmt.message)],
                return_type=None,
                invoke_kind="static",
                owner="Landroid/util/Log;",
            )
        ]

    def _compile_request_permissions_stmt(self, stmt):
        from dsl.capabilities import normalize_permission

        perms = [normalize_permission(p) for p in (stmt.permissions or [])]
        if not perms:
            raise RuntimeError("request_permissions requires at least one permission")
        arr_tmp = self._next_tmp("perm_arr")
        out = [
            assign(arr_tmp, new_array(const(len(perms)), "Ljava/lang/String;")),
        ]
        for idx, perm in enumerate(perms):
            out.append(
                array_set(
                    var(arr_tmp),
                    const(idx),
                    "Ljava/lang/String;",
                    const(perm),
                )
            )
        out.append(assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")))
        out.append(
            call_stmt(
                "requestPermissions",
                args=[var("ctx"), var(arr_tmp), const(int(getattr(stmt, "request_code", 0) or 0))],
                return_type=None,
                arg_types=["[Ljava/lang/String;", "I"],
                invoke_kind="virtual",
                owner="Landroid/app/Activity;",
            )
        )
        return out

    def _compile_navigate_stmt(self, stmt):
        if not self._screens:
            raise RuntimeError("Navigate used without any Screen definitions")
        target_idx = self._nav_screen_index(stmt.target)
        out = []
        stack_var = self._next_tmp("nav_stack")
        size_var = self._next_tmp("nav_size")
        cur_var = self._next_tmp("nav_current")
        new_size_var = self._next_tmp("nav_size")
        out.append(assign(stack_var, static_get("nav_stack", "[I")))
        out.append(assign(size_var, static_get("nav_size", "I")))
        out.append(assign(cur_var, static_get("nav_current", "I")))
        out.extend(self._nav_set_visibility_for_index(var(cur_var), 8))
        out.extend(self._nav_set_visibility_for_index(const(target_idx), 0))

        push_then = [
            array_set(var(stack_var), var(size_var), "I", const(target_idx)),
            assign(new_size_var, binary("+", var(size_var), const(1))),
            static_set("nav_size", "I", var(new_size_var)),
        ]
        replace_else = [
            assign(new_size_var, binary("-", var(size_var), const(1))),
            array_set(var(stack_var), var(new_size_var), "I", const(target_idx)),
            static_set("nav_size", "I", var(size_var)),
        ]
        out.append(
            if_(
                compare("<", var(size_var), const(self._nav_limit())),
                push_then,
                replace_else,
            )
        )
        out.append(static_set("nav_current", "I", const(target_idx)))
        return out

    def _compile_back_stmt(self, stmt):
        if not self._screens:
            raise RuntimeError("Back used without any Screen definitions")
        out = []
        stack_var = self._next_tmp("nav_stack")
        size_var = self._next_tmp("nav_size")
        cur_var = self._next_tmp("nav_current")
        new_size_var = self._next_tmp("nav_size")
        top_idx_var = self._next_tmp("nav_top_idx")
        prev_idx_var = self._next_tmp("nav_prev")

        out.append(assign(stack_var, static_get("nav_stack", "[I")))
        out.append(assign(size_var, static_get("nav_size", "I")))
        out.append(assign(cur_var, static_get("nav_current", "I")))

        then_block = []
        then_block.extend(self._nav_set_visibility_for_index(var(cur_var), 8))
        then_block.append(assign(new_size_var, binary("-", var(size_var), const(1))))
        then_block.append(assign(top_idx_var, binary("-", var(new_size_var), const(1))))
        then_block.append(assign(prev_idx_var, array_get(var(stack_var), var(top_idx_var), "I")))
        then_block.extend(self._nav_set_visibility_for_index(var(prev_idx_var), 0))
        then_block.append(static_set("nav_size", "I", var(new_size_var)))
        then_block.append(static_set("nav_current", "I", var(prev_idx_var)))

        out.append(if_(compare(">", var(size_var), const(1)), then_block, []))
        return out

    def _compile_system_back_method(self):
        if not self._screens:
            return method(
                "onSystemBack",
                params=[],
                param_types=[],
                return_type="I",
                body=[ret(const(0))],
            )

        out = []
        stack_var = self._next_tmp("nav_stack")
        size_var = self._next_tmp("nav_size")
        cur_var = self._next_tmp("nav_current")
        new_size_var = self._next_tmp("nav_size")
        top_idx_var = self._next_tmp("nav_top_idx")
        prev_idx_var = self._next_tmp("nav_prev")

        out.append(assign(stack_var, static_get("nav_stack", "[I")))
        out.append(assign(size_var, static_get("nav_size", "I")))
        out.append(assign(cur_var, static_get("nav_current", "I")))
        out.append(assign("handled", const(0)))

        then_block = []
        then_block.extend(self._nav_set_visibility_for_index(var(cur_var), 8))
        then_block.append(assign(new_size_var, binary("-", var(size_var), const(1))))
        then_block.append(assign(top_idx_var, binary("-", var(new_size_var), const(1))))
        then_block.append(assign(prev_idx_var, array_get(var(stack_var), var(top_idx_var), "I")))
        then_block.extend(self._nav_set_visibility_for_index(var(prev_idx_var), 0))
        then_block.append(static_set("nav_size", "I", var(new_size_var)))
        then_block.append(static_set("nav_current", "I", var(prev_idx_var)))
        then_block.append(assign("handled", const(1)))

        out.append(if_(compare(">", var(size_var), const(1)), then_block, []))
        out.append(ret(var("handled")))
        return method(
            "onSystemBack",
            params=[],
            param_types=[],
            return_type="I",
            body=out,
        )

    def _compile_replace_stmt(self, stmt):
        if not self._screens:
            raise RuntimeError("Replace used without any Screen definitions")
        target_idx = self._nav_screen_index(stmt.target)
        out = []
        stack_var = self._next_tmp("nav_stack")
        size_var = self._next_tmp("nav_size")
        cur_var = self._next_tmp("nav_current")
        top_idx_var = self._next_tmp("nav_top_idx")

        out.append(assign(stack_var, static_get("nav_stack", "[I")))
        out.append(assign(size_var, static_get("nav_size", "I")))
        out.append(assign(cur_var, static_get("nav_current", "I")))
        out.extend(self._nav_set_visibility_for_index(var(cur_var), 8))
        out.extend(self._nav_set_visibility_for_index(const(target_idx), 0))

        then_block = [
            assign(top_idx_var, binary("-", var(size_var), const(1))),
            array_set(var(stack_var), var(top_idx_var), "I", const(target_idx)),
            static_set("nav_size", "I", var(size_var)),
        ]
        else_block = [
            array_set(var(stack_var), const(0), "I", const(target_idx)),
            static_set("nav_size", "I", const(1)),
        ]
        out.append(if_(compare(">", var(size_var), const(0)), then_block, else_block))
        out.append(static_set("nav_current", "I", const(target_idx)))
        return out

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
                    accessor = self._state_accessor(part.name)
                    if accessor:
                        getter, _ = accessor
                        stmts.append(
                            assign(
                                "x",
                                call(
                                    getter,
                                    args=[],
                                    return_type="I",
                                    arg_types=[],
                                    invoke_kind="static",
                                    owner="LTest;",
                                ),
                            )
                        )
                    else:
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
