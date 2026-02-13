from ir.expr import Const
from ir.types import AhnaliType
import json
import os
import zipfile
from pathlib import Path


_TYPE_DESC_MAP = {
    AhnaliType.INT: "I",
    AhnaliType.FLOAT: "F",
    AhnaliType.BOOL: "Z",
    AhnaliType.STRING: "Ljava/lang/String;",
    AhnaliType.OBJECT: "Ljava/lang/Object;",
}


def _normalize_type(value):
    if isinstance(value, AhnaliType):
        if value is AhnaliType.UNKNOWN:
            return None
        return _TYPE_DESC_MAP.get(value)
    return value


def _normalize_arg_list(arg_types):
    if arg_types is None:
        return None
    return [_normalize_type(a) for a in arg_types]


def _normalize_sig_args(sig_args, invoke_kind, argc):
    if sig_args is None:
        return None
    sig_args = [_normalize_type(a) for a in sig_args]
    if invoke_kind in ("virtual", "direct", "interface", "super"):
        if len(sig_args) == argc:
            return list(sig_args[1:])
        if len(sig_args) == argc - 1:
            return list(sig_args)
        return None
    if len(sig_args) == argc:
        return list(sig_args)
    return None


def _infer_expr_type(expr):
    if isinstance(expr, Const):
        if isinstance(expr.value, bool):
            return "Z"
        if isinstance(expr.value, int):
            return "I"
        if isinstance(expr.value, str):
            return "Ljava/lang/String;"
    desc = getattr(expr, "desc", None)
    if isinstance(desc, str):
        return desc
    ret = getattr(expr, "return_type", None)
    if isinstance(ret, str):
        return ret
    return None


def _type_compatible(inferred, expected):
    if inferred == expected:
        return True
    if inferred is None or expected is None:
        return True
    # Minimal reference widening used by current DSL.
    if inferred == "Ljava/lang/String;" and expected in ("Ljava/lang/CharSequence;", "Ljava/lang/Object;"):
        return True
    if inferred.startswith("L") and expected == "Ljava/lang/Object;":
        return True
    if inferred.startswith("[") and expected == "Ljava/lang/Object;":
        return True
    return False


def _parse_type_list(sig: str) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(sig):
        c = sig[i]
        if c in "ZBCSIFJDV":
            out.append(c)
            i += 1
            continue
        if c == "L":
            j = sig.find(";", i)
            out.append(sig[i : j + 1])
            i = j + 1
            continue
        if c == "[":
            start = i
            i += 1
            while i < len(sig) and sig[i] == "[":
                i += 1
            if i < len(sig) and sig[i] == "L":
                j = sig.find(";", i)
                out.append(sig[start : j + 1])
                i = j + 1
            else:
                out.append(sig[start : i + 1])
                i += 1
            continue
        raise ValueError(f"Unexpected type descriptor: {sig}")
    return out


def _parse_descriptor(desc: str) -> tuple[list[str], str]:
    if not desc.startswith("("):
        raise ValueError(f"Bad descriptor: {desc}")
    args_sig, ret_sig = desc.split(")", 1)
    args = _parse_type_list(args_sig[1:])
    ret = ret_sig
    return args, ret


def _read_u1(data: bytes, idx: int) -> tuple[int, int]:
    return data[idx], idx + 1


def _read_u2(data: bytes, idx: int) -> tuple[int, int]:
    return int.from_bytes(data[idx : idx + 2], "big"), idx + 2


def _read_u4(data: bytes, idx: int) -> tuple[int, int]:
    return int.from_bytes(data[idx : idx + 4], "big"), idx + 4


