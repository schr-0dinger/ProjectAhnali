# cfg/builder.py

from cfg.graph import ControlFlowGraph
from cfg.validate import validate_cfg
from tests.ir_stub import Assign, If, While


class Terminator:
    def __init__(self, kind, **kwargs):
        self.kind = kind
        self.__dict__.update(kwargs)


class CFGBuilder:
    def __init__(self):
        self.cfg = ControlFlowGraph()

    def build(self, block_ir):
        """
        Build CFG from structured frontend IR block.
        """
        entry = self.cfg.new_block()
        exit = self.cfg.new_block()

        self.cfg.set_entry(entry)
        self.cfg.set_exit(exit)

        end = self._lower_block(block_ir, entry)

        # 1. Ensure all NON-exit blocks are terminated
        for block in self.cfg.blocks.values():
            if block is exit:
                continue
            if block.terminator is None:
                self._jump(block, exit)

        # 2. Exit block must terminate with return
        if exit.terminator is None:
            exit.terminator = Terminator("return")

        validate_cfg(self.cfg)
        return self.cfg


    # -------------------------------
    # Internal lowering helpers
    # -------------------------------

    def _lower_block(self, stmts, current):
        for stmt in stmts:
            if isinstance(stmt, Assign):
                current.statements.append(stmt)

            elif isinstance(stmt, If):
                current = self._lower_if(stmt, current)

            elif isinstance(stmt, While):
                current = self._lower_while(stmt, current)

            else:
                raise TypeError(f"Unsupported IR node: {stmt}")

        return current

    def _lower_if(self, stmt, current):
        then_entry = self.cfg.new_block()
        else_entry = self.cfg.new_block()
        merge = self.cfg.new_block()

        if not isinstance(stmt.cond, str):
            raise TypeError("Condition must be a variable name (defined before the branch)")

        current.terminator = Terminator(
            "branch",
            cond=stmt.cond,
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
        cond_block = self.cfg.new_block()
        body = self.cfg.new_block()
        exit = self.cfg.new_block()

        if not isinstance(stmt.cond, str):
            raise TypeError("Condition must be a variable name (SSA-backed)")

        self._jump(current, cond_block)

        cond_block.terminator = Terminator(
            "branch",
            cond=stmt.cond,
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
