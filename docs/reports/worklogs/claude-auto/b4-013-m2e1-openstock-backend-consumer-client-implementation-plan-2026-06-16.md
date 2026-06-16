# OpenStock Backend Consumer Client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a small MyStocks backend client for consuming OpenStock runtime contracts without changing existing MyStocks routes.

**Architecture:** MyStocks will introduce a backend-only `OpenStockClient` that wraps OpenStock REST calls, maps typed runtime failures, preserves request ids, and exposes testable methods for fetch and bars calls. Route migration is excluded from this package; M2-E1 only creates the consumer boundary that later packages can call.

**Tech Stack:** Python 3.12, `httpx.AsyncClient`, pytest, pytest-asyncio, GitNexus, OPENDOG, OpenSpec.

---

## Scope

Allowed source/test paths for implementation after formal source authorization:

- Create: `web/backend/app/services/openstock_client.py`
- Create: `tests/backend/test_openstock_client.py`
- Create closeout worklog: `docs/reports/worklogs/claude-auto/b4-013-m2e1-openstock-backend-consumer-client-closeout-2026-06-16.md`

Forbidden in M2-E1:

- No route migration in `web/backend/app/api/market/market_data_request.py`.
- No technical indicator or OHLCV service changes in `web/backend/app/api/v1/strategy/indicators.py` or `web/backend/app/services/data_service.py`.
- No edits to `web/backend/app/services/data_source_factory/**`.
- No edits to `web/backend/app/services/adapters_split/**`.
- No edits to `src/adapters/**` or provider portions of `src/data_sources/**`.
- No frontend edits.
- No OpenStock repository edits.
- No provider SDK calls in MyStocks.

## File Responsibilities

| File | Responsibility |
|---|---|
| `web/backend/app/services/openstock_client.py` | Backend consumer client, config, typed exceptions, request helpers, fetch/bars/health methods, response validation. |
| `tests/backend/test_openstock_client.py` | Focused unit tests using `httpx.MockTransport`; no network and no OpenStock process required. |
| closeout worklog | Records implementation summary, gates, and confirms no route/provider behavior changed. |

## Task 1: Consumer Client Contract Tests

**Files:**

- Create: `tests/backend/test_openstock_client.py`
- Create later: `web/backend/app/services/openstock_client.py`

- [ ] **Step 1: Write failing tests for the consumer client**

Create `tests/backend/test_openstock_client.py` with:

```python
from __future__ import annotations

import json

import httpx
import pytest

from web.backend.app.services.openstock_client import (
    OpenStockClient,
    OpenStockClientConfig,
    OpenStockInvalidResponse,
    OpenStockProviderUnavailable,
    OpenStockUnsupportedCategory,
)


@pytest.mark.asyncio
async def test_fetch_posts_data_fetch_and_preserves_runtime_metadata() -> None:
    captured: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(
            {
                "method": request.method,
                "path": request.url.path,
                "payload": json.loads(request.content.decode()),
            }
        )
        return httpx.Response(
            200,
            json={
                "data": [{"symbol": "000001.SZ", "price": 12.3}],
                "source": "akshare",
                "endpoint_name": "akshare.stock_zh_a_spot",
                "data_category": "REALTIME_QUOTES",
                "request_id": "req-quotes-1",
                "route_decision_id": "route-1",
                "latency_ms": 12.4,
                "staleness_ms": 0,
            },
        )

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local", timeout_seconds=2.0),
        transport=httpx.MockTransport(handler),
    )

    result = await client.fetch(
        "REALTIME_QUOTES",
        params={"symbols": ["000001.SZ"]},
        request_id="req-quotes-1",
    )

    assert captured == [
        {
            "method": "POST",
            "path": "/data/fetch",
            "payload": {
                "data_category": "REALTIME_QUOTES",
                "params": {"symbols": ["000001.SZ"]},
                "request_id": "req-quotes-1",
            },
        }
    ]
    assert result.data == [{"symbol": "000001.SZ", "price": 12.3}]
    assert result.source == "akshare"
    assert result.data_category == "REALTIME_QUOTES"
    assert result.request_id == "req-quotes-1"
    assert result.route_decision_id == "route-1"
    assert result.latency_ms == 12.4
    assert result.staleness_ms == 0


@pytest.mark.asyncio
async def test_fetch_bars_posts_data_bars_payload() -> None:
    captured: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content.decode()))
        return httpx.Response(
            200,
            json={
                "data": [{"date": "2026-06-16", "close": 10.5}],
                "source": "eltdx",
                "endpoint_name": "eltdx.tdx_7709",
                "data_category": "KLINES",
                "request_id": "bars-1",
            },
        )

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )

    result = await client.fetch_bars(
        symbol="000001.SZ",
        period="day",
        count=120,
        request_id="bars-1",
    )

    assert captured == [
        {
            "symbol": "000001.SZ",
            "period": "day",
            "count": 120,
            "request_id": "bars-1",
        }
    ]
    assert result.data == [{"date": "2026-06-16", "close": 10.5}]
    assert result.source == "eltdx"
    assert result.data_category == "KLINES"


@pytest.mark.asyncio
async def test_provider_unavailable_is_mapped_without_raw_provider_leak() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={
                "detail": {
                    "code": "provider_unavailable",
                    "message": "Provider adapter failed while fetching data.",
                    "category": "REALTIME_QUOTES",
                    "provider": "akshare",
                    "request_id": "req-failed",
                }
            },
        )

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(OpenStockProviderUnavailable) as exc_info:
        await client.fetch("REALTIME_QUOTES", request_id="req-failed")

    error = exc_info.value
    assert error.code == "provider_unavailable"
    assert error.category == "REALTIME_QUOTES"
    assert error.provider == "akshare"
    assert error.request_id == "req-failed"
    assert "stack" not in str(error).lower()


@pytest.mark.asyncio
async def test_unsupported_category_is_mapped_to_typed_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "Unsupported data_category: LHB"})

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(OpenStockUnsupportedCategory) as exc_info:
        await client.fetch("LHB", request_id="lhb-1")

    assert exc_info.value.category == "LHB"
    assert exc_info.value.request_id == "lhb-1"


@pytest.mark.asyncio
async def test_invalid_success_payload_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"source": "akshare"})

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(OpenStockInvalidResponse):
        await client.fetch("REALTIME_QUOTES")
```

