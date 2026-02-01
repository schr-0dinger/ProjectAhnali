# dalvik/dump.py

def dump_dalvik(dalvik_blocks):
    lines = []

    for block in dalvik_blocks.values():
        lines.append(f"\nB{block.id}:")
        for instr in block.instructions:
            lines.append(f"  {instr}")

    return "\n".join(lines)
