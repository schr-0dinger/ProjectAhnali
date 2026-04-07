# Project Workflow

This repository moves fastest when we treat Ahnali as two separate concerns:

1. The current product: a restricted Python DSL compiled through a verified SSA/Dalvik/Smali pipeline.
2. The next strategy: a broader smart-transpiler direction that must be layered onto the current compiler instead of replacing it in one jump.

## Default change workflow

1. Start with reality.
   Read the relevant docs, then confirm the actual code path in `dsl/`, `alpha_pipeline.py`, `apk/`, and `tests/`.
2. Classify the change.
   Decide whether it is a DSL-surface change, a lowering/runtime change, a compiler backend change, a toolchain change, or a docs/contracts change.
3. Preserve the stable backend.
   Treat `alpha_pipeline.py` and the CFG/SSA/Dalvik path as the stable execution spine unless the work is explicitly backend-focused.
4. Change the smallest layer that can own the feature.
   Prefer frontend analysis, lowering, or capability/runtime selection before changing SSA, regalloc, or emission.
5. Add or update tests first-class.
   Every behavior change needs tests under `tests/`, and contract changes must update the matching snapshot or policy gate.
6. Reconcile docs in the same change.
   If behavior, strategy, or scope changed, update the vault docs, `README.md`, and any workflow/skills guidance that would mislead the next contributor.

## Pipeline-change workflow

When evaluating a pipeline change, use this order:

1. Check whether the feature can be expressed as a frontend or lowering extension.
2. Check whether existing capability helpers or support-class injection already provide most of the runtime need.
3. Only then consider new IR, SSA, Dalvik, or emitter work.
4. If a change would require general Python semantics, record it as staged research unless there is a bounded subset and test plan.

## Strategic rule of thumb

The feasible migration path is:

`Python DSL subset -> feature analysis -> selective lowering/runtime selection -> existing verified backend`

The risky path is:

`full Python parser swap -> dynamic semantics everywhere -> backend rewrite`

Choose the first path by default.

## Local verification

```bash
PYTHONPATH=. pytest -q
PYTHONPATH=. python tools/docs_consistency.py
PYTHONPATH=. python tools/v1_scope_matrix.py --check --masterplan docs/Masterplan_All_In_One.md --matrix cfg/v1_scope_matrix.yaml
PYTHONPATH=. python tools/python_library_policy.py --policy cfg/python_library_policy.json
```

If you touch packaging or APK benchmarks, also run the relevant `tools/benchmark_apk.py` flow when the Android SDK/toolchain is available.

If you touch analyzer/runtime-selection work, also inspect the plan directly:

```bash
PYTHONPATH=. python tools/feature_runtime_plan.py --source path/to/file.py
```

And confirm build outputs include `runtime_plan.json` when applicable.

## Decision checkpoints

Pause and document tradeoffs before proceeding if a change would:

- weaken static-default behavior
- bypass validation gates
- add implicit runtime behavior
- blur the line between restricted DSL support and general Python support
- require new third-party dependencies

## Output expectations

Good changes in this repo usually include:

- code or docs aligned with actual behavior
- tests that pin the behavior
- updated strategy language when the plan changes
- a clear note about what is implemented now vs. deferred research
