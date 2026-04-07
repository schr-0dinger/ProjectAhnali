from __future__ import annotations

from collections.abc import Iterable

from dsl.runtime.modules import RuntimeModuleSpec, default_runtime_module_registry

from .profile import FeatureUsageProfile


def _append_unique(modules: list[RuntimeModuleSpec], seen: set[str], module: RuntimeModuleSpec):
    if module.name in seen:
        return
    seen.add(module.name)
    modules.append(module)


def select_runtime_modules(
    profile: FeatureUsageProfile,
    *,
    capability_bindings: Iterable[object] | None = None,
    support_classes: Iterable[tuple] | None = None,
) -> list[RuntimeModuleSpec]:
    registry = default_runtime_module_registry()
    selected: list[RuntimeModuleSpec] = []
    seen: set[str] = set()

    _append_unique(selected, seen, registry["core.static"])

    if profile.runtime.get("reactive_mode"):
        _append_unique(selected, seen, registry["app.mode.reactive"])

    if profile.collections.get("list"):
        _append_unique(selected, seen, registry["python.collections.list_wrapper"])
    if profile.collections.get("dict"):
        _append_unique(selected, seen, registry["python.collections.dict_wrapper"])
    if profile.collections.get("set"):
        _append_unique(selected, seen, registry["python.collections.set_wrapper"])
    if profile.collections.get("tuple"):
        _append_unique(selected, seen, registry["python.collections.tuple_wrapper"])

    if any(profile.introspection.get(name) for name in ("getattr", "setattr", "hasattr", "delattr")):
        _append_unique(selected, seen, registry["python.introspection.reflection"])

    if profile.runtime.get("string_methods") or profile.runtime.get("string_split_join"):
        _append_unique(selected, seen, registry["python.strings.methods"])

    if profile.android_api.get("uri_binding"):
        _append_unique(selected, seen, registry["android.bindings.uri"])
    if profile.android_api.get("intent_binding"):
        _append_unique(selected, seen, registry["android.bindings.intent"])
    if profile.android_api.get("activity_binding"):
        _append_unique(selected, seen, registry["android.bindings.activity"])

    if profile.async_features.get("async_def") or profile.async_features.get("await"):
        _append_unique(selected, seen, registry["python.async.async_runtime"])
    if profile.async_features.get("yield") or profile.async_features.get("yield_from"):
        _append_unique(selected, seen, registry["python.generators.iterator_runtime"])

    if profile.imports.get("import") or profile.imports.get("import_from"):
        _append_unique(selected, seen, registry["python.imports.static_loader"])

    if profile.functions.get("decorators"):
        _append_unique(selected, seen, registry["python.advanced.decorators"])
    if profile.control_flow.get("with") or profile.control_flow.get("async_with"):
        _append_unique(selected, seen, registry["python.advanced.context_managers"])
    if profile.functions.get("varargs"):
        _append_unique(selected, seen, registry["python.advanced.varargs"])

    if any(True for _ in (support_classes or [])):
        _append_unique(selected, seen, registry["support.event_listeners"])

    for binding in capability_bindings or []:
        capability = str(getattr(binding, "capability", "")).strip()
        if not capability:
            continue
        helper_class_desc = getattr(binding, "helper_class_desc", None)
        name = f"capability.{capability}"
        _append_unique(
            selected,
            seen,
            RuntimeModuleSpec(
                name=name,
                category="capability",
                trigger=f"uses={capability}",
                dependencies=("core.static",),
                helper_class_desc=helper_class_desc,
            ),
        )

    return selected
