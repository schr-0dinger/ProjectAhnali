from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RouteSpec:
    name: str
    args: dict[str, str] = field(default_factory=dict)
    defaults: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AppModeConfig:
    mode: str = "static"
    profile: str = "dev"


def validate_route_spec(value: RouteSpec | dict) -> RouteSpec:
    if isinstance(value, RouteSpec):
        obj = value
    elif isinstance(value, dict):
        obj = RouteSpec(
            name=str(value.get("name", "")),
            args={str(k): str(v) for k, v in dict(value.get("args", {})).items()},
            defaults={str(k): str(v) for k, v in dict(value.get("defaults", {})).items()},
        )
    else:
        raise RuntimeError("RouteSpec input must be RouteSpec or dict")

    if not obj.name.strip():
        raise RuntimeError("RouteSpec.name must be non-empty")

    # Optional strict path with pydantic if installed.
    try:
        from pydantic import BaseModel, ConfigDict, Field  # type: ignore

        class _RouteModel(BaseModel):
            model_config = ConfigDict(extra="forbid")
            name: str
            args: dict[str, str] = Field(default_factory=dict)
            defaults: dict[str, str] = Field(default_factory=dict)

        parsed = _RouteModel.model_validate(
            {
                "name": obj.name,
                "args": obj.args,
                "defaults": obj.defaults,
            }
        )
        return RouteSpec(name=parsed.name, args=dict(parsed.args), defaults=dict(parsed.defaults))
    except Exception:
        return obj


def validate_app_mode_config(value: AppModeConfig | dict) -> AppModeConfig:
    if isinstance(value, AppModeConfig):
        obj = value
    elif isinstance(value, dict):
        obj = AppModeConfig(
            mode=str(value.get("mode", "static")),
            profile=str(value.get("profile", "dev")),
        )
    else:
        raise RuntimeError("AppModeConfig input must be AppModeConfig or dict")

    mode = obj.mode.strip().lower()
    if mode not in {"static", "reactive"}:
        raise RuntimeError(f"AppModeConfig.mode must be 'static' or 'reactive', got {obj.mode!r}")

    profile = obj.profile.strip().lower()
    if profile not in {"dev", "staging", "prod"}:
        raise RuntimeError(
            f"AppModeConfig.profile must be one of dev/staging/prod, got {obj.profile!r}"
        )

    return AppModeConfig(mode=mode, profile=profile)
