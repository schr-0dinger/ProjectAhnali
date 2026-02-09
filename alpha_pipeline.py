# alpha_pipeline.py

from cfg.builder import CFGBuilder
from cfg.validate import validate_cfg
from cfg.dominance import (
    compute_dominators,
    compute_immediate_dominators,
    build_dominator_tree,
)
from cfg.frontier import compute_dominance_frontier
from passes.type_verify import verify_types
from ssa.insert_phi import insert_phi_nodes
from ssa.rename import SSARenamer
from ssa.verify import verify_ssa
from passes.lower_ssa_to_dalvik import LowerSSAToDalvik
from passes.dce import eliminate_dead_code
from passes.cfg_simplify import simplify_cfg
from passes.type_inference import TypeInferencePass
from passes.ssa_opt import optimize_ssa
from passes.liveness import compute_liveness
from passes.regalloc_linear import LinearScanAllocator
from passes.edge_split import split_critical_edges
from ir.method import MethodIR
from ir.program import ProgramIR
from dalvik.method import DalvikMethod

def build_program(frontend_ir):
    if isinstance(frontend_ir, ProgramIR):
        return {
            "methods": frontend_ir.methods,
            "fields": getattr(frontend_ir, "fields", []),
            "support_classes": getattr(frontend_ir, "support_classes", []),
            "method_class_map": getattr(frontend_ir, "method_class_map", {}),
        }

    if isinstance(frontend_ir, list) and frontend_ir:
        if all(isinstance(m, MethodIR) for m in frontend_ir):
            return {"methods": frontend_ir, "fields": [], "support_classes": [], "method_class_map": {}}

    return {
        "methods": [
            MethodIR(
                name="main",
                params=[],
                body=frontend_ir
            )
        ],
        "fields": [],
        "support_classes": [],
        "method_class_map": {},
    }


def compile_method(method_ir, *, ssa_opt=None):
    """
    Complete Alpha pipeline:
    Structured IR → CFG → Dominance → Phi → SSA → Verify
    """

    # 0. Method signature sanity
    if method_ir.param_types and len(method_ir.param_types) != len(method_ir.params):
        raise RuntimeError("param_types length must match params length")

    # 1. CFG
    cfg = CFGBuilder().build(method_ir.body)
    split_critical_edges(cfg)
    validate_cfg(cfg)

    # 2. Dominance
    dom = compute_dominators(cfg)
    idom = compute_immediate_dominators(cfg, dom)
    dom_tree = build_dominator_tree(idom)

    # 3. Dominance Frontier
    df = compute_dominance_frontier(cfg, idom)

    # 4. Collect def blocks
    def_blocks = {}
    for b in cfg.blocks.values():
        for stmt in b.statements:
            if hasattr(stmt, "defines") and stmt.defines():
                name = stmt.defines().name
                def_blocks.setdefault(name, set()).add(b)

    # 5. Phi insertion
    phi_nodes = insert_phi_nodes(cfg, df, def_blocks)

    # 6. SSA renaming
    renamer = SSARenamer(
        cfg,
        dom_tree,
        phi_nodes,
        params=method_ir.params,
        param_types=method_ir.param_types,
    )
    ssa_blocks = renamer.run()

    # 7. SSA verification (hard gate)
    verify_ssa(cfg, ssa_blocks, dom)

    # 8. NEW: Type Inference (Phase Omega Gate)
    TypeInferencePass(cfg, ssa_blocks).run()

    verify_types(ssa_blocks)
    ssa_opt = ssa_opt or {}
    optimize_ssa(
        ssa_blocks,
        enable_folding=ssa_opt.get("enable_folding", False),
        enable_copy_removal=ssa_opt.get("enable_copy_removal", False),
        enable_coalesce=ssa_opt.get("enable_coalesce", False),
    )

    _verify_method_returns(ssa_blocks, method_ir.return_type)

    # 9. SSA → Dalvik lowering (no registers)
    dalvik_blocks = LowerSSAToDalvik(cfg, ssa_blocks).run()

    # 10. Optimizations
    dalvik_blocks = eliminate_dead_code(dalvik_blocks)
    cfg, dalvik_blocks = simplify_cfg(cfg, dalvik_blocks)

    # 11. Liveness
    liveness = compute_liveness(cfg, dalvik_blocks)

    # 12. Register allocation (Zeta-2: linear scan, no spill)
    allocator = LinearScanAllocator()
    allocator.build_intervals(cfg, dalvik_blocks, liveness)
    allocator.allocate()

    allocator.assign_stack_slots()

    from passes.lower_ssa_to_dalvik import apply_spills
    apply_spills(dalvik_blocks, allocator.intervals)


    # Apply registers to Dalvik IR
    from passes.lower_ssa_to_dalvik import _apply_registers
    _apply_registers(dalvik_blocks, allocator.intervals)

    # 13. Smali emission (mandatory)
    dalvik_method = DalvikMethod(
        method_ir.name,
        dalvik_blocks,
        allocator,
        try_regions=getattr(cfg, "try_regions", []),
        return_type=getattr(method_ir, "return_type", None),
        param_types=getattr(method_ir, "param_types", None),
        param_ssa=getattr(renamer, "param_ssa", []),
    )
    from emit.smali_emit import emit_method_smali
    smali_method = "\n".join(emit_method_smali(dalvik_method))



    return {
        "cfg": cfg,
        "dominators": dom,
        "idom": idom,
        "dom_tree": dom_tree,
        "df": df,
        "phi_nodes": phi_nodes,
        "ssa": ssa_blocks,
        "dalvik": dalvik_blocks,
        "liveness": liveness,
        "regalloc": allocator,
        "smali_method": smali_method,
        "dalvik_method": dalvik_method,
    }

