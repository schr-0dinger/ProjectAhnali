from cfg.graph import ControlFlowGraph
from cfg.builder import Terminator
from dalvik.block import DalvikBlock
from dalvik.ir import DIf, DReturnVoid, DValue
from emit.smali_emit import emit_program_smali
from passes.regalloc_linear import LiveInterval
from ssa.value import SSAValue
from dalvik.method import DalvikMethod


def test_smali_emits_boolean_branch():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    b1 = cfg.new_block()
    b2 = cfg.new_block()

    cfg.set_entry(b0)
    cfg.set_exit(b2)

    b0.terminator = Terminator("branch", cond=None, true=b1, false=b2)
    b0.add_successor(b1)
    b0.add_successor(b2)
    b1.terminator = Terminator("return")
    b2.terminator = Terminator("return")

    d0 = DalvikBlock(b0)
    d1 = DalvikBlock(b1)
    d2 = DalvikBlock(b2)

    cond = SSAValue("c", 0)
    d0.emit(DIf(cond=DValue(cond), true_block=b1, false_block=b2))
    d1.emit(DReturnVoid())
    d2.emit(DReturnVoid())

    interval = LiveInterval(cond)
    interval.reg = 0
    allocator = type("A", (), {"intervals": [interval]})

    method = DalvikMethod("main", {b0: d0, b1: d1, b2: d2}, allocator)
    smali = emit_program_smali([method])

    assert "if-nez v0, :B" in smali
