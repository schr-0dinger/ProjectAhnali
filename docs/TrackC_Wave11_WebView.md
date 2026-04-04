# Track C Wave 11: WebView + Deterministic Policy Surface (Program 6-B)

Status: Completed on 2026-02-18

Starts the Web tranche in Program 6-B with deterministic WebView loading and explicit policy controls.

## Capability + ABI

- Capability: `Caps.WebView`
- Runtime helper: `Lcom/ahnali/runtime/WebHelper;`
- Helper methods:
  - `setPolicy(Landroid/app/Activity;IIII)I`
  - `loadUrl(Landroid/app/Activity;Ljava/lang/String;)I`
  - `loadUrlError(Landroid/app/Activity;Ljava/lang/String;)I`

Contract:
- `setPolicy(...)` returns `1` on policy update applied, `0` on null activity context.
- `loadUrl(...)` returns `1` on success, `0` on any failure.
- `loadUrlError(...)` returns explicit error codes:
  - `0`: success
  - `1`: invalid args/context
  - `2`: cleartext URL blocked by policy (`allow_cleartext=0`)
  - `3`: runtime setup failure (`WebSettings` unavailable)
  - `4`: runtime exception

## DSL surface

- `web_set_policy(js_enabled=0, dom_storage=0, allow_file_access=0, allow_cleartext=0)`
- `web_policy(...)` (alias)
- `web_load(url)`
- `open_web(url)` (alias)
- `web_load_result(url)`
- `web_load_error(url)`

## Conformance tests

- Capability/lowering/parser/toolchain: `tests/test_track_c_wave11_webview.py`
- Visible deterministic flow: `tests/test_track_c_wave11_visible_flow.py`
- ABI and mapping snapshot coverage: `tests/test_runtime_abi_v1.py`, `tests/test_runtime_abi_snapshot.py`, `cfg/runtime_abi_snapshot_v1.json`, `cfg/capability_mapping_snapshot_v1.json`

## Visible flow

The compiled app:
1. Applies deterministic Web policy settings.
2. Attempts a cleartext web load and reads deterministic error surface.
3. Routes success/failure into visible UI labels and deterministic fallback intent path.

References: `tests/test_track_c_wave11_visible_flow.py`, `docs/capability_runtime_mapping_v1.md`, `runtime_abi_v1.md`
