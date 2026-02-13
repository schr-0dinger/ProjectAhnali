from cfg.builder import Terminator
from cfg.graph import ControlFlowGraph
from dalvik.block import DalvikBlock
from dalvik.ir import DInvoke, DReturnVoid, DValue
from dalvik.method import DalvikMethod
from emit.smali_emit import emit_program_smali
from ir.types import AhnaliType
from passes.regalloc_linear import LiveInterval
from ssa.value import SSAValue


def test_smali_emits_all_invoke_families():
    cfg = ControlFlowGraph()
    b0 = cfg.new_block()
    cfg.set_entry(b0)
    cfg.set_exit(b0)
    b0.terminator = Terminator("return")

    d0 = DalvikBlock(b0)

    obj = SSAValue("obj", 0)
    obj.type = AhnaliType.OBJECT
    lst = SSAValue("lst", 0)
    lst.type = AhnaliType.OBJECT
    arg = SSAValue("arg", 0)
    arg.type = AhnaliType.INT

    d0.emit(
        DInvoke(
            method="foo",
            args=[DValue(arg)],
            dst=None,
            return_type=None,
            arg_types=[AhnaliType.INT],
            invoke_kind="static",
            owner="LTest;",
        )
    )
    d0.emit(
        DInvoke(
            method="notify",
            args=[DValue(obj)],
            dst=None,
            return_type=None,
            arg_types=["Ljava/lang/Object;"],
            invoke_kind="virtual",
            owner="Ljava/lang/Object;",
        )
    )
    d0.emit(
        DInvoke(
            method="<init>",
            args=[DValue(obj)],
            dst=None,
            return_type=None,
            arg_types=["Ljava/lang/Object;"],
            invoke_kind="direct",
            owner="Ljava/lang/Object;",
        )
    )
    d0.emit(
        DInvoke(
            method="size",
            args=[DValue(lst)],
            dst=None,
            return_type=None,
            arg_types=["Ljava/util/List;"],
            invoke_kind="interface",
            owner="Ljava/util/List;",
        )
    )
    d0.emit(
        DInvoke(
            method="toString",
            args=[DValue(obj)],
            dst=None,
            return_type=None,
            arg_types=["Ljava/lang/Object;"],
            invoke_kind="super",
            owner="Ljava/lang/Object;",
        )
    )
    d0.emit(DReturnVoid())

    i_obj = LiveInterval(obj)
    i_obj.reg = 0
    i_lst = LiveInterval(lst)
    i_lst.reg = 1
    i_arg = LiveInterval(arg)
    i_arg.reg = 2
    allocator = type("A", (), {"intervals": [i_obj, i_lst, i_arg]})

    method = DalvikMethod("main", {b0: d0}, allocator)
    smali = emit_program_smali([method])

    assert "invoke-static {v2}, LTest;->foo(I)V" in smali
    assert "invoke-virtual {v0}, Ljava/lang/Object;->notify()V" in smali
    assert "invoke-direct {v0}, Ljava/lang/Object;-><init>()V" in smali
    assert "invoke-interface {v1}, Ljava/util/List;->size()V" in smali
    assert "invoke-super {v0}, Ljava/lang/Object;->toString()V" in smali
