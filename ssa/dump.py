# ssa/dump.py

def dump_ssa(ssa_blocks):
    lines = []

    for cfg_block, ssa in ssa_blocks.items():
        lines.append(f"\nB{cfg_block.id}:")

        for phi in ssa.phis:
            incoming = ", ".join(
                f"B{b.id}:{v}" for b, v in phi.incoming.items()
            )
            lines.append(f"  {phi.target} = phi({incoming})")

        for stmt in ssa.statements:
            lines.append(f"  {stmt}")

    return "\n".join(lines)
