# emit/smali_emit.py

from dalvik.method import DalvikMethod
from dalvik.ir import (
    DAdd,
    DSub,
    DMul,
    DDiv,
    DRem,
    DInvoke,
    DReturn,
    DThrow,
    DNew,
    DNewArray,
    DStaticGet,
    DStaticPut,
    DInstanceGet,
    DInstancePut,
    DArrayGet,
    DArrayPut,
    DCheckCast,
    DPrimitiveCast,
)
from ir.types import AnaliType
from ir.expr import Const
import struct


def _build_reg_map(intervals, param_ssa=None):
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

    if param_ssa:
        for idx, ssa in enumerate(param_ssa):
            reg_map[ssa] = f"p{idx}"

    max_vreg = -1
    for reg in reg_map.values():
        if reg.startswith("v"):
            max_vreg = max(max_vreg, int(reg[1:]))
    locals_count = max_vreg + 1 if max_vreg >= 0 else 0

    return reg_map, locals_count


def emit_method_smali(method: DalvikMethod):
    reg_map, locals_count = _build_reg_map(method.allocator.intervals, method.param_ssa)
    param_count = len(method.param_types or [])
    range_temp_count = 0

    def _reg_index(reg):
        if reg.startswith("v"):
            return int(reg[1:])
        if reg.startswith("p"):
            return locals_count + int(reg[1:])
        return -1

    def _is_object_ssa(ssa):
        t = getattr(ssa, "type", None)
        if t in (AnaliType.OBJECT, AnaliType.STRING):
            return True
        if isinstance(t, str) and (t.startswith("L") or t.startswith("[")):
            return True
        return False

    def _move_opcode(src_reg, dst_reg, is_obj):
        src_idx = _reg_index(src_reg)
        dst_idx = _reg_index(dst_reg)
        if max(src_idx, dst_idx) > 255:
            return "move-object/16" if is_obj else "move/16"
        if max(src_idx, dst_idx) > 15:
            return "move-object/from16" if is_obj else "move/from16"
        return "move-object" if is_obj else "move"

    def _is_reference_desc(desc):
        return isinstance(desc, str) and (desc.startswith("L") or desc.startswith("["))

    def _field_opcode(prefix, desc):
        if _is_reference_desc(desc):
            return f"{prefix}-object"
        if desc in ("J", "D"):
            return f"{prefix}-wide"
        if desc == "Z":
            return f"{prefix}-boolean"
        if desc == "B":
            return f"{prefix}-byte"
        if desc == "C":
            return f"{prefix}-char"
        if desc == "S":
            return f"{prefix}-short"
        return prefix

    def _array_opcode(prefix, elem_desc):
        if _is_reference_desc(elem_desc):
            return f"{prefix}-object"
        if elem_desc in ("J", "D"):
            return f"{prefix}-wide"
        if elem_desc == "Z":
            return f"{prefix}-boolean"
        if elem_desc == "B":
            return f"{prefix}-byte"
        if elem_desc == "C":
            return f"{prefix}-char"
        if elem_desc == "S":
            return f"{prefix}-short"
        return prefix

    for block in method.blocks.values():
        for instr in block.instructions:
            if not isinstance(instr, DInvoke):
                continue
            regs = [reg_map[a.ssa] for a in instr.args]
            needs_range = len(regs) > 5 or any(_reg_index(r) > 15 for r in regs)
            if needs_range:
                range_temp_count = max(range_temp_count, len(regs))

    lines = []
    def _type_desc(t):
        if isinstance(t, str):
            if len(t) == 1:
                return t
            return t
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
        if t is None:
            return "V"
        raise RuntimeError(f"Unsupported type {t}")

    params_desc = "".join(_type_desc(t) for t in (method.param_types or []))
    ret_desc = _type_desc(method.return_type)

    total_regs = locals_count + param_count + range_temp_count
    lines.append(f".method public static {method.name}({params_desc}){ret_desc}")
    lines.append(f"    .registers {total_regs}")
    lines.append("")

    referenced = set()
    for block in method.blocks.values():
        for instr in block.instructions:
            if instr.__class__.__name__ == "DGoto":
                referenced.add(instr.target.id)
            elif instr.__class__.__name__ == "DIf":
                referenced.add(instr.true.id)
                referenced.add(instr.false.id)

    for start, end, handler, _ in method.try_regions:
        referenced.update({start.id, end.id, handler.id})

    for block in method.blocks.values():
        has_instr = bool(block.instructions)
        if block.id not in referenced and not has_instr:
            continue

        lines.append(f"  :B{block.id}")

        for instr in block.instructions:
            if instr.__class__.__name__ == "DConst":
                r = reg_map[instr.dst.ssa]
                if isinstance(instr.value, str):
                    s = instr.value.replace("\\", "\\\\").replace("\"", "\\\"")
                    lines.append(f"    const-string {r}, \"{s}\"")
                elif isinstance(instr.value, float):
                    bits = struct.unpack(">I", struct.pack(">f", instr.value))[0]
                    if bits & 0xFFFF == 0:
                        lines.append(f"    const/high16 {r}, 0x{bits >> 16:04x}")
                    else:
                        lines.append(f"    const {r}, 0x{bits:08x}")
                else:
                    val = int(instr.value)
                    if -8 <= val <= 7:
                        lines.append(f"    const/4 {r}, {val}")
                    elif -32768 <= val <= 32767:
                        lines.append(f"    const/16 {r}, {val}")
                    else:
                        lines.append(f"    const {r}, {val}")
            elif isinstance(instr, DNew):
                r = reg_map[instr.dst.ssa]
                lines.append(f"    new-instance {r}, {instr.class_desc}")
            elif isinstance(instr, DNewArray):
                r = reg_map[instr.dst.ssa]
                n = reg_map[instr.src.ssa]
                lines.append(f"    new-array {r}, {n}, {instr.array_desc}")
            elif isinstance(instr, DStaticGet):
                r = reg_map[instr.dst.ssa]
                op = _field_opcode("sget", instr.desc)
                lines.append(f"    {op} {r}, {instr.owner}->{instr.name}:{instr.desc}")
            elif isinstance(instr, DStaticPut):
                r = reg_map[instr.value.ssa]
                op = _field_opcode("sput", instr.desc)
                lines.append(f"    {op} {r}, {instr.owner}->{instr.name}:{instr.desc}")
            elif isinstance(instr, DInstanceGet):
                r = reg_map[instr.dst.ssa]
                o = reg_map[instr.obj.ssa]
                op = _field_opcode("iget", instr.desc)
                lines.append(f"    {op} {r}, {o}, {instr.owner}->{instr.name}:{instr.desc}")
            elif isinstance(instr, DInstancePut):
                o = reg_map[instr.obj.ssa]
                v = reg_map[instr.value.ssa]
                op = _field_opcode("iput", instr.desc)
                lines.append(f"    {op} {v}, {o}, {instr.owner}->{instr.name}:{instr.desc}")
            elif isinstance(instr, DArrayGet):
                r = reg_map[instr.dst.ssa]
                a = reg_map[instr.array.ssa]
                i = reg_map[instr.index.ssa]
                op = _array_opcode("aget", instr.elem_desc)
                lines.append(f"    {op} {r}, {a}, {i}")
            elif isinstance(instr, DArrayPut):
                a = reg_map[instr.array.ssa]
                i = reg_map[instr.index.ssa]
                v = reg_map[instr.value.ssa]
                op = _array_opcode("aput", instr.elem_desc)
                lines.append(f"    {op} {v}, {a}, {i}")
            elif isinstance(instr, DCheckCast):
                r = reg_map[instr.obj.ssa]
                lines.append(f"    check-cast {r}, {instr.desc}")
            elif isinstance(instr, DPrimitiveCast):
                rd = reg_map[instr.dst.ssa]
                rs = reg_map[instr.src.ssa]
                cast_op = f"{instr.from_desc.lower()}-to-{instr.to_desc.lower()}"
                lines.append(f"    {cast_op} {rd}, {rs}")

            elif instr.__class__.__name__ == "DMove":
                rd = reg_map[instr.dst.ssa]
                rs = reg_map[instr.src.ssa]
                if rd != rs:
                    op = _move_opcode(rs, rd, _is_object_ssa(instr.src.ssa))
                    lines.append(f"    {op} {rd}, {rs}")

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

                regs_list = [reg_map[a.ssa] for a in instr.args]
                needs_range = len(regs_list) > 5 or any(_reg_index(r) > 15 for r in regs_list)

                if needs_range:
                    temp_base = locals_count
                    range_invoke = f"{invoke}/range"

                    # Build arg type list aligned to args
                    if instr.invoke_kind in ("virtual", "direct", "interface", "super"):
                        if len(arg_types) == len(instr.args):
                            arg_types_for_args = arg_types
                        else:
                            arg_types_for_args = [instr.owner] + arg_types
                    else:
                        arg_types_for_args = arg_types

                    for i, (arg, arg_t) in enumerate(zip(instr.args, arg_types_for_args)):
                        src = reg_map[arg.ssa]
                        dst = f"v{temp_base + i}"
                        if src == dst:
                            continue
                        is_obj = isinstance(arg_t, str) and (arg_t.startswith("L") or arg_t.startswith("["))
                        move_op = _move_opcode(src, dst, is_obj)
                        lines.append(f"    {move_op} {dst}, {src}")

                    start = f"v{temp_base}"
                    end = f"v{temp_base + len(regs_list) - 1}"
                    lines.append(
                        f"    {range_invoke} {{{start} .. {end}}}, {instr.owner}->{instr.method}({arg_desc}){ret_desc}"
                    )
                else:
                    regs = ", ".join(regs_list)
                    lines.append(
                        f"    {invoke} {{{regs}}}, {instr.owner}->{instr.method}({arg_desc}){ret_desc}"
                    )

                if instr.dst and instr.return_type is not None:
                    rd = reg_map[instr.dst.ssa]
                    if (
                        instr.return_type == AnaliType.OBJECT
                        or instr.return_type == AnaliType.STRING
                        or (
                            isinstance(instr.return_type, str)
                            and (instr.return_type.startswith("L") or instr.return_type.startswith("["))
                        )
                    ):
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
                        elif isinstance(v, str):
                            value_type = AnaliType.STRING
                    if value_type in (None, AnaliType.UNKNOWN):
                        raise RuntimeError("Return type UNKNOWN; cannot emit Smali")
                if (
                    value_type == AnaliType.OBJECT
                    or value_type == AnaliType.STRING
                    or (isinstance(value_type, str) and value_type.startswith("L"))
                ):
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


def emit_program_smali(methods, class_name="LTest;", fields=None):
    lines = []
    lines.append(f".class public {class_name}")
    lines.append(".super Ljava/lang/Object;")
    lines.append("")

    for field in fields or []:
        lines.append(f".field {field.access} {field.name}:{field.desc}")
    if fields:
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
