# Track C Wave 14: Deep Linking (Program 6-B)

Status: Completed on 2026-02-18

Adds deterministic deep-link intake surfaces for app launch intent data.

## Capability + ABI

- Capability: `Caps.DeepLinking`
- Runtime helper: `Lcom/ahnali/runtime/DeepLinkHelper;`
- Helper methods:
  - `getLaunchUri(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;`
  - `getLaunchUriError(Landroid/app/Activity;)I`

Contract:
- `getLaunchUri(...)` returns launch URI string when present and valid, else returns provided fallback.
- `getLaunchUriError(...)` returns explicit error codes:
  - `0`: success (launch URI present)
  - `1`: missing/invalid launch URI context
  - `4`: runtime exception

## DSL surface

- `deep_link_get(fallback="")`
- `get_deep_link(fallback="")`
- `deep_link_error()`
- `get_deep_link_error()`

## Conformance tests

- Capability/lowering/parser/toolchain: `tests/test_track_c_wave14_deep_linking.py`
- Visible deterministic flow: `tests/test_track_c_wave14_visible_flow.py`
- ABI and mapping snapshot coverage: `tests/test_runtime_abi_v1.py`, `tests/test_runtime_abi_snapshot.py`, `cfg/runtime_abi_snapshot_v1.json`, `cfg/capability_mapping_snapshot_v1.json`

## Visible flow

The compiled app:
1. Reads launch URI and deterministic error code from deep-link helper APIs.
2. Routes success to visible preview/status labels.
3. Routes failure to deterministic URL-launch fallback behavior.
