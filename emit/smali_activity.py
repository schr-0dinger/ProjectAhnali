# emit/smali_activity.py

def emit_activity_smali(
    dalvik_blocks,
    reg_map,
    locals_count,
    package="com/anali/preview",
    activity="MainActivity",
):
    cls = f"L{package}/{activity};"

    lines = []

    # ---- Class ----
    lines.append(f".class public {cls}")
    lines.append(".super Landroid/app/Activity;")
    lines.append("")

    # ---- Constructor ----
    lines.append(".method public constructor <init>()V")
    lines.append("    .locals 1")
    lines.append("    invoke-direct {p0}, Landroid/app/Activity;-><init>()V")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")

    # ---- onCreate ----
    lines.append(".method protected onCreate(Landroid/os/Bundle;)V")
    lines.append(f"    .locals {locals_count}")
    lines.append("")

    # super.onCreate(p0, p1)
    lines.append(
        "    invoke-super {p0, p1}, "
        "Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V"
    )
    lines.append("")

    # ---- Body (lowered code) ----
    referenced = set()
    for block in dalvik_blocks.values():
        for instr in block.instructions:
            name = instr.__class__.__name__
            if name == "DGoto":
                referenced.add(instr.target.id)
            elif name == "DIf":
                referenced.add(instr.true.id)
                referenced.add(instr.false.id)

    for block in dalvik_blocks.values():
        if block.id not in referenced and not block.instructions:
            continue

        lines.append(f"  :B{block.id}")

        for instr in block.instructions:
            name = instr.__class__.__name__

            if name == "DConst":
                r = reg_map[instr.dst]
                if isinstance(instr.value, str):
                    s = instr.value.replace("\\", "\\\\").replace("\"", "\\\"")
                    lines.append(f"    const-string {r}, \"{s}\"")
                else:
                    lines.append(f"    const/4 {r}, {instr.value}")
            elif name == "DNew":
                r = reg_map[instr.dst]
                lines.append(f"    new-instance {r}, {instr.class_desc}")

            elif name == "DMove":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                lines.append(f"    move {rd}, {rs}")

            elif name in ("DAdd", "DSub", "DMul", "DDiv", "DRem"):
                rd = reg_map[instr.dst]
                ra = reg_map[instr.lhs]
                rb = reg_map[instr.rhs]

                opcode = {
                    "DAdd": "add-int",
                    "DSub": "sub-int",
                    "DMul": "mul-int",
                    "DDiv": "div-int",
                    "DRem": "rem-int",
                }[name]

                lines.append(
                    f"    {opcode} {rd}, {ra}, {rb}"
                )

            elif name == "DGoto":
                lines.append(f"    goto :B{instr.target.id}")

            elif name == "DIf":
                if instr.cmp:
                    op, a, b = instr.cmp
                    ra = reg_map[a]
                    rb = reg_map[b]

                    opcode = {
                        "<":  "if-lt",
                        "<=": "if-le",
                        ">":  "if-gt",
                        ">=": "if-ge",
                        "==": "if-eq",
                        "!=": "if-ne",
                    }[op]

                    lines.append(
                        f"    {opcode} {ra}, {rb}, :B{instr.true.id}"
                    )
                    lines.append(
                        f"    goto :B{instr.false.id}"
                    )

            elif name == "DInvoke":
                invoke = {
                    "static": "invoke-static",
                    "virtual": "invoke-virtual",
                    "direct": "invoke-direct",
                    "interface": "invoke-interface",
                }.get(instr.invoke_kind)
                if invoke is None:
                    raise RuntimeError(
                        f"Unsupported invoke kind: {instr.invoke_kind}"
                    )

                arg_types = instr.arg_types or [None] * len(instr.args)
                if instr.invoke_kind in ("virtual", "direct", "interface"):
                    if len(arg_types) == len(instr.args):
                        arg_types = arg_types[1:]
                    elif len(arg_types) != len(instr.args) - 1:
                        raise RuntimeError(
                            "Call arg_types length does not match args for instance invoke"
                        )
                elif len(arg_types) != len(instr.args):
                    raise RuntimeError(
                        "Call arg_types length does not match args"
                    )

                def _type_desc(t):
                    from ir.types import AnaliType
                    if isinstance(t, str):
                        if len(t) == 1:
                            return t
                        return t
                    if t is None:
                        raise RuntimeError("Call arg type missing")
                    if t == AnaliType.INT:
                        return "I"
                    if t == AnaliType.FLOAT:
                        return "F"
                    if t == AnaliType.BOOL:
                        return "Z"
                    if t == AnaliType.STRING:
                        return "Ljava/lang/String;"
                    if t == AnaliType.OBJECT:
                        return "Ljava/lang/Object;"
                    raise RuntimeError(f"Unsupported type {t}")

                arg_desc = "".join(_type_desc(t) for t in arg_types)

                from ir.types import AnaliType
                if instr.return_type is None:
                    ret_desc = "V"
                elif instr.return_type == AnaliType.INT:
                    ret_desc = "I"
                elif instr.return_type == AnaliType.FLOAT:
                    ret_desc = "F"
                elif instr.return_type == AnaliType.BOOL:
                    ret_desc = "Z"
                elif instr.return_type == AnaliType.STRING:
                    ret_desc = "Ljava/lang/String;"
                elif instr.return_type == AnaliType.OBJECT:
                    ret_desc = "Ljava/lang/Object;"
                elif isinstance(instr.return_type, str):
                    ret_desc = instr.return_type
                else:
                    raise RuntimeError(f"Unsupported return type {instr.return_type}")

                regs = ", ".join(reg_map[a.ssa] for a in instr.args)
                lines.append(
                    f"    {invoke} {{{regs}}}, {instr.owner}->{instr.method}({arg_desc}){ret_desc}"
                )

                if instr.dst and instr.return_type is not None:
                    rd = reg_map[instr.dst.ssa]
                    if (
                        instr.return_type == AnaliType.OBJECT
                        or instr.return_type == AnaliType.STRING
                        or (isinstance(instr.return_type, str) and instr.return_type.startswith("L"))
                    ):
                        lines.append(f"    move-result-object {rd}")
                    else:
                        lines.append(f"    move-result {rd}")

            elif name == "DReturnVoid":
                pass  # ignore inner return

    lines.append("")
    lines.append("    return-void")
    lines.append(".end method")

    return "\n".join(lines)