def alpha_pipeline(frontend_ir, *, ssa_opt=None):
    program = build_program(frontend_ir)

    compiled = {}
    for method in program["methods"]:
        compiled[method.name] = compile_method(method, ssa_opt=ssa_opt)

    # Eta-1 compatibility shim
    from emit.smali_emit import emit_program_smali
    method_class_map = program.get("method_class_map", {}) or {}

    if len(compiled) == 1 and "main" in compiled:
        main = compiled["main"]
        smali_class = emit_program_smali([main["dalvik_method"]], fields=program.get("fields", []))
        return {
            **main,
            "smali": smali_class,
            "smali_class": smali_class,
            "methods": compiled,
        }

    default_class = "LTest;"
    grouped = {}
    for method_name, out in compiled.items():
        cls = method_class_map.get(method_name, default_class)
        grouped.setdefault(cls, []).append(out["dalvik_method"])

    smali_class = emit_program_smali(
        grouped.get(default_class, []),
        class_name=default_class,
        fields=program.get("fields", []),
    )
    extra_smali_classes = {}
    for class_desc, methods in grouped.items():
        if class_desc == default_class:
            continue
        extra_smali_classes[class_desc] = emit_program_smali(
            methods,
            class_name=class_desc,
            fields=[],
        )

    return {
        "methods": compiled,
        "smali_class": smali_class,
        "extra_smali_classes": extra_smali_classes,
        "support_classes": program.get("support_classes", []),
    }


def _infer_value_type(val):
    from ir.expr import Const
    from ssa.value import SSAValue
    from ir.types import AnaliType

    if isinstance(val, SSAValue):
        return val.type
    if isinstance(val, Const):
        v = val.value
        if isinstance(v, bool):
            return AnaliType.BOOL
        if isinstance(v, int):
            return AnaliType.INT
        if isinstance(v, float):
            return AnaliType.FLOAT
        if isinstance(v, str):
            return AnaliType.STRING
    return AnaliType.UNKNOWN


def _verify_method_returns(ssa_blocks, return_type):
    from ir.stmt import Return
    from ir.types import AnaliType
    def _type_from_desc(desc):
        if desc in ("I", "J", "B", "C", "S"):
            return AnaliType.INT
        if desc == "Z":
            return AnaliType.BOOL
        if desc in ("F", "D"):
            return AnaliType.FLOAT
        if desc == "Ljava/lang/String;":
            return AnaliType.STRING
        if isinstance(desc, str) and (desc.startswith("L") or desc.startswith("[")):
            return AnaliType.OBJECT
        return AnaliType.UNKNOWN

    if isinstance(return_type, str):
        return_type = _type_from_desc(return_type)

    for block in ssa_blocks.values():
        for stmt in block.statements:
            if isinstance(stmt, Return):
                if return_type is None:
                    if stmt.value is not None:
                        raise RuntimeError("Void method cannot return a value")
                    continue
                if stmt.value is None:
                    raise RuntimeError("Non-void method must return a value")
                vtype = _infer_value_type(stmt.value)
                if vtype == AnaliType.UNKNOWN or vtype != return_type:
                    raise RuntimeError("Return type mismatch")
