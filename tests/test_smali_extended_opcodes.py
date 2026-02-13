from cfg.builder import Terminator
from cfg.graph import ControlFlowGraph
from dalvik.block import DalvikBlock
from dalvik.ir import (
    DArrayGet,
    DArrayPut,
    DCheckCast,
    DConst,
    DInstanceGet,
    DInstancePut,
    DNewArray,
    DPrimitiveCast,
    DReturnVoid,
    DStaticGet,
    DStaticPut,
    DValue,
)
from dalvik.method import DalvikMethod
from emit.smali_emit import emit_program_smali
from passes.regalloc_linear import LiveInterval
from ssa.value import SSAValue


def test_smali_emits_typed_field_array_and_cast_opcodes():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b0)
    b0.terminator = Terminator("return")
    d0 = DalvikBlock(b0)

    s_obj = SSAValue("obj", 0)
    s_arr = SSAValue("arr", 0)
    s_idx = SSAValue("idx", 0)
    s_i = SSAValue("i", 0)
    s_b = SSAValue("b", 0)
    s_c = SSAValue("c", 0)
    s_bool = SSAValue("z", 0)
    s_len = SSAValue("n", 0)
    s_arr_new = SSAValue("arr_new", 0)
    s_cast = SSAValue("cast", 0)

    d0.emit(DConst(DValue(s_idx), 0))
    d0.emit(DConst(DValue(s_i), 7))
    d0.emit(DStaticGet(DValue(s_bool), "LTest;", "sb", "Z"))
    d0.emit(DStaticPut(DValue(s_bool), "LTest;", "sb", "Z"))
    d0.emit(DStaticGet(DValue(s_b), "LTest;", "sbyte", "B"))
    d0.emit(DStaticGet(DValue(s_arr), "LTest;", "sarr", "[I"))
    d0.emit(DInstanceGet(DValue(s_c), DValue(s_obj), "LBox;", "ch", "C"))
    d0.emit(DInstancePut(DValue(s_obj), DValue(s_c), "LBox;", "ch", "C"))
    d0.emit(DArrayGet(DValue(s_bool), DValue(s_arr), DValue(s_idx), "Z"))
    d0.emit(DArrayPut(DValue(s_arr), DValue(s_idx), "S", DValue(s_i)))
    d0.emit(DConst(DValue(s_len), 4))
    d0.emit(DNewArray(DValue(s_arr_new), DValue(s_len), "[I"))
    d0.emit(DPrimitiveCast(DValue(s_cast), DValue(s_i), "I", "F"))
    d0.emit(DCheckCast(DValue(s_obj), "Ljava/lang/String;"))
    d0.emit(DReturnVoid())

    values = [s_obj, s_arr, s_idx, s_i, s_b, s_c, s_bool, s_len, s_arr_new, s_cast]
    intervals = []
    for idx, ssa in enumerate(values):
        itv = LiveInterval(ssa)
        itv.reg = idx
        intervals.append(itv)
    allocator = type("A", (), {"intervals": intervals})

    method = DalvikMethod("main", {b0: d0}, allocator)
    smali = emit_program_smali([method])

    assert "sget-boolean" in smali
    assert "sput-boolean" in smali
    assert "sget-byte" in smali
    assert "sget-object" in smali
    assert "iget-char" in smali
    assert "iput-char" in smali
    assert "aget-boolean" in smali
    assert "aput-short" in smali
    assert "new-array" in smali
    assert "int-to-float" in smali
    assert "check-cast" in smali
