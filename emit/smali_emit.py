# emit/smali_emit.py

from dalvik.method import DalvikMethod
from dalvik.ir import (
    DAdd,
    DSub,
    DMul,
    DDiv,
    DRem,
    DAnd,
    DOr,
    DXor,
    DShl,
    DShr,
    DUshr,
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
    DConstWide,
    DConstStringJumbo,
    DMoveWide,
    DSpillLoad,
    DSpillStore,
    DMoveResult,
    DMoveResultObject,
    DMoveResultWide,
    DMoveException,
    DInstanceOf,
    DIfZ,
    DPackedSwitch,
    DSparseSwitch,
    DMonitorEnter,
    DMonitorExit,
    DArrayLength,
    DFilledNewArray,
    DCompare,
)
from ir.types import AnaliType
from ir.expr import Const
import struct

LOW_REG_LIMIT = 16
TEMP_REG_COUNT = 3
TEMP_REG_START = LOW_REG_LIMIT - TEMP_REG_COUNT


def _build_reg_map(intervals, param_ssa=None):
    reg_map = {}
    max_reg = max(
        (i.reg for i in intervals if i.reg is not None),
        default=-1
    )
    spill_slots = [i for i in intervals if i.spilled]
    spill_base = max(max_reg + 1, TEMP_REG_START + TEMP_REG_COUNT)

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
    for interval in intervals:
        reg = reg_map.get(interval.value)
        if reg and reg.startswith("v"):
            base = int(reg[1:])
            max_vreg = max(max_vreg, base + (getattr(interval, "width", 1) - 1))
    locals_count = max_vreg + 1 if max_vreg >= 0 else 0

    return reg_map, locals_count


