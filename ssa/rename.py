# ssa/rename.py

from collections import defaultdict
from typing import Optional
from ssa.value import SSAValue
from ir.expr import (
    Compare,
    Var,
    Call,
    BinaryOp,
    New,
    NewArray,
    PrimitiveCast,
    StaticFieldGet,
    FieldGet,
    ArrayGet,
    CheckCast,
)
from ir.stmt import StaticFieldSet, FieldSet, ArraySet


class SSARenamer:
    def __init__(self, cfg, dom_tree, phi_nodes, params=None, param_types=None):
        self.cfg = cfg
        self.dom_tree = dom_tree
        self.phi_nodes = phi_nodes
        self.params = params or []
        self.param_types = param_types or []
        self.param_ssa = []

        self.stacks = defaultdict(list)
        self.counters = defaultdict(int)
        self.ssa_blocks = {}

    def run(self):
        self._seed_params()
        self._rename_block(self.cfg.entry)
        return self.ssa_blocks

    def _seed_params(self):
        if not self.params:
            return
        if self.param_types and len(self.param_types) != len(self.params):
            raise RuntimeError("param_types length must match params length")

        for idx, name in enumerate(self.params):
            version = self._new_version(name)
            val = SSAValue(name, version)
            val.def_block = self.cfg.entry
            if self.param_types:
                val.type = self.param_types[idx]
            self.stacks[name].append(val)
            self.param_ssa.append(val)

    def _rename_block(self, block):
        ssa_block = self._get_ssa_block(block)
        pushed = []

        # Phi targets
        for phi in self.phi_nodes.get(block, []):
            name = phi.target.name
            version = self._new_version(name)
            val = SSAValue(name, version)
            val.def_block = block
            phi.target = val
            self.stacks[name].append(val)
            pushed.append(name)
            ssa_block.phis.append(phi)

        # Statements
        for stmt in block.statements:
            # Rename uses
            for var in stmt.uses():
                if isinstance(var, SSAValue):
                    continue
                name = self._resolve_name(var)
                if name is None:
                    continue
                if hasattr(var, "replace_with"):
                    var.replace_with(self._current(name))

            # Normalize bare string expressions
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, str):
                stmt.expr = self._current(expr)
                expr = stmt.expr

            if isinstance(expr, Call):
                expr.args = [self._rename_expr(a) for a in expr.args]

            elif isinstance(expr, BinaryOp):
                expr.left = self._rename_expr(expr.left)
                expr.right = self._rename_expr(expr.right)
            elif isinstance(expr, New):
                expr.args = [self._rename_expr(a) for a in expr.args]
            elif isinstance(expr, NewArray):
                expr.length = self._rename_expr(expr.length)
            elif isinstance(expr, PrimitiveCast):
                expr.value = self._rename_expr(expr.value)
            elif isinstance(expr, StaticFieldGet):
                pass
            elif isinstance(expr, FieldGet):
                expr.obj = self._rename_expr(expr.obj)
            elif isinstance(expr, ArrayGet):
                expr.array = self._rename_expr(expr.array)
                expr.index = self._rename_expr(expr.index)
            elif isinstance(expr, CheckCast):
                expr.value = self._rename_expr(expr.value)

            if isinstance(stmt, StaticFieldSet):
                stmt.value = self._rename_expr(stmt.value)
            if isinstance(stmt, FieldSet):
                stmt.obj = self._rename_expr(stmt.obj)
                stmt.value = self._rename_expr(stmt.value)
            if isinstance(stmt, ArraySet):
                stmt.array = self._rename_expr(stmt.array)
                stmt.index = self._rename_expr(stmt.index)
                stmt.value = self._rename_expr(stmt.value)

            # Rename definitions
            defines = stmt.defines() if hasattr(stmt, "defines") else None
            if defines:
                name = self._resolve_name(defines)
                version = self._new_version(name)
                val = SSAValue(name, version)
                val.def_block = block
                stmt.replace_def(val)
                self.stacks[name].append(val)
                pushed.append(name)

            ssa_block.statements.append(stmt)

        # Terminator
        term = block.terminator
        if term and term.kind == "branch":
            if isinstance(term.cond, str):
                term.cond = self._current(term.cond)

            elif isinstance(term.cond, Compare):
                term.cond.left = self._rename_expr(term.cond.left)
                term.cond.right = self._rename_expr(term.cond.right)

        # Phi incoming edges
        for succ in block.successors:
            for phi in self.phi_nodes.get(succ, []):
                name = phi.target.name
                if self.stacks[name]:
                    val = self._current(name)
                else:
                    # Undefined along this edge → phi undef
                    val = SSAValue.undef(name)
                phi.add_incoming(block, val)

        # Recurse
        for child in self.dom_tree.get(block, []):
            self._rename_block(child)

        # Pop stack
        for name in reversed(pushed):
            self.stacks[name].pop()

    def _rename_expr(self, expr):
        if isinstance(expr, SSAValue):
            return expr
        name = self._resolve_name(expr)
        if name is not None:
            return self._current(name)
        return expr


    def _new_version(self, name):
        v = self.counters[name]
        self.counters[name] += 1
        return v

    def _current(self, name):
        if not self.stacks[name]:
            raise RuntimeError(f"Use of undefined variable '{name}'")
        return self.stacks[name][-1]



    def _get_ssa_block(self, block):
        if block not in self.ssa_blocks:
            from ssa.block import SSABlock
            self.ssa_blocks[block] = SSABlock(block)
        return self.ssa_blocks[block]

    def _resolve_name(self, obj) -> Optional[str]:
        if isinstance(obj, SSAValue):
            return obj.name
        if isinstance(obj, str):
            return obj
        if isinstance(obj, Var):
            return obj.name
        if hasattr(obj, "name") and not isinstance(
            obj,
            (StaticFieldGet, FieldGet, ArrayGet, CheckCast, NewArray, PrimitiveCast),
        ):
            return obj.name
        return None
