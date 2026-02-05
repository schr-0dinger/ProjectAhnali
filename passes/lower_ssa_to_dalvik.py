# passes/lower_ssa_to_dalvik.py

from dalvik.block import DalvikBlock
from dalvik.ir import (
    DValue,
    DConst,
    DMove,
    DIf,
    DGoto,
    DReturnVoid,
)
from ir.expr import Compare, BinaryOp, Const, Var
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
            for field in ("src", "lhs", "rhs", "cond"):
                if hasattr(instr, field):
                    d = getattr(instr, field)
                    if d and d.ssa in spill_map:
                        slot = spill_map[d.ssa].stack_slot
                        spill_val = DValue(d.ssa)
                        spill_val.reg = slot
                        tmp = DValue(d.ssa)
                        new_instrs.append(DMove(tmp, spill_val))
                        setattr(instr, field, tmp)

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

    for block in dalvik_blocks.values():
        for instr in block.instructions:
            for attr in ("dst", "src", "lhs", "rhs", "cond"):
                if hasattr(instr, attr):
                    d = getattr(instr, attr)
                    if d and d.ssa in regmap:
                        d.reg = regmap[d.ssa]


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
            db.emit(DReturnVoid())

        else:
            raise RuntimeError(f"Unknown terminator {kind}")

    def _lower_stmt(self, stmt, db):
        """
        Delta-2 lowering:
        - literals
        - moves
        - binary arithmetic
        """
        dst = DValue(stmt.defines())

        expr = stmt.expr

        if expr is None:
            return

        # Literal
        if isinstance(expr, int):
            db.emit(DConst(dst, expr))
            return

        # Binary arithmetic
        if isinstance(expr, BinaryOp):

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

        # Symbolic move (x = y)
        db.emit(DMove(dst, DValue(expr)))