def emit_activity_wrapper_smali(
    activity_desc: str = "Lcom/anali/preview/MainActivity;",
    target_desc: str = "LTest;",
    target_sig: str = "()V",
):
    lines = []

    lines.append(f".class public {activity_desc}")
    lines.append(".super Landroid/app/Activity;")
    lines.append("")

    lines.append(".method public constructor <init>()V")
    lines.append("    .locals 1")
    lines.append("    invoke-direct {p0}, Landroid/app/Activity;-><init>()V")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")

    lines.append(".method protected onCreate(Landroid/os/Bundle;)V")
    lines.append("    .locals 0")
    lines.append("    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V")
    if target_sig.startswith("()"):
        lines.append(f"    invoke-static {{}}, {target_desc}->main{target_sig}")
    else:
        lines.append(f"    invoke-static {{p0}}, {target_desc}->main{target_sig}")
    lines.append("    return-void")
    lines.append(".end method")

    return "\n".join(lines)


def emit_click_listener_smali(
    class_desc: str = "Lcom/anali/preview/AnaliClickListener;",
    target_desc: str = "LTest;",
    target_method: str = "onClick",
):
    lines = []

    lines.append(f".class public {class_desc}")
    lines.append(".super Ljava/lang/Object;")
    lines.append(".implements Landroid/view/View$OnClickListener;")
    lines.append("")

    lines.append(".method public constructor <init>()V")
    lines.append("    .locals 0")
    lines.append("    invoke-direct {p0}, Ljava/lang/Object;-><init>()V")
    lines.append("    return-void")
    lines.append(".end method")
    lines.append("")

    lines.append(".method public onClick(Landroid/view/View;)V")
    lines.append("    .locals 0")
    lines.append(f"    invoke-static {{p1}}, {target_desc}->{target_method}(Landroid/view/View;)V")
    lines.append("    return-void")
    lines.append(".end method")

    return "\n".join(lines)
