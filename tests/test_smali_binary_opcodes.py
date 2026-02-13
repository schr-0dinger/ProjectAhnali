from cfg.builder import Terminator
from cfg.graph import ControlFlowGraph
from dalvik.block import DalvikBlock
from dalvik.ir import (
    DAdd,
    DAnd,
    DConst,
    DOr,
    DRem,
    DReturnVoid,
    DShl,
    DShr,
    DSub,
    DUshr,
    DXor,
    DValue,
)
from dalvik.method import DalvikMethod
from emit.smali_emit import emit_program_smali
from ir.expr import Const
from passes.regalloc_linear import LiveInterval
from ssa.value import SSAValue


def _allocator_for(values, regs):
    intervals = []
    for value, reg in zip(values, regs):
        itv = LiveInterval(value)
        itv.reg = reg
        intervals.append(itv)
    return type("A", (), {"intervals": intervals})


def test_smali_emits_extended_binary_opcode_families():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b0)
    b0.terminator = Terminator("return")

    d0 = DalvikBlock(b0)
    s_x = SSAValue("x", 0)
    s_y = SSAValue("y", 0)
    s_dst = SSAValue("dst", 0)

    d0.emit(DAnd(DValue(s_dst), DValue(s_x), DValue(s_y), type_desc="I"))
    d0.emit(DOr(DValue(s_dst), DValue(s_x), DValue(s_y), type_desc="I"))
    d0.emit(DXor(DValue(s_dst), DValue(s_x), DValue(s_y), type_desc="I"))
    d0.emit(DShl(DValue(s_dst), DValue(s_x), DValue(s_y), type_desc="I"))
    d0.emit(DShr(DValue(s_dst), DValue(s_x), DValue(s_y), type_desc="I"))
    d0.emit(DUshr(DValue(s_dst), DValue(s_x), DValue(s_y), type_desc="I"))
    d0.emit(DReturnVoid())

    allocator = _allocator_for([s_x, s_y, s_dst], [0, 1, 2])
    method = DalvikMethod("main", {b0: d0}, allocator)
    smali = emit_program_smali([method])

    assert "and-int" in smali
    assert "or-int" in smali
    assert "xor-int" in smali
    assert "shl-int" in smali
    assert "shr-int" in smali
    assert "ushr-int" in smali


def test_smali_emits_binary_literal_and_2addr_forms():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b0)
    b0.terminator = Terminator("return")

    d0 = DalvikBlock(b0)
    s_acc = SSAValue("acc", 0)
    s_rhs = SSAValue("rhs", 0)
    c_three = Const(3)
    c_ten = Const(10)

    d0.emit(DConst(DValue(c_three), 3))
    d0.emit(DConst(DValue(c_ten), 10))
    d0.emit(DAdd(DValue(s_acc), DValue(s_acc), DValue(c_three), type_desc="I"))
    d0.emit(DSub(DValue(s_acc), DValue(c_ten), DValue(s_rhs), type_desc="I"))
    d0.emit(DRem(DValue(s_acc), DValue(s_acc), DValue(s_rhs), type_desc="I"))
    d0.emit(DReturnVoid())

    # Intentionally co-locate dst/lhs at v0 to make /2addr legal.
    allocator = _allocator_for([s_acc, s_rhs, c_three, c_ten], [0, 1, 2, 3])
    method = DalvikMethod("main", {b0: d0}, allocator)
    smali = emit_program_smali([method])

    assert "add-int/lit8 v0, v0, 3" in smali
    assert "rsub-int/lit8 v0, v1, 10" in smali
    assert "rem-int/2addr v0, v1" in smali
