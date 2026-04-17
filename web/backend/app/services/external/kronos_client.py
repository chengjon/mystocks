"""Thin HTTP client for the external Kronos service."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx


@dataclass
class _CacheEntry:
    value: Dict[str, Any]
    expires_at: datetime


class KronosClientError(RuntimeError):
    """Client-visible error raised for invalid Kronos requests or responses."""

    def __init__(self, message: str, *, code: str = "KRONOS_CLIENT_ERROR", status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class KronosServiceUnavailableError(RuntimeError):
    """Raised when the external Kronos service is unavailable or times out."""

    def __init__(self, message: str, *, code: str = "KRONOS_SERVICE_UNAVAILABLE", status_code: int = 503) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class KronosServiceClient:
    """Thin HTTP client for Kronos outbound integration."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_interval_seconds: Optional[float] = None,
        cache_ttl_seconds: Optional[int] = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("KRONOS_BASE_URL", "")).rstrip("/")
        self.timeout = timeout if timeout is not None else float(os.getenv("KRONOS_TIMEOUT_SECONDS", "5.0"))
        self.max_retries = max_retries if max_retries is not None else int(os.getenv("KRONOS_MAX_RETRIES", "3"))
        self.retry_interval_seconds = (
            retry_interval_seconds
            if retry_interval_seconds is not None
            else float(os.getenv("KRONOS_RETRY_INTERVAL_SECONDS", "0.1"))
        )
        self.cache_ttl_seconds = (
            cache_ttl_seconds if cache_ttl_seconds is not None else int(os.getenv("KRONOS_CACHE_TTL_SECONDS", "300"))
        )
        self._cache: dict[str, _CacheEntry] = {}

    async def predict_ohlcv(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a forecasting request to Kronos."""
        return await self._post_json("/v1/kronos/predict", payload, use_cache=True)

    async def encode_kline(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit an encoding request to Kronos."""
        return await self._post_json("/v1/kronos/encode", payload, use_cache=True)

    async def get_status(self) -> Dict[str, Any]:
        """Fetch the current runtime status from Kronos."""
        return await self._get_json("/v1/kronos/status", use_cache=False)

    def _build_cache_key(self, endpoint: str, payload: Dict[str, Any]) -> str:
        return f"{endpoint}:{json.dumps(payload, sort_keys=True, separators=(',', ':'))}"

    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(key)
        if entry is None:
            return None

        if entry.expires_at <= datetime.now(timezone.utc):
            self._cache.pop(key, None)
            return None

        cached_value = dict(entry.value)
        meta = dict(cached_value.get("meta", {}))
        meta["cached"] = True
        cached_value["meta"] = meta
        return cached_value

    def _set_cached(self, key: str, value: Dict[str, Any]) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.cache_ttl_seconds)
        self._cache[key] = _CacheEntry(value=dict(value), expires_at=expires_at)

    async def _post_json(self, endpoint: str, payload: Dict[str, Any], *, use_cache: bool) -> Dict[str, Any]:
        return await self._request_json("POST", endpoint, payload=payload, use_cache=use_cache)

    async def _get_json(self, endpoint: str, *, use_cache: bool) -> Dict[str, Any]:
        return await self._request_json("GET", endpoint, payload=None, use_cache=use_cache)

    async def _request_json(
        self,
        method: str,
        endpoint: str,
        *,
        payload: Optional[Dict[str, Any]],
        use_cache: bool,
    ) -> Dict[str, Any]:
        if not self.base_url:
            raise KronosServiceUnavailableError("KRONOS_BASE_URL is not configured", code="KRONOS_BASE_URL_MISSING")

        normalized_payload = payload or {}
        cache_key = self._build_cache_key(f"{method}:{endpoint}", normalized_payload)
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method == "POST":
                        response = await client.post(f"{self.base_url}{endpoint}", json=normalized_payload)
                    else:
                        response = await client.get(f"{self.base_url}{endpoint}")
                result = self._parse_response(response)
                if use_cache:
                    self._set_cached(cache_key, result)
                return result
            except KronosClientError:
                raise
            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                await self._sleep_retry()
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if 400 <= exc.response.status_code < 500:
                    raise self._map_http_error(exc.response) from exc
                if attempt >= self.max_retries:
                    raise self._map_http_error(exc.response) from exc
                await self._sleep_retry()

        raise KronosServiceUnavailableError(
            f"Kronos service request failed after {self.max_retries} attempts: {last_error}",
            code="KRONOS_SERVICE_UNAVAILABLE",
        ) from last_error

    async def _sleep_retry(self) -> None:
        import asyncio

        await asyncio.sleep(self.retry_interval_seconds)

    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            raise

        try:
            payload = response.json()
        except ValueError as exc:
            raise KronosClientError("Kronos returned non-JSON response", code="KRONOS_INVALID_RESPONSE") from exc

        if not isinstance(payload, dict):
            raise KronosClientError("Kronos returned an unexpected payload shape", code="KRONOS_INVALID_RESPONSE")

        success = payload.get("success", True)
        if success is False:
            error_code = str(payload.get("code", "KRONOS_REMOTE_ERROR"))
            message = str(payload.get("message", "Kronos request failed"))
            status_code = 503 if error_code in {"SERVICE_DOWN", "TIMEOUT", "QUEUE_FULL", "GPU_ERROR"} else 400
            error_cls = KronosServiceUnavailableError if status_code >= 500 else KronosClientError
            raise error_cls(message, code=error_code, status_code=status_code)

        result = {
            "data": payload.get("data", {}),
            "meta": payload.get("meta", {}),
            "request_id": payload.get("request_id"),
            "timestamp": payload.get("timestamp"),
            "message": payload.get("message", "ok"),
        }
        return result

    def _map_http_error(self, response: httpx.Response) -> KronosClientError | KronosServiceUnavailableError:
        try:
            payload = response.json()
        except ValueError:
            payload = {}

        code = str(payload.get("code", "KRONOS_HTTP_ERROR"))
        message = str(payload.get("message", response.text or "Kronos service returned an error"))
        if response.status_code >= 500:
            return KronosServiceUnavailableError(message, code=code, status_code=response.status_code)
        return KronosClientError(message, code=code, status_code=response.status_code)


_KRONOS_CLIENT: KronosServiceClient | None = None


def get_kronos_client() -> KronosServiceClient:
    """Return a process-local singleton Kronos client."""
    global _KRONOS_CLIENT
    if _KRONOS_CLIENT is None:
        _KRONOS_CLIENT = KronosServiceClient()
    return _KRONOS_CLIENT
