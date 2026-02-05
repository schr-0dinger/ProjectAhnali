# emit/smali_emit.py

from dalvik.method import DalvikMethod
from dalvik.ir import DAdd, DSub, DMul, DDiv, DRem, DInvoke, DReturn, DThrow
from ir.types import AnaliType
from ir.expr import Const


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


def emit_method_smali(method: DalvikMethod):
    reg_map, locals_count = _build_reg_map(method.allocator.intervals)

    lines = []
    def _type_desc(t):
        if t == AnaliType.INT:
            return "I"
        if t == AnaliType.FLOAT:
            return "F"
        if t == AnaliType.BOOL:
            return "Z"
        if t == AnaliType.OBJECT:
            return "Ljava/lang/Object;"
        if t is None:
            return "V"
        raise RuntimeError(f"Unsupported type {t}")

    params_desc = "".join(_type_desc(t) for t in (method.param_types or []))
    ret_desc = _type_desc(method.return_type)

    lines.append(f".method public static {method.name}({params_desc}){ret_desc}")
    lines.append(f"    .locals {locals_count}")
    lines.append("")

    for block in method.blocks.values():
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

            elif isinstance(instr, DInvoke):
                invoke = {
                    "static": "invoke-static",
                    "virtual": "invoke-virtual",
                }.get(instr.invoke_kind)
                if invoke is None:
                    raise RuntimeError(
                        f"Unsupported invoke kind: {instr.invoke_kind}"
                    )

                arg_types = instr.arg_types or [None] * len(instr.args)
                if len(arg_types) != len(instr.args):
                    raise RuntimeError(
                        "Call arg_types length does not match args"
                    )

                def _type_desc(t):
                    if t is None:
                        raise RuntimeError("Call arg type missing")
                    if t == AnaliType.INT:
                        return "I"
                    if t == AnaliType.FLOAT:
                        return "F"
                    if t == AnaliType.BOOL:
                        return "Z"
                    if t == AnaliType.OBJECT:
                        return "Ljava/lang/Object;"
                    raise RuntimeError(f"Unsupported type {t}")

                arg_desc = "".join(_type_desc(t) for t in arg_types)

                if instr.return_type is None:
                    ret_desc = "V"
                elif instr.return_type == AnaliType.INT:
                    ret_desc = "I"
                elif instr.return_type == AnaliType.FLOAT:
                    ret_desc = "F"
                elif instr.return_type == AnaliType.BOOL:
                    ret_desc = "Z"
                elif instr.return_type == AnaliType.OBJECT:
                    ret_desc = "Ljava/lang/Object;"
                else:
                    raise RuntimeError(f"Unsupported return type {instr.return_type}")

                regs = ", ".join(reg_map[a.ssa] for a in instr.args)
                lines.append(
                    f"    {invoke} {{{regs}}}, {instr.owner}->{instr.method}({arg_desc}){ret_desc}"
                )

                if instr.dst and instr.return_type is not None:
                    rd = reg_map[instr.dst.ssa]
                    if instr.return_type == AnaliType.OBJECT:
                        lines.append(f"    move-result-object {rd}")
                    else:
                        lines.append(f"    move-result {rd}")

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
            elif isinstance(instr, DReturn):
                rd = reg_map[instr.value.ssa]
                value_type = getattr(instr.value.ssa, "type", None)
                if value_type in (None, AnaliType.UNKNOWN):
                    if isinstance(instr.value.ssa, Const):
                        v = instr.value.ssa.value
                        if isinstance(v, bool):
                            value_type = AnaliType.BOOL
                        elif isinstance(v, int):
                            value_type = AnaliType.INT
                        elif isinstance(v, float):
                            value_type = AnaliType.FLOAT
                    if value_type in (None, AnaliType.UNKNOWN):
                        raise RuntimeError("Return type UNKNOWN; cannot emit Smali")
                if value_type == AnaliType.OBJECT:
                    lines.append(f"    return-object {rd}")
                else:
                    lines.append(f"    return {rd}")
            elif isinstance(instr, DThrow):
                rd = reg_map[instr.value.ssa]
                lines.append(f"    throw {rd}")

    if method.try_regions:
        lines.append("")
        for start, end, handler, exc_type in method.try_regions:
            if exc_type is None:
                lines.append(
                    f"    .catchall {{:B{start.id} .. :B{end.id}}} :B{handler.id}"
                )
            else:
                lines.append(
                    f"    .catch {exc_type} {{:B{start.id} .. :B{end.id}}} :B{handler.id}"
                )

    lines.append(".end method")
    return lines


def emit_program_smali(methods, class_name="LTest;"):
    lines = []
    lines.append(f".class public {class_name}")
    lines.append(".super Ljava/lang/Object;")
    lines.append("")

    for method in methods:
        lines.extend(emit_method_smali(method))
        lines.append("")

    if lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def emit_smali(dalvik_blocks, intervals, method_name="main", class_name="LTest;"):
    method = DalvikMethod(method_name, dalvik_blocks, type("A", (), {"intervals": intervals}))
    return emit_program_smali([method], class_name=class_name)
