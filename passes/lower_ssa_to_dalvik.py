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
from ir.expr import Compare
from ir.expr import BinaryOp
from dalvik.ir import DAdd, DSub, DMul, DDiv, DRem


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
                            DValue(term.cond.left),
                            DValue(term.cond.right),
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
            lhs = DValue(expr.left)
            rhs = DValue(expr.right)

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
