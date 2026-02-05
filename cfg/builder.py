# cfg/builder.py

from cfg.graph import ControlFlowGraph
from cfg.validate import validate_cfg
from tests.ir_stub import Assign, If, While, TryCatch as StubTryCatch
from ir.stmt import Return, TryCatch as IRTryCatch
from ir.expr import Compare, Call, Const, Var
from ir.stmt import Return


class Terminator:
    def __init__(self, kind, **kwargs):
        self.kind = kind
        self.__dict__.update(kwargs)


class CFGBuilder:
    def __init__(self):
        self.cfg = ControlFlowGraph()

    def build(self, block_ir):
        entry = self.cfg.new_block()
        exit = self.cfg.new_block()

        self.cfg.set_entry(entry)
        self.cfg.set_exit(exit)

        self._lower_block(block_ir, entry)

        for block in self.cfg.blocks.values():
            if block is exit:
                continue
            if block.terminator is None:
                self._jump(block, exit)

        if exit.terminator is None:
            exit.terminator = Terminator("return")

        validate_cfg(self.cfg)
        return self.cfg

    def _lower_block(self, stmts, current):
        for stmt in stmts:
            if isinstance(stmt, Assign):
                current.statements.append(stmt)

            elif isinstance(stmt, Return):
                current.statements.append(stmt)
                current.terminator = stmt
                return current

            elif hasattr(stmt, "expr") and isinstance(stmt.expr, Call):
                current.statements.append(stmt)

            elif isinstance(stmt, If):
                current = self._lower_if(stmt, current)

            elif isinstance(stmt, While):
                current = self._lower_while(stmt, current)

            elif isinstance(stmt, (StubTryCatch, IRTryCatch)):
                current = self._lower_try(stmt, current)

            else:
                raise TypeError(f"Unsupported IR node: {stmt}")

        return current

    def _lower_try(self, stmt, current):
        if not stmt.try_body:
            raise RuntimeError("Try block cannot be empty")
        if stmt.exception_type is not None:
            exc = stmt.exception_type
            if not (isinstance(exc, str) and exc.startswith("L") and exc.endswith(";")):
                raise RuntimeError("Exception type must be a Smali class descriptor")

        try_entry = self.cfg.new_block()
        handler_entry = self.cfg.new_block()
        merge = self.cfg.new_block()

        self._jump(current, try_entry)

        before_try = set(self.cfg.blocks.values())
        try_end = self._lower_block(stmt.try_body, try_entry)
        after_try = set(self.cfg.blocks.values())
        try_blocks = {try_entry} | (after_try - before_try)

        if try_end.terminator is None:
            self._jump(try_end, merge)

        handler_end = self._lower_block(stmt.except_body, handler_entry)
        if handler_end.terminator is None:
            self._jump(handler_end, merge)

        for b in try_blocks:
            b.add_exceptional_successor(handler_entry)

        # Record try region (start, end, handler, exception_type)
        self.cfg.try_regions.append(
            (try_entry, try_end, handler_entry, stmt.exception_type)
        )

        return merge

    def _normalize_condition(self, cond):
        # Accept Compare directly
        if isinstance(cond, Compare):
            return cond

        # Legacy DSL: If("x") → Compare("!=", Var("x"), 0)
        if isinstance(cond, str):
            return Compare("!=", Var(cond), Const(0))

        # Reject Var and everything else
        raise TypeError(
            f"If condition must be Compare or str, got {type(cond).__name__}"
        )

    def _lower_if(self, stmt, current):
        cond = self._normalize_condition(stmt.cond)

        then_entry = self.cfg.new_block()
        else_entry = self.cfg.new_block()
        merge = self.cfg.new_block()

        current.terminator = Terminator(
            "branch",
            cond=cond,
            true=then_entry,
            false=else_entry,
        )

        current.add_successor(then_entry)
        current.add_successor(else_entry)

        then_end = self._lower_block(stmt.then, then_entry)
        if then_end.terminator is None:
            self._jump(then_end, merge)

        else_end = self._lower_block(stmt.else_, else_entry)
        if else_end.terminator is None:
            self._jump(else_end, merge)

        return merge

    def _lower_while(self, stmt, current):
        cond = self._normalize_condition(stmt.cond)

        cond_block = self.cfg.new_block()
        body = self.cfg.new_block()
        exit = self.cfg.new_block()

        self._jump(current, cond_block)

        cond_block.terminator = Terminator(
            "branch",
            cond=cond,
            true=body,
            false=exit,
        )

        cond_block.add_successor(body)
        cond_block.add_successor(exit)

        body_end = self._lower_block(stmt.body, body)
        self._jump(body_end, cond_block)

        return exit

    def _jump(self, src, dst):
        src.terminator = Terminator("jump", target=dst)
        src.add_successor(dst)
