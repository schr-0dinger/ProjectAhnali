# passes/cfg_simplify.py

from dalvik.ir import DGoto


def simplify_cfg(cfg, dalvik_blocks):
    """
    Epsilon-3: control-flow simplification after DCE.

    Rules (safe, conservative):
    - Remove empty blocks with a single successor.
    - Do not remove entry/exit or blocks participating in try regions.
    - Do not cross exceptional edges.
    """
    protected = {cfg.entry, cfg.exit}
    for start, end, handler, _ in getattr(cfg, "try_regions", []):
        protected.update({start, end, handler})

    exceptional_preds = {b: set() for b in cfg.blocks.values()}
    for b in cfg.blocks.values():
        for succ in b.exceptional_successors:
            exceptional_preds[succ].add(b)

    def _remove_block(block):
        # Remove from cfg.blocks (keyed by id)
        for k, v in list(cfg.blocks.items()):
            if v is block:
                del cfg.blocks[k]
                break
        if block in dalvik_blocks:
            del dalvik_blocks[block]

    changed = True
    while changed:
        changed = False

        # Redundant goto elimination: remove blocks that only jump to their sole successor
        for block in list(cfg.blocks.values()):
            if block in protected:
                continue
            if exceptional_preds.get(block):
                continue
            if len(block.successors) != 1:
                continue
            if block.terminator is None or block.terminator.kind != "jump":
                continue
            dblock = dalvik_blocks.get(block)
            if dblock is None:
                continue
            if len(dblock.instructions) != 1 or not isinstance(dblock.instructions[0], DGoto):
                continue

            succ = next(iter(block.successors))
            for pred in list(block.predecessors):
                if block in pred.successors:
                    pred.successors.remove(block)
                pred.successors.add(succ)
                succ.predecessors.add(pred)

                term = pred.terminator
                if term and term.kind == "jump" and getattr(term, "target", None) is block:
                    term.target = succ
                elif term and term.kind == "branch":
                    if getattr(term, "true", None) is block:
                        term.true = succ
                    if getattr(term, "false", None) is block:
                        term.false = succ

            if block in succ.predecessors:
                succ.predecessors.remove(block)

            _remove_block(block)
            changed = True
            break

        # Block merging: merge block into its single predecessor when safe
        for block in list(cfg.blocks.values()):
            if block in protected:
                continue
            if exceptional_preds.get(block):
                continue
            if len(block.predecessors) != 1:
                continue
            pred = next(iter(block.predecessors))
            if pred in protected:
                continue
            if exceptional_preds.get(pred):
                continue
            if len(pred.successors) != 1:
                continue
            if block not in pred.successors:
                continue

            pred_db = dalvik_blocks.get(pred)
            block_db = dalvik_blocks.get(block)
            if pred_db is None or block_db is None:
                continue

            # Only merge if pred ends with a jump to block
            if pred.terminator is None or pred.terminator.kind != "jump":
                continue
            if pred.terminator.target is not block:
                continue

            # Remove the trailing goto and append block instructions
            if pred_db.instructions and isinstance(pred_db.instructions[-1], DGoto):
                pred_db.instructions.pop()

            pred_db.instructions.extend(block_db.instructions)

            # Rewire preds/terminator to block's successor/terminator
            pred.terminator = block.terminator
            pred.successors = set(block.successors)
            for succ in block.successors:
                if block in succ.predecessors:
                    succ.predecessors.remove(block)
                succ.predecessors.add(pred)

            _remove_block(block)
            changed = True
            break

        for block in list(cfg.blocks.values()):
            if block in protected:
                continue
            if exceptional_preds.get(block):
                continue
            if len(block.successors) != 1:
                continue
            dblock = dalvik_blocks.get(block)
            if dblock is None:
                continue
            if dblock.instructions:
                # If only a single DGoto remains, treat as empty
                if not (len(dblock.instructions) == 1 and isinstance(dblock.instructions[0], DGoto)):
                    continue

            succ = next(iter(block.successors))

            # Redirect normal predecessors to successor
            for pred in list(block.predecessors):
                if block in pred.successors:
                    pred.successors.remove(block)
                pred.successors.add(succ)
                succ.predecessors.add(pred)

                term = pred.terminator
                if term and term.kind == "jump" and getattr(term, "target", None) is block:
                    term.target = succ
                elif term and term.kind == "branch":
                    if getattr(term, "true", None) is block:
                        term.true = succ
                    if getattr(term, "false", None) is block:
                        term.false = succ

            if block in succ.predecessors:
                succ.predecessors.remove(block)

            _remove_block(block)
            changed = True
            break

    return cfg, dalvik_blocks
