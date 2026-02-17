from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class HttpRequestOptions:
    method: str = "GET"
    headers: str = ""
    body: str = ""
    timeout_ms: int = 8000
    retries: int = 0
    backoff_ms: int = 0
    retry_policy: str = "fixed"  # fixed|exponential
    use_tenacity: bool = False


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    error_code: int


def parse_headers(raw_headers: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in str(raw_headers).splitlines():
        item = line.strip()
        if not item:
            continue
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        out[key] = value
    return out


def _normalized_method(method: str) -> str:
    value = str(method or "GET").strip().upper()
    return value or "GET"


def _compute_backoff_ms(base_ms: int, attempt: int, policy: str) -> int:
    base = max(0, int(base_ms))
    if policy == "exponential":
        return base * (2 ** max(0, int(attempt)))
    return base


def _import_httpx():
    try:
        import httpx  # type: ignore

        return httpx
    except Exception:
        return None


def _request_once(url: str, fallback: str, options: HttpRequestOptions) -> HttpResult:
    httpx = _import_httpx()
    if httpx is None:
        return HttpResult(status=-1, body=str(fallback), error_code=2)

    method = _normalized_method(options.method)
    if method not in {"GET", "POST"}:
        return HttpResult(status=-1, body=str(fallback), error_code=1)

    timeout = max(1, int(options.timeout_ms)) / 1000.0
    headers = parse_headers(options.headers)
    content = str(options.body) if method == "POST" else ""

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.request(method, str(url), headers=headers, content=content)
    except Exception:
        return HttpResult(status=-1, body=str(fallback), error_code=2)

    if int(response.status_code) != 200:
        return HttpResult(status=int(response.status_code), body=str(fallback), error_code=3)

    text = response.text or ""
    if not text:
        return HttpResult(status=200, body=str(fallback), error_code=4)

    return HttpResult(status=200, body=text, error_code=0)


def sync_http_request(url: str, fallback: str = "", options: HttpRequestOptions | None = None) -> HttpResult:
    opts = options or HttpRequestOptions()
    attempts = max(0, int(opts.retries)) + 1

    # Optional tenacity path; deterministic policy parameters remain explicit.
    if opts.use_tenacity:
        try:
            from tenacity import Retrying, stop_after_attempt, wait_fixed, wait_exponential  # type: ignore

            wait = wait_fixed(max(0, int(opts.backoff_ms)) / 1000.0)
            if str(opts.retry_policy) == "exponential":
                wait = wait_exponential(multiplier=max(0, int(opts.backoff_ms)) / 1000.0, min=0)

            final_result = HttpResult(status=-1, body=str(fallback), error_code=2)
            for attempt in Retrying(stop=stop_after_attempt(attempts), wait=wait, reraise=False):
                with attempt:
                    result = _request_once(url, fallback, opts)
                    final_result = result
                    if result.error_code == 0:
                        return result
                    raise RuntimeError(f"deterministic-retry:{result.error_code}")
            return final_result
        except Exception:
            # Fall through to explicit loop to keep behavior deterministic when tenacity is absent.
            pass

    result = HttpResult(status=-1, body=str(fallback), error_code=2)
    for attempt in range(attempts):
        result = _request_once(url, fallback, opts)
        if result.error_code == 0:
            return result
        if attempt + 1 < attempts:
            delay_ms = _compute_backoff_ms(opts.backoff_ms, attempt, str(opts.retry_policy))
            if delay_ms > 0:
                # Host-side helper only; compile/runtime contracts stay explicit.
                import time

                time.sleep(delay_ms / 1000.0)
    return result


async def async_http_request(
    url: str,
    fallback: str = "",
    options: HttpRequestOptions | None = None,
) -> HttpResult:
    opts = options or HttpRequestOptions()
    attempts = max(0, int(opts.retries)) + 1

    httpx = _import_httpx()
    if httpx is None:
        return HttpResult(status=-1, body=str(fallback), error_code=2)

    method = _normalized_method(opts.method)
    if method not in {"GET", "POST"}:
        return HttpResult(status=-1, body=str(fallback), error_code=1)

    timeout = max(1, int(opts.timeout_ms)) / 1000.0
    headers = parse_headers(opts.headers)
    content = str(opts.body) if method == "POST" else ""

    result = HttpResult(status=-1, body=str(fallback), error_code=2)
    for attempt in range(attempts):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(method, str(url), headers=headers, content=content)
        except Exception:
            result = HttpResult(status=-1, body=str(fallback), error_code=2)
        else:
            status = int(response.status_code)
            if status != 200:
                result = HttpResult(status=status, body=str(fallback), error_code=3)
            else:
                body = response.text or ""
                if not body:
                    result = HttpResult(status=200, body=str(fallback), error_code=4)
                else:
                    return HttpResult(status=200, body=body, error_code=0)

        if attempt + 1 < attempts:
            delay_ms = _compute_backoff_ms(opts.backoff_ms, attempt, str(opts.retry_policy))
            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000.0)

    return result
