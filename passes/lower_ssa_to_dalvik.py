# passes/lower_ssa_to_dalvik.py

from dalvik.block import DalvikBlock
from dalvik.ir import (
    DValue,
    DConst,
    DMove,
    DIf,
    DGoto,
    DReturnVoid,
    DReturn,
    DInvoke,
    DThrow,
    DNew,
)
from ir.expr import Compare, BinaryOp, Const, Var, Call, New
from ir.types import AnaliType
from dalvik.ir import DAdd, DSub, DMul, DDiv, DRem


# passes/lower_ssa_to_dalvik.py

from ssa.value import SSAValue


def apply_spills(dalvik_blocks, intervals):
    spill_map = {i.value: i for i in intervals if i.spilled}

    for block in dalvik_blocks.values():
        new_instrs = []

        for instr in block.instructions:
            # ---- reload before uses ----
            for field in ("src", "lhs", "rhs", "cond", "value"):
                if hasattr(instr, field):
                    d = getattr(instr, field)
                    if d and hasattr(d, "ssa") and d.ssa in spill_map:
                        slot = spill_map[d.ssa].stack_slot
                        spill_val = DValue(d.ssa)
                        spill_val.reg = slot
                        tmp = DValue(d.ssa)
                        new_instrs.append(DMove(tmp, spill_val))
                        setattr(instr, field, tmp)

            if hasattr(instr, "args"):
                new_args = []
                for d in instr.args:
                    if d and d.ssa in spill_map:
                        slot = spill_map[d.ssa].stack_slot
                        spill_val = DValue(d.ssa)
                        spill_val.reg = slot
                        tmp = DValue(d.ssa)
                        new_instrs.append(DMove(tmp, spill_val))
                        new_args.append(tmp)
                    else:
                        new_args.append(d)
                instr.args = new_args

            new_instrs.append(instr)

            # ---- spill after defs ----
            if hasattr(instr, "dst") and instr.dst and instr.dst.ssa in spill_map:
                slot = spill_map[instr.dst.ssa].stack_slot
                spill_val = DValue(instr.dst.ssa)
                spill_val.reg = slot
                new_instrs.append(DMove(spill_val, instr.dst))

        block.instructions = new_instrs


def _apply_registers(dalvik_blocks, intervals):
    regmap = {i.value: i.reg for i in intervals}
    spill_slots = {i.value: i.stack_slot for i in intervals if i.spilled}

    for block in dalvik_blocks.values():
        for instr in block.instructions:
            for attr in ("dst", "src", "lhs", "rhs", "cond", "value"):
                if hasattr(instr, attr):
                    d = getattr(instr, attr)
                    if d and hasattr(d, "ssa") and d.ssa in regmap:
                        reg = regmap[d.ssa]
                        if reg is not None:
                            d.reg = reg
                        elif d.reg is None and d.ssa in spill_slots:
                            d.reg = spill_slots[d.ssa]
            if hasattr(instr, "args"):
                for d in instr.args:
                    if d and hasattr(d, "ssa") and d.ssa in regmap:
                        reg = regmap[d.ssa]
                        if reg is not None:
                            d.reg = reg
                        elif d.reg is None and d.ssa in spill_slots:
                            d.reg = spill_slots[d.ssa]


