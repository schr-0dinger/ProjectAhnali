from __future__ import annotations

from dsl.deps import collect_dependency_artifacts


def register(registry):
    # Core UI + statement lowering lives in _PythonicContext. Register a low-priority
    # catch-all so plugins can override specific widget/stmt handling.
    registry.register_ui(object, lambda ctx, item, parent_id: ctx._render_ui_core(item, parent_id), priority=-100)
    registry.register_stmt(object, lambda ctx, stmt: ctx._compile_stmt_core(stmt), priority=-100)
    registry.register_deps("core", collect_dependency_artifacts, priority=-100)
