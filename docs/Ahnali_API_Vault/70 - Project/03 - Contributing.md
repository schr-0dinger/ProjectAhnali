---
tags: [ahnali, project, contributing]
---

# Contributing

> [!abstract] How to help
> The project is open to contributions. Here's what's useful and how to get started.

## What's most useful right now

1. **Docs alignment** - if you spot something in the docs that doesn't match the code, fix it
2. **Test coverage gaps** - run the suite, find what's not covered, add tests
3. **Optimization backlog** - pick an item from [[60 - Architecture/03 - Optimization Backlog]] and implement it behind a flag
4. **Widget surface completion** - Dropdown and PopupMenu text-typography surfaces are partial

## How to run things

```bash
# Tests
PYTHONPATH=. pytest -q

# Size benchmark (no device needed)
PYTHONPATH=. python tools/benchmark_apk.py --skip-cold-start --api 34

# Check library policy
PYTHONPATH=. python tools/python_library_policy.py
```

## Guidelines

- **Correctness over features** - if your change breaks a test, it's not ready
- **One thing per PR** - don't bundle unrelated changes
- **Tests for everything** - new code needs tests
- **Update docs** - if you change behavior, update the docs
- **Follow the library policy** - no new dependencies without updating `cfg/python_library_policy.json`
- **Preserve the backend spine** - prefer frontend/lowering/runtime-selection changes before rewriting CFG/SSA/Dalvik stages

## Where to look

- Compiler pipeline: `dsl/`, `ir/`, `cfg/`, `ssa/`, `dalvik/`, `passes/`, `emit/`
- DSL surface: `dsl/app.py`, `dsl/widgets.py`, `dsl/api.py`
- Capabilities: `dsl/capabilities.py`, `dsl/runtime/`
- Tests: `tests/`
- Tooling: `tools/`
- Config: `cfg/`

## Workflow docs

- Repo workflow: `WORKFLOW.md`
- Repo skills map: `skills.md`

## Questions?

Open an issue. The maintainers will respond.

## Learn more

- Current status: [[70 - Project/01 - Current Status]]
- Roadmap: [[70 - Project/02 - Roadmap]]
- Python library policy: [[50 - Tooling/05 - Python Library Policy]]
