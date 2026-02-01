# ssa/insert_phi.py

from collections import defaultdict
from ssa.phi import Phi
from ssa.value import SSAValue


def insert_phi_nodes(cfg, dominance_frontier, def_blocks):
    """
    Insert Phi nodes using dominance frontier.

    Args:
        cfg: ControlFlowGraph
        dominance_frontier: dict[BasicBlock, set[BasicBlock]]
        def_blocks: dict[str, set[BasicBlock]]
            variable name -> blocks where it is assigned

    Returns:
        dict[BasicBlock, list[Phi]]
    """

    phi_nodes = defaultdict(list)

    for var, blocks in def_blocks.items():
        worklist = list(blocks)
        has_phi = set()

        while worklist:
            b = worklist.pop()

            for y in dominance_frontier[b]:
                if (y, var) in has_phi:
                    continue

                # Create an unversioned Phi target (version assigned later)
                target = SSAValue(var, version=None)
                phi = Phi(target)

                phi_nodes[y].append(phi)
                has_phi.add((y, var))

                # If y does not already define var, it becomes a new def site
                if y not in blocks:
                    worklist.append(y)

    return phi_nodes