- [ ] **Step 2: Run tests to verify they fail because the module is missing**

Run:

```bash
pytest tests/backend/test_openstock_client.py -q
```

Expected: import failure for `web.backend.app.services.openstock_client`.

## Task 2: Minimal OpenStock Client Implementation

**Files:**

- Create: `web/backend/app/services/openstock_client.py`
- Test: `tests/backend/test_openstock_client.py`

- [ ] **Step 1: Implement the client module**

Create `web/backend/app/services/openstock_client.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import httpx


@dataclass(frozen=True)
class OpenStockClientConfig:
    base_url: str
    timeout_seconds: float = 5.0


@dataclass(frozen=True)
class OpenStockFetchResult:
    data: Any
    source: str | None
    endpoint_name: str | None
    data_category: str | None
    request_id: str | None
    route_decision_id: str | None = None
    latency_ms: float | None = None
    staleness_ms: float | None = None
    raw: Mapping[str, Any] | None = None


class OpenStockClientError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "openstock_client_error",
        category: str | None = None,
        provider: str | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.category = category
        self.provider = provider
        self.request_id = request_id


class OpenStockProviderUnavailable(OpenStockClientError):
    pass


class OpenStockUnsupportedCategory(OpenStockClientError):
    pass


class OpenStockTimeout(OpenStockClientError):
    pass


class OpenStockInvalidResponse(OpenStockClientError):
    pass


class OpenStockClient:
    def __init__(
        self,
        config: OpenStockClientConfig,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url.rstrip("/"),
            timeout=config.timeout_seconds,
            transport=transport,
        )

    async def fetch(
        self,
        data_category: str,
        *,
        params: Mapping[str, Any] | None = None,
        request_id: str | None = None,
    ) -> OpenStockFetchResult:
        payload: dict[str, Any] = {"data_category": data_category}
        if params is not None:
            payload["params"] = dict(params)
        if request_id is not None:
            payload["request_id"] = request_id
        response = await self._post("/data/fetch", payload)
        return self._parse_fetch_result(response, category=data_category, request_id=request_id)

    async def fetch_bars(
        self,
        *,
        symbol: str,
        period: str = "day",
        count: int = 100,
        request_id: str | None = None,
    ) -> OpenStockFetchResult:
        payload: dict[str, Any] = {
            "symbol": symbol,
            "period": period,
            "count": count,
        }
        if request_id is not None:
            payload["request_id"] = request_id
        response = await self._post("/data/bars", payload)
        return self._parse_fetch_result(response, category="KLINES", request_id=request_id)

    async def ready(self) -> Mapping[str, Any]:
        try:
            response = await self._client.get("/health/ready")
        except httpx.TimeoutException as exc:
            raise OpenStockTimeout("OpenStock readiness request timed out", code="openstock_timeout") from exc
        self._raise_for_error(response, category=None, request_id=None)
        body = response.json()
        if not isinstance(body, Mapping):
            raise OpenStockInvalidResponse("OpenStock readiness response is not an object")
        return body

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _post(self, path: str, payload: Mapping[str, Any]) -> httpx.Response:
        try:
            response = await self._client.post(path, json=dict(payload))
        except httpx.TimeoutException as exc:
            raise OpenStockTimeout(
                "OpenStock request timed out",
                code="openstock_timeout",
                category=str(payload.get("data_category") or ""),
                request_id=str(payload.get("request_id") or ""),
            ) from exc
        self._raise_for_error(
            response,
            category=str(payload.get("data_category") or ""),
            request_id=str(payload.get("request_id") or ""),
        )
        return response

    def _parse_fetch_result(
        self,
        response: httpx.Response,
        *,
        category: str | None,
        request_id: str | None,
    ) -> OpenStockFetchResult:
        body = response.json()
        if not isinstance(body, Mapping) or "data" not in body:
            raise OpenStockInvalidResponse(
                "OpenStock fetch response is missing data",
                category=category,
                request_id=request_id,
            )
        return OpenStockFetchResult(
            data=body["data"],
            source=_optional_str(body.get("source")),
            endpoint_name=_optional_str(body.get("endpoint_name")),
            data_category=_optional_str(body.get("data_category")),
            request_id=_optional_str(body.get("request_id")),
            route_decision_id=_optional_str(body.get("route_decision_id")),
            latency_ms=_optional_float(body.get("latency_ms")),
            staleness_ms=_optional_float(body.get("staleness_ms")),
            raw=body,
        )

    def _raise_for_error(
        self,
        response: httpx.Response,
        *,
        category: str | None,
        request_id: str | None,
    ) -> None:
        if response.status_code < 400:
            return

        detail = _response_detail(response)
        if isinstance(detail, Mapping):
            code = _optional_str(detail.get("code")) or "openstock_error"
            message = _optional_str(detail.get("message")) or "OpenStock request failed"
            error_category = _optional_str(detail.get("category")) or category
            provider = _optional_str(detail.get("provider"))
            error_request_id = _optional_str(detail.get("request_id")) or request_id
            if code == "provider_unavailable":
                raise OpenStockProviderUnavailable(
                    message,
                    code=code,
                    category=error_category,
                    provider=provider,
                    request_id=error_request_id,
                )
            raise OpenStockClientError(
                message,
                code=code,
                category=error_category,
                provider=provider,
                request_id=error_request_id,
            )

        message = str(detail)
        if response.status_code == 422 and "Unsupported data_category" in message:
            raise OpenStockUnsupportedCategory(
                message,
                code="unsupported_data_category",
                category=category,
                request_id=request_id,
            )
        raise OpenStockClientError(
            message,
            code=f"openstock_http_{response.status_code}",
            category=category,
            request_id=request_id,
        )


def _response_detail(response: httpx.Response) -> Any:
    try:
        body = response.json()
    except ValueError:
        return response.text
    if isinstance(body, Mapping) and "detail" in body:
        return body["detail"]
    return body


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _optional_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None
```