def _read_cp_entry(data: bytes, idx: int):
    tag, idx = _read_u1(data, idx)
    if tag == 1:  # Utf8
        length, idx = _read_u2(data, idx)
        value = data[idx : idx + length].decode("utf-8", errors="replace")
        return ("Utf8", value), idx + length, 1
    if tag == 7:  # Class
        name_index, idx = _read_u2(data, idx)
        return ("Class", name_index), idx, 1
    if tag == 8:  # String
        idx2, idx = _read_u2(data, idx)
        return ("String", idx2), idx, 1
    if tag in (9, 10, 11):  # Field/Method/InterfaceMethod ref
        idx = idx + 4
        return ("Ref", None), idx, 1
    if tag == 12:  # NameAndType
        idx = idx + 4
        return ("NameType", None), idx, 1
    if tag in (3, 4):  # Integer/Float
        idx = idx + 4
        return ("Num", None), idx, 1
    if tag in (5, 6):  # Long/Double (two slots)
        idx = idx + 8
        return ("Num2", None), idx, 2
    if tag == 15:  # MethodHandle
        idx = idx + 3
        return ("Handle", None), idx, 1
    if tag == 16:  # MethodType
        idx = idx + 2
        return ("MethodType", None), idx, 1
    if tag == 18:  # InvokeDynamic
        idx = idx + 4
        return ("InvokeDynamic", None), idx, 1
    if tag in (19, 20):  # Module, Package
        idx = idx + 2
        return ("Module", None), idx, 1
    raise ValueError(f"Unsupported constant pool tag {tag}")


def _parse_classfile(data: bytes):
    idx = 0
    magic, idx = _read_u4(data, idx)
    if magic != 0xCAFEBABE:
        raise ValueError("Bad class file")
    _, idx = _read_u2(data, idx)
    _, idx = _read_u2(data, idx)
    cp_count, idx = _read_u2(data, idx)
    cp = [None] * cp_count
    i = 1
    while i < cp_count:
        entry, idx, slots = _read_cp_entry(data, idx)
        cp[i] = entry
        i += slots
    access_flags, idx = _read_u2(data, idx)
    this_class, idx = _read_u2(data, idx)
    _, idx = _read_u2(data, idx)
    interfaces_count, idx = _read_u2(data, idx)
    idx += interfaces_count * 2
    fields_count, idx = _read_u2(data, idx)
    for _ in range(fields_count):
        idx += 6
        attr_count, idx = _read_u2(data, idx)
        for _ in range(attr_count):
            _, idx = _read_u2(data, idx)
            length, idx = _read_u4(data, idx)
            idx += length
    methods = []
    methods_count, idx = _read_u2(data, idx)
    for _ in range(methods_count):
        m_access, idx = _read_u2(data, idx)
        name_index, idx = _read_u2(data, idx)
        desc_index, idx = _read_u2(data, idx)
        attr_count, idx = _read_u2(data, idx)
        for _ in range(attr_count):
            _, idx = _read_u2(data, idx)
            length, idx = _read_u4(data, idx)
            idx += length
        methods.append((m_access, name_index, desc_index))
    class_entry = cp[this_class]
    if class_entry is None or class_entry[0] != "Class":
        raise ValueError("Bad class name")
    name_index = class_entry[1]
    name_entry = cp[name_index]
    class_name = name_entry[1]
    return access_flags, class_name, cp, methods


_ANDROID_JAR_PATH: Path | None = None
_DYNAMIC_LOADED: set[str] = set()
_DYNAMIC_MISSING: set[str] = set()


def _find_android_jar() -> Path | None:
    global _ANDROID_JAR_PATH
    if _ANDROID_JAR_PATH is not None:
        return _ANDROID_JAR_PATH
    candidates: list[Path] = []
    env_path = os.getenv("ANDROID_JAR")
    if env_path:
        candidates.append(Path(env_path))
    for parent in Path(__file__).resolve().parents:
        candidates.append(parent / "android.jar")
    sdk_root = os.getenv("ANDROID_HOME") or os.getenv("ANDROID_SDK_ROOT")
    if sdk_root:
        platforms = Path(sdk_root) / "platforms"
        if platforms.exists():
            items = []
            for p in platforms.glob("android-*"):
                try:
                    api = int(p.name.split("-")[-1])
                except ValueError:
                    api = -1
                items.append((api, p))
            for _, p in sorted(items, reverse=True):
                candidates.append(p / "android.jar")
    for candidate in candidates:
        if candidate.exists():
            _ANDROID_JAR_PATH = candidate
            return candidate
    _ANDROID_JAR_PATH = None
    return None