class LowerSSAToDalvik:
    def __init__(self, cfg, ssa_blocks):
        self.cfg = cfg
        self.ssa_blocks = ssa_blocks

        # CFG block -> DalvikBlock
        self.blocks = {}

    # ----------------------------
    # Entry point
    # ----------------------------

    def run(self):
        # 1. Create Dalvik blocks
        for cfg_block in self.cfg.blocks.values():
            self.blocks[cfg_block] = DalvikBlock(cfg_block)

        # 2. Lower SSA blocks
        for cfg_block, ssa_block in self.ssa_blocks.items():
            self._lower_block(cfg_block, ssa_block)

        return self.blocks

    # ----------------------------
    # Lowering helpers
    # ----------------------------

    def _as_dvalue(self, value, db):

        if isinstance(value, DValue):
            return value

        if isinstance(value, Const):
            dv = DValue(value)
            db.emit(DConst(dv, value.value))
            return dv

        if isinstance(value, SSAValue):
            return DValue(value)

        if isinstance(value, Var):
            # Legacy unresolved variable (e.g., If("c"))
            # Treat as symbolic value; verifier decides legality
            return DValue(value)

        raise RuntimeError(
            f"Dalvik lowering received unsupported value: {value}"
        )



    def _lower_block(self, cfg_block, ssa_block):
        db = self.blocks[cfg_block]

        # --- Phi elimination (edge moves) ---
        for succ in cfg_block.successors:
            succ_ssa = self.ssa_blocks.get(succ)
            if not succ_ssa:
                continue

            for phi in succ_ssa.phis:
                src = phi.incoming[cfg_block]
                dst = phi.target
                db.emit(DMove(DValue(dst), DValue(src)))

        # --- Lower SSA statements ---
        for stmt in ssa_block.statements:
            self._lower_stmt(stmt, db)

        # --- Terminator ---
        term = cfg_block.terminator
        kind = term.kind

        if kind == "branch":
            if isinstance(term.cond, Compare):
                # Relational branch
                db.emit(
                    DIf(
                        cmp=(
                            term.cond.op,
                            self._as_dvalue(term.cond.left, db),
                            self._as_dvalue(term.cond.right, db),
                        ),
                        true_block=term.true,
                        false_block=term.false,
                    )
                )

            else:
                # Boolean SSA condition
                if not hasattr(term.cond, "version"):
                    raise RuntimeError(
                        "Branch condition must be SSAValue "
                        "(did you forget to define it?)"
                    )

                db.emit(
                    DIf(
                        cond=DValue(term.cond),
                        true_block=term.true,
                        false_block=term.false,
                    )
                )

        elif kind == "jump":
            db.emit(DGoto(term.target))

        elif kind == "return":
            if hasattr(term, "value") and term.value is not None:
                ret = self._as_dvalue(term.value, db)
                if isinstance(ret.ssa, SSAValue) and ret.ssa.type == AnaliType.UNKNOWN:
                    raise RuntimeError(
                        f"Return type UNKNOWN for {ret.ssa}"
                    )
                db.emit(DReturn(ret))
            else:
                db.emit(DReturnVoid())

        elif kind == "throw":
            val = self._as_dvalue(term.value, db)
            if isinstance(val.ssa, SSAValue):
                if val.ssa.type != AnaliType.OBJECT:
                    raise RuntimeError(
                        f"Throw requires OBJECT type, got {val.ssa.type}"
                    )
            db.emit(DThrow(val))

        else:
            raise RuntimeError(f"Unknown terminator {kind}")

    def _lower_stmt(self, stmt, db):
        """
        Delta-2 lowering:
        - literals
        - moves
        - binary arithmetic
        - calls (Eta-2 scaffolding)
        """
        defines = stmt.defines() if hasattr(stmt, "defines") else None
        dst = DValue(defines) if defines is not None else None

        expr = getattr(stmt, "expr", None)

        if expr is None:
            return

        # Literal
        if isinstance(expr, int):
            if dst is None:
                raise RuntimeError("Literal must be assigned to a destination")
            db.emit(DConst(dst, expr))
            return

        # Binary arithmetic
        if isinstance(expr, BinaryOp):
            if dst is None:
                raise RuntimeError("BinaryOp must be assigned to a destination")

            expr_type = stmt.defines().type

            if expr_type == AnaliType.INT:
                op_map = {"+": DAdd, "-": DSub, "*": DMul, "/": DDiv, "%": DRem}
            elif expr_type == AnaliType.FLOAT:
                # Future-proofing: Phase Omega allows adding DAddFloat easily here
                raise NotImplementedError("Float arithmetic not yet implemented")
            else:
                raise RuntimeError(f"Cannot perform arithmetic on type {expr_type}")          


            lhs = self._as_dvalue(expr.left, db)
            rhs = self._as_dvalue(expr.right, db)

            op_map = {
                "+": DAdd,
                "-": DSub,
                "*": DMul,
                "/": DDiv,
                "%": DRem,
            }

            instr_cls = op_map[expr.op]
            db.emit(instr_cls(dst, lhs, rhs))
            return

        # Call (Eta-2 scaffolding)
        if isinstance(expr, Call):
            return_type = expr.return_type
            if return_type is None:
                if dst is not None:
                    raise RuntimeError(
                        "Void call cannot assign to a destination"
                    )
                db.emit(
                    DInvoke(
                        method=expr.func_name,
                        args=[self._as_dvalue(a, db) for a in expr.args],
                        dst=None,
                        return_type=None,
                        arg_types=expr.arg_types,
                        invoke_kind=expr.invoke_kind,
                        owner=expr.owner,
                    )
                )
                return
            if dst is None:
                raise RuntimeError(
                    "Non-void call must assign to a destination"
                )
            if return_type == AnaliType.UNKNOWN:
                raise RuntimeError(
                    "Call return type is UNKNOWN; Eta-2 requires typed calls."
                )

            args = [self._as_dvalue(a, db) for a in expr.args]

            def _infer_arg_type(dval):
                if not hasattr(dval, "ssa"):
                    return AnaliType.UNKNOWN
                ssa = dval.ssa
                if isinstance(ssa, SSAValue):
                    return ssa.type
                if isinstance(ssa, Const):
                    v = ssa.value
                    if isinstance(v, bool):
                        return AnaliType.BOOL
                    if isinstance(v, int):
                        return AnaliType.INT
                    if isinstance(v, float):
                        return AnaliType.FLOAT
                return AnaliType.UNKNOWN

            if expr.arg_types is None:
                arg_types = [_infer_arg_type(a) for a in args]
            else:
                arg_types = expr.arg_types

            for t in arg_types:
                if t == AnaliType.UNKNOWN:
                    raise RuntimeError(
                        "Call arg type UNKNOWN; Eta-2 requires typed calls."
                    )

            db.emit(
                DInvoke(
                    method=expr.func_name,
                    args=args,
                    dst=dst,
                    return_type=return_type,
                    arg_types=arg_types,
                    invoke_kind=expr.invoke_kind,
                    owner=expr.owner,
                )
            )
            return

        # New instance (constructor)
        if isinstance(expr, New):
            if dst is None:
                raise RuntimeError("New must be assigned to a destination")
            db.emit(DNew(dst, expr.class_desc))
            ctor_args = [dst]
            ctor_args.extend(self._as_dvalue(a, db) for a in expr.args)
            db.emit(
                DInvoke(
                    method="<init>",
                    args=ctor_args,
                    dst=None,
                    return_type=None,
                    arg_types=expr.arg_types,
                    invoke_kind="direct",
                    owner=expr.class_desc,
                )
            )
            return

        # Symbolic move (x = y)
        if dst is None:
            raise RuntimeError("Move must be assigned to a destination")
        db.emit(DMove(dst, DValue(expr)))