- [ ] **Step 2: Run focused tests**

Run:

```bash
pytest tests/backend/test_openstock_client.py -q
```

Expected: all tests pass.

## Task 3: Static Validation And Scope Guard

**Files:**

- Verify only: `web/backend/app/services/openstock_client.py`
- Verify only: `tests/backend/test_openstock_client.py`

- [ ] **Step 1: Run py_compile**

Run:

```bash
python -m py_compile web/backend/app/services/openstock_client.py tests/backend/test_openstock_client.py
```

Expected: command exits 0.

- [ ] **Step 2: Run ruff on focused files**

Run:

```bash
python -m ruff check web/backend/app/services/openstock_client.py tests/backend/test_openstock_client.py
```

Expected: `All checks passed!`

- [ ] **Step 3: Confirm forbidden files are untouched**

Run:

```bash
git diff --name-only -- web/backend/app/api/market/market_data_request.py web/backend/app/api/v1/strategy/indicators.py web/backend/app/services/data_service.py web/backend/app/services/data_source_factory web/backend/app/services/adapters_split src/adapters src/data_sources web/frontend /opt/claude/openstock
```

Expected: no output.

## Task 4: Commit Gate

**Files:**

- Stage only:
  - `web/backend/app/services/openstock_client.py`
  - `tests/backend/test_openstock_client.py`
  - closeout worklog
  - FUNCTION_TREE governance files if the node status is advanced during implementation

- [ ] **Step 1: Run GitNexus staged verification**

Run:

```bash
node .gitnexus/run.cjs verify-staged --repo mystocks --cwd /opt/claude/mystocks_spec --json
node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks --cwd /opt/claude/mystocks_spec
```

Expected: changed scope limited to the OpenStock client, focused test, and closeout/governance files; risk should be low unless a route file is touched, which is forbidden in M2-E1.

- [ ] **Step 2: Run OPENDOG verification check**

Run:

```bash
OPENDOG_HOME=/root/.opendog /opt/claude/opendog/target/release/opendog verification --id mystocks --json
```

Expected: no `cleanup_blockers` and no `failing_runs`.

- [ ] **Step 3: Commit**

Run:

```bash
git add web/backend/app/services/openstock_client.py tests/backend/test_openstock_client.py docs/reports/worklogs/claude-auto/b4-013-m2e1-openstock-backend-consumer-client-closeout-2026-06-16.md
git commit -m "B4.013-M2-E1: add OpenStock backend consumer client"
```

Expected: commit contains no route migration and no provider adapter changes.

## Self-Review

- Spec coverage: covers the M1-E3 requirement for a MyStocks backend OpenStock consumer client, typed error mapping, request id preservation, and route compatibility preservation.
- Scope check: excludes route migration and provider contract gaps; those belong to M2-E2 and OpenStock-P1.
- Placeholder scan: no placeholder tasks; M2-E1 includes exact files, test code, implementation code, and commands.
- Type consistency: tests and implementation use the same `OpenStockClient`, `OpenStockClientConfig`, `OpenStockFetchResult`, and typed exceptions.
