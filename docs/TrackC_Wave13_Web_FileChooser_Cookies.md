# Track C Wave 13: Web File Chooser + Cookie Manager (Program 6-B)

Status: Completed on 2026-02-18

Extends the Web tranche with deterministic file chooser dispatch and cookie-manager surfaces.

## Capability + ABI

- Capability: `Caps.WebView`
- Runtime helper: `Lcom/ahnali/runtime/WebHelper;`
- Helper methods:
  - `chooseFile(Landroid/app/Activity;Ljava/lang/String;)I`
  - `chooseFileError(Landroid/app/Activity;Ljava/lang/String;)I`
  - `setCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `setCookieError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I`
  - `getCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`
  - `getCookieError(Landroid/app/Activity;Ljava/lang/String;)I`

Contract:
- `chooseFile(...)` returns `1` on success, `0` on any failure.
- `chooseFileError(...)` error codes:
  - `0`: success
  - `1`: invalid args/context
  - `3`: chooser handler not found
  - `4`: runtime exception
- `setCookie(...)` returns `1` on success, `0` on any failure.
- `setCookieError(...)` error codes:
  - `0`: success
  - `1`: invalid args/context
  - `3`: cookie manager unavailable
  - `4`: runtime exception
- `getCookie(...)` returns cookie value or provided fallback deterministically.
- `getCookieError(...)` error codes:
  - `0`: cookie available
  - `1`: invalid args/context
  - `3`: cookie manager unavailable or cookie missing
  - `4`: runtime exception

## DSL surface

- `web_choose_file(mime_type="*/*")`
- `web_file_chooser(mime_type="*/*")` (alias)
- `web_choose_file_result(mime_type="*/*")`
- `web_choose_file_error(mime_type="*/*")`
- `web_cookie_set(url, cookie)`
- `web_set_cookie(url, cookie)` (alias)
- `web_cookie_set_result(url, cookie)`
- `web_cookie_set_error(url, cookie)`
- `web_cookie_get(url, fallback="")`
- `web_get_cookie(url, fallback="")` (alias)
- `web_cookie_get_error(url)`

## Conformance tests

- Capability/lowering/parser/toolchain: `tests/test_track_c_wave13_web_file_cookie.py`
- Visible deterministic flow: `tests/test_track_c_wave13_visible_flow.py`
- ABI and mapping snapshot coverage: `tests/test_runtime_abi_v1.py`, `tests/test_runtime_abi_snapshot.py`, `cfg/runtime_abi_snapshot_v1.json`, `cfg/capability_mapping_snapshot_v1.json`

## Visible flow

The compiled app:
1. Seeds a deterministic cookie value.
2. Attempts file chooser dispatch and reads deterministic chooser error surface.
3. Routes success/failure into visible labels and fallback intent path.

References: `tests/test_track_c_wave13_visible_flow.py`, `docs/capability_runtime_mapping_v1.md`, `runtime_abi_v1.md`
