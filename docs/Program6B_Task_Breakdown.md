# Program 6-B — Capability Breadth

This breaks down the remaining capability work from section 8.5 of the masterplan. The scope matrix in `cfg/v1_scope_matrix.yaml` is the source of truth for what's done, what's deferred, and what's blocked.

## Already shipped

Waves 9 through 18 are all done:
- Clipboard, Sharing/intents, WebView + JS bridge + file chooser + cookies
- Deep linking
- WorkManager, AlarmManager, JobScheduler
- Sharing completion (file share + open result)

## What's left

**Scope matrix cleanup (done):** Reconciled the scope matrix, promoted completed slices, removed stale entries. The `v1_scope_matrix.py` check and docs consistency gate both pass.

**Deep-link expansion (done):** Deterministic helper-call surface for opening and routing intent data. Full DSL → lowering → runtime → test → docs chain.

**Background work (done):** Three tranches — WorkManager, AlarmManager, JobScheduler. Each has deterministic APIs, error codes, tests, and visible flow coverage.

**Sharing/intents completion (done):** Closed the remaining intent/deep-link/custom URI gaps with deterministic result/error surfaces.

## Deferred beyond v1

These are explicitly parked. They're not forgotten, but they're not happening until the static compiler is frozen and we've got breathing room:

- **Media (audio/video/camera):** Helper surfaces are planned but need the deterministic contract treatment before they ship.
- **Sensors/location advanced:** Basic location is done. Advanced sensor APIs need proper fallback behavior tests.
- **Device connectivity (Bluetooth/NFC):** Same story — deterministic unavailability and permission error codes need to be defined.
- **File/storage expansion (SAF, file picker, external storage):** URI/string return contracts are straightforward, just haven't been prioritized.

## Closure criteria

Program 6-B is done when:
1. Every implemented slice shows up as completed in the masterplan and docs
2. Nothing in the scope matrix is left in a vague "planned" state — everything is either done or explicitly deferred
3. Each completed item has tests and docs
4. ABI and capability mapping snapshots are updated and green in CI
5. At least one visible deterministic flow exists per major tranche

We're close. The remaining work is mostly housekeeping — making sure the docs and scope matrix accurately reflect what's actually in the code.
