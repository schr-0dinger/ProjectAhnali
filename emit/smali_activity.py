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
    lines.append(".method public <init>()V")
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
    for block in dalvik_blocks.values():
        lines.append(f"  :B{block.id}")

        for instr in block.instructions:
            name = instr.__class__.__name__

            if name == "DConst":
                r = reg_map[instr.dst]
                lines.append(f"    const/4 {r}, {instr.value}")

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

            elif name == "DReturnVoid":
                pass  # ignore inner return

    lines.append("")
    lines.append("    return-void")
    lines.append(".end method")

    return "\n".join(lines)
