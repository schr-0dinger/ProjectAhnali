# Track C Wave 9: Clipboard (Program 6-B Start)

Status: Completed on 2026-02-18

First slice from the Sharing/Intents/Clipboard tranche in Program 6-B.

## Capability + ABI

- Capability: `Caps.Clipboard`
- Runtime helper: `Lcom/ahnali/runtime/ClipboardHelper;`
- Helper methods:
  - `setText(Landroid/app/Activity;Ljava/lang/String;)I`
  - `getText(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;`

Contract:
- `setText(...)` returns `1` on success, `0` on null args/service-missing/exception.
- `getText(...)` returns clipboard text when available, else returns the provided fallback.

## DSL surface

- `clipboard_set(text)`
- `set_clipboard(text)`
- `clipboard_get(fallback="")`
- `get_clipboard(fallback="")`

## Conformance tests

- Capability/lowering/parser/toolchain: `tests/test_track_c_wave9_clipboard.py`
- Visible deterministic flow: `tests/test_track_c_wave9_visible_flow.py`
- ABI and mapping snapshot coverage: `tests/test_runtime_abi_v1.py`, `tests/test_runtime_abi_snapshot.py`, `cfg/runtime_abi_snapshot_v1.json`, `cfg/capability_mapping_snapshot_v1.json`

## Visible flow

The compiled app:
1. Seeds clipboard data and notification channel.
2. Reads deterministic notification error surface.
3. Routes success to URL launch using clipboard value.
4. Routes failure to deterministic fallback URL/text.

References: `tests/test_track_c_wave9_visible_flow.py`, `docs/capability_runtime_mapping_v1.md`, `runtime_abi_v1.md`
