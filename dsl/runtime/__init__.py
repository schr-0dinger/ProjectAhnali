"""Runtime-facing Python wrappers for optional host-side integrations.

These modules intentionally keep third-party imports isolated behind explicit
contracts so static mode semantics never gain hidden observers or implicit
runtime behavior.
"""

from .async_scope import LifecycleAsyncScope
from .diagnostics import DiagnosticMessage, DiagnosticReporter
from .http_client import HttpRequestOptions, HttpResult, async_http_request, sync_http_request
from .models import AppModeConfig, RouteSpec, validate_app_mode_config, validate_route_spec

__all__ = [
    "DiagnosticMessage",
    "DiagnosticReporter",
    "HttpRequestOptions",
    "HttpResult",
    "sync_http_request",
    "async_http_request",
    "RouteSpec",
    "AppModeConfig",
    "validate_route_spec",
    "validate_app_mode_config",
    "LifecycleAsyncScope",
]
