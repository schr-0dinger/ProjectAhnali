from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RuntimeModuleSpec:
    name: str
    category: str
    trigger: str
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    helper_class_desc: str | None = None
    helper_method: str | None = None
    helper_sig: str | None = None


def default_runtime_module_registry() -> dict[str, RuntimeModuleSpec]:
    modules = [
        RuntimeModuleSpec(
            name="core.static",
            category="core",
            trigger="always",
        ),
        RuntimeModuleSpec(
            name="app.mode.reactive",
            category="mode",
            trigger="app_mode=reactive",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/ReactiveRuntime;",
            helper_method="init",
            helper_sig="()V",
        ),
        RuntimeModuleSpec(
            name="python.collections.list_wrapper",
            category="python",
            trigger="list literal / list builtin",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/ListWrapperRuntime;",
            helper_method="create",
            helper_sig="()Ljava/util/ArrayList;",
        ),
        RuntimeModuleSpec(
            name="python.collections.dict_wrapper",
            category="python",
            trigger="dict literal / dict builtin",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/DictWrapperRuntime;",
            helper_method="create",
            helper_sig="()Ljava/util/HashMap;",
        ),
        RuntimeModuleSpec(
            name="python.collections.set_wrapper",
            category="python",
            trigger="set literal / set builtin",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/SetWrapperRuntime;",
            helper_method="create",
            helper_sig="()Ljava/util/HashSet;",
        ),
        RuntimeModuleSpec(
            name="python.collections.tuple_wrapper",
            category="python",
            trigger="tuple literal / tuple builtin",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/TupleWrapperRuntime;",
            helper_method="create",
            helper_sig="(I)[Ljava/lang/Object;",
        ),
        RuntimeModuleSpec(
            name="python.introspection.reflection",
            category="python",
            trigger="getattr/setattr/hasattr/delattr",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/ReflectionRuntime;",
            helper_method="getText",
            helper_sig="(Landroid/widget/TextView;)Ljava/lang/String;",
        ),
        RuntimeModuleSpec(
            name="python.strings.methods",
            category="python",
            trigger="string method helpers",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/StringMethodsRuntime;",
            helper_method="split",
            helper_sig="(Ljava/lang/String;Ljava/lang/String;)Ljava/util/ArrayList;",
        ),
        RuntimeModuleSpec(
            name="android.bindings.uri",
            category="android",
            trigger="android_uri_parse",
            dependencies=("core.static",),
        ),
        RuntimeModuleSpec(
            name="android.bindings.intent",
            category="android",
            trigger="android_intent_view / android_intent_chooser",
            dependencies=("core.static",),
        ),
        RuntimeModuleSpec(
            name="android.bindings.activity",
            category="android",
            trigger="android_start_activity",
            dependencies=("core.static",),
        ),
        RuntimeModuleSpec(
            name="python.async.async_runtime",
            category="python",
            trigger="async def / await",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/AsyncRuntime;",
            helper_method="init",
            helper_sig="()V",
        ),
        RuntimeModuleSpec(
            name="python.generators.iterator_runtime",
            category="python",
            trigger="yield / yield from",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/IteratorRuntime;",
            helper_method="init",
            helper_sig="()V",
        ),
        RuntimeModuleSpec(
            name="python.imports.static_loader",
            category="python",
            trigger="import / from import",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/StaticImportRuntime;",
            helper_method="init",
            helper_sig="()V",
        ),
        RuntimeModuleSpec(
            name="support.event_listeners",
            category="support",
            trigger="generated support listener classes",
            dependencies=("core.static",),
        ),
        RuntimeModuleSpec(
            name="python.advanced.decorators",
            category="python",
            trigger="function decorators",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/DecoratorRuntime;",
            helper_method="wrap",
            helper_sig="(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;",
        ),
        RuntimeModuleSpec(
            name="python.advanced.context_managers",
            category="python",
            trigger="with statement / context managers",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/ContextManagerRuntime;",
            helper_method="enter",
            helper_sig="(Ljava/lang/Object;)Ljava/lang/Object;",
        ),
        RuntimeModuleSpec(
            name="python.advanced.varargs",
            category="python",
            trigger="*args / **kwargs in function definitions",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/VarargsRuntime;",
            helper_method="pack",
            helper_sig="([Ljava/lang/Object;)[Ljava/lang/Object;",
        ),
        RuntimeModuleSpec(
            name="python.oop.inheritance",
            category="python",
            trigger="class inheritance (class Foo(Bar))",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/InheritanceRuntime;",
            helper_method="init",
            helper_sig="()V",
        ),
        RuntimeModuleSpec(
            name="python.oop.descriptors",
            category="python",
            trigger="descriptors (__get__, __set__, __delete__)",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/DescriptorRuntime;",
            helper_method="init",
            helper_sig="()V",
        ),
        RuntimeModuleSpec(
            name="python.oop.metaclasses",
            category="python",
            trigger="metaclass definition",
            dependencies=("core.static",),
            helper_class_desc="Lcom/ahnali/runtime/MetaclassRuntime;",
            helper_method="init",
            helper_sig="()V",
        ),
    ]
    return {module.name: module for module in modules}
