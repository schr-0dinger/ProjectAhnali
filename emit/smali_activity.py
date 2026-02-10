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
            elif name == "DIfZ":
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
                elif isinstance(instr.value, float):
                    import struct
                    bits = struct.unpack(">I", struct.pack(">f", instr.value))[0]
                    if bits & 0xFFFF == 0:
                        lines.append(f"    const/high16 {r}, 0x{bits & 0xFFFF0000:08x}")
                    else:
                        lines.append(f"    const {r}, 0x{bits:08x}")
                else:
                    lines.append(f"    const/4 {r}, {instr.value}")
            elif name == "DConstWide":
                r = reg_map[instr.dst]
                if isinstance(instr.value, float):
                    import struct
                    bits = struct.unpack(">Q", struct.pack(">d", instr.value))[0]
                    lines.append(f"    const-wide {r}, 0x{bits:016x}")
                else:
                    lines.append(f"    const-wide {r}, {int(instr.value)}")
            elif name == "DConstStringJumbo":
                r = reg_map[instr.dst]
                s = str(instr.value).replace("\\", "\\\\").replace("\"", "\\\"")
                lines.append(f"    const-string/jumbo {r}, \"{s}\"")
            elif name == "DNew":
                r = reg_map[instr.dst]
                lines.append(f"    new-instance {r}, {instr.class_desc}")

            elif name == "DMove":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                lines.append(f"    move {rd}, {rs}")
            elif name == "DSpillLoad":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                value_type = getattr(getattr(instr.dst, "ssa", None), "type", None)
                if value_type in ("J", "D"):
                    lines.append(f"    move-wide {rd}, {rs}")
                else:
                    lines.append(f"    move {rd}, {rs}")
            elif name == "DSpillStore":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                value_type = getattr(getattr(instr.src, "ssa", None), "type", None)
                if value_type in ("J", "D"):
                    lines.append(f"    move-wide {rd}, {rs}")
                else:
                    lines.append(f"    move {rd}, {rs}")
            elif name == "DMoveWide":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                lines.append(f"    move-wide {rd}, {rs}")
            elif name == "DMoveResult":
                rd = reg_map[instr.dst]
                lines.append(f"    move-result {rd}")
            elif name == "DMoveResultObject":
                rd = reg_map[instr.dst]
                lines.append(f"    move-result-object {rd}")
            elif name == "DMoveResultWide":
                rd = reg_map[instr.dst]
                lines.append(f"    move-result-wide {rd}")
            elif name == "DMoveException":
                rd = reg_map[instr.dst]
                lines.append(f"    move-exception {rd}")
            elif name == "DArrayLength":
                rd = reg_map[instr.dst]
                ra = reg_map[instr.array]
                lines.append(f"    array-length {rd}, {ra}")
            elif name == "DFilledNewArray":
                regs = ", ".join(reg_map[a.ssa] for a in instr.args)
                lines.append(
                    f"    filled-new-array {{{regs}}}, {instr.array_desc}"
                )
                rd = reg_map[instr.dst]
                lines.append(f"    move-result-object {rd}")

            elif name in ("DAdd", "DSub", "DMul", "DDiv", "DRem"):
                rd = reg_map[instr.dst]
                ra = reg_map[instr.lhs]
                rb = reg_map[instr.rhs]

                type_desc = getattr(instr, "type_desc", "I")
                if type_desc in ("B", "C", "S", "Z"):
                    type_desc = "I"

                op_base = {
                    "DAdd": "add",
                    "DSub": "sub",
                    "DMul": "mul",
                    "DDiv": "div",
                    "DRem": "rem",
                }[name]

                suffix = {
                    "I": "int",
                    "J": "long",
                    "F": "float",
                    "D": "double",
                }.get(type_desc)
                if suffix is None:
                    raise RuntimeError(f"Unsupported binary op type {type_desc}")

                opcode = f"{op_base}-{suffix}"

                lines.append(
                    f"    {opcode} {rd}, {ra}, {rb}"
                )

            elif name == "DCompare":
                rd = reg_map[instr.dst]
                ra = reg_map[instr.lhs]
                rb = reg_map[instr.rhs]
                if instr.cmp_kind == "long":
                    opcode = "cmp-long"
                elif instr.cmp_kind == "float":
                    opcode = "cmpl-float" if instr.nan_mode == "cmpl" else "cmpg-float"
                elif instr.cmp_kind == "double":
                    opcode = "cmpl-double" if instr.nan_mode == "cmpl" else "cmpg-double"
                else:
                    raise RuntimeError(f"Unsupported compare kind {instr.cmp_kind}")
                lines.append(f"    {opcode} {rd}, {ra}, {rb}")

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
            elif name == "DIfZ":
                r = reg_map[instr.cond]
                lines.append(
                    f"    if-{instr.op} {r}, :B{instr.true.id}"
                )
                lines.append(
                    f"    goto :B{instr.false.id}"
                )

            elif name == "DInvoke":
                invoke = {
                    "static": "invoke-static",
                    "virtual": "invoke-virtual",
                    "direct": "invoke-direct",
                    "super": "invoke-super",
                    "interface": "invoke-interface",
                }.get(instr.invoke_kind)
                if invoke is None:
                    raise RuntimeError(
                        f"Unsupported invoke kind: {instr.invoke_kind}"
                    )

                arg_types = instr.arg_types or [None] * len(instr.args)
                if instr.invoke_kind in ("virtual", "direct", "interface", "super"):
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
                    if instr.return_type in ("J", "D"):
                        lines.append(f"    move-result-wide {rd}")
                    elif (
                        instr.return_type == AnaliType.OBJECT
                        or instr.return_type == AnaliType.STRING
                        or (isinstance(instr.return_type, str) and instr.return_type.startswith("L"))
                    ):
                        lines.append(f"    move-result-object {rd}")
                    else:
                        lines.append(f"    move-result {rd}")
            elif name == "DInstanceOf":
                rd = reg_map[instr.dst]
                ro = reg_map[instr.obj]
                lines.append(f"    instance-of {rd}, {ro}, {instr.desc}")

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
