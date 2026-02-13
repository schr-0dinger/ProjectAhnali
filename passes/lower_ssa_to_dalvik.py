# passes/lower_ssa_to_dalvik.py

from dalvik.block import DalvikBlock
from dalvik.ir import (
    DValue,
    DConst,
    DMove,
    DMoveWide,
    DSpillLoad,
    DSpillStore,
    DIf,
    DIfZ,
    DGoto,
    DReturnVoid,
    DReturn,
    DInvoke,
    DThrow,
    DNew,
    DStaticGet,
    DStaticPut,
    DInstanceGet,
    DInstancePut,
    DArrayGet,
    DArrayPut,
    DCheckCast,
    DPrimitiveCast,
    DNewArray,
    DInstanceOf,
    DArrayLength,
    DFilledNewArray,
    DCompare,
)
from ir.expr import (
    Compare,
    BinaryOp,
    Const,
    Var,
    Call,
    New,
    NewArray,
    PrimitiveCast,
    StaticFieldGet,
    FieldGet,
    ArrayGet,
    ArrayLength,
    CheckCast,
    InstanceOf,
    FilledNewArray,
)
from ir.stmt import StaticFieldSet, FieldSet, ArraySet, CallStmt
from ir.types import AnaliType
from dalvik.ir import DAdd, DSub, DMul, DDiv, DRem, DAnd, DOr, DXor, DShl, DShr, DUshr


# passes/lower_ssa_to_dalvik.py

from ssa.value import SSAValue
from passes.ignored_return import allow_ignored_return


def _is_wide_ssa(ssa):
    t = getattr(ssa, "type", None)
    return t in ("J", "D")


def apply_spills(dalvik_blocks, intervals):
    spill_map = {i.value: i for i in intervals if i.spilled}

    for block in dalvik_blocks.values():
        new_instrs = []

        for instr in block.instructions:
            # ---- reload before uses ----
            for field in ("src", "lhs", "rhs", "cond", "value", "obj", "array", "index"):
                if hasattr(instr, field):
                    d = getattr(instr, field)
                    if d and hasattr(d, "ssa") and d.ssa in spill_map:
                        slot = spill_map[d.ssa].stack_slot
                        spill_val = DValue(d.ssa)
                        spill_val.reg = slot
                        tmp = DValue(d.ssa)
                        if _is_wide_ssa(d.ssa):
                            new_instrs.append(DSpillLoad(tmp, spill_val))
                        else:
                            new_instrs.append(DSpillLoad(tmp, spill_val))
                        setattr(instr, field, tmp)

            if hasattr(instr, "args"):
                new_args = []
                for d in instr.args:
                    if d and d.ssa in spill_map:
                        slot = spill_map[d.ssa].stack_slot
                        spill_val = DValue(d.ssa)
                        spill_val.reg = slot
                        tmp = DValue(d.ssa)
                        new_instrs.append(DSpillLoad(tmp, spill_val))
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
                new_instrs.append(DSpillStore(spill_val, instr.dst))

        block.instructions = new_instrs


