from cfg.builder import Terminator
from cfg.graph import ControlFlowGraph
from dalvik.block import DalvikBlock
from dalvik.ir import DConst, DPrimitiveCast, DReturnVoid, DValue
from dalvik.method import DalvikMethod
from emit.smali_emit import emit_program_smali
from passes.regalloc_linear import LiveInterval
from ssa.value import SSAValue


def test_smali_emits_group4_primitive_casts():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b0)
    b0.terminator = Terminator("return")
    d0 = DalvikBlock(b0)

    s_i = SSAValue("i", 0)
    s_f = SSAValue("f", 0)
    s_l = SSAValue("l", 0)
    s_d = SSAValue("d", 0)
    s_b = SSAValue("b", 0)
    s_s = SSAValue("s", 0)
    s_c = SSAValue("c", 0)

    d0.emit(DConst(DValue(s_i), 7))
    d0.emit(DPrimitiveCast(DValue(s_f), DValue(s_i), "I", "F"))
    d0.emit(DPrimitiveCast(DValue(s_l), DValue(s_i), "I", "J"))
    d0.emit(DPrimitiveCast(DValue(s_i), DValue(s_l), "J", "I"))
    d0.emit(DPrimitiveCast(DValue(s_d), DValue(s_f), "F", "D"))
    d0.emit(DPrimitiveCast(DValue(s_f), DValue(s_d), "D", "F"))
    d0.emit(DPrimitiveCast(DValue(s_b), DValue(s_i), "I", "B"))
    d0.emit(DPrimitiveCast(DValue(s_s), DValue(s_i), "I", "S"))
    d0.emit(DPrimitiveCast(DValue(s_c), DValue(s_i), "I", "C"))
    d0.emit(DReturnVoid())

    values = [s_i, s_f, s_l, s_d, s_b, s_s, s_c]
    intervals = []
    for idx, ssa in enumerate(values):
        itv = LiveInterval(ssa)
        itv.reg = idx
        intervals.append(itv)
    allocator = type("A", (), {"intervals": intervals})

    method = DalvikMethod("main", {b0: d0}, allocator)
    smali = emit_program_smali([method])

    assert "int-to-float" in smali
    assert "int-to-long" in smali
    assert "long-to-int" in smali
    assert "float-to-double" in smali
    assert "double-to-float" in smali
    assert "int-to-byte" in smali
    assert "int-to-short" in smali
    assert "int-to-char" in smali
