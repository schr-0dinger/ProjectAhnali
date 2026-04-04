# Track C Wave 18: Sharing/Intents Completion (Program 6-B Task B5)

Status: Complete
Date: 2026-02-18

Closes the remaining sharing/intents gap by adding deterministic file-share surfaces and explicit open-external result/error expression paths.

## Contract

- Capability: `Caps.Sharing`
- Runtime helper: `Lcom/ahnali/runtime/ShareHelper;`
- New helper methods:
  - `shareFile(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I`
  - `shareFileError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I`

Existing helper methods retained:
- `shareText(...)`, `shareTextError(...)`, `openUri(...)`, `openUriError(...)`

## DSL Surface

- Statement APIs:
  - `share_file(uri, chooser_title="Share file via", mime_type="*/*")`
  - `share_uri(...)` (alias)
- Result/error expression APIs:
  - `share_file_result(uri, chooser_title="Share file via", mime_type="*/*")`
  - `share_file_error(uri, chooser_title="Share file via", mime_type="*/*")`
  - `open_external_result(uri)`
  - `open_uri_result(uri)` (alias)

## Error contract

- `shareFile`: `1` success, `0` failure.
- `shareFileError`: `0` success, `1` invalid args/context, `3` no handler/activity not found, `4` exception.
- `openUri`/`openUriError` semantics remain unchanged.

## Conformance

- `tests/test_track_c_wave18_sharing_completion.py`
- `tests/test_track_c_wave18_visible_flow.py`
- Cross-contract gates: `tests/test_runtime_abi_snapshot.py`, `tests/test_capability_diagnostics_contract.py`
