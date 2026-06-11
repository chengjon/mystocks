from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Sequence

CacheState = str


@dataclass(frozen=True)
class DataSourceRequest:
    data_category: str
    params: Mapping[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timeout_ms: int | None = None
    freshness_ms: int | None = None


@dataclass(frozen=True)
class RouteDecision:
    data_category: str
    endpoint_name: str
    source: str
    endpoint_info: Mapping[str, Any]
    route_decision_id: str
    fallback_candidates: Sequence[str] = field(default_factory=tuple)
    reason: str = "best_endpoint"


@dataclass(frozen=True)
class DataSourceResult:
    data: Any
    source: str
    endpoint_name: str
    route_decision_id: str
    request_id: str
    exchange_time: Any
    received_at: str
    staleness_ms: int
    cache_state: CacheState
    quality_flags: list[str]
    latency_ms: float


class DataSourceClientError(RuntimeError):
    error_type = "DataSourceClientError"

    def __init__(
        self,
        message: str,
        *,
        request_id: str,
        endpoint_name: str | None = None,
        route_decision_id: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.request_id = request_id
        self.endpoint_name = endpoint_name
        self.route_decision_id = route_decision_id
        self.__cause__ = cause


class ProviderUnavailableError(DataSourceClientError):
    error_type = "ProviderUnavailable"


class ProviderTimeoutError(DataSourceClientError):
    error_type = "ProviderTimeout"


class RateLimitedError(DataSourceClientError):
    error_type = "RateLimited"


class CircuitOpenError(DataSourceClientError):
    error_type = "CircuitOpen"


class RegistryNotFoundError(DataSourceClientError):
    error_type = "RegistryNotFound"


class InvalidRequestError(DataSourceClientError):
    error_type = "InvalidRequest"


class DataQualityFailedError(DataSourceClientError):
    error_type = "DataQualityFailed"


class DataSourceClient(Protocol):
    def resolve_route(self, request: DataSourceRequest) -> RouteDecision: ...

    def fetch_snapshot(self, request: DataSourceRequest) -> DataSourceResult: ...

    def fetch_batch(self, requests: Sequence[DataSourceRequest]) -> list[DataSourceResult]: ...


class DataSourceTransport(Protocol):
    def post_json(self, path: str, payload: dict[str, Any], timeout_ms: int | None = None) -> Mapping[str, Any]: ...


class UrlLibJsonTransport:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def post_json(self, path: str, payload: dict[str, Any], timeout_ms: int | None = None) -> Mapping[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self._base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        timeout = None if timeout_ms is None else timeout_ms / 1000
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
        except TimeoutError:
            raise
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise exc.reason
            raise ProviderUnavailableError(
                f"Remote data-source runtime request failed: {exc}",
                request_id=str(payload.get("request_id") or ""),
                cause=exc,
            ) from exc
        return json.loads(response_body)


class LocalDataSourceClient:
    def __init__(self, manager: Any | None = None) -> None:
        if manager is None:
            from src.core.data_source.base import DataSourceManagerV2

            manager = DataSourceManagerV2()
        self._manager = manager

    def resolve_route(self, request: DataSourceRequest) -> RouteDecision:
        if not request.data_category.strip():
            raise InvalidRequestError(
                "data_category is required",
                request_id=request.request_id,
            )

        endpoint_info = self._manager.get_best_endpoint(request.data_category)
        if not endpoint_info:
            raise RegistryNotFoundError(
                f"No data-source endpoint found for category {request.data_category}",
                request_id=request.request_id,
            )

        endpoint_name = _endpoint_name(endpoint_info)
        source = _source_name(endpoint_info)
        return RouteDecision(
            data_category=request.data_category,
            endpoint_name=endpoint_name,
            source=source,
            endpoint_info=endpoint_info,
            route_decision_id=f"route-{request.request_id}-{endpoint_name}",
            fallback_candidates=tuple(_fallback_candidates(endpoint_info)),
        )

    def fetch_snapshot(self, request: DataSourceRequest) -> DataSourceResult:
        started = time.perf_counter()
        route = self.resolve_route(request)
        try:
            data = self._manager._call_endpoint(route.endpoint_info, **dict(request.params))
        except TimeoutError as exc:
            raise ProviderTimeoutError(
                f"Provider timed out for endpoint {route.endpoint_name}",
                request_id=request.request_id,
                endpoint_name=route.endpoint_name,
                route_decision_id=route.route_decision_id,
                cause=exc,
            ) from exc
        except DataSourceClientError:
            raise
        except Exception as exc:
            error_class = _typed_error_class(exc)
            raise error_class(
                f"{error_class.error_type} for endpoint {route.endpoint_name}: {exc}",
                request_id=request.request_id,
                endpoint_name=route.endpoint_name,
                route_decision_id=route.route_decision_id,
                cause=exc,
            ) from exc

        latency_ms = (time.perf_counter() - started) * 1000
        return DataSourceResult(
            data=data,
            source=route.source,
            endpoint_name=route.endpoint_name,
            route_decision_id=route.route_decision_id,
            request_id=request.request_id,
            exchange_time=_exchange_time(data),
            received_at=datetime.now(timezone.utc).isoformat(),
            staleness_ms=_staleness_ms(route.endpoint_info),
            cache_state=_cache_state(route.endpoint_info),
            quality_flags=_quality_flags(route.endpoint_info),
            latency_ms=latency_ms,
        )

    def fetch_batch(self, requests: Sequence[DataSourceRequest]) -> list[DataSourceResult]:
        return [self.fetch_snapshot(request) for request in requests]


class RemoteDataSourceClient:
    def __init__(self, base_url: str, transport: DataSourceTransport | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._transport = transport or UrlLibJsonTransport(self._base_url)

    def resolve_route(self, request: DataSourceRequest) -> RouteDecision:
        if not request.data_category.strip():
            raise InvalidRequestError(
                "data_category is required",
                request_id=request.request_id,
            )
        try:
            payload = self._transport.post_json("/routing/best", _request_payload(request), request.timeout_ms)
        except TimeoutError as exc:
            raise ProviderTimeoutError(
                "Remote data-source runtime route request timed out",
                request_id=request.request_id,
                cause=exc,
            ) from exc
        except DataSourceClientError:
            raise
        except Exception as exc:
            raise ProviderUnavailableError(
                f"Remote data-source runtime route request failed: {exc}",
                request_id=request.request_id,
                cause=exc,
            ) from exc
        return _route_decision_from_payload(request, payload)

    def fetch_snapshot(self, request: DataSourceRequest) -> DataSourceResult:
        if not request.data_category.strip():
            raise InvalidRequestError(
                "data_category is required",
                request_id=request.request_id,
            )
        try:
            payload = self._transport.post_json("/data/fetch", _request_payload(request), request.timeout_ms)
        except TimeoutError as exc:
            raise ProviderTimeoutError(
                "Remote data-source runtime fetch request timed out",
                request_id=request.request_id,
                cause=exc,
            ) from exc
        except DataSourceClientError:
            raise
        except Exception as exc:
            error_class = _typed_error_class(exc)
            raise error_class(
                f"{error_class.error_type} from remote data-source runtime: {exc}",
                request_id=request.request_id,
                cause=exc,
            ) from exc
        return _result_from_payload(request, payload)

    def fetch_batch(self, requests: Sequence[DataSourceRequest]) -> list[DataSourceResult]:
        request_list = list(requests)
        timeout_ms = max(
            (request.timeout_ms for request in request_list if request.timeout_ms is not None),
            default=None,
        )
        try:
            payload = self._transport.post_json(
                "/data/batch",
                {"requests": [_request_payload(request) for request in request_list]},
                timeout_ms,
            )
        except TimeoutError as exc:
            raise ProviderTimeoutError(
                "Remote data-source runtime batch request timed out",
                request_id="batch",
                cause=exc,
            ) from exc
        except DataSourceClientError:
            raise
        except Exception as exc:
            error_class = _typed_error_class(exc)
            raise error_class(
                f"{error_class.error_type} from remote data-source runtime batch: {exc}",
                request_id="batch",
                cause=exc,
            ) from exc

        result_payloads = payload.get("results") or []
        return [
            _result_from_payload(request, result_payload)
            for request, result_payload in zip(request_list, result_payloads, strict=False)
        ]


def create_data_source_client(
    *,
    mode: str | None = None,
    manager: Any | None = None,
    base_url: str | None = None,
    transport: DataSourceTransport | None = None,
) -> DataSourceClient:
    selected_mode = (mode or os.getenv("DATA_SOURCE_CLIENT_MODE") or "local").strip().lower()
    if selected_mode == "local":
        return LocalDataSourceClient(manager=manager)
    if selected_mode == "remote":
        resolved_base_url = base_url or os.getenv("OPENSTOCK_BASE_URL") or "http://localhost:8031"
        return RemoteDataSourceClient(base_url=resolved_base_url, transport=transport)
    raise InvalidRequestError(
        f"Unsupported DATA_SOURCE_CLIENT_MODE: {selected_mode}",
        request_id="create-data-source-client",
    )


def _request_payload(request: DataSourceRequest) -> dict[str, Any]:
    return {
        "data_category": request.data_category,
        "params": dict(request.params),
        "request_id": request.request_id,
        "timeout_ms": request.timeout_ms,
        "freshness_ms": request.freshness_ms,
    }


def _route_decision_from_payload(request: DataSourceRequest, payload: Mapping[str, Any]) -> RouteDecision:
    endpoint_info = payload.get("endpoint_info") or {
        "endpoint_name": payload.get("endpoint_name"),
        "source": payload.get("source"),
    }
    return RouteDecision(
        data_category=str(payload.get("data_category") or request.data_category),
        endpoint_name=str(payload.get("endpoint_name") or _endpoint_name(endpoint_info)),
        source=str(payload.get("source") or _source_name(endpoint_info)),
        endpoint_info=endpoint_info,
        route_decision_id=str(payload.get("route_decision_id") or f"route-{request.request_id}"),
        fallback_candidates=tuple(str(candidate) for candidate in payload.get("fallback_candidates") or []),
        reason=str(payload.get("reason") or "remote_runtime"),
    )


def _result_from_payload(request: DataSourceRequest, payload: Mapping[str, Any]) -> DataSourceResult:
    return DataSourceResult(
        data=payload.get("data"),
        source=str(payload.get("source") or "unknown"),
        endpoint_name=str(payload.get("endpoint_name") or "unknown"),
        route_decision_id=str(payload.get("route_decision_id") or f"route-{request.request_id}"),
        request_id=str(payload.get("request_id") or request.request_id),
        exchange_time=payload.get("exchange_time"),
        received_at=str(payload.get("received_at") or datetime.now(timezone.utc).isoformat()),
        staleness_ms=_coerce_non_negative_int(payload.get("staleness_ms", 0)),
        cache_state=_coerce_cache_state(payload.get("cache_state")),
        quality_flags=[str(flag) for flag in payload.get("quality_flags") or []],
        latency_ms=float(payload.get("latency_ms") or 0.0),
    )


def _endpoint_name(endpoint_info: Mapping[str, Any]) -> str:
    value = (
        endpoint_info.get("endpoint_name")
        or endpoint_info.get("name")
        or endpoint_info.get("api_name")
        or endpoint_info.get("id")
    )
    return str(value or "unknown")


def _source_name(endpoint_info: Mapping[str, Any]) -> str:
    value = endpoint_info.get("source") or endpoint_info.get("provider") or endpoint_info.get("data_source")
    return str(value or "unknown")


def _fallback_candidates(endpoint_info: Mapping[str, Any]) -> list[str]:
    candidates = endpoint_info.get("fallback_candidates") or endpoint_info.get("fallbacks") or []
    return [str(candidate) for candidate in candidates]


def _cache_state(endpoint_info: Mapping[str, Any]) -> CacheState:
    return _coerce_cache_state(endpoint_info.get("cache_state"))


def _coerce_cache_state(value: Any) -> CacheState:
    state = str(value or "miss")
    if state not in {"fresh", "stale", "miss", "bypass"}:
        return "miss"
    return state


def _quality_flags(endpoint_info: Mapping[str, Any]) -> list[str]:
    flags = endpoint_info.get("quality_flags") or []
    return [str(flag) for flag in flags]


def _staleness_ms(endpoint_info: Mapping[str, Any]) -> int:
    return _coerce_non_negative_int(endpoint_info.get("staleness_ms", 0))


def _coerce_non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _exchange_time(data: Any) -> Any:
    if isinstance(data, Mapping):
        return data.get("exchange_time")
    return None


def _typed_error_class(exc: Exception) -> type[DataSourceClientError]:
    marker = f"{exc.__class__.__name__} {exc}".lower()
    if "rate" in marker and "limit" in marker:
        return RateLimitedError
    if "circuit" in marker:
        return CircuitOpenError
    if "quality" in marker or "validation" in marker:
        return DataQualityFailedError
    return ProviderUnavailableError
