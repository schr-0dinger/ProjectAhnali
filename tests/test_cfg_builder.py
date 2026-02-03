from cfg.builder import CFGBuilder
from tests.ir_stub import Assign, If, While


def test_if_else_cfg_shape():
    ir = [
        Assign("x", 0),
        If(
            cond="c",
            then=[Assign("x", 1)],
            else_=[Assign("x", 2)],
        ),
        Assign("y", "x"),
    ]

    cfg = CFGBuilder().build(ir)

    blocks = list(cfg.blocks.values())

    # Expect: entry + then + else + merge + exit = 5
    assert len(blocks) == 5

    entry = cfg.entry
    merge = None

    for b in blocks:
        if len(b.predecessors) == 2:
            merge = b

    assert merge is not None, "Merge block not created"

    # Merge must have exactly 2 predecessors
    assert len(merge.predecessors) == 2

from alpha_pipeline import alpha_pipeline
from ssa.dump import dump_ssa
from dalvik.dump import dump_dalvik
from tests.ir_stub import Assign, If

ir = [
    Assign("x", 0),
    Assign("c", 1),
    If("c", [Assign("x", 1)], [Assign("x", 2)]),
    Assign("y", "x"),
]

result = alpha_pipeline(ir)

print("=== SSA ===")
print(dump_ssa(result["ssa"]))

print("=== DALVIK ===")
print(dump_dalvik(result["dalvik"]))
