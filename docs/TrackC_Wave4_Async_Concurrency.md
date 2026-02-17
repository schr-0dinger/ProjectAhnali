# Track C Wave 4 Async Concurrency + Request Options

Status: Completed (core ABI slice)  
Date: 2026-02-17

This wave extends async networking with concurrent token surfaces, request-option wiring, and typed async JSON adapters.

## Delivered

- Multi-request tokened async state in `HttpHelper` (token-indexed cancel/progress/error/status/body stores).
- Async request-option worker wiring:
  - method, headers, body arguments flow through `http_get_route_async(...)` into worker helper calls.
  - timeout/retry remain deterministic.
- Typed async response adapters:
  - `http_async_json_field(token, key, fallback)`
  - `http_async_json_field_error(token, key)`
  - `http_async_json_array_length(token, fallback)`

## ABI Additions

- Request-option helper calls:
  - `httpRequestWithTimeout(...)`
  - `httpRequestStatusWithTimeout(...)`
  - `httpRequestErrorWithTimeout(...)`
- Token-store init helpers:
  - `ensureAsyncStores()`
  - `initAsyncToken(I)`
- Typed async JSON helper calls:
  - `getAsyncJsonField(...)`
  - `getAsyncJsonFieldError(...)`
  - `getAsyncJsonArrayLength(...)`
  - `getAsyncJsonArrayLengthError(...)`

## Deterministic Error Surfaces

- Async networking errors keep explicit code mapping (`0,1,2,3,4,7,8`).
- JSON adapter error surfaces preserve deterministic mapping for malformed payload (`5`) and missing key (`6`).

## Conformance

- `tests/test_track_c_wave4_async_networking.py`
