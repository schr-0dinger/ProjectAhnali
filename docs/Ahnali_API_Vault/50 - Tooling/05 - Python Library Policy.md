---
tags: [ahnali, tooling, python, dependencies, policy]
---

# Python Library Policy

> [!abstract] Keep it lean
> Every external dependency needs a reason to exist and must stay out of the core compilation path.

## What's allowed

| Library | Why | Where |
|---|---|---|
| `rich` | Nice terminal output for diagnostics | `dsl.runtime.diagnostics` only |
| `httpx` | HTTP helper wrappers | `dsl.runtime.http_client` only |
| `tenacity` (optional) | Retry/backoff for HTTP | `dsl.runtime.http_client` only |
| `pydantic` (optional) | Strict model validation | `dsl.runtime.models` only |
| `pytest` (test-only) | Testing | `tests/` only |

## Standard library

We use `dataclasses` for typed models and `asyncio` for lifecycle-scoped async work. That's it.

## What's not allowed

Nothing that pulls in a runtime engine or framework:
- Reactive engines (rx, reactivex)
- DI frameworks (injector, dependency_injector)
- Web frameworks (fastapi, flask, django)
- Big ORMs (sqlalchemy, peewee)
- Symbolic math (sympy)

## The wrapper rule

Third-party libs get imported from wrapper modules only. Nothing from the parser, lowering, or static compilation paths touches a third-party import directly.

## Enforcement

Policy file: `cfg/python_library_policy.json`
Checker: `tools/python_library_policy.py`
CI gate: "Check Python library policy" step in `.github/workflows/ci.yml`

Add a dependency without updating the policy file → CI catches it.

## Learn more

- CI gates: [[50 - Tooling/04 - CI Gates]]
- Design philosophy: [[20 - Core Concepts/06 - Design Philosophy]]
