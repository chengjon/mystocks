from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import httpx


DEFAULT_SUPPORTED_CATEGORIES = ("REALTIME_QUOTES", "KLINES")


@dataclass(frozen=True)
class OpenStockClientConfig:
    base_url: str
    timeout_seconds: float = 5.0
    supported_categories: Sequence[str] = DEFAULT_SUPPORTED_CATEGORIES
    headers: Mapping[str, str] | None = None


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
        self._supported_categories = frozenset(config.supported_categories)
        client_kwargs: dict[str, Any] = {
            "base_url": config.base_url.rstrip("/"),
            "timeout": config.timeout_seconds,
            "transport": transport,
        }
        if config.headers:
            client_kwargs["headers"] = dict(config.headers)
        self._client = httpx.AsyncClient(**client_kwargs)

    async def fetch(
        self,
        data_category: str,
        *,
        params: Mapping[str, Any] | None = None,
        request_id: str | None = None,
    ) -> OpenStockFetchResult:
        self._validate_category(data_category, request_id=request_id)
        payload: dict[str, Any] = {"data_category": data_category}
        if params is not None:
            payload["params"] = dict(params)
        if request_id is not None:
            payload["request_id"] = request_id
        response = await self._post(
            "/data/fetch",
            payload,
            category=data_category,
            request_id=request_id,
        )
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
        response = await self._post(
            "/data/bars",
            payload,
            category="KLINES",
            request_id=request_id,
        )
        return self._parse_fetch_result(response, category="KLINES", request_id=request_id)

    async def ready(self) -> bool:
        try:
            response = await self._client.get("/health")
        except httpx.HTTPError:
            return False
        return response.status_code < 500

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> OpenStockClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    def _validate_category(self, data_category: str, *, request_id: str | None) -> None:
        if data_category not in self._supported_categories:
            raise OpenStockUnsupportedCategory(
                f"Unsupported data_category: {data_category}",
                code="unsupported_data_category",
                category=data_category,
                request_id=request_id,
            )

    async def _post(
        self,
        path: str,
        payload: Mapping[str, Any],
        *,
        category: str | None,
        request_id: str | None,
    ) -> httpx.Response:
        try:
            response = await self._client.post(path, json=dict(payload))
        except httpx.TimeoutException as exc:
            raise OpenStockTimeout(
                "OpenStock request timed out",
                code="openstock_timeout",
                category=category,
                request_id=request_id,
            ) from exc
        self._raise_for_error(response, category=category, request_id=request_id)
        return response

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
            if _is_unsupported_category(response.status_code, code, message):
                raise OpenStockUnsupportedCategory(
                    message,
                    code="unsupported_data_category",
                    category=error_category,
                    provider=provider,
                    request_id=error_request_id,
                )
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

    def _parse_fetch_result(
        self,
        response: httpx.Response,
        *,
        category: str | None,
        request_id: str | None,
    ) -> OpenStockFetchResult:
        try:
            body = response.json()
        except ValueError as exc:
            raise OpenStockInvalidResponse(
                "OpenStock fetch response is not valid JSON",
                category=category,
                request_id=request_id,
            ) from exc
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


def _response_detail(response: httpx.Response) -> Any:
    try:
        body = response.json()
    except ValueError:
        return response.text
    if isinstance(body, Mapping) and "detail" in body:
        return body["detail"]
    return body


def _is_unsupported_category(status_code: int, code: str, message: str) -> bool:
    if code in {"unsupported_data_category", "unsupported_category"}:
        return True
    return status_code == 422 and "Unsupported data_category" in message


def _optional_str(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _optional_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


__all__ = [
    "OpenStockClient",
    "OpenStockClientConfig",
    "OpenStockClientError",
    "OpenStockFetchResult",
    "OpenStockInvalidResponse",
    "OpenStockProviderUnavailable",
    "OpenStockTimeout",
    "OpenStockUnsupportedCategory",
]
