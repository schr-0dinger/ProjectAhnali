# emit/smali_emit.py

def emit_smali(dalvik_blocks, reg_map, locals_count):
    lines = []

    lines.append(".class public LTest;")
    lines.append(".super Ljava/lang/Object;")
    lines.append("")
    lines.append(".method public static main()V")
    lines.append(f"    .locals {locals_count}")
    lines.append("")

    for block in dalvik_blocks.values():
        lines.append(f"  :B{block.id}")

        for instr in block.instructions:
            if instr.__class__.__name__ == "DConst":
                r = reg_map[instr.dst]
                lines.append(f"    const/4 {r}, {instr.value}")

            elif instr.__class__.__name__ == "DMove":
                rd = reg_map[instr.dst]
                rs = reg_map[instr.src]
                lines.append(f"    move {rd}, {rs}")

            elif instr.__class__.__name__ == "DGoto":
                lines.append(f"    goto :B{instr.target.id}")

            elif instr.__class__.__name__ == "DIf":
                # Alpha: opaque condition
                lines.append(
                    f"    # if {instr.cond} goto :B{instr.true.id} else :B{instr.false.id}"
                )

            elif instr.__class__.__name__ == "DReturnVoid":
                lines.append("    return-void")

    lines.append(".end method")
    return "\n".join(lines)