def _apply_registers(dalvik_blocks, intervals):
    regmap = {i.value: i.reg for i in intervals}
    spill_slots = {i.value: i.stack_slot for i in intervals if i.spilled}

    for block in dalvik_blocks.values():
        for instr in block.instructions:
            for attr in ("dst", "src", "lhs", "rhs", "cond", "value", "obj", "array", "index"):
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
        self._tmp_idx = 0

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

    def _new_temp(self, *, prefix="tmp", typ=AnaliType.INT):
        v = SSAValue(prefix, self._tmp_idx)
        self._tmp_idx += 1
        v.type = typ
        return v

    def _value_type(self, value):
        if isinstance(value, Const):
            if isinstance(value.value, bool):
                return AnaliType.BOOL
            if isinstance(value.value, int):
                return AnaliType.INT
            if isinstance(value.value, float):
                return AnaliType.FLOAT
            if isinstance(value.value, str):
                return AnaliType.STRING
            return None
        if isinstance(value, SSAValue):
            return value.type
        return None

    def _is_ref_type(self, t):
        if t in (AnaliType.OBJECT, AnaliType.STRING):
            return True
        if isinstance(t, str) and (t.startswith("L") or t.startswith("[")):
            return True
        return False

    def _normalize_prim_type(self, t):
        if t in (AnaliType.INT, AnaliType.BOOL):
            return "I"
        if t == AnaliType.FLOAT:
            return "F"
        if t in ("I", "J", "F", "D"):
            return t
        return None

    def _is_wide_value(self, value):
        t = getattr(value, "type", None)
        return t in ("J", "D")

    def _emit_move(self, db, dst, src):
        if self._is_wide_value(dst.ssa):
            db.emit(DMoveWide(dst, src))
        else:
            db.emit(DMove(dst, src))



    def _lower_block(self, cfg_block, ssa_block):
        db = self.blocks[cfg_block]

        # --- Lower SSA statements ---
        for stmt in ssa_block.statements:
            self._lower_stmt(stmt, db)

        # --- Phi elimination (edge moves) ---
        for succ in cfg_block.successors:
            succ_ssa = self.ssa_blocks.get(succ)
            if not succ_ssa:
                continue

            for phi in succ_ssa.phis:
                src = phi.incoming[cfg_block]
                dst = phi.target
                if isinstance(src, SSAValue) and getattr(src, "is_undef", False):
                    db.emit(DConst(DValue(dst), 0))
                    continue
                if isinstance(src, Const):
                    if self._is_wide_value(dst):
                        db.emit(DConstWide(DValue(dst), src.value))
                    else:
                        db.emit(DConst(DValue(dst), src.value))
                elif isinstance(src, (int, float, bool)):
                    if self._is_wide_value(dst):
                        db.emit(DConstWide(DValue(dst), src))
                    else:
                        db.emit(DConst(DValue(dst), src))
                else:
                    self._emit_move(db, DValue(dst), DValue(src))

        # --- Terminator ---
        term = cfg_block.terminator
        kind = term.kind

        if kind == "branch":
            if isinstance(term.cond, Compare):
                lhs = self._as_dvalue(term.cond.left, db)
                rhs = self._as_dvalue(term.cond.right, db)
                left_t = self._value_type(term.cond.left)
                right_t = self._value_type(term.cond.right)

                if self._is_ref_type(left_t) or self._is_ref_type(right_t):
                    if term.cond.op not in ("==", "!="):
                        raise RuntimeError("Reference compare only supports == or !=")
                    db.emit(
                        DIf(
                            cmp=(term.cond.op, lhs, rhs),
                            true_block=term.true,
                            false_block=term.false,
                        )
                    )
                else:
                    prim_left = self._normalize_prim_type(left_t)
                    prim_right = self._normalize_prim_type(right_t)
                    prim = prim_left or prim_right or "I"

                    if prim in ("J", "F", "D"):
                        cmp_kind = {
                            "J": "long",
                            "F": "float",
                            "D": "double",
                        }[prim]
                        if term.cond.op in ("<", "<="):
                            nan_mode = "cmpg"
                        elif term.cond.op in (">", ">="):
                            nan_mode = "cmpl"
                        elif term.cond.op == "==":
                            nan_mode = "cmpl"
                        else:
                            nan_mode = "cmpg"
                        tmp = self._new_temp(prefix="cmp", typ=AnaliType.INT)
                        db.emit(
                            DCompare(
                                DValue(tmp),
                                lhs,
                                rhs,
                                cmp_kind=cmp_kind,
                                nan_mode=nan_mode if cmp_kind in ("float", "double") else None,
                            )
                        )
                        z_op = {
                            "<": "ltz",
                            "<=": "lez",
                            ">": "gtz",
                            ">=": "gez",
                            "==": "eqz",
                            "!=": "nez",
                        }[term.cond.op]
                        db.emit(
                            DIfZ(
                                cond=DValue(tmp),
                                op=z_op,
                                true_block=term.true,
                                false_block=term.false,
                            )
                        )
                    else:
                        db.emit(
                            DIf(
                                cmp=(term.cond.op, lhs, rhs),
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
        if isinstance(stmt, StaticFieldSet):
            db.emit(
                DStaticPut(
                    self._as_dvalue(stmt.value, db),
                    stmt.owner,
                    stmt.name,
                    stmt.desc,
                )
            )
            return
        if isinstance(stmt, FieldSet):
            db.emit(
                DInstancePut(
                    self._as_dvalue(stmt.obj, db),
                    self._as_dvalue(stmt.value, db),
                    stmt.owner,
                    stmt.name,
                    stmt.desc,
                )
            )
            return
        if isinstance(stmt, ArraySet):
            db.emit(
                DArrayPut(
                    self._as_dvalue(stmt.array, db),
                    self._as_dvalue(stmt.index, db),
                    stmt.elem_desc,
                    self._as_dvalue(stmt.value, db),
                )
            )
            return

        defines = stmt.defines() if hasattr(stmt, "defines") else None
        dst = DValue(defines) if defines is not None else None

        expr = getattr(stmt, "expr", None)

        if expr is None:
            return

        # Literal / Const
        if isinstance(expr, int):
            if dst is None:
                raise RuntimeError("Literal must be assigned to a destination")
            if self._is_wide_value(dst.ssa):
                db.emit(DConstWide(dst, expr))
            else:
                db.emit(DConst(dst, expr))
            return

        if isinstance(expr, Const):
            if dst is None:
                raise RuntimeError("Const must be assigned to a destination")
            if self._is_wide_value(dst.ssa):
                db.emit(DConstWide(dst, expr.value))
            else:
                db.emit(DConst(dst, expr.value))
            return

        # Binary arithmetic
        if isinstance(expr, BinaryOp):
            if dst is None:
                raise RuntimeError("BinaryOp must be assigned to a destination")

            expr_type = stmt.defines().type

            if expr_type in (AnaliType.INT, AnaliType.BOOL):
                type_desc = "I"
            elif expr_type == AnaliType.FLOAT:
                type_desc = "F"
            elif expr_type in ("J", "D"):
                type_desc = expr_type
            elif expr_type in ("I", "F"):
                type_desc = expr_type
            else:
                raise RuntimeError(f"Cannot perform arithmetic on type {expr_type}")

            lhs = self._as_dvalue(expr.left, db)
            rhs = self._as_dvalue(expr.right, db)

            arith_ops = {"+", "-", "*", "/", "%"}
            bitwise_ops = {"&", "|", "^"}
            shift_ops = {"<<", ">>", ">>>"}

            if expr.op in arith_ops and type_desc not in {"I", "J", "F", "D"}:
                raise RuntimeError(f"Operator {expr.op} does not support type {expr_type}")
            if expr.op in bitwise_ops and type_desc not in {"I", "J"}:
                raise RuntimeError(f"Operator {expr.op} does not support type {expr_type}")
            if expr.op in shift_ops:
                if type_desc not in {"I", "J"}:
                    raise RuntimeError(f"Operator {expr.op} does not support type {expr_type}")
                rhs_type = self._value_type(expr.right)
                if rhs_type not in (AnaliType.INT, AnaliType.BOOL, "I", "B", "C", "S"):
                    raise RuntimeError(
                        f"Shift rhs must be int-like for {expr.op}, got {rhs_type}"
                    )

            op_map = {
                "+": DAdd,
                "-": DSub,
                "*": DMul,
                "/": DDiv,
                "%": DRem,
                "&": DAnd,
                "|": DOr,
                "^": DXor,
                "<<": DShl,
                ">>": DShr,
                ">>>": DUshr,
            }

            instr_cls = op_map.get(expr.op)
            if instr_cls is None:
                raise RuntimeError(f"Unsupported binary operator {expr.op}")
            db.emit(instr_cls(dst, lhs, rhs, type_desc=type_desc))
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
                if isinstance(stmt, CallStmt) and allow_ignored_return(expr):
                    db.emit(
                        DInvoke(
                            method=expr.func_name,
                            args=[self._as_dvalue(a, db) for a in expr.args],
                            dst=None,
                            return_type=return_type,
                            arg_types=expr.arg_types,
                            invoke_kind=expr.invoke_kind,
                            owner=expr.owner,
                        )
                    )
                    return
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
                    if isinstance(v, str):
                        return AnaliType.STRING
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
        if isinstance(expr, NewArray):
            if dst is None:
                raise RuntimeError("NewArray must be assigned to a destination")
            db.emit(
                DNewArray(
                    dst,
                    self._as_dvalue(expr.length, db),
                    expr.array_desc,
                )
            )
            return

        # Static field get
        if isinstance(expr, StaticFieldGet):
            if dst is None:
                raise RuntimeError("StaticFieldGet must be assigned to a destination")
            db.emit(DStaticGet(dst, expr.owner, expr.name, expr.desc))
            return
        if isinstance(expr, FieldGet):
            if dst is None:
                raise RuntimeError("FieldGet must be assigned to a destination")
            db.emit(
                DInstanceGet(
                    dst,
                    self._as_dvalue(expr.obj, db),
                    expr.owner,
                    expr.name,
                    expr.desc,
                )
            )
            return
        if isinstance(expr, ArrayGet):
            if dst is None:
                raise RuntimeError("ArrayGet must be assigned to a destination")
            db.emit(
                DArrayGet(
                    dst,
                    self._as_dvalue(expr.array, db),
                    self._as_dvalue(expr.index, db),
                    expr.elem_desc,
                )
            )
            return
        if isinstance(expr, ArrayLength):
            if dst is None:
                raise RuntimeError("ArrayLength must be assigned to a destination")
            db.emit(
                DArrayLength(
                    dst,
                    self._as_dvalue(expr.array, db),
                )
            )
            return
        if isinstance(expr, CheckCast):
            if dst is None:
                raise RuntimeError("CheckCast must be assigned to a destination")
            # emit move + check-cast on the same reg
            self._emit_move(db, dst, self._as_dvalue(expr.value, db))
            db.emit(DCheckCast(dst, expr.desc))
            return
        if isinstance(expr, InstanceOf):
            if dst is None:
                raise RuntimeError("InstanceOf must be assigned to a destination")
            db.emit(
                DInstanceOf(
                    dst,
                    self._as_dvalue(expr.value, db),
                    expr.desc,
                )
            )
            return
        if isinstance(expr, PrimitiveCast):
            if dst is None:
                raise RuntimeError("PrimitiveCast must be assigned to a destination")
            db.emit(
                DPrimitiveCast(
                    dst,
                    self._as_dvalue(expr.value, db),
                    expr.from_desc,
                    expr.to_desc,
                )
            )
            return
        if isinstance(expr, FilledNewArray):
            if dst is None:
                raise RuntimeError("FilledNewArray must be assigned to a destination")
            args = [self._as_dvalue(a, db) for a in expr.args]
            db.emit(
                DFilledNewArray(
                    dst,
                    args,
                    expr.array_desc,
                )
            )
            return

        # Symbolic move (x = y)
        if dst is None:
            raise RuntimeError("Move must be assigned to a destination")
        self._emit_move(db, dst, DValue(expr))
