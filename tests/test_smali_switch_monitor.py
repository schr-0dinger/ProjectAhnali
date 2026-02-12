from cfg.builder import Terminator
from cfg.graph import ControlFlowGraph
from dalvik.block import DalvikBlock
from dalvik.ir import (
    DConst,
    DMonitorEnter,
    DMonitorExit,
    DPackedSwitch,
    DReturnVoid,
    DSparseSwitch,
    DValue,
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


def test_smali_emits_packed_switch_payload_and_monitor_ops():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    b1 = cfg.new_block()
    b2 = cfg.new_block()
    b3 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b3)
    b0.terminator = Terminator("branch")
    b1.terminator = Terminator("return")
    b2.terminator = Terminator("return")
    b3.terminator = Terminator("return")

    d0 = DalvikBlock(b0)
    d1 = DalvikBlock(b1)
    d2 = DalvikBlock(b2)
    d3 = DalvikBlock(b3)

    s_lock = SSAValue("lock", 0)
    s_sel = SSAValue("sel", 0)

    d0.emit(DConst(DValue(s_sel), 2))
    d0.emit(DMonitorEnter(DValue(s_lock)))
    d0.emit(
        DPackedSwitch(
            cond=DValue(s_sel),
            first_key=1,
            targets=[b1, b2],
            default_block=b3,
        )
    )
    d1.emit(DMonitorExit(DValue(s_lock)))
    d1.emit(DReturnVoid())
    d2.emit(DReturnVoid())
    d3.emit(DReturnVoid())

    allocator = _allocator_for([s_lock, s_sel])
    method = DalvikMethod("main", {b0: d0, b1: d1, b2: d2, b3: d3}, allocator)
    smali = emit_program_smali([method])
    true_a = f":B{b1.id}"
    true_b = f":B{b2.id}"
    default_label = f":B{b3.id}"

    assert "monitor-enter v0" in smali
    assert "monitor-exit v0" in smali
    assert "packed-switch v1, :pswitch_data_0" in smali
    assert ".packed-switch 1" in smali
    assert f"goto {default_label}" in smali
    assert true_a in smali and true_b in smali


def test_smali_emits_sparse_switch_payload():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    b1 = cfg.new_block()
    b2 = cfg.new_block()
    b3 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b3)
    b0.terminator = Terminator("branch")
    b1.terminator = Terminator("return")
    b2.terminator = Terminator("return")
    b3.terminator = Terminator("return")

    d0 = DalvikBlock(b0)
    d1 = DalvikBlock(b1)
    d2 = DalvikBlock(b2)
    d3 = DalvikBlock(b3)

    s_sel = SSAValue("sel", 0)

    d0.emit(
        DSparseSwitch(
            cond=DValue(s_sel),
            keys=[-3, 7],
            targets=[b1, b2],
            default_block=b3,
        )
    )
    d1.emit(DReturnVoid())
    d2.emit(DReturnVoid())
    d3.emit(DReturnVoid())

    allocator = _allocator_for([s_sel])
    method = DalvikMethod("main", {b0: d0, b1: d1, b2: d2, b3: d3}, allocator)
    smali = emit_program_smali([method])
    label_b1 = f":B{b1.id}"
    label_b2 = f":B{b2.id}"
    default_label = f":B{b3.id}"

    assert "sparse-switch v0, :sswitch_data_0" in smali
    assert ".sparse-switch" in smali
    assert f"-3 -> {label_b1}" in smali
    assert f"7 -> {label_b2}" in smali
    assert f"goto {default_label}" in smali


def test_smali_rejects_unsorted_sparse_switch_keys():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    b1 = cfg.new_block()
    b2 = cfg.new_block()
    b3 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b3)
    b0.terminator = Terminator("branch")
    b1.terminator = Terminator("return")
    b2.terminator = Terminator("return")
    b3.terminator = Terminator("return")

    d0 = DalvikBlock(b0)
    d1 = DalvikBlock(b1)
    d2 = DalvikBlock(b2)
    d3 = DalvikBlock(b3)

    s_sel = SSAValue("sel", 0)
    d0.emit(
        DSparseSwitch(
            cond=DValue(s_sel),
            keys=[7, -3],
            targets=[b1, b2],
            default_block=b3,
        )
    )
    d1.emit(DReturnVoid())
    d2.emit(DReturnVoid())
    d3.emit(DReturnVoid())

    allocator = _allocator_for([s_sel])
    method = DalvikMethod("main", {b0: d0, b1: d1, b2: d2, b3: d3}, allocator)

    import pytest

    with pytest.raises(RuntimeError, match="sparse-switch keys must be sorted ascending"):
        emit_program_smali([method])