def _ensure_dynamic_signatures(owner_desc: str) -> None:
    if owner_desc in _DYNAMIC_LOADED or owner_desc in _DYNAMIC_MISSING:
        return
    if not (isinstance(owner_desc, str) and owner_desc.startswith("L") and owner_desc.endswith(";")):
        _DYNAMIC_MISSING.add(owner_desc)
        return
    jar_path = _find_android_jar()
    if jar_path is None:
        _DYNAMIC_MISSING.add(owner_desc)
        return
    class_path = owner_desc[1:-1] + ".class"
    try:
        with zipfile.ZipFile(jar_path, "r") as zf:
            data = zf.read(class_path)
    except Exception:
        _DYNAMIC_MISSING.add(owner_desc)
        return
    try:
        access_flags, internal_name, cp, methods = _parse_classfile(data)
    except Exception:
        _DYNAMIC_MISSING.add(owner_desc)
        return
    is_interface = bool(access_flags & 0x0200)
    for m_access, name_index, desc_index in methods:
        if not (m_access & 0x0001):
            continue
        name_entry = cp[name_index]
        desc_entry = cp[desc_index]
        if not name_entry or not desc_entry:
            continue
        method_name = name_entry[1]
        desc = desc_entry[1]
        try:
            args, ret = _parse_descriptor(desc)
        except Exception:
            continue
        if method_name == "<init>":
            _CTOR_SIGS.setdefault(owner_desc, args)
            key = (owner_desc, "<init>", "direct")
            existing = _METHOD_SIGS.get(key)
            candidate = (None, args)
            if existing is None:
                _METHOD_SIGS[key] = [candidate]
            elif isinstance(existing, list):
                if candidate not in existing:
                    existing.append(candidate)
            else:
                if existing != candidate:
                    _METHOD_SIGS[key] = [existing, candidate]
            continue
        is_static = bool(m_access & 0x0008)
        invoke_kind = "static" if is_static else ("interface" if is_interface else "virtual")
        key = (owner_desc, method_name, invoke_kind)
        candidate = (ret if ret != "V" else None, args)
        existing = _METHOD_SIGS.get(key)
        if existing is None:
            _METHOD_SIGS[key] = [candidate]
        elif isinstance(existing, list):
            if candidate not in existing:
                existing.append(candidate)
        else:
            if existing != candidate:
                _METHOD_SIGS[key] = [existing, candidate]
        if invoke_kind == "virtual":
            key = (owner_desc, method_name, "super")
            existing = _METHOD_SIGS.get(key)
            if existing is None:
                _METHOD_SIGS[key] = [candidate]
            elif isinstance(existing, list):
                if candidate not in existing:
                    existing.append(candidate)
            else:
                if existing != candidate:
                    _METHOD_SIGS[key] = [existing, candidate]
    _DYNAMIC_LOADED.add(owner_desc)


