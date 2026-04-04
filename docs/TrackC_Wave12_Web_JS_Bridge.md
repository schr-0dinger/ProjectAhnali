# Track C Wave 12: Web JS Bridge (Policy-Constrained)

Status: Completed on 2026-02-18

Extends the Web tranche with deterministic JavaScript bridge registration behind explicit policy constraints.

## Capability + ABI

- Capability: `Caps.WebView`
- Runtime helper: `Lcom/ahnali/runtime/WebHelper;`
- Helper methods:
  - `addJsBridge(Landroid/app/Activity;Ljava/lang/String;)I`
  - `addJsBridgeError(Landroid/app/Activity;Ljava/lang/String;)I`

Contract:
- `addJsBridge(...)` returns `1` on success, `0` on any failure.
- `addJsBridgeError(...)` returns explicit error codes:
  - `0`: success
  - `1`: invalid args/context
  - `2`: JS bridge blocked by policy (`js_enabled=0`)
  - `3`: runtime setup failure (`WebSettings` unavailable)
  - `4`: runtime exception
  - `5`: bridge-name policy violation (must start with `ahnali_`)

## DSL surface

- `web_add_js_bridge(bridge_name)`
- `web_register_js_bridge(bridge_name)` (alias)
- `web_add_js_bridge_result(bridge_name)`
- `web_add_js_bridge_error(bridge_name)`

## Conformance tests

- Capability/lowering/parser/toolchain: `tests/test_track_c_wave12_web_js_bridge.py`
- Visible deterministic flow: `tests/test_track_c_wave12_visible_flow.py`
- ABI and mapping snapshot coverage: `tests/test_runtime_abi_v1.py`, `tests/test_runtime_abi_snapshot.py`, `cfg/runtime_abi_snapshot_v1.json`, `cfg/capability_mapping_snapshot_v1.json`

## Visible flow

The compiled app:
1. Sets a policy disabling JS bridge registration.
2. Attempts bridge registration and reads deterministic error surface.
3. Routes success/failure into visible labels and fallback intent path.

References: `tests/test_track_c_wave12_visible_flow.py`, `docs/capability_runtime_mapping_v1.md`, `runtime_abi_v1.md`
