from __future__ import annotations

from dsl.widgets import _UIColumn, _UIConstraint, _UIRelative, _UIRow
from dsl.ast import _StmtSnackbar, _StmtIf, _StmtWhile, _StmtAssign, _StmtSetText, _ExprBinary, _ExprCompare, _ExprBoolOp, _ExprUnary, _ExprFormat


def _walk_items(items, *, need_constraint_flag):
    for item in items:
        if isinstance(item, _UIConstraint):
            need_constraint_flag[0] = True
        if isinstance(item, (_UIRow, _UIColumn, _UIRelative, _UIConstraint)) and getattr(item, "items", None):
            _walk_items(item.items, need_constraint_flag=need_constraint_flag)


def _walk_stmts(stmts, *, need_material_flag):
    for stmt in stmts:
        if isinstance(stmt, _StmtSnackbar):
            need_material_flag[0] = True
        if isinstance(stmt, _StmtIf):
            _walk_stmts(stmt.then or [], need_material_flag=need_material_flag)
            _walk_stmts(stmt.else_ or [], need_material_flag=need_material_flag)
        if isinstance(stmt, _StmtWhile):
            _walk_stmts(stmt.body or [], need_material_flag=need_material_flag)
        if isinstance(stmt, (_StmtAssign, _StmtSetText)):
            continue
        if isinstance(stmt, (_ExprBinary, _ExprCompare, _ExprBoolOp, _ExprUnary, _ExprFormat)):
            continue


def collect_dependency_artifacts(ui_items, click_specs=None):
    """
    Return (required_aars, jar_allowlist) based on the UI tree.

    Extend this mapping as new widgets introduce non-platform deps.
    """
    need_constraint = [False]
    need_material = [False]
    _walk_items(ui_items, need_constraint_flag=need_constraint)
    if click_specs:
        for spec in click_specs:
            _walk_stmts(spec.stmts or [], need_material_flag=need_material)

    required_aars = set()
    jar_allowlist = set()
    if need_constraint[0]:
        required_aars.add("constraintlayout")
        # ConstraintLayout runtime depends on constraintlayout-core + collection.
        jar_allowlist.update({"constraintlayout-core", "collection"})
    # Material is handled by plugins; core stays minimal.
    return required_aars, jar_allowlist
