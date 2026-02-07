from ir.expr import Const


def _normalize_sig_args(sig_args, invoke_kind, argc):
    if sig_args is None:
        return None
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


def _resolve_signature(name, args, *, return_type, arg_types, invoke_kind, owner):
    key = (owner, name, invoke_kind)
    entry = _METHOD_SIGS.get(key)
    if entry is None:
        return return_type, arg_types

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
            pnorm = _normalize_sig_args(provided, invoke_kind, len(args))
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

    if return_type is None:
        return_type = sig_ret
    elif sig_ret is not None and return_type != sig_ret:
        raise RuntimeError(
            f"Call return_type mismatch for {owner}->{name}: {return_type} vs {sig_ret}"
        )

    if arg_types is None:
        arg_types = sig_args

    return return_type, arg_types


_METHOD_SIGS = {
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
    ("Landroid/widget/ImageButton;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Toolbar;", "<init>", "direct"): (None, ["Landroid/content/Context;"]),
    ("Landroid/widget/Toolbar;", "setTitle", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
    ("Landroid/widget/Toolbar;", "setTitleTextColor", "virtual"): (None, ["I"]),
    ("Landroid/view/View;", "setContentDescription", "virtual"): (None, ["Ljava/lang/CharSequence;"]),
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
    ("Landroid/view/ViewGroup;", "addView", "virtual"): (None, ["Landroid/view/View;"]),
    ("Landroid/view/View;", "setOnClickListener", "virtual"): (
        None,
        ["Landroid/view/View$OnClickListener;"],
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


_CTOR_SIGS = {
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
    "Lcom/anali/preview/AnaliClickListener;": [],
    "Ljava/lang/StringBuilder;": [],
    "Landroid/widget/RelativeLayout;": ["Landroid/content/Context;"],
    "Landroidx/constraintlayout/widget/ConstraintLayout;": ["Landroid/content/Context;"],
    "Landroid/widget/LinearLayout$LayoutParams;": ["I", "I"],
    "Landroid/widget/RelativeLayout$LayoutParams;": ["I", "I"],
    "Landroidx/constraintlayout/widget/ConstraintLayout$LayoutParams;": ["I", "I"],
}
