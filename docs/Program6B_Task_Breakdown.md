# Program 6-B Task Breakdown (Capability Breadth, Section 8.5)

Status: Active  
Mode: Static-default, deterministic helper contracts required per slice

This document breaks Program 6-B into execution tasks with strict completion gates.

## Already completed (baseline)

1. Wave 9: Clipboard (`Caps.Clipboard`)
2. Wave 10: Sharing + external intents (`Caps.Sharing`)
3. Wave 11: WebView + policy/settings (`Caps.Web`)
4. Wave 12: JS bridge constrained surface (`Caps.Web`)
5. Wave 13: File chooser + cookie manager (`Caps.Web`)

## Program 6-B completion tasks

1. Task B0: Scope matrix reconciliation and drift lock (completed)
- Update `cfg/v1_scope_matrix.yaml` statuses for completed 8.5 slices (waves 9-13).
- Ensure each completed scope item has test/doc references populated.
- Gate: `tools/v1_scope_matrix.py --check` and docs consistency checks pass.

2. Task B1: Deep-link expansion (completed)
- Add deterministic deep-link helper-call surface (open + route intent data).
- Add DSL/parser/lowering/runtime helper/tests/visible flow/docs.
- Gate: deep-link slice passes ABI snapshot, capability mapping snapshot, and visible-flow tests.

3. Task B2: Background work tranche A (`WorkManager`) (next immediate)
- Add deterministic enqueue/cancel/status-result APIs.
- Add helper ABI contract and error-code mapping.
- Add compile + selected runtime integration tests.
- Gate: WorkManager slice is fully contract-complete.

4. Task B3: Background work tranche B (`AlarmManager`)
- Add deterministic schedule/cancel APIs with explicit parameter validation.
- Add fallback/error contracts and tests.
- Gate: AlarmManager slice is fully contract-complete.

5. Task B4: Background work tranche C (`JobScheduler`)
- Add deterministic schedule/cancel/status APIs.
- Add API level guards and deterministic diagnostics.
- Gate: JobScheduler slice is fully contract-complete.

6. Task B5: Sharing/intents completion pass
- Close remaining 8.5 intent/deep-link/custom URI/open-app gaps.
- Add deterministic result/error surfaces for each new helper call.
- Gate: all retained sharing/intents scope entries are done.

7. Task B6: Media tranche A (audio/video core)
- Add retained audio/video deterministic helper surfaces.
- Add explicit capability + permission diagnostics.
- Gate: media slice ships with visible flow and ABI snapshot update.

8. Task B7: Media tranche B (camera retained subset)
- Add retained camera preview/capture surface under deterministic constraints.
- Add permission-denied and runtime-failure deterministic codes.
- Gate: camera retained subset is contract-complete.

9. Task B8: Sensors/location advanced retained subset
- Add retained advanced location/sensor APIs under deterministic contracts.
- Add sampling/availability fallback behavior tests.
- Gate: retained sensor/location items are done.

10. Task B9: Device-connectivity retained subset
- Add retained Bluetooth/NFC/connectivity expansion surfaces in scope.
- Add deterministic unavailability and permission error codes.
- Gate: retained device-connectivity items are done.

11. Task B10: File/storage capability retained subset
- Add retained file picker/SAF/external-storage capability APIs.
- Keep deterministic URI/string return contracts.
- Gate: retained storage capability items are done.

12. Task B11: Program 6-B closure and freeze
- Reconcile masterplan + README + capability mapping + ABI docs with code reality.
- Freeze ABI/capability snapshots for Program 6-B surfaces.
- Gate: no planned retained 8.5 item remains without explicit defer/non-goal decision.

## Completion criteria for Program 6-B

1. All retained `8.5` scope entries are `done` in `cfg/v1_scope_matrix.yaml`.
2. Every completed item has parser/lowering/toolchain tests and docs references.
3. Runtime ABI snapshot + capability mapping snapshot are updated and green in CI.
4. At least one visible deterministic flow exists per major 8.5 tranche.
5. No high-severity capability contract drift remains.