def _resolve_signature(name, args, *, return_type, arg_types, invoke_kind, owner):
    key = (owner, name, invoke_kind)
    entry = _METHOD_SIGS.get(key)
    if entry is None:
        _ensure_dynamic_signatures(owner)
        entry = _METHOD_SIGS.get(key)
    if entry is None and invoke_kind == "super":
        entry = _METHOD_SIGS.get((owner, name, "virtual"))
    if entry is None:
        return _normalize_type(return_type), _normalize_arg_list(arg_types)

    candidates = entry if isinstance(entry, list) else [entry]
    user_arg_types = list(arg_types) if arg_types is not None else None
    inferred_arg_types = [_infer_expr_type(a) for a in args]
    inferred_norm = _normalize_sig_args(inferred_arg_types, invoke_kind, len(args))
    if inferred_norm is None:
        inferred_norm = inferred_arg_types

    best = None
    best_score = -1

    for sig_ret, sig_args in candidates:
        norm = _normalize_sig_args(sig_args, invoke_kind, len(args))
        if norm is None:
            continue

        provided = user_arg_types
        check_types = inferred_norm
        if provided is not None:
            pnorm = _normalize_sig_args(_normalize_arg_list(provided), invoke_kind, len(args))
            if pnorm is None:
                continue
            if any(p is not None and p != s for p, s in zip(pnorm, norm)):
                continue
            check_types = pnorm

        score = 0
        compatible = True
        for inf, s in zip(check_types, norm):
            if _type_compatible(inf, s):
                if inf == s:
                    score += 2
                elif inf is not None:
                    score += 1
            else:
                compatible = False
                break
        if not compatible:
            continue

        if best is None or score > best_score:
            best = (sig_ret, sig_args)
            best_score = score

    if best is None:
        expected = [c[1] for c in candidates]
        raise RuntimeError(
            f"No matching overload for {owner}->{name} with arg_types={arg_types}; candidates={expected}"
        )

    sig_ret, sig_args = best
    return_type = _normalize_type(return_type)
    sig_ret = _normalize_type(sig_ret)

    if return_type is None:
        return_type = sig_ret
    elif sig_ret is not None and return_type != sig_ret:
        raise RuntimeError(
            f"Call return_type mismatch for {owner}->{name}: {return_type} vs {sig_ret}"
        )

    if arg_types is None:
        arg_types = sig_args

    return return_type, arg_types


