import re

from alpha_pipeline import alpha_pipeline
from tests.ir_stub import Assign, If, TryCatch


LABEL_DEF_RE = re.compile(r"^\s*:B(\d+)\s*$")
LABEL_REF_RE = re.compile(r":B(\d+)")


def _label_defs(smali):
    defs = set()
    for line in smali.splitlines():
        m = LABEL_DEF_RE.match(line)
        if m:
            defs.add(int(m.group(1)))
    return defs


def _label_refs(smali):
    refs = set()
    for line in smali.splitlines():
        if line.strip().startswith((".catch", ".catchall", "if-", "goto")):
            for m in LABEL_REF_RE.findall(line):
                refs.add(int(m))
    return refs


def test_smali_branch_targets_defined_after_cfg_simplify():
    ir = [
        Assign("x", 1),
        If("x", [Assign("y", 1)], [Assign("y", 2)]),
        If("y", [Assign("z", 3)], [Assign("z", 4)]),
        If("z", [], []),
    ]

    smali = alpha_pipeline(ir)["smali"]
    defs = _label_defs(smali)
    refs = _label_refs(smali)

    # All referenced branch targets must still exist after simplification.
    assert refs.issubset(defs)


def test_smali_trycatch_targets_defined_after_block_merging():
    ir = [
        Assign("x", 1),
        TryCatch(
            try_body=[
                If("x", [Assign("a", 1)], [Assign("a", 2)]),
                Assign("b", "a"),
            ],
            except_body=[Assign("e", 3)],
            exception_type="Ljava/lang/Exception;",
        ),
        If("b", [], []),
    ]

    smali = alpha_pipeline(ir)["smali"]
    defs = _label_defs(smali)
    refs = _label_refs(smali)

    assert refs.issubset(defs)
