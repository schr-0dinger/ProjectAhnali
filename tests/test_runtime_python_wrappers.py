import asyncio

from dsl.runtime.async_scope import LifecycleAsyncScope
from dsl.runtime.diagnostics import DiagnosticMessage, DiagnosticReporter
from dsl.runtime.http_client import HttpRequestOptions, _compute_backoff_ms, parse_headers
from dsl.runtime.models import AppModeConfig, RouteSpec, validate_app_mode_config, validate_route_spec


def test_diagnostic_reporter_plain_fallback_is_deterministic():
    reporter = DiagnosticReporter(use_rich=False)
    out = reporter.render(
        DiagnosticMessage(
            level="error",
            code="ReactiveModeError",
            message="reactive API requires mode",
            hint="set app_config(mode='reactive')",
        )
    )
    assert "[error] ReactiveModeError" in out
    assert "Fix: set app_config(mode='reactive')" in out


def test_http_parse_headers_and_backoff_policy_are_deterministic():
    headers = parse_headers("X-One: a\ninvalid\nX-Two: b\n")
    assert headers == {"X-One": "a", "X-Two": "b"}

    assert _compute_backoff_ms(50, 0, "fixed") == 50
    assert _compute_backoff_ms(50, 2, "fixed") == 50
    assert _compute_backoff_ms(50, 0, "exponential") == 50
    assert _compute_backoff_ms(50, 2, "exponential") == 200

    opts = HttpRequestOptions(method="POST", retries=2, retry_policy="exponential")
    assert opts.method == "POST"
    assert opts.retries == 2


def test_models_validation_supports_dataclass_and_dict_paths():
    route = validate_route_spec(
        {
            "name": "Details",
            "args": {"id": "String"},
            "defaults": {"id": "0"},
        }
    )
    assert isinstance(route, RouteSpec)
    assert route.name == "Details"

    mode = validate_app_mode_config({"mode": "reactive", "profile": "staging"})
    assert isinstance(mode, AppModeConfig)
    assert mode.mode == "reactive"
    assert mode.profile == "staging"


def test_lifecycle_async_scope_cancels_all_tasks():
    async def _runner():
        scope = LifecycleAsyncScope()

        async def _slow():
            await asyncio.sleep(5)

        scope.create_task(_slow())
        scope.create_task(_slow())
        assert scope.active_count == 2

        await scope.cancel_all()
        assert scope.active_count == 0

    asyncio.run(_runner())
