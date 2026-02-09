from cfg.builder import Terminator
from cfg.graph import ControlFlowGraph
from dalvik.block import DalvikBlock
from dalvik.ir import (
    DConstWide,
    DConstStringJumbo,
    DInstanceOf,
    DIfZ,
    DMoveResult,
    DMoveResultObject,
    DMoveResultWide,
    DMoveException,
    DReturnVoid,
    DValue,
    DArrayLength,
    DFilledNewArray,
)
from dalvik.method import DalvikMethod
from emit.smali_emit import emit_program_smali
from passes.regalloc_linear import LiveInterval
from ssa.value import SSAValue


def _allocator_for(values):
    intervals = []
    for idx, ssa in enumerate(values):
        itv = LiveInterval(ssa)
        itv.reg = idx
        intervals.append(itv)
    return type("A", (), {"intervals": intervals})


def test_smali_emits_group1_group2_opcodes():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    b1 = cfg.new_block()
    b2 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b2)
    b0.terminator = Terminator("return")
    b1.terminator = Terminator("return")
    b2.terminator = Terminator("return")

    d0 = DalvikBlock(b0)
    d1 = DalvikBlock(b1)
    d2 = DalvikBlock(b2)

    s_obj = SSAValue("obj", 0)
    s_is = SSAValue("is", 0)
    s_wide = SSAValue("w", 0)
    s_str = SSAValue("s", 0)
    s_tmp = SSAValue("t", 0)
    s_exc = SSAValue("e", 0)
    s_arr = SSAValue("arr", 0)
    s_len = SSAValue("len", 0)

    d0.emit(DConstWide(DValue(s_wide), 0x1122334455667788))
    d0.emit(DConstStringJumbo(DValue(s_str), "hello jumbo"))
    d0.emit(DInstanceOf(DValue(s_is), DValue(s_obj), "Ljava/lang/String;"))
    d0.emit(DMoveResult(DValue(s_tmp)))
    d0.emit(DMoveResultObject(DValue(s_tmp)))
    d0.emit(DMoveResultWide(DValue(s_tmp)))
    d0.emit(DFilledNewArray(DValue(s_arr), [DValue(s_is), DValue(s_is)], "[I"))
    d0.emit(DArrayLength(DValue(s_len), DValue(s_arr)))
    d0.emit(DIfZ(cond=DValue(s_is), op="eqz", true_block=b1, false_block=b2))

    d1.emit(DMoveException(DValue(s_exc)))
    d1.emit(DReturnVoid())
    d2.emit(DReturnVoid())

    allocator = _allocator_for([s_obj, s_is, s_wide, s_str, s_tmp, s_exc, s_arr, s_len])
    method = DalvikMethod("main", {b0: d0, b1: d1, b2: d2}, allocator)
    smali = emit_program_smali([method])

    assert "const-wide" in smali
    assert "const-string/jumbo" in smali
    assert "instance-of" in smali
    assert "move-result " in smali
    assert "move-result-object" in smali
    assert "move-result-wide" in smali
    assert "move-exception" in smali
    assert "if-eqz" in smali
    assert "filled-new-array" in smali
    assert "array-length" in smali
