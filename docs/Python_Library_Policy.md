# Python Library Policy

Keep the Python side lean. Every external dependency needs a reason to exist, and it needs to stay out of the core compilation path.

## What's allowed

- **rich** — nicer terminal output for diagnostics. Used through `dsl.runtime.diagnostics`, never imported directly in compiler code.
- **httpx** — HTTP helper wrappers. Same wrapper rule.
- **tenacity** (optional) — retry/backoff for the HTTP wrappers. Only pulled in when you actually need retries.
- **pydantic** (optional) — strict validation for typed models. Again, wrapper-only.
- **pytest** — tests only. Stays in `tests/`.

## Standard library

We lean on `dataclasses` for typed models and `asyncio` for lifecycle-scoped async work. That's it for required stdlib.

## What's not allowed

Nothing that pulls in a runtime engine or framework. Specifically:
- Reactive engines (rx, reactivex)
- DI frameworks (injector, dependency_injector)
- Web frameworks (fastapi, flask, django)
- Big ORMs (sqlalchemy, peewee, tortoise)
- Symbolic math (sympy)

## The wrapper rule

Third-party libs get imported from wrapper modules only:
- `dsl.runtime.diagnostics` for rich
- `dsl.runtime.http_client` for httpx/tenacity
- `dsl.runtime.models` for pydantic

Nothing from the parser, lowering, or static compilation paths touches a third-party import directly. The CLI goes through `dsl.runtime.diagnostics` so you get Rich formatting when it's installed and plain text when it's not.

## Determinism

Static mode is always the default. Reactive mode is opt-in. Retry behavior has to be explicit — fixed or exponential, your choice, but it's declared, not hidden.

## Enforcement

The policy lives in `cfg/python_library_policy.json`. The checker is `tools/python_library_policy.py`. CI runs it on every push under the "Check Python library policy" step. If you add a dependency without updating the policy file, CI catches it.
