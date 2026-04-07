from __future__ import annotations

import ast
import inspect
import textwrap
from collections import Counter
from collections.abc import Iterable

from ir.program import ProgramIR

from dsl.android.bindings import default_android_binding_registry

from .profile import FeatureUsageProfile

_BUILTIN_NAMES = {
    "print",
    "int",
    "str",
    "float",
    "len",
    "range",
    "enumerate",
    "zip",
    "list",
    "dict",
    "set",
    "tuple",
    "getattr",
    "setattr",
    "hasattr",
    "delattr",
    "isinstance",
    "type",
    "super",
}

_INTROSPECTION_BUILTINS = {"getattr", "setattr", "hasattr", "delattr"}
_ANDROID_BINDINGS = default_android_binding_registry()


def _empty_flags(*keys: str) -> dict[str, bool]:
    return {key: False for key in keys}


class _FeatureCollector(ast.NodeVisitor):
    def __init__(self):
        self.collections = _empty_flags("list", "dict", "set", "tuple", "list_comprehension", "dict_comprehension", "set_comprehension")
        self.control_flow = _empty_flags("if", "for", "while", "try", "with")
        self.functions = _empty_flags("def", "lambda", "return")
        self.classes = _empty_flags("class")
        self.async_features = _empty_flags("async_def", "await", "yield", "yield_from")
        self.introspection = _empty_flags("getattr", "setattr", "hasattr", "delattr")
        self.imports = _empty_flags("import", "import_from")
        self.builtins = _empty_flags(*sorted(_BUILTIN_NAMES))
        self.android_api = _empty_flags(
            "android_import",
            "androidx_import",
            "java_import",
            "uri_binding",
            "intent_binding",
            "activity_binding",
        )
        self.runtime = _empty_flags("string_methods", "string_split_join")

    def visit_If(self, node: ast.If):
        self.control_flow["if"] = True
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.control_flow["for"] = True
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self.control_flow["while"] = True
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        self.control_flow["try"] = True
        self.generic_visit(node)

    def visit_With(self, node: ast.With):
        self.control_flow["with"] = True
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions["def"] = True
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.functions["def"] = True
        self.async_features["async_def"] = True
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return):
        self.functions["return"] = True
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda):
        self.functions["lambda"] = True
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes["class"] = True
        self.generic_visit(node)

    def visit_Await(self, node: ast.Await):
        self.async_features["await"] = True
        self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield):
        self.async_features["yield"] = True
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom):
        self.async_features["yield_from"] = True
        self.generic_visit(node)

    def visit_List(self, node: ast.List):
        self.collections["list"] = True
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict):
        self.collections["dict"] = True
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set):
        self.collections["set"] = True
        self.generic_visit(node)

    def visit_Tuple(self, node: ast.Tuple):
        self.collections["tuple"] = True
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp):
        self.collections["list_comprehension"] = True
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp):
        self.collections["dict_comprehension"] = True
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp):
        self.collections["set_comprehension"] = True
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        self.imports["import"] = True
        for alias in node.names:
            self._mark_import(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.imports["import_from"] = True
        self._mark_import(node.module or "")
        self.generic_visit(node)

    def _mark_import(self, module_name: str):
        if module_name.startswith("androidx"):
            self.android_api["androidx_import"] = True
        elif module_name.startswith("android"):
            self.android_api["android_import"] = True
        elif module_name.startswith("java"):
            self.android_api["java_import"] = True

    def visit_Call(self, node: ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            name = func.id
            if name in self.builtins:
                self.builtins[name] = True
            if name in self.collections:
                self.collections[name] = True
            if name in _INTROSPECTION_BUILTINS:
                self.introspection[name] = True
            binding = _ANDROID_BINDINGS.get(name)
            if binding is not None:
                for flag in binding.analyzer_flags:
                    self.android_api[flag] = True
        elif isinstance(func, ast.Attribute):
            method_name = str(getattr(func, "attr", "") or "").strip().lower()
            if method_name in {"strip", "replace", "lower", "upper", "split", "join", "format"}:
                self.runtime["string_methods"] = True
            if method_name in {"split", "join"}:
                self.runtime["string_split_join"] = True
        self.generic_visit(node)


def _tree_from_source(source: str, *, filename: str = "<string>") -> ast.AST:
    return ast.parse(source, filename=filename)


def _tree_from_callable(value) -> ast.AST:
    src = textwrap.dedent(inspect.getsource(value))
    return _tree_from_source(src, filename=getattr(value, "__name__", "<callable>"))


def analyze_features(source) -> FeatureUsageProfile:
    if isinstance(source, ast.AST):
        tree = source
        source_kind = "ast"
        source_name = ""
    elif isinstance(source, str):
        tree = _tree_from_source(source)
        source_kind = "source"
        source_name = "<string>"
    elif callable(source):
        tree = _tree_from_callable(source)
        source_kind = "callable"
        source_name = getattr(source, "__name__", "")
    else:
        raise RuntimeError("analyze_features input must be source text, AST, or callable")

    collector = _FeatureCollector()
    collector.visit(tree)
    counts = Counter()
    for bucket in (
        collector.collections,
        collector.control_flow,
        collector.functions,
        collector.classes,
        collector.async_features,
        collector.introspection,
        collector.imports,
        collector.builtins,
        collector.android_api,
        collector.runtime,
    ):
        counts["enabled_flags"] += sum(1 for enabled in bucket.values() if enabled)

    return FeatureUsageProfile(
        source_kind=source_kind,
        source_name=source_name,
        collections=collector.collections,
        control_flow=collector.control_flow,
        functions=collector.functions,
        classes=collector.classes,
        async_features=collector.async_features,
        introspection=collector.introspection,
        imports=collector.imports,
        builtins=collector.builtins,
        android_api=collector.android_api,
        runtime=collector.runtime,
        counts=dict(counts),
    )


def analyze_frontend_ir(
    frontend_ir: ProgramIR,
    *,
    app_mode: str = "static",
    capability_bindings: Iterable[object] | None = None,
) -> FeatureUsageProfile:
    if not isinstance(frontend_ir, ProgramIR):
        raise RuntimeError("analyze_frontend_ir expects ProgramIR")

    capability_names = tuple(
        sorted(
            {
                str(getattr(binding, "capability", "")).strip()
                for binding in (capability_bindings or [])
                if str(getattr(binding, "capability", "")).strip()
            }
        )
    )
    support_kinds = []
    for entry in getattr(frontend_ir, "support_classes", []) or []:
        if len(entry) >= 4:
            support_kinds.append(str(entry[3]))
        else:
            support_kinds.append("support_class")

    counts = {
        "methods": len(getattr(frontend_ir, "methods", []) or []),
        "fields": len(getattr(frontend_ir, "fields", []) or []),
        "support_classes": len(getattr(frontend_ir, "support_classes", []) or []),
        "capabilities": len(capability_names),
    }

    return FeatureUsageProfile(
        source_kind="program_ir",
        source_name=type(frontend_ir).__name__,
        collections={},
        control_flow={},
        functions={"def": bool(counts["methods"])},
        classes={},
        async_features={},
        introspection={},
        imports={},
        builtins={},
        android_api={},
        runtime={
            "reactive_mode": str(app_mode).strip().lower() == "reactive",
            "capabilities": bool(capability_names),
            "support_classes": bool(counts["support_classes"]),
        },
        counts=counts,
        capabilities=capability_names,
        support_class_kinds=tuple(sorted(set(support_kinds))),
    )


def merge_feature_profiles(*profiles: FeatureUsageProfile | None) -> FeatureUsageProfile:
    valid = [profile for profile in profiles if profile is not None]
    if not valid:
        return FeatureUsageProfile(source_kind="merged")

    def _merge_flags(attr: str) -> dict[str, bool]:
        keys: set[str] = set()
        for profile in valid:
            keys.update(getattr(profile, attr).keys())
        return {
            key: any(bool(getattr(profile, attr).get(key, False)) for profile in valid)
            for key in sorted(keys)
        }

    counts: dict[str, int] = {}
    for profile in valid:
        for key, value in profile.counts.items():
            counts[key] = counts.get(key, 0) + int(value)

    capabilities = tuple(
        sorted({cap for profile in valid for cap in profile.capabilities})
    )
    support_class_kinds = tuple(
        sorted({kind for profile in valid for kind in profile.support_class_kinds})
    )

    return FeatureUsageProfile(
        source_kind="merged",
        source_name=" + ".join(filter(None, [profile.source_name for profile in valid])),
        collections=_merge_flags("collections"),
        control_flow=_merge_flags("control_flow"),
        functions=_merge_flags("functions"),
        classes=_merge_flags("classes"),
        async_features=_merge_flags("async_features"),
        introspection=_merge_flags("introspection"),
        imports=_merge_flags("imports"),
        builtins=_merge_flags("builtins"),
        android_api=_merge_flags("android_api"),
        runtime=_merge_flags("runtime"),
        counts=counts,
        capabilities=capabilities,
        support_class_kinds=support_class_kinds,
    )
