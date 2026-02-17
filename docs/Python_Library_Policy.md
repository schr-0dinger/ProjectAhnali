# Python Library Policy (Static-First, Reactive-Optional)

Status: Enforced in CI

This policy keeps Python-side dependencies minimal and purpose-justified while preserving Ahnali determinism.

## Allowed External Libraries

- `rich`: structured diagnostics rendering.
- `httpx`: sync/async HTTP helper wrappers.
- `tenacity` (optional): explicit retry/backoff orchestration for HTTP wrappers.
- `pydantic` (optional): strict validation path for typed route/config models.
- `pytest` (test-only): allowed only under `tests/`.

## Required Standard Library Foundations

- `dataclasses`: typed route/config models.
- `asyncio`: lifecycle-scoped async primitives.

## Disallowed Heavy Libraries

- Reactive engines (`rx`, `reactivex`)
- Full DI frameworks (`injector`, `dependency_injector`)
- Web frameworks (`fastapi`, `flask`, `django`)
- Large ORMs (`sqlalchemy`, `peewee`, `tortoise`)
- Symbolic math libs (`sympy`)

## Wrapper Boundary Rule

External libraries must be imported only from explicit wrapper modules:

- `dsl.runtime.diagnostics` for `rich`
- `dsl.runtime.http_client` for `httpx`/`tenacity`
- `dsl.runtime.models` for `pydantic`

No direct third-party imports are allowed in DSL lowering, parser, or static-mode compilation paths.

## Determinism Constraints

- Static mode remains default.
- Reactive mode is explicit opt-in.
- No hidden observers or implicit runtime mutation in static mode.
- Retry behavior must be explicit and policy-driven (`fixed` or `exponential`).

## CI Enforcement

- Policy file: `cfg/python_library_policy.json`
- Checker: `tools/python_library_policy.py`
- CI gate: `.github/workflows/ci.yml` step `Check Python library policy`
