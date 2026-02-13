from cfg.graph import ControlFlowGraph
from cfg.builder import Terminator
from dalvik.block import DalvikBlock
from dalvik.ir import DInvoke, DReturn, DValue
from dalvik.method import DalvikMethod
from emit.smali_emit import emit_program_smali
from ir.types import AhnaliType
from passes.regalloc_linear import LiveInterval
from ssa.value import SSAValue


def test_smali_emits_invoke_and_return():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    b1 = cfg.new_block()

    cfg.set_entry(b0)
    cfg.set_exit(b1)

    b0.terminator = Terminator("jump", target=b1)
    b0.add_successor(b1)
    b1.terminator = Terminator("return")

    d0 = DalvikBlock(b0)
    d1 = DalvikBlock(b1)

    arg = SSAValue("a", 0)
    arg.type = AhnaliType.INT
    ret = SSAValue("r", 0)
    ret.type = AhnaliType.INT

    d0.emit(
        DInvoke(
            method="foo",
            args=[DValue(arg)],
            dst=DValue(ret),
            return_type=AhnaliType.INT,
            arg_types=[AhnaliType.INT],
        )
    )
    d1.emit(DReturn(DValue(ret)))

    a_interval = LiveInterval(arg)
    a_interval.reg = 0
    r_interval = LiveInterval(ret)
    r_interval.reg = 1
    allocator = type("A", (), {"intervals": [a_interval, r_interval]})

    method = DalvikMethod("main", {b0: d0, b1: d1}, allocator)
    smali = emit_program_smali([method])

    assert "invoke-static {v0}, LTest;->foo(I)I" in smali
    assert "move-result v1" in smali
    assert "return v1" in smali