def emit_method_smali(method: DalvikMethod):
    reg_map, locals_count = _build_reg_map(method.allocator.intervals, method.param_ssa)
    param_count = len(method.param_types or [])
    range_temp_count = 0
    temp_reg_count = TEMP_REG_COUNT
    temp_reg_start = TEMP_REG_START

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

    def _move_wide_opcode(src_reg, dst_reg):
        src_idx = _reg_index(src_reg)
        dst_idx = _reg_index(dst_reg)
        if max(src_idx, dst_idx) > 255:
            return "move-wide/16"
        if max(src_idx, dst_idx) > 15:
            return "move-wide/from16"
        return "move-wide"

    def _primitive_cast_opcode(from_desc, to_desc):
        def _norm(desc):
            if desc in ("B", "C", "S", "Z"):
                return "I"
            return desc

        from_norm = _norm(from_desc)
        to_norm = _norm(to_desc)

        if to_desc in ("B", "C", "S"):
            if from_norm != "I":
                raise RuntimeError(f"Invalid primitive cast {from_desc}->{to_desc}")
            return {
                "B": "int-to-byte",
                "C": "int-to-char",
                "S": "int-to-short",
            }[to_desc]

        if from_norm == to_norm:
            return None

        opcode_map = {
            ("I", "J"): "int-to-long",
            ("I", "F"): "int-to-float",
            ("I", "D"): "int-to-double",
            ("J", "I"): "long-to-int",
            ("J", "F"): "long-to-float",
            ("J", "D"): "long-to-double",
            ("F", "I"): "float-to-int",
            ("F", "J"): "float-to-long",
            ("F", "D"): "float-to-double",
            ("D", "I"): "double-to-int",
            ("D", "J"): "double-to-long",
            ("D", "F"): "double-to-float",
        }
        op = opcode_map.get((from_norm, to_norm))
        if op is None:
            raise RuntimeError(f"Unsupported primitive cast {from_desc}->{to_desc}")
        return op

    def _temp_regs():
        return [f"v{temp_reg_start + i}" for i in range(temp_reg_count)]

    def _ensure_reg(reg, max_idx, is_obj, temp_reg, pre_lines):
        if _reg_index(reg) <= max_idx:
            return reg, False
        move_op = _move_opcode(reg, temp_reg, is_obj)
        pre_lines.append(f"    {move_op} {temp_reg}, {reg}")
        return temp_reg, True

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

    def _next_reg(reg):
        return f"{reg[0]}{int(reg[1:]) + 1}"

    def _is_wide_desc(desc):
        return desc in ("J", "D")

    def _is_int_const_ssa(value):
        return (
            isinstance(value, Const)
            and isinstance(value.value, int)
            and not isinstance(value.value, bool)
        )

    def _int_const_range(value):
        if -128 <= value <= 127:
            return "lit8"
        if -32768 <= value <= 32767:
            return "lit16"
        return None

    def _can_use_2addr(dst_reg, rhs_reg, type_desc):
        dst_idx = _reg_index(dst_reg)
        rhs_idx = _reg_index(rhs_reg)
        if dst_idx > 15 or rhs_idx > 15:
            return False
        if type_desc in ("J", "D"):
            return dst_idx <= 14 and rhs_idx <= 14
        return True

    def _coerce_type_desc(t, *, allow_none=False):
        if isinstance(t, str):
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
        if t is None and allow_none:
            return None
        raise RuntimeError(f"Unsupported type {t}")

    def _invoke_arg_types_aligned(instr):
        arg_types = list(instr.arg_types or [None] * len(instr.args))
        if instr.invoke_kind in ("virtual", "direct", "interface", "super"):
            if len(arg_types) == len(instr.args) - 1:
                arg_types = [instr.owner] + arg_types
            elif len(arg_types) != len(instr.args):
                raise RuntimeError(
                    "Call arg_types length does not match args for instance invoke"
                )
        elif len(arg_types) != len(instr.args):
            raise RuntimeError("Call arg_types length does not match args")
        return arg_types

    def _invoke_word_regs(instr, aligned_types):
        out = []
        for arg, arg_type in zip(instr.args, aligned_types):
            reg = reg_map[arg.ssa]
            desc = _coerce_type_desc(arg_type, allow_none=True)
            if desc is None:
                desc = _coerce_type_desc(getattr(arg.ssa, "type", None), allow_none=True)
            out.append(reg)
            if _is_wide_desc(desc):
                out.append(_next_reg(reg))
        return out

    def _needs_low_temp_regs():
        for block in method.blocks.values():
            for instr in block.instructions:
                if isinstance(instr, DInstanceGet):
                    o = reg_map[instr.obj.ssa]
                    r = reg_map[instr.dst.ssa]
                    if _reg_index(o) > 15 or _reg_index(r) > 15:
                        return True
                elif isinstance(instr, DInstancePut):
                    o = reg_map[instr.obj.ssa]
                    v = reg_map[instr.value.ssa]
                    if _reg_index(o) > 15 or _reg_index(v) > 15:
                        return True
                elif isinstance(instr, DInstanceOf):
                    o = reg_map[instr.obj.ssa]
                    r = reg_map[instr.dst.ssa]
                    if _reg_index(o) > 15 or _reg_index(r) > 15:
                        return True
        return False

    if _needs_low_temp_regs():
        locals_count = max(locals_count, TEMP_REG_START + TEMP_REG_COUNT)

    for block in method.blocks.values():
        for instr in block.instructions:
            if isinstance(instr, DInvoke):
                aligned_types = _invoke_arg_types_aligned(instr)
                regs = _invoke_word_regs(instr, aligned_types)
                needs_range = len(regs) > 5 or any(_reg_index(r) > 15 for r in regs)
                if needs_range:
                    range_temp_count = max(range_temp_count, len(regs))
                continue
            if isinstance(instr, DFilledNewArray):
                regs = [reg_map[a.ssa] for a in instr.args]
                needs_range = len(regs) > 5 or any(_reg_index(r) > 15 for r in regs)
                if needs_range:
                    range_temp_count = max(range_temp_count, len(regs))

    lines = []
    total_regs = locals_count + param_count + range_temp_count
    max_idx = total_regs - 1 if total_regs > 0 else 0
    if max_idx > 255:
        raise RuntimeError(
            f"Register index {max_idx} exceeds 255; spill pressure too high for current encoding."
        )
    if max_idx > 65535:
        raise RuntimeError(
            f"Register index {max_idx} exceeds 65535; method has too many registers."
        )
    params_desc = "".join(_coerce_type_desc(t) for t in (method.param_types or []))
    ret_desc = "V" if method.return_type is None else _coerce_type_desc(method.return_type)

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
            elif instr.__class__.__name__ == "DIfZ":
                referenced.add(instr.true.id)
                referenced.add(instr.false.id)
            elif isinstance(instr, DPackedSwitch):
                referenced.add(instr.default.id)
                referenced.update(target.id for target in instr.targets)
            elif isinstance(instr, DSparseSwitch):
                referenced.add(instr.default.id)
                referenced.update(target.id for target in instr.targets)

    for start, end, handler, _ in method.try_regions:
        referenced.update({start.id, end.id, handler.id})

    switch_payloads = []
    switch_payload_idx = 0

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
                        lines.append(f"    const/high16 {r}, 0x{bits & 0xFFFF0000:08x}")
                    else:
                        lines.append(f"    const {r}, 0x{bits:08x}")
                else:
                    val = int(instr.value)
                    if -8 <= val <= 7:
                        if _reg_index(r) > 15:
                            lines.append(f"    const/16 {r}, {val}")
                        else:
                            lines.append(f"    const/4 {r}, {val}")
                    elif -32768 <= val <= 32767:
                        lines.append(f"    const/16 {r}, {val}")
                    else:
                        lines.append(f"    const {r}, {val}")
            elif isinstance(instr, DConstWide):
                r = reg_map[instr.dst.ssa]
                if isinstance(instr.value, float):
                    bits = struct.unpack(">Q", struct.pack(">d", instr.value))[0]
                    lines.append(f"    const-wide {r}, 0x{bits:016x}")
                else:
                    val = int(instr.value)
                    lines.append(f"    const-wide {r}, {val}")
            elif isinstance(instr, DConstStringJumbo):
                r = reg_map[instr.dst.ssa]
                s = str(instr.value).replace("\\", "\\\\").replace("\"", "\\\"")
                lines.append(f"    const-string/jumbo {r}, \"{s}\"")
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
                pre = []
                temps = _temp_regs()
                ti = 0
                o = reg_map[instr.obj.ssa]
                o_reg, moved_obj = _ensure_reg(
                    o, 15, True, temps[ti], pre
                )
                if moved_obj:
                    ti += 1
                r = reg_map[instr.dst.ssa]
                r_reg = r
                post = []
                if _reg_index(r) > 15:
                    if ti >= len(temps):
                        raise RuntimeError("Not enough temp registers for iget")
                    r_reg = temps[ti]
                    ti += 1
                    move_op = _move_opcode(r_reg, r, _is_reference_desc(instr.desc))
                    post.append(f"    {move_op} {r}, {r_reg}")
                op = _field_opcode("iget", instr.desc)
                lines.extend(pre)
                lines.append(f"    {op} {r_reg}, {o_reg}, {instr.owner}->{instr.name}:{instr.desc}")
                lines.extend(post)
            elif isinstance(instr, DInstancePut):
                pre = []
                temps = _temp_regs()
                ti = 0
                o = reg_map[instr.obj.ssa]
                v = reg_map[instr.value.ssa]
                v_reg, moved_v = _ensure_reg(
                    v, 15, _is_reference_desc(instr.desc), temps[ti], pre
                )
                if moved_v:
                    ti += 1
                o_reg, moved_o = _ensure_reg(
                    o, 15, True, temps[ti], pre
                )
                if moved_o:
                    ti += 1
                op = _field_opcode("iput", instr.desc)
                lines.extend(pre)
                lines.append(f"    {op} {v_reg}, {o_reg}, {instr.owner}->{instr.name}:{instr.desc}")
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
            elif isinstance(instr, DArrayLength):
                r = reg_map[instr.dst.ssa]
                a = reg_map[instr.array.ssa]
                lines.append(f"    array-length {r}, {a}")
            elif isinstance(instr, DFilledNewArray):
                regs_list = [reg_map[a.ssa] for a in instr.args]
                needs_range = len(regs_list) > 5 or any(_reg_index(r) > 15 for r in regs_list)
                if needs_range:
                    temp_base = locals_count
                    for i, arg in enumerate(instr.args):
                        src = reg_map[arg.ssa]
                        dst = f"v{temp_base + i}"
                        if src == dst:
                            continue
                        is_obj = _is_object_ssa(arg.ssa)
                        move_op = _move_opcode(src, dst, is_obj)
                        lines.append(f"    {move_op} {dst}, {src}")
                    start = f"v{temp_base}"
                    end = f"v{temp_base + len(regs_list) - 1}"
                    lines.append(
                        f"    filled-new-array/range {{{start} .. {end}}}, {instr.array_desc}"
                    )
                else:
                    regs = ", ".join(regs_list)
                    lines.append(
                        f"    filled-new-array {{{regs}}}, {instr.array_desc}"
                    )
                rd = reg_map[instr.dst.ssa]
                lines.append(f"    move-result-object {rd}")
            elif isinstance(instr, DInstanceOf):
                pre = []
                temps = _temp_regs()
                ti = 0
                o = reg_map[instr.obj.ssa]
                o_reg, moved_obj = _ensure_reg(
                    o, 15, True, temps[ti], pre
                )
                if moved_obj:
                    ti += 1
                r = reg_map[instr.dst.ssa]
                r_reg = r
                post = []
                if _reg_index(r) > 15:
                    if ti >= len(temps):
                        raise RuntimeError("Not enough temp registers for instance-of")
                    r_reg = temps[ti]
                    ti += 1
                    post.append(f"    move {r}, {r_reg}")
                lines.extend(pre)
                lines.append(f"    instance-of {r_reg}, {o_reg}, {instr.desc}")
                lines.extend(post)
            elif isinstance(instr, DCheckCast):
                r = reg_map[instr.obj.ssa]
                lines.append(f"    check-cast {r}, {instr.desc}")
            elif isinstance(instr, DPrimitiveCast):
                rd = reg_map[instr.dst.ssa]
                rs = reg_map[instr.src.ssa]
                cast_op = _primitive_cast_opcode(instr.from_desc, instr.to_desc)
                if cast_op is None:
                    if rd != rs:
                        if instr.to_desc in ("J", "D") or instr.from_desc in ("J", "D"):
                            op = _move_wide_opcode(rs, rd)
                        else:
                            op = _move_opcode(rs, rd, False)
                        lines.append(f"    {op} {rd}, {rs}")
                else:
                    lines.append(f"    {cast_op} {rd}, {rs}")

            elif instr.__class__.__name__ == "DMove":
                rd = reg_map[instr.dst.ssa]
                rs = reg_map[instr.src.ssa]
                if rd != rs:
                    is_obj = _is_object_ssa(instr.src.ssa) or _is_object_ssa(instr.dst.ssa)
                    op = _move_opcode(rs, rd, is_obj)
                    lines.append(f"    {op} {rd}, {rs}")
            elif instr.__class__.__name__ == "DSpillLoad":
                rd = reg_map[instr.dst.ssa]
                rs = reg_map[instr.src.ssa]
                if rd != rs:
                    value_type = getattr(instr.dst.ssa, "type", None)
                    if value_type in ("J", "D"):
                        op = _move_wide_opcode(rs, rd)
                    else:
                        is_obj = _is_object_ssa(instr.dst.ssa)
                        op = _move_opcode(rs, rd, is_obj)
                    lines.append(f"    {op} {rd}, {rs}")
            elif instr.__class__.__name__ == "DSpillStore":
                rd = reg_map[instr.dst.ssa]
                rs = reg_map[instr.src.ssa]
                if rd != rs:
                    value_type = getattr(instr.src.ssa, "type", None)
                    if value_type in ("J", "D"):
                        op = _move_wide_opcode(rs, rd)
                    else:
                        is_obj = _is_object_ssa(instr.src.ssa)
                        op = _move_opcode(rs, rd, is_obj)
                    lines.append(f"    {op} {rd}, {rs}")
            elif isinstance(instr, DMoveWide):
                rd = reg_map[instr.dst.ssa]
                rs = reg_map[instr.src.ssa]
                if rd != rs:
                    op = _move_wide_opcode(rs, rd)
                    lines.append(f"    {op} {rd}, {rs}")
            elif isinstance(instr, DMoveResult):
                rd = reg_map[instr.dst.ssa]
                lines.append(f"    move-result {rd}")
            elif isinstance(instr, DMoveResultObject):
                rd = reg_map[instr.dst.ssa]
                lines.append(f"    move-result-object {rd}")
            elif isinstance(instr, DMoveResultWide):
                rd = reg_map[instr.dst.ssa]
                lines.append(f"    move-result-wide {rd}")
            elif isinstance(instr, DMoveException):
                rd = reg_map[instr.dst.ssa]
                lines.append(f"    move-exception {rd}")
            elif isinstance(instr, DMonitorEnter):
                rv = reg_map[instr.value.ssa]
                lines.append(f"    monitor-enter {rv}")
            elif isinstance(instr, DMonitorExit):
                rv = reg_map[instr.value.ssa]
                lines.append(f"    monitor-exit {rv}")

            elif isinstance(instr, (DAdd, DSub, DMul, DDiv, DRem, DAnd, DOr, DXor, DShl, DShr, DUshr)):
                rd = reg_map[instr.dst.ssa]
                ra = reg_map[instr.lhs.ssa]
                rb = reg_map[instr.rhs.ssa]

                type_desc = getattr(instr, "type_desc", "I")
                if type_desc in ("B", "C", "S", "Z"):
                    type_desc = "I"

                op_base = {
                    "DAdd": "add",
                    "DSub": "sub",
                    "DMul": "mul",
                    "DDiv": "div",
                    "DRem": "rem",
                    "DAnd": "and",
                    "DOr": "or",
                    "DXor": "xor",
                    "DShl": "shl",
                    "DShr": "shr",
                    "DUshr": "ushr",
                }[instr.__class__.__name__]

                if op_base in {"and", "or", "xor", "shl", "shr", "ushr"}:
                    suffix = {
                        "I": "int",
                        "J": "long",
                    }.get(type_desc)
                else:
                    suffix = {
                        "I": "int",
                        "J": "long",
                        "F": "float",
                        "D": "double",
                    }.get(type_desc)
                if suffix is None:
                    raise RuntimeError(f"Unsupported binary op type {type_desc}")

                rhs_const = instr.rhs.ssa if hasattr(instr.rhs, "ssa") else None
                lhs_const = instr.lhs.ssa if hasattr(instr.lhs, "ssa") else None

                # int literal opcodes: add/sub/rsub/mul/div/rem/and/or/xor/shl/shr/ushr-int/lit8|lit16
                if type_desc == "I" and _is_int_const_ssa(rhs_const):
                    lit = rhs_const.value
                    lit_kind = _int_const_range(lit)
                    if lit_kind and op_base in {"add", "mul", "div", "rem", "and", "or", "xor"}:
                        lines.append(f"    {op_base}-int/{lit_kind} {rd}, {ra}, {lit}")
                        continue
                    if lit_kind == "lit8" and op_base in {"shl", "shr", "ushr"}:
                        lines.append(f"    {op_base}-int/lit8 {rd}, {ra}, {lit}")
                        continue
                    if op_base == "sub":
                        neg_lit = -lit
                        neg_kind = _int_const_range(neg_lit)
                        if neg_kind:
                            lines.append(f"    add-int/{neg_kind} {rd}, {ra}, {neg_lit}")
                            continue

                # rsub-int/lit8|lit16: (const - reg)
                if type_desc == "I" and _is_int_const_ssa(lhs_const):
                    lit = lhs_const.value
                    lit_kind = _int_const_range(lit)
                    if lit_kind and op_base == "sub":
                        if lit_kind == "lit8":
                            lines.append(f"    rsub-int/lit8 {rd}, {rb}, {lit}")
                        else:
                            lines.append(f"    rsub-int {rd}, {rb}, {lit}")
                        continue

                if rd == ra and _can_use_2addr(rd, rb, type_desc):
                    lines.append(f"    {op_base}-{suffix}/2addr {rd}, {rb}")
                    continue

                opcode = f"{op_base}-{suffix}"
                lines.append(f"    {opcode} {rd}, {ra}, {rb}")

            elif isinstance(instr, DCompare):
                rd = reg_map[instr.dst.ssa]
                ra = reg_map[instr.lhs.ssa]
                rb = reg_map[instr.rhs.ssa]
                if instr.cmp_kind == "long":
                    opcode = "cmp-long"
                elif instr.cmp_kind == "float":
                    opcode = "cmpl-float" if instr.nan_mode == "cmpl" else "cmpg-float"
                elif instr.cmp_kind == "double":
                    opcode = "cmpl-double" if instr.nan_mode == "cmpl" else "cmpg-double"
                else:
                    raise RuntimeError(f"Unsupported compare kind {instr.cmp_kind}")
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

                aligned_types = _invoke_arg_types_aligned(instr)
                is_instance_invoke = instr.invoke_kind in ("virtual", "direct", "interface", "super")
                param_types = aligned_types[1:] if is_instance_invoke else aligned_types

                param_descs = []
                for idx, arg_type in enumerate(param_types):
                    desc = _coerce_type_desc(arg_type, allow_none=True)
                    if desc is None:
                        arg_idx = idx + 1 if is_instance_invoke else idx
                        desc = _coerce_type_desc(getattr(instr.args[arg_idx].ssa, "type", None), allow_none=True)
                    if desc is None:
                        raise RuntimeError("Call arg type missing")
                    param_descs.append(desc)
                arg_desc = "".join(param_descs)

                ret_desc = "V" if instr.return_type is None else _coerce_type_desc(instr.return_type)

                regs_list = _invoke_word_regs(instr, aligned_types)
                needs_range = len(regs_list) > 5 or any(_reg_index(r) > 15 for r in regs_list)

                if needs_range:
                    temp_base = locals_count
                    range_invoke = f"{invoke}/range"
                    cursor = 0
                    for arg, arg_type in zip(instr.args, aligned_types):
                        src = reg_map[arg.ssa]
                        desc = _coerce_type_desc(arg_type, allow_none=True)
                        if desc is None:
                            desc = _coerce_type_desc(getattr(arg.ssa, "type", None), allow_none=True)
                        dst = f"v{temp_base + cursor}"
                        if _is_wide_desc(desc):
                            if src != dst:
                                move_op = _move_wide_opcode(src, dst)
                                lines.append(f"    {move_op} {dst}, {src}")
                            cursor += 2
                        else:
                            if src != dst:
                                is_obj = _is_reference_desc(desc)
                                move_op = _move_opcode(src, dst, is_obj)
                                lines.append(f"    {move_op} {dst}, {src}")
                            cursor += 1

                    start = f"v{temp_base}"
                    end = f"v{temp_base + cursor - 1}"
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
                    if ret_desc in ("J", "D"):
                        lines.append(f"    move-result-wide {rd}")
                    elif _is_reference_desc(ret_desc):
                        lines.append(f"    move-result-object {rd}")
                    else:
                        lines.append(f"    move-result {rd}")

            elif instr.__class__.__name__ == "DGoto":
                lines.append(f"    goto :B{instr.target.id}")

            elif instr.__class__.__name__ == "DIf":
                if instr.cmp:
                    op, a, b = instr.cmp
                    pre = []
                    temps = _temp_regs()
                    ti = 0
                    ra = reg_map[a.ssa]
                    rb = reg_map[b.ssa]
                    ra_reg, moved_ra = _ensure_reg(
                        ra, 15, _is_object_ssa(a.ssa), temps[ti], pre
                    )
                    if moved_ra:
                        ti += 1
                    rb_reg, moved_rb = _ensure_reg(
                        rb, 15, _is_object_ssa(b.ssa), temps[ti], pre
                    )
                    if moved_rb:
                        ti += 1

                    opcode = {
                        "<":  "if-lt",
                        "<=": "if-le",
                        ">":  "if-gt",
                        ">=": "if-ge",
                        "==": "if-eq",
                        "!=": "if-ne",
                    }[op]

                    lines.extend(pre)
                    lines.append(
                        f"    {opcode} {ra_reg}, {rb_reg}, :B{instr.true.id}"
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
            elif isinstance(instr, DIfZ):
                r = reg_map[instr.cond.ssa]
                pre = []
                temps = _temp_regs()
                r_reg, _ = _ensure_reg(
                    r, 255, _is_object_ssa(instr.cond.ssa), temps[0], pre
                )
                lines.extend(pre)
                lines.append(
                    f"    if-{instr.op} {r_reg}, :B{instr.true.id}"
                )
                lines.append(
                    f"    goto :B{instr.false.id}"
                )
            elif isinstance(instr, DPackedSwitch):
                r = reg_map[instr.cond.ssa]
                payload_label = f":pswitch_data_{switch_payload_idx}"
                switch_payload_idx += 1
                lines.append(f"    packed-switch {r}, {payload_label}")
                lines.append(f"    goto :B{instr.default.id}")

                payload = [f"  {payload_label}", f"    .packed-switch {instr.first_key}"]
                for target in instr.targets:
                    payload.append(f"        :B{target.id}")
                payload.append("    .end packed-switch")
                switch_payloads.extend(payload)
            elif isinstance(instr, DSparseSwitch):
                if instr.keys != sorted(instr.keys):
                    raise RuntimeError("sparse-switch keys must be sorted ascending")
                if len(set(instr.keys)) != len(instr.keys):
                    raise RuntimeError("sparse-switch keys must be unique")
                if len(instr.keys) != len(instr.targets):
                    raise RuntimeError("sparse-switch keys/targets length mismatch")

                r = reg_map[instr.cond.ssa]
                payload_label = f":sswitch_data_{switch_payload_idx}"
                switch_payload_idx += 1
                lines.append(f"    sparse-switch {r}, {payload_label}")
                lines.append(f"    goto :B{instr.default.id}")

                payload = [f"  {payload_label}", "    .sparse-switch"]
                for key, target in zip(instr.keys, instr.targets):
                    payload.append(f"        {int(key)} -> :B{target.id}")
                payload.append("    .end sparse-switch")
                switch_payloads.extend(payload)

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
                if value_type in ("J", "D"):
                    lines.append(f"    return-wide {rd}")
                elif (
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

    if switch_payloads:
        lines.append("")
        lines.extend(switch_payloads)

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
