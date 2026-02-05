from alpha_pipeline import alpha_pipeline
from passes.dce import eliminate_dead_code
from tests.ir_stub import Assign, If
from dalvik.ir import DIf


def test_ssa_coalesce_preserves_branch_semantics():
    ir = [
        Assign("x", 1),
        Assign("y", "x"),
        Assign("z", "y"),
        If("z", [], []),
    ]

    result = alpha_pipeline(ir, ssa_opt={"enable_coalesce": True})
    dalvik = result["dalvik"]

    # Ensure branch still exists after aggressive coalescing + DCE
    assert any(isinstance(i, DIf) for b in dalvik.values() for i in b.instructions)


def test_coalesce_dce_instruction_count_does_not_increase():
    ir = [
        Assign("x", 1),
        Assign("y", "x"),
        Assign("z", "y"),
        If("z", [], []),
    ]

    baseline = alpha_pipeline(ir, ssa_opt={"enable_coalesce": False})
    baseline_dalvik = baseline["dalvik"]
    eliminate_dead_code(baseline_dalvik)
    baseline_count = sum(len(b.instructions) for b in baseline_dalvik.values())

    optimized = alpha_pipeline(ir, ssa_opt={"enable_coalesce": True})
    optimized_dalvik = optimized["dalvik"]
    eliminate_dead_code(optimized_dalvik)
    optimized_count = sum(len(b.instructions) for b in optimized_dalvik.values())

    assert optimized_count <= baseline_count
