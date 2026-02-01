
# emit/smali_preview.py

def emit_smali_preview(dalvik_blocks):
    lines = []

    lines.append(".class public LTest;")
    lines.append(".super Ljava/lang/Object;")
    lines.append("")
    lines.append(".method public static main()V")
    lines.append("    .locals 16")
    lines.append("")

    reg_map = {}
    next_reg = 0

    def reg(val):
        nonlocal next_reg
        if val not in reg_map:
            reg_map[val] = f"v{next_reg}"
            next_reg += 1
        return reg_map[val]

    for block in dalvik_blocks.values():
        lines.append(f"  :B{block.id}")

        for instr in block.instructions:
            s = str(instr)

            if " = const " in s:
                dst, value = s.split(" = const ")
                lines.append(f"    const/4 {reg(dst)}, {value}")

            elif " = move " in s:
                dst, src = s.split(" = move ")
                lines.append(f"    move {reg(dst)}, {reg(src)}")

            elif s.startswith("if "):
                lines.append(f"    # {s}  ; preview-only")

            elif s.startswith("goto"):
                lines.append(f"    # {s}  ; preview-only")

            elif s == "return-void":
                lines.append("    return-void")

    lines.append(".end method")
    return "\n".join(lines)