_METHOD_SIGS_MANUAL = {
    ("Landroid/widget/TextView;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/TextView;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/EditText;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/EditText;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/EditText;", "setHint", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/CheckBox;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/CheckBox;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/CheckBox;", "setChecked", "virtual"): (None, ["Z"]),
    ("Landroid/widget/RadioButton;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/RadioButton;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/RadioButton;", "setChecked", "virtual"): (None, ["Z"]),
    ("Landroid/widget/Switch;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Switch;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/Switch;", "setChecked", "virtual"): (None, ["Z"]),
    ("Landroid/widget/SeekBar;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/SeekBar;", "setMax", "virtual"): (None, ["I"]),
    ("Landroid/widget/SeekBar;", "setProgress", "virtual"): (None, ["I"]),
    ("Landroid/widget/Spinner;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Spinner;", "setAdapter", "virtual"): (None, ["Landroid/widget/SpinnerAdapter;"]),
    ("Landroid/widget/ArrayAdapter;", "<init>", "direct"): (None, ["Landroid/content/Context;", "I"]),
    ("Landroid/widget/ArrayAdapter;", "add", "virtual"): (None, ["Ljava/lang/Object;"]),
    ("Landroid/widget/ArrayAdapter;", "setDropDownViewResource", "virtual"): (None, ["I"]),
    ("Landroid/widget/ImageView;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/ImageView;", "setImageResource", "virtual"): (None, ["I"]),
    ("Landroid/widget/ImageButton;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/ProgressBar;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/ProgressBar;", "setIndeterminate", "virtual"): (None, ["Z"]),
    ("Landroid/widget/ProgressBar;", "setMax", "virtual"): (None, ["I"]),
    ("Landroid/widget/ProgressBar;", "setProgress", "virtual"): (None, ["I"]),
    ("Landroid/widget/RadioGroup;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Toolbar;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Toolbar;", "setTitle", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/Toolbar;", "setTitleTextColor", "virtual"): (None, ["I"]),
    ("Landroid/view/View;", "setContentDescription", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/view/View;", "setImportantForAccessibility", "virtual"): (None, ["I"]),
    ("Landroid/view/View;", "setAlpha", "virtual"): (None, ["F"]),
    ("Landroid/view/View;", "setRotation", "virtual"): (None, ["F"]),
    ("Landroid/view/View;", "setScaleX", "virtual"): (None, ["F"]),
    ("Landroid/view/View;", "setScaleY", "virtual"): (None, ["F"]),
    ("Landroid/view/View;", "setTranslationX", "virtual"): (None, ["F"]),
    ("Landroid/view/View;", "setTranslationY", "virtual"): (None, ["F"]),
    ("Landroid/view/View;", "setClipToOutline", "virtual"): (None, ["Z"]),
    ("Landroid/view/View;", "setElevation", "virtual"): (None, ["F"]),
    ("Landroid/view/View;", "setRenderEffect", "virtual"): (
        None,
        ["Landroid/graphics/RenderEffect;"],
    ),
    ("Landroid/view/View;", "setStateListAnimator", "virtual"): (None, ["Landroid/animation/StateListAnimator;"]),
    ("Landroid/view/ViewGroup;", "setClipChildren", "virtual"): (None, ["Z"]),
    ("Landroid/widget/TextView;", "setShadowLayer", "virtual"): (None, ["F", "F", "F", "I"]),
    ("Landroid/graphics/drawable/GradientDrawable;", "setOrientation", "virtual"): (
        None,
        ["Landroid/graphics/drawable/GradientDrawable$Orientation;"],
    ),
    ("Landroid/graphics/drawable/GradientDrawable;", "setColors", "virtual"): (None, ["[I"]),
    ("Landroid/graphics/drawable/GradientDrawable;", "setStroke", "virtual"): (None, ["I", "I"]),
    ("Landroid/graphics/drawable/GradientDrawable;", "setCornerRadii", "virtual"): (None, ["[F"]),
    ("Landroid/animation/ObjectAnimator;", "ofFloat", "static"): (
        "Landroid/animation/ObjectAnimator;",
        ["Ljava/lang/Object;", "Ljava/lang/String;", "[F"],
    ),
    ("Landroid/graphics/RenderEffect;", "createBlurEffect", "static"): (
        "Landroid/graphics/RenderEffect;",
        ["F", "F", "Landroid/graphics/Shader$TileMode;"],
    ),
    ("Landroid/animation/StateListAnimator;", "addState", "virtual"): (
        None,
        ["[I", "Landroid/animation/Animator;"],
    ),
    ("Landroid/widget/Button;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Button;", "setText", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/app/Activity;", "setContentView", "virtual"): (None, ["Landroid/view/View;"]),
    ("Landroid/app/Activity;", "setTitle", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/app/Activity;", "findViewById", "virtual"): ("Landroid/view/View;", ["I"]),
    ("Landroid/content/Context;", "getPackageName", "virtual"): ("Ljava/lang/String;", []),
    ("Landroid/content/Context;", "getResources", "virtual"): ("Landroid/content/res/Resources;", []),
    ("Landroid/content/res/Resources;", "getIdentifier", "virtual"): (
        "I",
        ["Ljava/lang/String;", "Ljava/lang/String;", "Ljava/lang/String;"],
    ),
    ("Landroid/content/res/Resources;", "getString", "virtual"): ("Ljava/lang/String;", ["I"]),
    ("Landroid/content/res/Resources;", "getColor", "virtual"): ("I", ["I"]),
    ("Landroid/content/res/Resources;", "getDimensionPixelSize", "virtual"): ("I", ["I"]),
    ("Landroid/content/res/Resources;", "getDimension", "virtual"): ("F", ["I"]),
    ("Landroid/widget/Toast;", "makeText", "static"): (
        "Landroid/widget/Toast;",
        ["Landroid/content/Context;", "Ljava/lang/CharSequence;", "I"],
    ),
    ("Landroid/widget/Toast;", "show", "virtual"): (None, []),
    ("Lcom/google/android/material/snackbar/Snackbar;", "make", "static"): (
        "Lcom/google/android/material/snackbar/Snackbar;",
        ["Landroid/view/View;", "Ljava/lang/CharSequence;", "I"],
    ),
    ("Lcom/google/android/material/snackbar/Snackbar;", "show", "virtual"): (None, []),
    ("Landroid/widget/LinearLayout;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/ScrollView;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/LinearLayout;", "setOrientation", "virtual"): (None, ["I"]),
    ("Landroid/widget/LinearLayout;", "setGravity", "virtual"): (None, ["I"]),
    ("Landroid/widget/LinearLayout;", "setWeightSum", "virtual"): (None, ["F"]),
    ("Landroid/view/View;", "setId", "virtual"): (None, ["I"]),
    ("Landroid/widget/RelativeLayout$LayoutParams;", "addRule", "virtual"): (None, ["I", "I"]),
    ("Landroid/view/ViewGroup;", "addView", "virtual"): (None, ["Landroid/view/View;"]),
    ("Landroid/view/View;", "setOnClickListener", "virtual"): (
        None,
        ["Landroid/view/View$OnClickListener;"],
    ),
    ("Landroid/widget/TextView;", "setInputType", "virtual"): (None, ["I"]),
    ("Landroid/widget/TextView;", "setImeOptions", "virtual"): (None, ["I"]),
    ("Landroid/widget/TextView;", "setFilters", "virtual"): (None, ["[Landroid/text/InputFilter;"]),
    ("Landroid/widget/TextView;", "setSingleLine", "virtual"): (None, ["Z"]),
    ("Landroid/widget/TextView;", "setTransformationMethod", "virtual"): (
        None,
        ["Landroid/text/method/TransformationMethod;"],
    ),
    ("Landroid/text/method/PasswordTransformationMethod;", "getInstance", "static"): (
        "Landroid/text/method/PasswordTransformationMethod;",
        [],
    ),
    ("Landroid/widget/CompoundButton;", "setOnCheckedChangeListener", "virtual"): (
        None,
        ["Landroid/widget/CompoundButton$OnCheckedChangeListener;"],
    ),
    ("Landroid/widget/SeekBar;", "setOnSeekBarChangeListener", "virtual"): (
        None,
        ["Landroid/widget/SeekBar$OnSeekBarChangeListener;"],
    ),
    ("Landroid/widget/RadioGroup;", "setOnCheckedChangeListener", "virtual"): (
        None,
        ["Landroid/widget/RadioGroup$OnCheckedChangeListener;"],
    ),
    ("Landroid/view/View;", "setPadding", "virtual"): (
        None,
        ["I", "I", "I", "I"],
    ),
    ("Landroid/widget/TextView;", "setGravity", "virtual"): (None, ["I"]),
    ("Landroid/widget/TextView;", "setTextSize", "virtual"): [
        (None, ["F"]),
        (None, ["I", "F"]),
    ],
    ("Landroid/view/View;", "setLayoutParams", "virtual"): (
        None,
        ["Landroid/view/ViewGroup$LayoutParams;"],
    ),
    ("Landroid/view/View;", "setVisibility", "virtual"): (None, ["I"]),
    ("Landroid/app/AlertDialog$Builder;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/app/AlertDialog$Builder;", "setTitle", "virtual"): ("Landroid/app/AlertDialog$Builder;", ["Ljava/lang/CharSequence;"]),
    ("Landroid/app/AlertDialog$Builder;", "setMessage", "virtual"): ("Landroid/app/AlertDialog$Builder;", ["Ljava/lang/CharSequence;"]),
    ("Landroid/app/AlertDialog$Builder;", "show", "virtual"): ("Landroid/app/AlertDialog;", []),
    ("Landroid/util/Log;", "d", "static"): (
        "I",
        ["Ljava/lang/String;", "Ljava/lang/String;"],
    ),
    ("Ljava/lang/String;", "valueOf", "static"): (
        "Ljava/lang/String;",
        ["I"],
    ),
    ("Ljava/lang/StringBuilder;", "<init>", "direct"): (None, []),
    ("Ljava/lang/StringBuilder;", "append", "virtual"): [
        ("Ljava/lang/StringBuilder;", ["Ljava/lang/String;"]),
        ("Ljava/lang/StringBuilder;", ["I"]),
    ],
    ("Ljava/lang/StringBuilder;", "toString", "virtual"): ("Ljava/lang/String;", []),
}


_CTOR_SIGS_MANUAL = {
    "Landroid/widget/TextView;": ["Landroid/content/Context;"],
    "Landroid/widget/Button;": ["Landroid/content/Context;"],
    "Landroid/widget/EditText;": ["Landroid/content/Context;"],
    "Landroid/widget/CheckBox;": ["Landroid/content/Context;"],
    "Landroid/widget/RadioButton;": ["Landroid/content/Context;"],
    "Landroid/widget/Switch;": ["Landroid/content/Context;"],
    "Landroid/widget/SeekBar;": ["Landroid/content/Context;"],
    "Landroid/widget/Spinner;": ["Landroid/content/Context;"],
    "Landroid/widget/ArrayAdapter;": ["Landroid/content/Context;", "I"],
    "Landroid/widget/ImageButton;": ["Landroid/content/Context;"],
    "Landroid/widget/Toolbar;": ["Landroid/content/Context;"],
    "Landroid/app/AlertDialog$Builder;": ["Landroid/content/Context;"],
    "Landroid/widget/LinearLayout;": ["Landroid/content/Context;"],
    "Landroid/widget/ScrollView;": ["Landroid/content/Context;"],
    "Landroid/view/View;": ["Landroid/content/Context;"],
    "Landroid/widget/ImageView;": ["Landroid/content/Context;"],
    "Landroid/widget/ProgressBar;": ["Landroid/content/Context;"],
    "Landroid/widget/RadioGroup;": ["Landroid/content/Context;"],
    "Landroid/graphics/drawable/GradientDrawable;": [],
    "Landroid/graphics/drawable/RippleDrawable;": [
        "Landroid/content/res/ColorStateList;",
        "Landroid/graphics/drawable/Drawable;",
        "Landroid/graphics/drawable/Drawable;",
    ],
    "Lcom/ahnali/preview/AhnaliClickListener;": [],
    "Ljava/lang/StringBuilder;": [],
    "Landroid/widget/RelativeLayout;": ["Landroid/content/Context;"],
    "Landroidx/constraintlayout/widget/ConstraintLayout;": ["Landroid/content/Context;"],
    "Landroid/animation/StateListAnimator;": [],
    "Landroid/widget/LinearLayout$LayoutParams;": ["I", "I"],
    "Landroid/text/InputFilter$LengthFilter;": ["I"],
    "Landroid/widget/RelativeLayout$LayoutParams;": ["I", "I"],
    "Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;": ["I", "I"],
    "Landroid/widget/RelativeLayout;": ["Landroid/content/Context;"],
    "Landroidx/constraintlayout/widget/ConstraintLayout;": ["Landroid/content/Context;"],
}


def _load_signature_db(path: str | Path) -> tuple[dict, dict]:
    p = Path(path)
    data = json.loads(p.read_text())
    method_sigs: dict[tuple[str, str, str], list[tuple[str | None, list[str]]]] = {}
    for row in data.get("methods", []):
        key = (row["owner"], row["name"], row["invoke"])
        method_sigs.setdefault(key, []).append((row.get("ret"), row.get("args", [])))
    ctor_sigs: dict[str, list[str]] = {}
    for row in data.get("ctors", []):
        ctor_sigs.setdefault(row["owner"], row.get("args", []))
    return method_sigs, ctor_sigs


def load_signature_db(path: str | Path = "dsl/android/signatures_db.json") -> None:
    global _METHOD_SIGS, _CTOR_SIGS
    method_sigs, ctor_sigs = _load_signature_db(path)
    method_sigs.update(_METHOD_SIGS_MANUAL)
    ctor_sigs.update(_CTOR_SIGS_MANUAL)
    _METHOD_SIGS = method_sigs
    _CTOR_SIGS = ctor_sigs


_METHOD_SIGS = dict(_METHOD_SIGS_MANUAL)
_CTOR_SIGS = dict(_CTOR_SIGS_MANUAL)
_db_path = Path(__file__).with_name("signatures_db.json")
if _db_path.exists():
    try:
        load_signature_db(_db_path)
    except Exception:
        _METHOD_SIGS = dict(_METHOD_SIGS_MANUAL)
        _CTOR_SIGS = dict(_CTOR_SIGS_MANUAL)
