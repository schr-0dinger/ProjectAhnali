import hashlib
import copy
import re
from typing import Any

from ir.expr import Var

from dsl.android.resources import _parse_color
from dsl.ast import (
    _ExprBinary,
    _ExprBoolOp,
    _ExprCompare,
    _ExprConst,
    _ExprFormat,
    _ExprStorageGet,
    _ExprSymbol,
    _ExprUnary,
    _StmtAssign,
    _StmtExitApp,
    _StmtIf,
    _StmtBack,
    _StmtAnimate,
    _StmtAnimationGroup,
    _StmtReplace,
    _StmtRequestPermissions,
    _StmtSetText,
    _StmtSimpleDialog,
    _StmtSnackbar,
    _StmtToast,
    _StmtOpenUrl,
    _StmtCheckConnectivity,
    _StmtStorageGet,
    _StmtStorageRemove,
    _StmtStoragePut,
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
    on_radio_group_change_view,
    on_slider_change_view,
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
    Gradient,
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
    _UIHorizontalScrollView,
    _UIIcon,
    _UIIconButton,
    _UIImage,
    _UIListView,
    _UIPopupMenuButton,
    _UIProgressBar,
    _UIRadio,
    _UIRadioGroup,
    _UIRelative,
    _UIRaisedButton,
    _UIRow,
    _UIScrollView,
    _UIScreen,
    _UISlider,
    _UISwitch,
    _UIText,
    _UITextField,
    _UIView,
)
from dsl.lowering.attr_registry import ATTR_METHODS


