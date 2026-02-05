# emit/smali_emit.py

from dalvik.method import DalvikMethod
from dalvik.ir import DAdd, DSub, DMul, DDiv, DRem


def emit_method(method: DalvikMethod):
    lines = []

    lines.append(f".method public static {method.name}()V")
    lines.append(f"    .locals {method.locals_count}")

    for block in method.blocks.values():
        for instr in block.instructions:
            lines.append(f"    {instr}")

    lines.append("    return-void")
    lines.append(".end method")

    return lines

def _build_reg_map(intervals):
    reg_map = {}
    max_reg = max(
        (i.reg for i in intervals if i.reg is not None),
        default=-1
    )
    spill_slots = [i for i in intervals if i.spilled]
    spill_base = max_reg + 1

    for interval in intervals:
        if interval.spilled:
            reg = spill_base + interval.stack_slot
        else:
            reg = interval.reg
        reg_map[interval.value] = f"v{reg}"

    locals_count = (max_reg + 1) + len(spill_slots)
    return reg_map, locals_count


def emit_smali(dalvik_blocks, intervals):
    lines = []
    reg_map, locals_count = _build_reg_map(intervals)

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
                r = reg_map[instr.dst.ssa]
                lines.append(f"    const/4 {r}, {instr.value}")

            elif instr.__class__.__name__ == "DMove":
                rd = reg_map[instr.dst.ssa]
                rs = reg_map[instr.src.ssa]
                lines.append(f"    move {rd}, {rs}")

            elif isinstance(instr, (DAdd, DSub, DMul, DDiv, DRem)):
                rd = reg_map[instr.dst.ssa]
                ra = reg_map[instr.lhs.ssa]
                rb = reg_map[instr.rhs.ssa]

                opcode = {
                    "DAdd": "add-int",
                    "DSub": "sub-int",
                    "DMul": "mul-int",
                    "DDiv": "div-int",
                    "DRem": "rem-int",
                }[instr.__class__.__name__]

                lines.append(f"    {opcode} {rd}, {ra}, {rb}")

            elif instr.__class__.__name__ == "DGoto":
                lines.append(f"    goto :B{instr.target.id}")

            elif instr.__class__.__name__ == "DIf":
                if instr.cmp:
                    op, a, b = instr.cmp
                    ra = reg_map[a.ssa]
                    rb = reg_map[b.ssa]

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
                else:
                    r = reg_map[instr.cond.ssa]
                    lines.append(
                        f"    if-nez {r}, :B{instr.true.id}"
                    )
                    lines.append(
                        f"    goto :B{instr.false.id}"
                    )

            elif instr.__class__.__name__ == "DReturnVoid":
                lines.append("    return-void")

    lines.append(".end method")
    return "\n".join(lines)
