from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FeatureUsageProfile:
    source_kind: str
    source_name: str = ""
    collections: dict[str, bool] = field(default_factory=dict)
    control_flow: dict[str, bool] = field(default_factory=dict)
    functions: dict[str, bool] = field(default_factory=dict)
    classes: dict[str, bool] = field(default_factory=dict)
    async_features: dict[str, bool] = field(default_factory=dict)
    introspection: dict[str, bool] = field(default_factory=dict)
    imports: dict[str, bool] = field(default_factory=dict)
    builtins: dict[str, bool] = field(default_factory=dict)
    android_api: dict[str, bool] = field(default_factory=dict)
    runtime: dict[str, bool] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    capabilities: tuple[str, ...] = ()
    support_class_kinds: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "source_kind": self.source_kind,
            "source_name": self.source_name,
            "collections": dict(self.collections),
            "control_flow": dict(self.control_flow),
            "functions": dict(self.functions),
            "classes": dict(self.classes),
            "async_features": dict(self.async_features),
            "introspection": dict(self.introspection),
            "imports": dict(self.imports),
            "builtins": dict(self.builtins),
            "android_api": dict(self.android_api),
            "runtime": dict(self.runtime),
            "counts": dict(self.counts),
            "capabilities": list(self.capabilities),
            "support_class_kinds": list(self.support_class_kinds),
        }
