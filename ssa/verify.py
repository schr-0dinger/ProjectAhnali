# ssa/verify.py

from ssa.value import SSAValue

class SSAVerificationError(RuntimeError):
    pass


def verify_ssa(cfg, ssa_blocks, dominators):
    """
    Verify SSA invariants.

    This is a skeleton: called after SSA renaming exists.
    """

    _verify_single_definition(ssa_blocks)
    _verify_uses_dominated(ssa_blocks, dominators)
    _verify_phi_legality(ssa_blocks)


def _verify_single_definition(ssa_blocks):
    seen = set()

    for block in ssa_blocks.values():
        for phi in block.phis:
            if phi.target in seen:
                raise SSAVerificationError(
                    f"Multiple definitions of {phi.target}"
                )
            seen.add(phi.target)

        for stmt in block.statements:
            if hasattr(stmt, "defines"):
                val = stmt.defines()
                if val in seen:
                    raise SSAVerificationError(
                        f"Multiple definitions of {val}"
                    )
                seen.add(val)


def _verify_uses_dominated(ssa_blocks, dominators):
    for block in ssa_blocks.values():
        for stmt in block.statements:
            for used in stmt.uses():
                val = used.name

                # Ignore literals / non-SSA values
                if not isinstance(val, SSAValue):
                    continue

                def_block = val.def_block
                if def_block not in dominators[block.cfg_block]:
                    raise SSAVerificationError(
                        f"Use of {val} not dominated by its definition"
                    )


def _verify_phi_legality(ssa_blocks):
    for block in ssa_blocks.values():
        preds = set(block.cfg_block.predecessors)

        for phi in block.phis:
            incoming = set(phi.incoming.keys())

            if preds != incoming:
                raise SSAVerificationError(
                    f"Phi in block {block.cfg_block.id} "
                    f"has mismatched predecessors"
                )

            if len(preds) < 2:
                raise SSAVerificationError(
                    f"Illegal Phi in block {block.cfg_block.id} "
                    f"with <2 predecessors"
                )
