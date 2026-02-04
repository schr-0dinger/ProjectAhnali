# ssa/rename.py

from collections import defaultdict
from ssa.value import SSAValue
from ir.expr import Compare, Var


class SSARenamer:
    def __init__(self, cfg, dom_tree, phi_nodes):
        """
        Args:
            cfg: ControlFlowGraph
            dom_tree: dict[BasicBlock, list[BasicBlock]]
            phi_nodes: dict[BasicBlock, list[Phi]]
        """
        self.cfg = cfg
        self.dom_tree = dom_tree
        self.phi_nodes = phi_nodes

        self.stacks = defaultdict(list)
        self.counters = defaultdict(int)

        # Result: block -> SSABlock
        self.ssa_blocks = {}

    # -----------------------------
    # Entry point
    # -----------------------------

    def run(self):
        self._rename_block(self.cfg.entry)
        return self.ssa_blocks

    # -----------------------------
    # Core algorithm
    # -----------------------------

    def _rename_block(self, block):
        # Create SSA block wrapper
        ssa_block = self._get_ssa_block(block)

        pushed = []

        # 1. Rename Phi targets
        for phi in self.phi_nodes.get(block, []):
            name = phi.target.name
            version = self._new_version(name)
            val = SSAValue(name, version)
            val.def_block = block
            phi.target = val
            self.stacks[name].append(val)
            pushed.append(name)
            ssa_block.phis.append(phi)

        # 2. Rename statements
        for stmt in block.statements:
            # Rename uses
            for var in stmt.uses():
                var.replace_with(self._current(var.name))

            # Some IR stubs use a bare string for simple moves (e.g. z = "y").
            # Normalize those to SSAValues so later passes see true SSA uses.
            expr = getattr(stmt, "expr", None)
            if isinstance(expr, str):
                stmt.expr = self._current(expr)

            # Rename definitions
            if stmt.defines():
                name = stmt.defines().name
                version = self._new_version(name)
                val = SSAValue(name, version)
                val.def_block = block
                stmt.replace_def(val)
                self.stacks[name].append(val)
                pushed.append(name)

            ssa_block.statements.append(stmt)

        # --- Rename terminator condition (if any) ---
        term = block.terminator
        if term and term.kind == "branch":
            if isinstance(term.cond, str):
                term.cond = self._current(term.cond)

            elif isinstance(term.cond, Compare):
                # Rename variables inside comparison
                def rename(e):
                    if isinstance(e, Var):
                        return self._current(e.name)
                    return e

                term.cond.left = rename(term.cond.left)
                term.cond.right = rename(term.cond.right)

            else:
                raise RuntimeError("Invalid branch condition")


        # 3. Populate Phi incoming edges
        for succ in block.successors:
            for phi in self.phi_nodes.get(succ, []):
                name = phi.target.name
                phi.add_incoming(block, self._current(name))

        # 4. Recurse into dominator tree children
        for child in self.dom_tree.get(block, []):
            self._rename_block(child)

        # 5. Pop stack entries created in this block
        for name in reversed(pushed):
            self.stacks[name].pop()

    # -----------------------------
    # Helpers
    # -----------------------------

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
