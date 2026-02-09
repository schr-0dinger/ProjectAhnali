from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(order=True)
class _HandlerEntry:
    priority: int
    cls: type
    handler: Callable


class PluginRegistry:
    def __init__(self):
        self._ui_handlers: list[_HandlerEntry] = []
        self._stmt_handlers: list[_HandlerEntry] = []
        self._deps_collectors: list[_HandlerEntry] = []

    def register_ui(self, cls: type, handler: Callable, *, priority: int = 0):
        self._ui_handlers.append(_HandlerEntry(priority, cls, handler))
        self._ui_handlers.sort(reverse=True)

    def register_stmt(self, cls: type, handler: Callable, *, priority: int = 0):
        self._stmt_handlers.append(_HandlerEntry(priority, cls, handler))
        self._stmt_handlers.sort(reverse=True)

    def register_deps(self, key: str, collector: Callable, *, priority: int = 0):
        # key is for readability/debugging only.
        self._deps_collectors.append(_HandlerEntry(priority, str, (key, collector)))
        self._deps_collectors.sort(reverse=True)

    def render_ui(self, ctx, item, parent_id):
        if getattr(item, "_plugin_override", None) == "core":
            return None
        for entry in self._ui_handlers:
            if isinstance(item, entry.cls):
                return entry.handler(ctx, item, parent_id)
        return None

    def compile_stmt(self, ctx, stmt):
        for entry in self._stmt_handlers:
            if isinstance(stmt, entry.cls):
                return entry.handler(ctx, stmt)
        return None

    def collect_deps(self, ui_items, click_specs) -> tuple[set[str], set[str]]:
        required_aars: set[str] = set()
        jar_allowlist: set[str] = set()
        for entry in self._deps_collectors:
            key, collector = entry.handler
            deps = collector(ui_items, click_specs)
            if not deps:
                continue
            req, jars = deps
            required_aars.update(req or [])
            jar_allowlist.update(jars or [])
        return required_aars, jar_allowlist


def load_plugins(plugin_names: Iterable[str]):
    registry = PluginRegistry()
    for name in plugin_names:
        module_name = f"dsl.plugins.{name}"
        mod = __import__(module_name, fromlist=["register"])
        if not hasattr(mod, "register"):
            raise RuntimeError(f"Plugin {name} has no register(registry) function")
        mod.register(registry)
    return registry
