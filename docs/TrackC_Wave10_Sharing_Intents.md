# Track C Wave 10: Sharing + Intents (Program 6-B)

Status: Completed on 2026-02-18

This wave extends the Program 6-B Sharing/Intents/Clipboard tranche with deterministic
sharing and external-intent dispatch surfaces.

## Capability + ABI

- Capability: `Caps.Sharing`
- Runtime helper: `Lcom/ahnali/runtime/ShareHelper;`
- Helper methods:
  - `shareText(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `shareTextError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `openUri(Landroid/app/Activity;Ljava/lang/String;)I`
  - `openUriError(Landroid/app/Activity;Ljava/lang/String;)I`

Deterministic contract:
- `shareText(...)` returns `1` on success, `0` on failure.
- `openUri(...)` returns `1` on success, `0` on failure.
- `shareTextError(...)` and `openUriError(...)` return explicit error codes:
  - `0`: success
  - `1`: invalid args
  - `3`: no matching activity
  - `4`: runtime exception

## DSL surface

- `share_text(text, chooser_title="Share via")`
- `share(text, chooser_title="Share via")`
- `share_text_result(text, chooser_title="Share via")`
- `share_text_error(text, chooser_title="Share via")`
- `open_external(uri)`
- `open_uri(uri)`
- `open_external_error(uri)`

## Conformance tests

- Capability/lowering/parser/toolchain:
  - `tests/test_track_c_wave10_sharing_intents.py`
- Visible deterministic flow:
  - `tests/test_track_c_wave10_visible_flow.py`
- ABI and mapping snapshot coverage:
  - `tests/test_runtime_abi_v1.py`
  - `tests/test_runtime_abi_snapshot.py`
  - `cfg/runtime_abi_snapshot_v1.json`
  - `cfg/capability_mapping_snapshot_v1.json`

## Visible flow summary

The Wave 10 flow compiles an app that:
1. Dispatches a share intent and open-external intent from button handlers.
2. Reads deterministic helper return/error surfaces (`share_text_result/error`, `open_external_error`).
3. Routes result/error values to visible labels for deterministic fallback behavior.

References:
- `tests/test_track_c_wave10_visible_flow.py`
- `docs/capability_runtime_mapping_v1.md`
- `runtime_abi_v1.md`