class _PythonicContext:
    def __init__(
        self,
        state_spec: State,
        ui_spec: Any,
        theme_spec: Theme,
        *,
        min_sdk: int = 21,
        registry=None,
        runtime_bindings=None,
    ):
        self.state_spec = state_spec
        self.ui_spec = ui_spec
        self.theme_spec = theme_spec
        self.min_sdk = int(min_sdk)
        self.registry = registry
        self.capability_runtime_bindings = dict(runtime_bindings or {})
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
        self._local_var_types: dict[str, str] = {}
        self._container_orientation = {self.root_id: "vertical"}
        self._lint_warnings = []
        self._lint_warning_keys = set()
        self._screens = []
        self._screen_map = {}
        self._screen_transitions = {}
        self._current_screen = None
        self._view_screen = {}
        self._nav_stack_limit = 0
        self._popup_button_items = {}
        self._generated_support_classes = []

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
        if kind == "scroll_view":
            return "Landroid/widget/ScrollView;"
        if kind == "horizontal_scroll_view":
            return "Landroid/widget/HorizontalScrollView;"
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
        if kind == "list_view":
            return "Landroid/widget/ListView;"
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
            "scroll_view",
            "horizontal_scroll_view",
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
            "list_view",
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

    def _queue_support_class(self, class_desc: str, target_method: str, target_desc: str, kind: str):
        entry = (class_desc, target_method, target_desc, kind)
        if entry not in self._generated_support_classes:
            self._generated_support_classes.append(entry)

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

    def _normalize_screen_transition(self, raw):
        if raw is None:
            return None
        key = str(raw).strip().lower().replace("-", "_")
        allowed = {
            "fade",
            "slide_left",
            "slide_right",
            "slide_up",
            "slide_down",
        }
        if key not in allowed:
            supported = ", ".join(sorted(allowed))
            raise RuntimeError(
                f"Unsupported screen transition '{raw}'. Supported: [{supported}]"
            )
        return key

    def _screen_transition_for_name(self, screen_name):
        return self._screen_transitions.get(screen_name)

    def _screen_transition_for_index(self, idx):
        if idx < 0 or idx >= len(self._screens):
            return None
        name = self._screens[idx][0]
        return self._screen_transition_for_name(name)

    def _nav_emit_enter_transition_for_screen(self, screen_id, transition):
        if not transition:
            return []
        field_name = self.view_fields.get(screen_id)
        if not field_name:
            raise RuntimeError(f"Missing view field for screen '{screen_id}'")
        desc = self._view_desc("screen")
        screen_var = self._next_tmp(f"{screen_id}_anim")
        animator_var = self._next_tmp(f"{screen_id}_animator")
        out = [assign(screen_var, static_get(field_name, desc))]

        if transition == "fade":
            out.append(
                call_stmt(
                    "setAlpha",
                    args=[var(screen_var), const(0.0)],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
            anim_method = "alpha"
            anim_value = 1.0
        elif transition == "slide_left":
            out.append(
                call_stmt(
                    "setTranslationX",
                    args=[var(screen_var), const(96.0)],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
            anim_method = "translationX"
            anim_value = 0.0
        elif transition == "slide_right":
            out.append(
                call_stmt(
                    "setTranslationX",
                    args=[var(screen_var), const(-96.0)],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
            anim_method = "translationX"
            anim_value = 0.0
        elif transition == "slide_up":
            out.append(
                call_stmt(
                    "setTranslationY",
                    args=[var(screen_var), const(96.0)],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
            anim_method = "translationY"
            anim_value = 0.0
        elif transition == "slide_down":
            out.append(
                call_stmt(
                    "setTranslationY",
                    args=[var(screen_var), const(-96.0)],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )
            anim_method = "translationY"
            anim_value = 0.0
        else:
            raise RuntimeError(f"Unsupported transition '{transition}'")

        out.append(
            assign(
                animator_var,
                call(
                    "animate",
                    args=[var(screen_var)],
                    return_type="Landroid/view/ViewPropertyAnimator;",
                    arg_types=[],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                ),
            )
        )
        out.append(
            assign(
                animator_var,
                call(
                    anim_method,
                    args=[var(animator_var), const(anim_value)],
                    return_type=None,
                    arg_types=["F"],
                    invoke_kind="virtual",
                    owner="Landroid/view/ViewPropertyAnimator;",
                ),
            )
        )
        out.append(
            call_stmt(
                "start",
                args=[var(animator_var)],
                return_type=None,
                arg_types=[],
                invoke_kind="virtual",
                owner="Landroid/view/ViewPropertyAnimator;",
            )
        )
        return out

    def _nav_emit_enter_transition_for_index(self, idx_expr):
        out = []
        for idx, (name, screen_id) in enumerate(self._screens):
            transition = self._screen_transition_for_name(name)
            if not transition:
                continue
            then = self._nav_emit_enter_transition_for_screen(screen_id, transition)
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

    def _coerce_bool_flag(self, value, *, field_name):
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        raise RuntimeError(f"{field_name} must be a bool when provided.")

    def _warn_once(self, key: str, message: str):
        if key in self._lint_warning_keys:
            return
        self._lint_warning_keys.add(key)
        self._lint_warnings.append(message)

    def _style_field_supported_kinds(self, field_name: str, field_value):
        if field_name in {"font_family", "font_weight", "font_style"}:
            meta = ATTR_METHODS.get("typeface")
            if meta and meta.supported_kinds is not None:
                return set(meta.supported_kinds)
            return None

        if field_name == "track_tint":
            supported = set()
            for key in ("slider_track_tint", "switch_track_tint"):
                meta = ATTR_METHODS.get(key)
                if meta and meta.supported_kinds is not None:
                    supported.update(meta.supported_kinds)
            return supported or None

        if field_name == "text_color" and isinstance(field_value, ColorState):
            meta = ATTR_METHODS.get("text_color_state")
            if meta and meta.supported_kinds is not None:
                return set(meta.supported_kinds)
            return None

        meta = ATTR_METHODS.get(field_name)
        if meta and meta.supported_kinds is not None:
            return set(meta.supported_kinds)
        return None

    def _validate_style_fields_for_widget(self, item, style_obj, *, source: str):
        if not isinstance(style_obj, Style):
            return
        kind = self.view_types.get(item.id)
        if kind is None:
            return
        for field_name, field_value in style_obj.__dict__.items():
            if field_value is None:
                continue
            supported = self._style_field_supported_kinds(field_name, field_value)
            if supported is None:
                continue
            if kind in supported:
                continue
            supported_list = ", ".join(sorted(supported))
            raise RuntimeError(
                f"Incompatible style field '{field_name}' on widget '{item.id}' "
                f"(kind={kind}) in {source}. Supported kinds: [{supported_list}]"
            )

    def _validate_state_keys(self):
        reserved_keys = {"app_ctx", "nav_stack", "nav_size", "nav_current"}
        view_field_names = set(self.view_fields.values())
        for key in self.state_spec.values.keys():
            if not isinstance(key, str):
                raise RuntimeError(
                    f"Invalid state key {key!r}. State keys must be strings."
                )
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                raise RuntimeError(
                    f"Invalid state key '{key}'. Expected pattern: [A-Za-z_][A-Za-z0-9_]*."
                )
            if key in reserved_keys:
                raise RuntimeError(
                    f"Invalid state key '{key}'. This key is reserved by the runtime."
                )
            if key in view_field_names:
                raise RuntimeError(
                    f"Invalid state key '{key}'. It conflicts with a generated widget field name."
                )

    def _resolve_text_input_type_value(self, item):
        type_class_text = 0x00000001
        type_class_number = 0x00000002
        type_mask_class = 0x0000000F
        type_text_flag_multi_line = 0x00020000
        type_text_flag_cap_characters = 0x00001000
        type_text_flag_cap_words = 0x00002000
        type_text_flag_cap_sentences = 0x00004000
        type_text_variation_password = 0x00000080
        type_number_variation_password = 0x00000010

        raw_input_type = getattr(item, "input_type", None)
        raw_single_line = getattr(item, "single_line", None)
        raw_password = getattr(item, "password", False)
        raw_auto_capitalize = getattr(item, "auto_capitalize", None)
        raw_numeric_only = getattr(item, "numeric_only", False)

        single_line = self._coerce_bool_flag(raw_single_line, field_name="single_line")
        password = self._coerce_bool_flag(raw_password, field_name="password")
        numeric_only = self._coerce_bool_flag(raw_numeric_only, field_name="numeric_only")

        has_config = (
            raw_input_type is not None
            or single_line is not None
            or bool(password)
            or raw_auto_capitalize is not None
            or bool(numeric_only)
        )
        if not has_config:
            return None

        if raw_input_type is None:
            input_type_value = type_class_text
        elif isinstance(raw_input_type, bool):
            raise RuntimeError("input_type must be a string or int, not bool.")
        elif isinstance(raw_input_type, int):
            input_type_value = int(raw_input_type)
        elif isinstance(raw_input_type, str):
            mapping = {
                "text": type_class_text,
                "multiline": type_class_text | type_text_flag_multi_line,
                "email": type_class_text | 0x00000020,
                "uri": type_class_text | 0x00000010,
                "password": type_class_text | type_text_variation_password,
                "text_password": type_class_text | type_text_variation_password,
                "visible_password": type_class_text | 0x00000090,
                "number": type_class_number,
                "number_decimal": type_class_number | 0x00002000,
                "number_signed": type_class_number | 0x00001000,
                "number_decimal_signed": type_class_number | 0x00003000,
                "number_password": type_class_number | type_number_variation_password,
                "phone": 0x00000003,
                "datetime": 0x00000004,
                "date": 0x00000014,
                "time": 0x00000024,
            }
            key = raw_input_type.strip().lower()
            if key not in mapping:
                known = ", ".join(sorted(mapping.keys()))
                raise RuntimeError(f"Unsupported input_type '{raw_input_type}'. Known: [{known}]")
            input_type_value = mapping[key]
        else:
            raise RuntimeError("input_type must be a string or int.")

        if numeric_only:
            input_type_value = (input_type_value & ~type_mask_class) | type_class_number

        if raw_auto_capitalize is not None:
            if (input_type_value & type_mask_class) != type_class_text:
                raise RuntimeError("auto_capitalize is only valid for text input types.")
            if isinstance(raw_auto_capitalize, bool):
                cap_mode = "sentences" if raw_auto_capitalize else "none"
            elif isinstance(raw_auto_capitalize, str):
                cap_mode = raw_auto_capitalize.strip().lower()
            else:
                raise RuntimeError("auto_capitalize must be bool or one of: none, characters, words, sentences.")
            cap_map = {
                "none": 0,
                "characters": type_text_flag_cap_characters,
                "words": type_text_flag_cap_words,
                "sentences": type_text_flag_cap_sentences,
            }
            if cap_mode not in cap_map:
                known = ", ".join(sorted(cap_map.keys()))
                raise RuntimeError(f"Unsupported auto_capitalize '{raw_auto_capitalize}'. Known: [{known}]")
            input_type_value &= ~(
                type_text_flag_cap_characters
                | type_text_flag_cap_words
                | type_text_flag_cap_sentences
            )
            input_type_value |= cap_map[cap_mode]

        if single_line is not None and (input_type_value & type_mask_class) == type_class_text:
            if single_line:
                input_type_value &= ~type_text_flag_multi_line
            else:
                input_type_value |= type_text_flag_multi_line

        if password:
            if (input_type_value & type_mask_class) == type_class_number:
                input_type_value |= type_number_variation_password
            else:
                input_type_value = (input_type_value & ~type_mask_class) | type_class_text
                input_type_value |= type_text_variation_password

        return int(input_type_value)

    def _resolve_ime_options_value(self, raw_value):
        if raw_value is None:
            return None
        if isinstance(raw_value, bool):
            raise RuntimeError("ime_options must be string or int, not bool.")
        if isinstance(raw_value, int):
            return int(raw_value)
        if not isinstance(raw_value, str):
            raise RuntimeError("ime_options must be string or int.")

        mapping = {
            "unspecified": 0x00000000,
            "none": 0x00000001,
            "go": 0x00000002,
            "search": 0x00000003,
            "send": 0x00000004,
            "next": 0x00000005,
            "done": 0x00000006,
            "previous": 0x00000007,
            "no_fullscreen": 0x02000000,
            "no_extract_ui": 0x10000000,
            "no_enter_action": 0x40000000,
        }
        value = 0
        parts = [p.strip().lower() for p in raw_value.replace(",", "|").split("|") if p.strip()]
        if not parts:
            raise RuntimeError("ime_options string cannot be empty.")
        for part in parts:
            token = part
            for prefix in ("ime_action_", "action_", "ime_flag_", "flag_"):
                if token.startswith(prefix):
                    token = token[len(prefix):]
            if token not in mapping:
                known = ", ".join(sorted(mapping.keys()))
                raise RuntimeError(f"Unsupported ime_options token '{part}'. Known: [{known}]")
            value |= mapping[token]
        return int(value)

    def _build_text_field_input_config_stmts(self, item):
        stmts = []

        input_type_value = self._resolve_text_input_type_value(item)
        if input_type_value is not None:
            stmts.append(
                call_stmt(
                    "setInputType",
                    args=[var(item.id), const(input_type_value)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/TextView;",
                )
            )

        ime_options_value = self._resolve_ime_options_value(getattr(item, "ime_options", None))
        if ime_options_value is not None:
            stmts.append(
                call_stmt(
                    "setImeOptions",
                    args=[var(item.id), const(ime_options_value)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/TextView;",
                )
            )

        max_length_value = getattr(item, "max_length", None)
        if max_length_value is not None:
            if isinstance(max_length_value, bool):
                raise RuntimeError("max_length must be an integer >= 0.")
            try:
                max_length_int = int(max_length_value)
            except (TypeError, ValueError):
                raise RuntimeError("max_length must be an integer >= 0.") from None
            if max_length_int < 0:
                raise RuntimeError("max_length must be >= 0.")
            filter_var = self._next_tmp(f"{item.id}_length_filter")
            filters_arr = self._next_tmp(f"{item.id}_filters")
            stmts.extend(
                [
                    assign(
                        filter_var,
                        new(
                            "Landroid/text/InputFilter$LengthFilter;",
                            args=[const(max_length_int)],
                            arg_types=["I"],
                        ),
                    ),
                    assign(filters_arr, new_array(const(1), "Landroid/text/InputFilter;")),
                    array_set(
                        var(filters_arr),
                        const(0),
                        "Landroid/text/InputFilter;",
                        var(filter_var),
                    ),
                    call_stmt(
                        "setFilters",
                        args=[var(item.id), var(filters_arr)],
                        return_type=None,
                        arg_types=["[Landroid/text/InputFilter;"],
                        invoke_kind="virtual",
                        owner="Landroid/widget/TextView;",
                    ),
                ]
            )

        single_line_value = self._coerce_bool_flag(getattr(item, "single_line", None), field_name="single_line")
        if single_line_value is not None:
            stmts.append(
                call_stmt(
                    "setSingleLine",
                    args=[var(item.id), const(1 if single_line_value else 0)],
                    return_type=None,
                    arg_types=["Z"],
                    invoke_kind="virtual",
                    owner="Landroid/widget/TextView;",
                )
            )

        password_enabled = self._coerce_bool_flag(getattr(item, "password", False), field_name="password")
        if password_enabled:
            transform_var = self._next_tmp(f"{item.id}_password_tm")
            stmts.extend(
                [
                    assign(
                        transform_var,
                        call(
                            "getInstance",
                            args=[],
                            invoke_kind="static",
                            owner="Landroid/text/method/PasswordTransformationMethod;",
                            return_type="Landroid/text/method/PasswordTransformationMethod;",
                        ),
                    ),
                    call_stmt(
                        "setTransformationMethod",
                        args=[var(item.id), var(transform_var)],
                        return_type=None,
                        arg_types=["Landroid/text/method/TransformationMethod;"],
                        invoke_kind="virtual",
                        owner="Landroid/widget/TextView;",
                    ),
                ]
            )

        return stmts

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
        self._screens = []
        self._screen_map = {}
        self._screen_transitions = {}
        self._view_screen = {}
        self._current_screen = None
        self._nav_stack_limit = 0
        self._generated_support_classes = []
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
        self._validate_state_keys()
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
                listener_desc = f"Lcom/ahnali/preview/AhnaliClickListener_{target_id};"
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
                if view_kind not in {"checkbox", "switch", "radio", "slider", "radio_group"}:
                    raise RuntimeError(
                        "on_change target "
                        f"'{target_id}' must be checkbox/switch/radio/slider/radio_group (kind={view_kind})."
                    )
                handler_name = f"onChange_{target_id}"
                listener_desc = f"Lcom/ahnali/preview/AhnaliChangeListener_{target_id};"
                if view_kind in {"checkbox", "switch", "radio"}:
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
                elif view_kind == "slider":
                    tmp_slider = f"_chg_{target_id}"
                    body.append(assign(tmp_slider, static_get(view_field, view_desc)))
                    body.extend(
                        on_slider_change_view(
                            var(tmp_slider),
                            handler_name=handler_name,
                            listener_class_desc=listener_desc,
                        )
                    )
                    support_classes.append((listener_desc, handler_name, handler_owner_desc, "slider_change"))
                    handler_methods.append(
                        (
                            handler_name,
                            ["seekbar", "progress", "from_user"],
                            ["Landroid/widget/SeekBar;", "I", "Z"],
                            compiled_stmts,
                        )
                    )
                elif view_kind == "radio_group":
                    tmp_group = f"_chg_{target_id}"
                    body.append(assign(tmp_group, static_get(view_field, view_desc)))
                    body.extend(
                        on_radio_group_change_view(
                            var(tmp_group),
                            handler_name=handler_name,
                            listener_class_desc=listener_desc,
                        )
                    )
                    support_classes.append((listener_desc, handler_name, handler_owner_desc, "radiogroup_change"))
                    handler_methods.append(
                        (
                            handler_name,
                            ["group", "checked_id"],
                            ["Landroid/widget/RadioGroup;", "I"],
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
                listener_desc = f"Lcom/ahnali/preview/AhnaliTextChangeListener_{target_id};"
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
                listener_desc = f"Lcom/ahnali/preview/AhnaliItemSelectedListener_{target_id};"
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
                listener_desc = f"Lcom/ahnali/preview/AhnaliFocusChangeListener_{target_id};"
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
                listener_desc = f"Lcom/ahnali/preview/AhnaliMenuItemListener_{target_id};"
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
            listener_desc = f"Lcom/ahnali/preview/AhnaliClickListener_{popup_id}_popup;"
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
        for extra_entry in self._generated_support_classes:
            if extra_entry not in support_classes:
                support_classes.append(extra_entry)

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
            body.extend(self._build_text_field_input_config_stmts(item))
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
        elif isinstance(item, _UIListView):
            item.id = self._register_view(item.id, "list_view")
            if item.layout is None:
                item.layout = ("match_parent", "wrap")
            item_layout_res = int(item.item_layout_res)
            if item_layout_res != 0x1090003:
                raise RuntimeError(
                    f"ListView '{item.id}' item_layout={item_layout_res} is not yet supported by "
                    "the deterministic adapter path; use simple_list_item_1."
                )
            adapter_name = f"adapter_{item.id}"
            items_array_name = f"items_{item.id}"
            adapter_class_desc = f"Lcom/ahnali/preview/AhnaliListAdapter_{item.id};"
            body.extend(
                [
                    assign(item.id, new("Landroid/widget/ListView;", args=[var("ctx")])),
                    assign(
                        items_array_name,
                        new_array(const(len(item.items)), "Ljava/lang/String;"),
                    ),
                ]
            )
            for idx, val in enumerate(item.items):
                item_key = self._add_string_resource(f"{item.id}_item", str(val))
                item_load, item_expr = self._load_string_expr(
                    item_key,
                    ctx_expr=var("ctx"),
                    prefix=f"{item.id}_item",
                )
                body.extend(item_load)
                body.append(
                    array_set(
                        var(items_array_name),
                        const(idx),
                        "Ljava/lang/String;",
                        item_expr,
                    )
                )
            body.extend(
                [
                    assign(
                        adapter_name,
                        new(
                            adapter_class_desc,
                            args=[var("ctx"), var(items_array_name)],
                            arg_types=["Landroid/content/Context;", "[Ljava/lang/String;"],
                        ),
                    ),
                    call_stmt(
                        "setAdapter",
                        args=[var(item.id), var(adapter_name)],
                        return_type=None,
                        invoke_kind="virtual",
                        owner="Landroid/widget/ListView;",
                    ),
                ]
            )
            self._queue_support_class(
                adapter_class_desc,
                str(item_layout_res),
                "LTest;",
                "list_adapter",
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
        elif isinstance(item, _UIScrollView):
            if len(item.items) != 1:
                raise RuntimeError(
                    f"ScrollView requires exactly one direct child; got {len(item.items)}."
                )
            item.id = self._register_view(item.id, "scroll_view")
            body.extend(
                [assign(item.id, new("Landroid/widget/ScrollView;", args=[var("ctx")]))]
            )
            body.extend(self._apply_view_layout(item, parent_id))
            body.append(add_view(var(parent_id), var(item.id)))
            body.extend(self._capture_view_static(item.id))
            body.extend(self._build_ui_items(item.id, item.items))
        elif isinstance(item, _UIHorizontalScrollView):
            if len(item.items) != 1:
                raise RuntimeError(
                    "HorizontalScrollView requires exactly one direct child; "
                    f"got {len(item.items)}."
                )
            item.id = self._register_view(item.id, "horizontal_scroll_view")
            body.extend(
                [
                    assign(
                        item.id,
                        new("Landroid/widget/HorizontalScrollView;", args=[var("ctx")]),
                    )
                ]
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
            self._screen_transitions[item.name] = self._normalize_screen_transition(
                getattr(item, "transition", None)
            )
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
        prev_local_types = self._local_var_types
        try:
            self._local_vars = set()
            self._local_var_types = {}
            out = self._compile_stmt_block(stmts)
            out.append(ret())
            return out
        finally:
            self._local_vars = prev_locals
            self._local_var_types = prev_local_types

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
        if isinstance(stmt, _StmtAnimate):
            return self._compile_animate_stmt(stmt)
        if isinstance(stmt, _StmtAnimationGroup):
            return self._compile_animation_group_stmt(stmt)
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
        if isinstance(stmt, _StmtOpenUrl):
            return self._compile_open_url_stmt(stmt)
        if isinstance(stmt, _StmtCheckConnectivity):
            return self._compile_check_connectivity_stmt(stmt)
        if isinstance(stmt, _StmtStoragePut):
            return self._compile_storage_put_stmt(stmt)
        if isinstance(stmt, _StmtStorageGet):
            return self._compile_storage_get_stmt(stmt)
        if isinstance(stmt, _StmtStorageRemove):
            return self._compile_storage_remove_stmt(stmt)
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

    def _normalize_anim_property(self, raw):
        key = str(raw).strip().lower().replace("-", "_")
        mapping = {
            "rotation": "rotate",
            "rotate": "rotate",
            "scale": "scale",
            "scale_x": "scale_x",
            "scalex": "scale_x",
            "scale_y": "scale_y",
            "scaley": "scale_y",
            "translate_x": "translate_x",
            "translation_x": "translate_x",
            "translate_y": "translate_y",
            "translation_y": "translate_y",
            "alpha": "alpha",
            "elevation": "elevation",
        }
        return mapping.get(key, key)

    def _normalize_anim_interpolator(self, raw):
        if raw is None:
            return None
        key = str(raw).strip().lower().replace("-", "_")
        mapping = {
            "linear": "linear",
            "accelerate": "accelerate",
            "ease_in": "accelerate",
            "decelerate": "decelerate",
            "ease_out": "decelerate",
            "accelerate_decelerate": "accelerate_decelerate",
            "ease_in_out": "accelerate_decelerate",
        }
        if key not in mapping:
            allowed = ", ".join(sorted(mapping.keys()))
            raise RuntimeError(
                f"Unsupported interpolator '{raw}'. Supported: [{allowed}]"
            )
        return mapping[key]

    def _coerce_anim_float(self, value, *, field_name):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RuntimeError(f"{field_name} must be numeric, got {value!r}")
        return float(value)

    def _expand_anim_properties(self, raw_properties):
        allowed = {
            "rotate",
            "scale",
            "scale_x",
            "scale_y",
            "translate_x",
            "translate_y",
            "alpha",
            "elevation",
        }
        normalized = {}
        for key, value in (raw_properties or {}).items():
            prop = self._normalize_anim_property(key)
            if prop not in allowed:
                supported = ", ".join(sorted(allowed))
                raise RuntimeError(
                    f"Unsupported animation property '{key}'. Supported: [{supported}]"
                )
            normalized[prop] = self._coerce_anim_float(value, field_name=f"animation '{prop}'")

        scale_value = normalized.get("scale")
        if scale_value is not None:
            normalized.setdefault("scale_x", scale_value)
            normalized.setdefault("scale_y", scale_value)
            normalized.pop("scale", None)
        return normalized

    def _long_const_expr(self, value, *, field_name, prefix):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RuntimeError(f"{field_name} must be numeric")
        int_value = int(value)
        int_var = self._next_tmp(f"{prefix}_i")
        long_var = self._next_tmp(f"{prefix}_j")
        return [
            assign(int_var, const(int_value)),
            assign(long_var, primitive_cast(var(int_var), "I", "J")),
        ], var(long_var)

    def _animation_target_ref(self, target_id, *, prefix):
        if target_id not in self.view_types:
            known = ", ".join(sorted(self.view_types.keys()))
            raise RuntimeError(
                f"Unknown animation target '{target_id}'. Known ids: [{known}]"
            )
        view_kind = self.view_types[target_id]
        view_desc = self._view_desc(view_kind)
        view_field = self.view_fields[target_id]
        view_var = self._next_tmp(prefix)
        return [assign(view_var, static_get(view_field, view_desc))], var(view_var)

    def _emit_interpolator_instance(self, interpolator, *, prefix):
        normalized = self._normalize_anim_interpolator(interpolator)
        if normalized is None:
            return [], None
        class_map = {
            "linear": "Landroid/view/animation/LinearInterpolator;",
            "accelerate": "Landroid/view/animation/AccelerateInterpolator;",
            "decelerate": "Landroid/view/animation/DecelerateInterpolator;",
            "accelerate_decelerate": "Landroid/view/animation/AccelerateDecelerateInterpolator;",
        }
        interp_var = self._next_tmp(prefix)
        return [assign(interp_var, new(class_map[normalized], args=[]))], var(interp_var)

    def _apply_animator_timing(self, *, animator_expr, owner_desc, duration, delay, interpolator, prefix):
        out = []
        animator_name = getattr(animator_expr, "name", None)
        if duration is not None:
            duration_setup, duration_expr = self._long_const_expr(
                duration,
                field_name="duration",
                prefix=f"{prefix}_duration",
            )
            out.extend(duration_setup)
            if animator_name:
                out.append(
                    assign(
                        animator_name,
                        call(
                            "setDuration",
                            args=[animator_expr, duration_expr],
                            return_type=None,
                            arg_types=["J"],
                            invoke_kind="virtual",
                            owner=owner_desc,
                        ),
                    )
                )
            else:
                out.append(
                    call_stmt(
                        "setDuration",
                        args=[animator_expr, duration_expr],
                        return_type=None,
                        arg_types=["J"],
                        invoke_kind="virtual",
                        owner=owner_desc,
                    )
                )
        if delay is not None:
            delay_setup, delay_expr = self._long_const_expr(
                delay,
                field_name="delay",
                prefix=f"{prefix}_delay",
            )
            out.extend(delay_setup)
            if owner_desc == "Landroid/view/ViewPropertyAnimator;" and animator_name:
                out.append(
                    assign(
                        animator_name,
                        call(
                            "setStartDelay",
                            args=[animator_expr, delay_expr],
                            return_type=None,
                            arg_types=["J"],
                            invoke_kind="virtual",
                            owner=owner_desc,
                        ),
                    )
                )
            else:
                out.append(
                    call_stmt(
                        "setStartDelay",
                        args=[animator_expr, delay_expr],
                        return_type=None,
                        arg_types=["J"],
                        invoke_kind="virtual",
                        owner=owner_desc,
                    )
                )
        interp_setup, interp_expr = self._emit_interpolator_instance(
            interpolator,
            prefix=f"{prefix}_interp",
        )
        out.extend(interp_setup)
        if interp_expr is not None:
            if owner_desc == "Landroid/view/ViewPropertyAnimator;" and animator_name:
                out.append(
                    assign(
                        animator_name,
                        call(
                            "setInterpolator",
                            args=[animator_expr, interp_expr],
                            return_type=None,
                            arg_types=["Landroid/animation/TimeInterpolator;"],
                            invoke_kind="virtual",
                            owner=owner_desc,
                        ),
                    )
                )
            else:
                out.append(
                    call_stmt(
                        "setInterpolator",
                        args=[animator_expr, interp_expr],
                        return_type=None,
                        arg_types=["Landroid/animation/TimeInterpolator;"],
                        invoke_kind="virtual",
                        owner=owner_desc,
                    )
                )
        return out

    def _build_property_object_animator(self, *, view_expr, property_name, value, duration, delay, interpolator, prefix):
        out = []
        values_var = self._next_tmp(f"{prefix}_vals")
        animator_var = self._next_tmp(f"{prefix}_anim")
        out.extend(
            [
                assign(values_var, new_array(const(1), "F")),
                array_set(
                    var(values_var),
                    const(0),
                    "F",
                    const(self._coerce_anim_float(value, field_name=property_name)),
                ),
                assign(
                    animator_var,
                    call(
                        "ofFloat",
                        args=[view_expr, const(property_name), var(values_var)],
                        return_type="Landroid/animation/ObjectAnimator;",
                        arg_types=["Ljava/lang/Object;", "Ljava/lang/String;", "[F"],
                        invoke_kind="static",
                        owner="Landroid/animation/ObjectAnimator;",
                    ),
                ),
            ]
        )
        out.extend(
            self._apply_animator_timing(
                animator_expr=var(animator_var),
                owner_desc="Landroid/animation/ValueAnimator;",
                duration=duration,
                delay=delay,
                interpolator=interpolator,
                prefix=f"{prefix}_timing",
            )
        )
        return out, var(animator_var)

    def _build_object_animator_for_stmt(self, stmt, *, prefix):
        properties = self._expand_anim_properties(getattr(stmt, "properties", {}))
        if not properties:
            raise RuntimeError("Animation requires at least one property")

        out, view_expr = self._animation_target_ref(stmt.target, prefix=f"{prefix}_view")
        prop_map = {
            "rotate": "rotation",
            "scale_x": "scaleX",
            "scale_y": "scaleY",
            "translate_x": "translationX",
            "translate_y": "translationY",
            "alpha": "alpha",
            "elevation": "elevation",
        }

        animator_vars = []
        for idx, prop in enumerate(
            ["rotate", "scale_x", "scale_y", "translate_x", "translate_y", "alpha", "elevation"]
        ):
            if prop not in properties:
                continue
            prop_out, anim_expr = self._build_property_object_animator(
                view_expr=view_expr,
                property_name=prop_map[prop],
                value=properties[prop],
                duration=stmt.duration,
                delay=stmt.delay,
                interpolator=stmt.interpolator,
                prefix=f"{prefix}_{prop}_{idx}",
            )
            out.extend(prop_out)
            animator_vars.append(anim_expr)

        if not animator_vars:
            raise RuntimeError("Animation expanded to no animatable properties")
        if len(animator_vars) == 1:
            return out, animator_vars[0]

        set_var = self._next_tmp(f"{prefix}_set")
        arr_var = self._next_tmp(f"{prefix}_arr")
        out.extend(
            [
                assign(set_var, new("Landroid/animation/AnimatorSet;", args=[])),
                assign(arr_var, new_array(const(len(animator_vars)), "Landroid/animation/Animator;")),
            ]
        )
        for i, anim_expr in enumerate(animator_vars):
            out.append(array_set(var(arr_var), const(i), "Landroid/animation/Animator;", anim_expr))
        out.append(
            call_stmt(
                "playTogether",
                args=[var(set_var), var(arr_var)],
                return_type=None,
                arg_types=["[Landroid/animation/Animator;"],
                invoke_kind="virtual",
                owner="Landroid/animation/AnimatorSet;",
            )
        )
        return out, var(set_var)

    def _build_group_animator(self, group_stmt, *, prefix):
        if group_stmt.mode not in {"sequence", "parallel"}:
            raise RuntimeError(f"Unsupported animation group mode '{group_stmt.mode}'")
        if not group_stmt.animations:
            raise RuntimeError("Animation group requires at least one child animation")

        out = []
        child_vars = []
        for idx, child in enumerate(group_stmt.animations):
            child_prefix = f"{prefix}_{idx}"
            if isinstance(child, _StmtAnimate):
                child_out, child_anim = self._build_object_animator_for_stmt(child, prefix=child_prefix)
            elif isinstance(child, _StmtAnimationGroup):
                child_out, child_anim = self._build_group_animator(child, prefix=child_prefix)
            else:
                raise RuntimeError(f"Unsupported animation child: {child}")
            out.extend(child_out)
            child_vars.append(child_anim)

        if len(child_vars) == 1:
            return out, child_vars[0]

        set_var = self._next_tmp(f"{prefix}_set")
        arr_var = self._next_tmp(f"{prefix}_arr")
        out.extend(
            [
                assign(set_var, new("Landroid/animation/AnimatorSet;", args=[])),
                assign(arr_var, new_array(const(len(child_vars)), "Landroid/animation/Animator;")),
            ]
        )
        for i, child_anim in enumerate(child_vars):
            out.append(array_set(var(arr_var), const(i), "Landroid/animation/Animator;", child_anim))
        method_name = "playSequentially" if group_stmt.mode == "sequence" else "playTogether"
        out.append(
            call_stmt(
                method_name,
                args=[var(set_var), var(arr_var)],
                return_type=None,
                arg_types=["[Landroid/animation/Animator;"],
                invoke_kind="virtual",
                owner="Landroid/animation/AnimatorSet;",
            )
        )
        return out, var(set_var)

    def _compile_animate_stmt(self, stmt):
        properties = self._expand_anim_properties(getattr(stmt, "properties", {}))
        if not properties:
            raise RuntimeError("animate requires at least one property")

        out, view_expr = self._animation_target_ref(stmt.target, prefix=f"{stmt.target}_anim_view")

        non_elevation = {}
        if "elevation" in properties:
            elevation_value = properties["elevation"]
        else:
            elevation_value = None
        for key in ("rotate", "scale_x", "scale_y", "translate_x", "translate_y", "alpha"):
            if key in properties:
                non_elevation[key] = properties[key]

        if non_elevation:
            animator_var = self._next_tmp(f"{stmt.target}_vpa")
            out.append(
                assign(
                    animator_var,
                    call(
                        "animate",
                        args=[view_expr],
                        return_type="Landroid/view/ViewPropertyAnimator;",
                        arg_types=[],
                        invoke_kind="virtual",
                        owner="Landroid/view/View;",
                    ),
                )
            )
            prop_calls = {
                "rotate": "rotation",
                "scale_x": "scaleX",
                "scale_y": "scaleY",
                "translate_x": "translationX",
                "translate_y": "translationY",
                "alpha": "alpha",
            }
            for prop in ("rotate", "scale_x", "scale_y", "translate_x", "translate_y", "alpha"):
                if prop not in non_elevation:
                    continue
                out.append(
                    assign(
                        animator_var,
                        call(
                            prop_calls[prop],
                            args=[var(animator_var), const(non_elevation[prop])],
                            return_type=None,
                            arg_types=["F"],
                            invoke_kind="virtual",
                            owner="Landroid/view/ViewPropertyAnimator;",
                        ),
                    )
                )
            out.extend(
                self._apply_animator_timing(
                    animator_expr=var(animator_var),
                    owner_desc="Landroid/view/ViewPropertyAnimator;",
                    duration=stmt.duration,
                    delay=stmt.delay,
                    interpolator=stmt.interpolator,
                    prefix=f"{stmt.target}_vpa_timing",
                )
            )
            out.append(
                call_stmt(
                    "start",
                    args=[var(animator_var)],
                    return_type=None,
                    arg_types=[],
                    invoke_kind="virtual",
                    owner="Landroid/view/ViewPropertyAnimator;",
                )
            )

        if elevation_value is not None:
            elev_out, elev_anim = self._build_property_object_animator(
                view_expr=view_expr,
                property_name="elevation",
                value=elevation_value,
                duration=stmt.duration,
                delay=stmt.delay,
                interpolator=stmt.interpolator,
                prefix=f"{stmt.target}_elev",
            )
            out.extend(elev_out)
            out.append(
                call_stmt(
                    "start",
                    args=[elev_anim],
                    return_type=None,
                    arg_types=[],
                    invoke_kind="virtual",
                    owner="Landroid/animation/Animator;",
                )
            )
        return out

    def _compile_animation_group_stmt(self, stmt):
        out, animator_expr = self._build_group_animator(stmt, prefix="anim_group")
        out.append(
            call_stmt(
                "start",
                args=[animator_expr],
                return_type=None,
                arg_types=[],
                invoke_kind="virtual",
                owner="Landroid/animation/Animator;",
            )
        )
        return out

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

    def _theme_style_for_item(self, item):
        theme = self.theme_spec
        if isinstance(item, _UIAppBar):
            return theme.text.merged(theme.appbar)
        if isinstance(item, _UITextField):
            return theme.text.merged(theme.input)
        if isinstance(item, (_UICheckbox, _UIRadio, _UISwitch)):
            return theme.text.merged(theme.selector)
        if isinstance(item, (_UISlider, _UIDropdownButton, _UIPopupMenuButton, _UIRadioGroup)):
            return theme.selector
        if isinstance(item, _UIProgressBar):
            return theme.progress
        if isinstance(item, _UIIcon):
            return theme.text.merged(theme.icon)
        if isinstance(item, _UIRow):
            # Backward-compatible override path for existing row/column channels.
            return theme.container.merged(theme.row)
        if isinstance(item, _UIColumn) and not isinstance(item, (_UIContainer, _UICard)):
            return theme.container.merged(theme.column)
        if isinstance(item, (_UIContainer, _UICard, _UIRelative, _UIConstraint, _UIScreen)):
            return theme.container
        if isinstance(item, _UIText):
            return theme.text
        if isinstance(item, _UIButton) and not isinstance(
            item, (_UISlider, _UIDropdownButton, _UIPopupMenuButton)
        ):
            return theme.button
        return Style()

    def _widget_default_style_for_item(self, item):
        if isinstance(item, _UIRow):
            return Style(layout=("match_parent", "wrap"))
        if isinstance(item, _UICard):
            return Style(
                background="#FFFFFFFF",
                radius=Dp(12),
                padding=Dp(12),
            )
        if isinstance(item, _UIDivider):
            return Style(
                layout=("match_parent", getattr(item, "thickness", Dp(1))),
                background=getattr(item, "color", "#FFD1D5DB"),
            )
        return Style()

    def _emit_style_precedence_lints(self, item, theme_style, item_style):
        if not isinstance(item_style, Style):
            return
        keys = tuple(item_style.__dict__.keys())
        for attr_name in keys:
            inline_set = getattr(item, attr_name, None) is not None
            style_set = getattr(item_style, attr_name, None) is not None
            theme_set = getattr(theme_style, attr_name, None) is not None
            if not style_set:
                continue
            # Emit only when there is a real overlap among user-controlled layers.
            if inline_set or theme_set:
                self._warn_once(
                    f"precedence:{item.id}:{attr_name}",
                    f"'{item.id}.{attr_name}' is defined in multiple layers; "
                    "precedence is inline attrs > style= > Theme channel > widget defaults.",
                )

    def _apply_view_layout(self, item, parent_id):
        out = []

        item_style = item.style if getattr(item, "style", None) else None
        theme_style = self._theme_style_for_item(item)
        widget_default_style = self._widget_default_style_for_item(item)
        self._validate_style_fields_for_widget(item, theme_style, source="Theme channel")
        self._validate_style_fields_for_widget(item, item_style, source="style=")
        # Deterministic precedence: inline attrs > style= > Theme channel > widget defaults.
        style = widget_default_style.merged(theme_style).merged(item_style)
        self._emit_style_precedence_lints(item, theme_style, item_style)

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
        border_width_value = getattr(item, "border_width", None) if getattr(item, "border_width", None) is not None else getattr(style, "border_width", None)
        border_color_value = getattr(item, "border_color", None) if getattr(item, "border_color", None) is not None else getattr(style, "border_color", None)
        border_radius_value = getattr(item, "border_radius", None) if getattr(item, "border_radius", None) is not None else getattr(style, "border_radius", None)
        ripple_color_value = getattr(item, "ripple_color", None) if getattr(item, "ripple_color", None) is not None else getattr(style, "ripple_color", None)
        blur_radius_value = getattr(item, "blur_radius", None) if getattr(item, "blur_radius", None) is not None else getattr(style, "blur_radius", None)
        rotation_value = getattr(item, "rotation", None) if getattr(item, "rotation", None) is not None else getattr(style, "rotation", None)
        scale_x_value = getattr(item, "scale_x", None) if getattr(item, "scale_x", None) is not None else getattr(style, "scale_x", None)
        scale_y_value = getattr(item, "scale_y", None) if getattr(item, "scale_y", None) is not None else getattr(style, "scale_y", None)
        translation_x_value = (
            getattr(item, "translation_x", None)
            if getattr(item, "translation_x", None) is not None
            else getattr(style, "translation_x", None)
        )
        translation_y_value = (
            getattr(item, "translation_y", None)
            if getattr(item, "translation_y", None) is not None
            else getattr(style, "translation_y", None)
        )
        clip_to_outline_value = (
            getattr(item, "clip_to_outline", None)
            if getattr(item, "clip_to_outline", None) is not None
            else getattr(style, "clip_to_outline", None)
        )
        clip_children_value = (
            getattr(item, "clip_children", None)
            if getattr(item, "clip_children", None) is not None
            else getattr(style, "clip_children", None)
        )
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
        opacity_value = getattr(item, "opacity", None) if getattr(item, "opacity", None) is not None else getattr(style, "opacity", None)
        elevation_value = getattr(item, "elevation", None) if getattr(item, "elevation", None) is not None else getattr(style, "elevation", None)
        pressed_elevation_value = (
            getattr(item, "pressed_elevation", None)
            if getattr(item, "pressed_elevation", None) is not None
            else getattr(style, "pressed_elevation", None)
        )
        text_shadow_color_value = (
            getattr(item, "text_shadow_color", None)
            if getattr(item, "text_shadow_color", None) is not None
            else getattr(style, "text_shadow_color", None)
        )
        text_shadow_radius_value = (
            getattr(item, "text_shadow_radius", None)
            if getattr(item, "text_shadow_radius", None) is not None
            else getattr(style, "text_shadow_radius", None)
        )
        text_shadow_dx_value = (
            getattr(item, "text_shadow_dx", None)
            if getattr(item, "text_shadow_dx", None) is not None
            else getattr(style, "text_shadow_dx", None)
        )
        text_shadow_dy_value = (
            getattr(item, "text_shadow_dy", None)
            if getattr(item, "text_shadow_dy", None) is not None
            else getattr(style, "text_shadow_dy", None)
        )
        content_description_value = getattr(item, "content_description", None)
        if content_description_value is None:
            content_description_value = getattr(item, "accessibility_label", None)
        important_for_accessibility_value = getattr(item, "important_for_accessibility", None)

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
        txt_color = None if isinstance(text_color_value, ColorState) else _parse_color(text_color_value, palette)

        out.extend(
            self._emit_background_visual_effects(
                view_id=item.id,
                background_value=background_value,
                radius_value=radius_value,
                border_width_value=border_width_value,
                border_color_value=border_color_value,
                border_radius_value=border_radius_value,
                ripple_color_value=ripple_color_value,
            )
        )

        if clip_to_outline_value is not None:
            clip_to_outline = self._coerce_bool_flag(
                clip_to_outline_value,
                field_name="clip_to_outline",
            )
            out.append(
                call_stmt(
                    "setClipToOutline",
                    args=[var(item.id), const(1 if clip_to_outline else 0)],
                    return_type=None,
                    arg_types=["Z"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                )
            )

        if clip_children_value is not None:
            clip_children = self._coerce_bool_flag(
                clip_children_value,
                field_name="clip_children",
            )
            if self.view_types.get(item.id) not in {
                "row",
                "column",
                "relative",
                "constraint",
                "container",
                "card",
                "radio_group",
                "screen",
            }:
                raise RuntimeError(
                    f"clip_children is only supported on container widgets; '{item.id}' is kind={self.view_types.get(item.id)}."
                )
            out.append(
                call_stmt(
                    "setClipChildren",
                    args=[var(item.id), const(1 if clip_children else 0)],
                    return_type=None,
                    arg_types=["Z"],
                    invoke_kind="virtual",
                    owner="Landroid/view/ViewGroup;",
                )
            )

        if blur_radius_value is not None:
            out.extend(
                self._emit_blur_effect(
                    view_id=item.id,
                    blur_radius_value=blur_radius_value,
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

        if opacity_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="opacity",
                    raw_value=self._normalize_opacity(opacity_value),
                )
            )

        if rotation_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="rotation",
                    raw_value=rotation_value,
                )
            )

        if scale_x_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="scale_x",
                    raw_value=scale_x_value,
                )
            )

        if scale_y_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="scale_y",
                    raw_value=scale_y_value,
                )
            )

        if translation_x_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="translation_x",
                    raw_value=translation_x_value,
                )
            )

        if translation_y_value is not None:
            out.extend(
                self._emit_attr_call(
                    view_id=item.id,
                    attr_name="translation_y",
                    raw_value=translation_y_value,
                )
            )

        if elevation_value is not None:
            out.extend(
                self._emit_elevation_setter(
                    view_id=item.id,
                    value=elevation_value,
                    field_name="elevation",
                    prefix=f"{item.id}_elevation",
                )
            )
        if pressed_elevation_value is not None:
            base_elevation_value = elevation_value if elevation_value is not None else Dp(0)
            out.extend(
                self._emit_pressed_elevation_animator(
                    view_id=item.id,
                    base_value=base_elevation_value,
                    pressed_value=pressed_elevation_value,
                )
            )

        if (
            text_shadow_color_value is not None
            or text_shadow_radius_value is not None
            or text_shadow_dx_value is not None
            or text_shadow_dy_value is not None
        ):
            out.extend(
                self._emit_text_shadow_setter(
                    view_id=item.id,
                    color_value=text_shadow_color_value,
                    radius_value=text_shadow_radius_value,
                    dx_value=text_shadow_dx_value,
                    dy_value=text_shadow_dy_value,
                )
            )

        if content_description_value is not None:
            if isinstance(content_description_value, bool):
                raise RuntimeError(
                    f"content_description on '{item.id}' must be a string."
                )
            out.extend(
                self._set_text_from_resource(
                    item.id,
                    str(content_description_value),
                    "Landroid/view/View;",
                    f"{item.id}_content_desc",
                    ctx_expr=var("ctx"),
                    method_name="setContentDescription",
                )
            )

        if important_for_accessibility_value is not None:
            important_for_accessibility_int = self._normalize_important_for_accessibility(
                important_for_accessibility_value
            )
            out.append(
                call_stmt(
                    "setImportantForAccessibility",
                    args=[var(item.id), const(important_for_accessibility_int)],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
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

    def _normalize_important_for_accessibility(self, value):
        mapping = {
            "auto": 0,
            "yes": 1,
            "true": 1,
            "no": 2,
            "false": 2,
            "no_hide_descendants": 4,
            "no-hide-descendants": 4,
            "nohidedescendants": 4,
        }
        if isinstance(value, bool):
            return 1 if value else 2
        if isinstance(value, int) and not isinstance(value, bool):
            if value in (0, 1, 2, 4):
                return value
        elif isinstance(value, str):
            key = value.strip().lower()
            if key in mapping:
                return mapping[key]
        raise RuntimeError(
            "Unsupported important_for_accessibility value "
            f"{value!r}. Use auto/yes/no/no_hide_descendants, bool, or 0/1/2/4."
        )

    def _normalize_opacity(self, value):
        if isinstance(value, bool):
            raise RuntimeError("opacity must be a number in range [0.0, 1.0], not bool.")
        if not isinstance(value, (int, float)):
            raise RuntimeError("opacity must be a number in range [0.0, 1.0].")
        f = float(value)
        if f < 0.0 or f > 1.0:
            raise RuntimeError(f"opacity {value!r} is out of range. Expected [0.0, 1.0].")
        return f

    def _normalize_gradient_direction(self, direction):
        if direction is None:
            key = "left_to_right"
        elif isinstance(direction, str):
            key = direction.strip().lower()
        else:
            raise RuntimeError("Gradient direction must be a string.")
        mapping = {
            "left_to_right": "LEFT_RIGHT",
            "right_to_left": "RIGHT_LEFT",
            "top_to_bottom": "TOP_BOTTOM",
            "bottom_to_top": "BOTTOM_TOP",
            "tl_br": "TL_BR",
            "tr_bl": "TR_BL",
            "bl_tr": "BL_TR",
            "br_tl": "BR_TL",
            "top_left_bottom_right": "TL_BR",
            "top_right_bottom_left": "TR_BL",
            "bottom_left_top_right": "BL_TR",
            "bottom_right_top_left": "BR_TL",
        }
        if key not in mapping:
            known = ", ".join(sorted(mapping.keys()))
            raise RuntimeError(f"Unsupported Gradient direction '{direction}'. Known: [{known}]")
        return mapping[key]

    def _normalize_corner_radii(self, value):
        if value is None:
            return None, None
        if isinstance(value, (list, tuple)):
            if len(value) != 4:
                raise RuntimeError("border_radius tuple/list must have 4 values: (top_left, top_right, bottom_right, bottom_left).")
            out = []
            for idx, entry in enumerate(value):
                out.append(
                    self._normalize_dimension_value(
                        entry,
                        field_name=f"border_radius[{idx}]",
                    )
                )
            return out, False
        return [
            self._normalize_dimension_value(value, field_name="border_radius"),
            self._normalize_dimension_value(value, field_name="border_radius"),
            self._normalize_dimension_value(value, field_name="border_radius"),
            self._normalize_dimension_value(value, field_name="border_radius"),
        ], True

    def _emit_background_visual_effects(
        self,
        *,
        view_id,
        background_value,
        radius_value,
        border_width_value,
        border_color_value,
        border_radius_value,
        ripple_color_value,
    ):
        out = []
        palette = self.theme_spec.palette

        gradient_value = background_value if isinstance(background_value, Gradient) else None
        if gradient_value is None:
            if isinstance(background_value, ColorState):
                self._warn_once(
                    f"background_color_state_default:{view_id}",
                    f"'{view_id}.background' uses ColorState; only the default color is applied to background fill.",
                )
                try:
                    bg_color_value = _parse_color(background_value.default, palette)
                except RuntimeError as exc:
                    raise RuntimeError(
                        f"Invalid color on '{view_id}.background': {exc}"
                    ) from None
            else:
                try:
                    bg_color_value = _parse_color(background_value, palette)
                except RuntimeError as exc:
                    raise RuntimeError(
                        f"Invalid color on '{view_id}.background': {exc}"
                    ) from None
        else:
            bg_color_value = None

        if isinstance(border_color_value, ColorState):
            border_color_value = border_color_value.default
        try:
            border_color = _parse_color(border_color_value, palette)
        except RuntimeError as exc:
            raise RuntimeError(
                f"Invalid color on '{view_id}.border_color': {exc}"
            ) from None

        effective_radius = border_radius_value if border_radius_value is not None else radius_value
        corner_values, uniform_corners = self._normalize_corner_radii(effective_radius)

        if border_width_value is None and border_color is not None:
            border_width_value = Dp(1)
            self._warn_once(
                f"border_width_default:{view_id}",
                f"'{view_id}.border_width' is not set; defaulting to dp(1) because border_color is provided.",
            )
        if border_width_value is not None and border_color is None:
            raise RuntimeError("border_color is required when border_width is set.")

        use_shape = (
            gradient_value is not None
            or corner_values is not None
            or border_width_value is not None
            or ripple_color_value is not None
        )

        if not use_shape:
            if bg_color_value is not None:
                out.extend(
                    self._emit_attr_call(
                        view_id=view_id,
                        attr_name="background_color",
                        raw_value=bg_color_value,
                    )
                )
            return out

        shape_var = self._next_tmp(f"{view_id}_shape")
        out.append(
            assign(
                shape_var,
                new("Landroid/graphics/drawable/GradientDrawable;", args=[]),
            )
        )

        if gradient_value is not None:
            try:
                start_color = _parse_color(gradient_value.start, palette)
            except RuntimeError as exc:
                raise RuntimeError(
                    f"Invalid gradient config on '{view_id}.background.start': {exc}"
                ) from None
            try:
                end_color = _parse_color(gradient_value.end, palette)
            except RuntimeError as exc:
                raise RuntimeError(
                    f"Invalid gradient config on '{view_id}.background.end': {exc}"
                ) from None
            if start_color is None:
                raise RuntimeError(
                    f"Invalid gradient config on '{view_id}.background.start': "
                    f"expected a parseable color, got {gradient_value.start!r}."
                )
            if end_color is None:
                raise RuntimeError(
                    f"Invalid gradient config on '{view_id}.background.end': "
                    f"expected a parseable color, got {gradient_value.end!r}."
                )
            try:
                orientation_field = self._normalize_gradient_direction(gradient_value.direction)
            except RuntimeError as exc:
                raise RuntimeError(
                    f"Invalid gradient config on '{view_id}.background.direction': {exc}"
                ) from None
            orientation_var = self._next_tmp(f"{view_id}_grad_orientation")
            colors_var = self._next_tmp(f"{view_id}_grad_colors")
            out.extend(
                [
                    assign(
                        orientation_var,
                        static_get(
                            orientation_field,
                            "Landroid/graphics/drawable/GradientDrawable$Orientation;",
                            owner="Landroid/graphics/drawable/GradientDrawable$Orientation;",
                        ),
                    ),
                    call_stmt(
                        "setOrientation",
                        args=[var(shape_var), var(orientation_var)],
                        return_type=None,
                        arg_types=["Landroid/graphics/drawable/GradientDrawable$Orientation;"],
                        invoke_kind="virtual",
                        owner="Landroid/graphics/drawable/GradientDrawable;",
                    ),
                    assign(colors_var, new_array(const(2), "I")),
                    array_set(var(colors_var), const(0), "I", const(start_color)),
                    array_set(var(colors_var), const(1), "I", const(end_color)),
                    call_stmt(
                        "setColors",
                        args=[var(shape_var), var(colors_var)],
                        return_type=None,
                        arg_types=["[I"],
                        invoke_kind="virtual",
                        owner="Landroid/graphics/drawable/GradientDrawable;",
                    ),
                ]
            )
        else:
            fill_color = bg_color_value if bg_color_value is not None else 0x00000000
            fill_key = self._add_color_resource(f"{view_id}_fill", fill_color)
            fill_setup, fill_expr = self._load_color_expr(
                fill_key,
                ctx_expr=var("ctx"),
                prefix=f"{view_id}_fill",
            )
            out.extend(fill_setup)
            out.append(
                call_stmt(
                    "setColor",
                    args=[var(shape_var), fill_expr],
                    return_type=None,
                    arg_types=["I"],
                    invoke_kind="virtual",
                    owner="Landroid/graphics/drawable/GradientDrawable;",
                )
            )

        if corner_values is not None:
            if uniform_corners:
                radius_setup, radius_expr = self._dimension_float_expr(
                    corner_values[0],
                    field_name="border_radius",
                    prefix=f"{view_id}_corner_radius",
                )
                out.extend(radius_setup)
                out.append(
                    call_stmt(
                        "setCornerRadius",
                        args=[var(shape_var), radius_expr],
                        return_type=None,
                        arg_types=["F"],
                        invoke_kind="virtual",
                        owner="Landroid/graphics/drawable/GradientDrawable;",
                    )
                )
            else:
                radii_var = self._next_tmp(f"{view_id}_corner_radii")
                out.append(assign(radii_var, new_array(const(8), "F")))
                for idx, entry in enumerate(corner_values):
                    dim_setup, dim_expr = self._dimension_float_expr(
                        entry,
                        field_name=f"border_radius[{idx}]",
                        prefix=f"{view_id}_corner_r{idx}",
                    )
                    out.extend(dim_setup)
                    out.append(array_set(var(radii_var), const(idx * 2), "F", dim_expr))
                    out.append(array_set(var(radii_var), const(idx * 2 + 1), "F", dim_expr))
                out.append(
                    call_stmt(
                        "setCornerRadii",
                        args=[var(shape_var), var(radii_var)],
                        return_type=None,
                        arg_types=["[F"],
                        invoke_kind="virtual",
                        owner="Landroid/graphics/drawable/GradientDrawable;",
                    )
                )

        if border_width_value is not None:
            border_w_setup, border_w_expr = self._dimension_px_expr(
                border_width_value,
                field_name="border_width",
                prefix=f"{view_id}_border_width",
            )
            border_color_key = self._add_color_resource(f"{view_id}_border", border_color)
            border_c_setup, border_c_expr = self._load_color_expr(
                border_color_key,
                ctx_expr=var("ctx"),
                prefix=f"{view_id}_border",
            )
            out.extend(border_w_setup)
            out.extend(border_c_setup)
            out.append(
                call_stmt(
                    "setStroke",
                    args=[var(shape_var), border_w_expr, border_c_expr],
                    return_type=None,
                    arg_types=["I", "I"],
                    invoke_kind="virtual",
                    owner="Landroid/graphics/drawable/GradientDrawable;",
                )
            )

        drawable_expr = var(shape_var)
        if ripple_color_value is not None:
            ripple_stmts, ripple_expr = self._build_color_state_list_expr(
                view_id,
                "ripple_color",
                ripple_color_value,
                self.theme_spec.palette,
            )
            out.extend(ripple_stmts)
            if ripple_expr is not None:
                ripple_var = self._next_tmp(f"{view_id}_ripple")
                out.append(
                    assign(
                        ripple_var,
                        new(
                            "Landroid/graphics/drawable/RippleDrawable;",
                            args=[ripple_expr, drawable_expr, const(0)],
                            arg_types=[
                                "Landroid/content/res/ColorStateList;",
                                "Landroid/graphics/drawable/Drawable;",
                                "Landroid/graphics/drawable/Drawable;",
                            ],
                        ),
                    )
                )
                drawable_expr = var(ripple_var)

        out.append(
            call_stmt(
                "setBackground",
                args=[var(view_id), drawable_expr],
                return_type=None,
                arg_types=["Landroid/graphics/drawable/Drawable;"],
                invoke_kind="virtual",
                owner="Landroid/view/View;",
            )
        )
        return out

    def _emit_blur_effect(self, *, view_id, blur_radius_value):
        if self.min_sdk < 31:
            self._warn_once(
                "blur_radius_min_sdk",
                f"blur_radius is ignored because min_sdk={self.min_sdk} < 31 (RenderEffect API 31+).",
            )
            return []

        normalized_radius = self._normalize_dimension_value(
            blur_radius_value,
            field_name="blur_radius",
        )
        if normalized_radius.value < 0:
            raise RuntimeError("blur_radius must be >= 0.")

        out = []
        radius_setup, radius_expr = self._dimension_float_expr(
            normalized_radius,
            field_name="blur_radius",
            prefix=f"{view_id}_blur_radius",
        )
        tile_mode_var = self._next_tmp(f"{view_id}_blur_tile_mode")
        effect_var = self._next_tmp(f"{view_id}_blur_effect")
        out.extend(radius_setup)
        out.extend(
            [
                assign(
                    tile_mode_var,
                    static_get(
                        "CLAMP",
                        "Landroid/graphics/Shader$TileMode;",
                        owner="Landroid/graphics/Shader$TileMode;",
                    ),
                ),
                assign(
                    effect_var,
                    call(
                        "createBlurEffect",
                        args=[radius_expr, radius_expr, var(tile_mode_var)],
                        return_type="Landroid/graphics/RenderEffect;",
                        arg_types=["F", "F", "Landroid/graphics/Shader$TileMode;"],
                        invoke_kind="static",
                        owner="Landroid/graphics/RenderEffect;",
                    ),
                ),
                call_stmt(
                    "setRenderEffect",
                    args=[var(view_id), var(effect_var)],
                    return_type=None,
                    arg_types=["Landroid/graphics/RenderEffect;"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                ),
            ]
        )
        return out

    def _normalize_dimension_value(self, value, *, field_name):
        if isinstance(value, bool):
            raise RuntimeError(f"{field_name} must be a number or dp()/px() unit, not bool.")
        if isinstance(value, (int, float)):
            return Dp(value)
        if isinstance(value, (Dp, Px)):
            return value
        raise RuntimeError(f"{field_name} must be a number or dp()/px() unit.")

    def _dimension_float_expr(self, value, *, field_name, prefix):
        normalized = self._normalize_dimension_value(value, field_name=field_name)
        key = self._add_dimen_resource(prefix, normalized)
        return self._load_dimen_float_expr(key, ctx_expr=var("ctx"), prefix=prefix)

    def _dimension_px_expr(self, value, *, field_name, prefix):
        normalized = self._normalize_dimension_value(value, field_name=field_name)
        key = self._add_dimen_resource(prefix, normalized)
        return self._load_dimen_px_expr(key, ctx_expr=var("ctx"), prefix=prefix)

    def _emit_elevation_setter(self, *, view_id, value, field_name, prefix):
        out = []
        setup, value_expr = self._dimension_float_expr(
            value,
            field_name=field_name,
            prefix=prefix,
        )
        out.extend(setup)
        out.append(
            call_stmt(
                "setElevation",
                args=[var(view_id), value_expr],
                return_type=None,
                arg_types=["F"],
                invoke_kind="virtual",
                owner="Landroid/view/View;",
            )
        )
        return out

    def _emit_pressed_elevation_animator(self, *, view_id, base_value, pressed_value):
        out = []
        base_setup, base_expr = self._dimension_float_expr(
            base_value,
            field_name="elevation",
            prefix=f"{view_id}_elevation_default",
        )
        pressed_setup, pressed_expr = self._dimension_float_expr(
            pressed_value,
            field_name="pressed_elevation",
            prefix=f"{view_id}_elevation_pressed",
        )
        out.extend(base_setup)
        out.extend(pressed_setup)

        pressed_values = self._next_tmp(f"{view_id}_pressed_elev_vals")
        default_values = self._next_tmp(f"{view_id}_default_elev_vals")
        pressed_anim = self._next_tmp(f"{view_id}_pressed_elev_anim")
        default_anim = self._next_tmp(f"{view_id}_default_elev_anim")
        pressed_state = self._next_tmp(f"{view_id}_pressed_state")
        default_state = self._next_tmp(f"{view_id}_default_state")
        state_animator = self._next_tmp(f"{view_id}_state_animator")

        out.extend(
            [
                assign(pressed_values, new_array(const(1), "F")),
                array_set(var(pressed_values), const(0), "F", pressed_expr),
                assign(default_values, new_array(const(1), "F")),
                array_set(var(default_values), const(0), "F", base_expr),
                assign(
                    pressed_anim,
                    call(
                        "ofFloat",
                        args=[var(view_id), const("elevation"), var(pressed_values)],
                        return_type="Landroid/animation/ObjectAnimator;",
                        arg_types=["Ljava/lang/Object;", "Ljava/lang/String;", "[F"],
                        invoke_kind="static",
                        owner="Landroid/animation/ObjectAnimator;",
                    ),
                ),
                assign(
                    default_anim,
                    call(
                        "ofFloat",
                        args=[var(view_id), const("elevation"), var(default_values)],
                        return_type="Landroid/animation/ObjectAnimator;",
                        arg_types=["Ljava/lang/Object;", "Ljava/lang/String;", "[F"],
                        invoke_kind="static",
                        owner="Landroid/animation/ObjectAnimator;",
                    ),
                ),
                assign(pressed_state, new_array(const(1), "I")),
                array_set(var(pressed_state), const(0), "I", const(0x10100A7)),
                assign(default_state, new_array(const(0), "I")),
                assign(state_animator, new("Landroid/animation/StateListAnimator;", args=[])),
                call_stmt(
                    "addState",
                    args=[var(state_animator), var(pressed_state), var(pressed_anim)],
                    return_type=None,
                    arg_types=["[I", "Landroid/animation/Animator;"],
                    invoke_kind="virtual",
                    owner="Landroid/animation/StateListAnimator;",
                ),
                call_stmt(
                    "addState",
                    args=[var(state_animator), var(default_state), var(default_anim)],
                    return_type=None,
                    arg_types=["[I", "Landroid/animation/Animator;"],
                    invoke_kind="virtual",
                    owner="Landroid/animation/StateListAnimator;",
                ),
                call_stmt(
                    "setStateListAnimator",
                    args=[var(view_id), var(state_animator)],
                    return_type=None,
                    arg_types=["Landroid/animation/StateListAnimator;"],
                    invoke_kind="virtual",
                    owner="Landroid/view/View;",
                ),
            ]
        )
        return out

    def _emit_text_shadow_setter(self, *, view_id, color_value, radius_value, dx_value, dy_value):
        kind = self.view_types.get(view_id)
        text_kinds = {
            "text",
            "button",
            "raised_button",
            "flat_button",
            "text_field",
            "checkbox",
            "radio",
            "switch",
            "popup_button",
            "icon",
        }
        if kind not in text_kinds:
            raise RuntimeError(
                f"text shadow is only supported on text-like widgets; '{view_id}' is kind={kind}."
            )

        out = []
        palette = self.theme_spec.palette
        if isinstance(color_value, ColorState):
            parsed_color = _parse_color(color_value.default, palette)
        else:
            parsed_color = _parse_color(color_value, palette)
        if parsed_color is None:
            parsed_color = _parse_color("#FF000000", palette)
        color_key = self._add_color_resource(f"{view_id}_text_shadow", parsed_color)
        color_setup, color_expr = self._load_color_expr(
            color_key,
            ctx_expr=var("ctx"),
            prefix=f"{view_id}_text_shadow",
        )
        out.extend(color_setup)

        radius_raw = Dp(0) if radius_value is None else radius_value
        dx_raw = Dp(0) if dx_value is None else dx_value
        dy_raw = Dp(0) if dy_value is None else dy_value
        radius_setup, radius_expr = self._dimension_float_expr(
            radius_raw,
            field_name="text_shadow_radius",
            prefix=f"{view_id}_text_shadow_radius",
        )
        dx_setup, dx_expr = self._dimension_float_expr(
            dx_raw,
            field_name="text_shadow_dx",
            prefix=f"{view_id}_text_shadow_dx",
        )
        dy_setup, dy_expr = self._dimension_float_expr(
            dy_raw,
            field_name="text_shadow_dy",
            prefix=f"{view_id}_text_shadow_dy",
        )
        out.extend(radius_setup)
        out.extend(dx_setup)
        out.extend(dy_setup)

        out.append(
            call_stmt(
                "setShadowLayer",
                args=[var(view_id), radius_expr, dx_expr, dy_expr, color_expr],
                return_type=None,
                arg_types=["F", "F", "F", "I"],
                invoke_kind="virtual",
                owner="Landroid/widget/TextView;",
            )
        )
        return out

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

        value_type = "I"
        if isinstance(stmt.value, (_ExprConst, _ExprSymbol, _ExprBinary)):
            prefix, result = self._compile_int_expr(stmt.value)
        elif isinstance(stmt.value, _ExprStorageGet):
            prefix, result = self._compile_storage_get_call(
                key=stmt.value.key,
                default_value=stmt.value.default_value,
                tmp_prefix="storage_get_result",
            )
            value_type = "Ljava/lang/String;"
        else:
            raise RuntimeError(
                f"Unsupported assignment expression for '{name}': {type(stmt.value).__name__}. "
                "Expected int const/symbol/arithmetic expression or storage_get(...)."
            )

        if name in self.state_spec.values:
            if value_type != "I":
                raise RuntimeError(
                    f"State variable '{name}' only supports integer assignment; "
                    f"got {value_type}."
                )
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
        self._local_var_types[name] = value_type
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
                local_type = self._local_var_types.get(expr.name, "I")
                if local_type != "I":
                    raise RuntimeError(
                        f"Arithmetic expression requires int symbol '{expr.name}', got {local_type}."
                    )
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
        if isinstance(stmt.value, _ExprSymbol):
            name = stmt.value.name
            if name in self._local_var_types:
                local_type = self._local_var_types[name]
                if local_type == "Ljava/lang/String;":
                    return [
                        assign("v", static_get(view_field, view_desc)),
                        call_stmt(
                            "setText",
                            args=[var("v"), var(name)],
                            return_type=None,
                            arg_types=["Ljava/lang/CharSequence;"],
                            invoke_kind="virtual",
                            owner=view_desc,
                        ),
                    ]
                if local_type == "I":
                    return [
                        assign(
                            "s",
                            call(
                                "valueOf",
                                args=[var(name)],
                                return_type="Ljava/lang/String;",
                                arg_types=["I"],
                                invoke_kind="static",
                                owner="Ljava/lang/String;",
                            ),
                        ),
                        assign("v", static_get(view_field, view_desc)),
                        call_stmt(
                            "setText",
                            args=[var("v"), var("s")],
                            return_type=None,
                            arg_types=["Ljava/lang/CharSequence;"],
                            invoke_kind="virtual",
                            owner=view_desc,
                        ),
                    ]
            raise RuntimeError(
                f"{view_id}.text references unknown symbol '{name}'. "
                "Only local assigned symbols are supported here."
            )
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

    def _compile_open_url_stmt(self, stmt):
        binding = self.capability_runtime_bindings.get("URLLauncher")
        if binding is None:
            raise RuntimeError(
                "open_url requires URLLauncher capability. "
                "Declare app_config(uses=[Caps.URLLauncher]) first."
            )
        if binding.mode != "helper_call":
            raise RuntimeError(
                "URLLauncher capability must be helper_call mode for open_url."
            )
        if not (binding.helper_class_desc and binding.helper_method):
            raise RuntimeError("URLLauncher helper binding is missing helper metadata.")
        result_tmp = self._next_tmp("url_launch_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx"), const(str(stmt.url))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_check_connectivity_stmt(self, stmt):
        binding = self.capability_runtime_bindings.get("Connectivity")
        if binding is None:
            raise RuntimeError(
                "check_connectivity requires Connectivity capability. "
                "Declare app_config(uses=[Caps.Connectivity]) first."
            )
        if binding.mode != "helper_call":
            raise RuntimeError(
                "Connectivity capability must be helper_call mode for check_connectivity."
            )
        if not (binding.helper_class_desc and binding.helper_method):
            raise RuntimeError("Connectivity helper binding is missing helper metadata.")
        result_tmp = self._next_tmp("connectivity_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx")],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_storage_put_stmt(self, stmt):
        binding = self.capability_runtime_bindings.get("Storage")
        if binding is None:
            raise RuntimeError(
                "storage_put requires Storage capability. "
                "Declare app_config(uses=[Caps.Storage]) first."
            )
        if binding.mode != "helper_call":
            raise RuntimeError(
                "Storage capability must be helper_call mode for storage_put."
            )
        if not (binding.helper_class_desc and binding.helper_method):
            raise RuntimeError("Storage helper binding is missing helper metadata.")
        result_tmp = self._next_tmp("storage_put_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx"), const(str(stmt.key)), const(str(stmt.value))],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_storage_get_call(self, *, key: str, default_value: str, tmp_prefix: str):
        binding = self.capability_runtime_bindings.get("Storage")
        if binding is None:
            raise RuntimeError(
                "storage_get requires Storage capability. "
                "Declare app_config(uses=[Caps.Storage]) first."
            )
        if binding.mode != "helper_call":
            raise RuntimeError(
                "Storage capability must be helper_call mode for storage_get."
            )
        if not binding.helper_class_desc:
            raise RuntimeError("Storage helper binding is missing helper class metadata.")
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getString",
                    args=[var("ctx"), const(str(key)), const(str(default_value))],
                    return_type="Ljava/lang/String;",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_storage_get_stmt(self, stmt):
        out, _ = self._compile_storage_get_call(
            key=stmt.key,
            default_value=stmt.default_value,
            tmp_prefix="storage_get_ignored",
        )
        return out

    def _compile_storage_remove_stmt(self, stmt):
        binding = self.capability_runtime_bindings.get("Storage")
        if binding is None:
            raise RuntimeError(
                "storage_remove requires Storage capability. "
                "Declare app_config(uses=[Caps.Storage]) first."
            )
        if binding.mode != "helper_call":
            raise RuntimeError(
                "Storage capability must be helper_call mode for storage_remove."
            )
        if not binding.helper_class_desc:
            raise RuntimeError("Storage helper binding is missing helper class metadata.")
        result_tmp = self._next_tmp("storage_remove_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "remove",
                    args=[var("ctx"), const(str(stmt.key))],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
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
        out.extend(self._nav_set_visibility_for_index(const(target_idx), 0))
        out.extend(self._nav_emit_enter_transition_for_index(const(target_idx)))
        out.extend(self._nav_set_visibility_for_index(var(cur_var), 8))

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
        then_block.append(assign(new_size_var, binary("-", var(size_var), const(1))))
        then_block.append(assign(top_idx_var, binary("-", var(new_size_var), const(1))))
        then_block.append(assign(prev_idx_var, array_get(var(stack_var), var(top_idx_var), "I")))
        then_block.extend(self._nav_set_visibility_for_index(var(prev_idx_var), 0))
        then_block.extend(self._nav_emit_enter_transition_for_index(var(prev_idx_var)))
        then_block.extend(self._nav_set_visibility_for_index(var(cur_var), 8))
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
        then_block.append(assign(new_size_var, binary("-", var(size_var), const(1))))
        then_block.append(assign(top_idx_var, binary("-", var(new_size_var), const(1))))
        then_block.append(assign(prev_idx_var, array_get(var(stack_var), var(top_idx_var), "I")))
        then_block.extend(self._nav_set_visibility_for_index(var(prev_idx_var), 0))
        then_block.extend(self._nav_emit_enter_transition_for_index(var(prev_idx_var)))
        then_block.extend(self._nav_set_visibility_for_index(var(cur_var), 8))
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
        out.extend(self._nav_set_visibility_for_index(const(target_idx), 0))
        out.extend(self._nav_emit_enter_transition_for_index(const(target_idx)))
        out.extend(self._nav_set_visibility_for_index(var(cur_var), 8))

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
                local_type = self._local_var_types.get(part.name)
                append_arg_types = ["I"]
                if local_type == "Ljava/lang/String;":
                    append_arg_types = ["Ljava/lang/String;"]
                stmts.append(
                    assign(
                        "sb",
                        call(
                            "append",
                            args=[var("sb"), var("x")],
                            return_type="Ljava/lang/StringBuilder;",
                            arg_types=append_arg_types,
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
