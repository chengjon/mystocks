"""Distributed Windows bridge adapter with a repo-owned qmt live-contract boundary."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping

import httpx

from app.services.data_source_interface import IDataSource, HealthStatus, HealthStatusEnum
from src.utils.trading_runtime_config import (
    get_trading_qmt_bridge_contract_version,
    get_trading_qmt_bridge_token,
)

logger = __import__("logging").getLogger(__name__)

BRIDGE_CONTRACT_VERSION_HEADER = "X-Bridge-Contract-Version"
BRIDGE_AUTH_SCHEME = "Bearer"
QMT_PROVIDER_NAME = "qmt"
QMT_SUBMIT_ORDER_METHOD = "submit_order"
LIVE_BRIDGE_AUTH_FAILED = "live_bridge_auth_failed"
LIVE_BRIDGE_UNSUPPORTED_CONTRACT_VERSION = "live_bridge_unsupported_contract_version"
LIVE_BRIDGE_UNSUPPORTED_METHOD = "live_bridge_unsupported_method"
LIVE_BRIDGE_UNAVAILABLE = "live_bridge_unavailable"
LIVE_BRIDGE_INVALID_RESULT = "live_bridge_invalid_result"

_HTTP_AUTH_FAILURES = {401, 403}
_HTTP_UNSUPPORTED_METHOD_FAILURES = {404, 405}
_HTTP_VERSION_FAILURES = {400, 406, 409, 412, 426}
_ALLOWED_PROVIDER_METHODS = {QMT_PROVIDER_NAME: frozenset({QMT_SUBMIT_ORDER_METHOD})}


class MultiSourceBridgeAdapter(IDataSource):
    """多源桥接适配器 - 负责调度远程 Windows 代理。"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "distributed_bridge"
        self.providers = dict(config.get("providers", {}))
        self.timeout = float(config.get("timeout", 30.0))
        self.bridge_token = _extract_config_str(
            config,
            "bridge_token",
            "auth_token",
        ) or get_trading_qmt_bridge_token()
        self.bridge_contract_version = _extract_config_str(
            config,
            "bridge_contract_version",
        ) or get_trading_qmt_bridge_contract_version()

    async def get_data(self, endpoint: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """按批准的 provider/method 白名单触发远程 Windows `qmt` 任务。"""
        provider_name, method = self._parse_endpoint(endpoint)
        allowlist_failure = self._validate_execute_target(provider_name, method)
        if allowlist_failure is not None:
            return allowlist_failure
        config_failure = self._validate_contract_configuration(provider_name=provider_name, method=method)
        if config_failure is not None:
            return config_failure

        base_url = self._resolve_provider_url(provider_name)
        if not base_url:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method=method,
                reason_code=LIVE_BRIDGE_UNAVAILABLE,
                reason_detail=f"Provider '{provider_name}' not configured in registry",
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("Triggering remote task: %s via %s", provider_name, method)
                response = await client.post(
                    f"{base_url}/api/v1/task/execute",
                    json={
                        "provider": provider_name,
                        "method": method,
                        "params": params or {},
                        "write_to_nas": True,
                    },
                    headers=self._build_contract_headers(),
                )
        except httpx.RequestError as exc:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method=method,
                reason_code=LIVE_BRIDGE_UNAVAILABLE,
                reason_detail=str(exc),
            )

        return self._normalize_execute_response(
            response=response,
            provider_name=provider_name,
            method=method,
        )

    async def get_task_result(self, provider_name: str, task_id: str) -> Dict[str, Any]:
        """按 `task_id` 轮询远程 Windows `qmt` 代理结果。"""
        allowlist_failure = self._validate_result_target(provider_name=provider_name, task_id=task_id)
        if allowlist_failure is not None:
            return allowlist_failure
        config_failure = self._validate_contract_configuration(
            provider_name=provider_name,
            method="task_result",
            task_id=task_id,
        )
        if config_failure is not None:
            return config_failure

        base_url = self._resolve_provider_url(provider_name)
        if not base_url:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method="task_result",
                task_id=task_id,
                reason_code=LIVE_BRIDGE_UNAVAILABLE,
                reason_detail=f"Provider '{provider_name}' not configured in registry",
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("Polling remote task result: %s %s", provider_name, task_id)
                response = await client.get(
                    f"{base_url}/api/v1/task/result/{task_id}",
                    headers=self._build_contract_headers(),
                )
        except httpx.RequestError as exc:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method="task_result",
                task_id=task_id,
                reason_code=LIVE_BRIDGE_UNAVAILABLE,
                reason_detail=str(exc),
            )

        return self._normalize_result_response(
            response=response,
            provider_name=provider_name,
            task_id=task_id,
        )

    async def health_check(self) -> HealthStatus:
        """检查所有 Provider 的在线状态。"""
        results = []
        async with httpx.AsyncClient(timeout=2.0) as client:
            for name, url in self.providers.items():
                try:
                    resp = await client.get(f"{url}/health")
                    if resp.status_code == 200:
                        results.append(f"{name}:OK")
                except Exception:
                    results.append(f"{name}:OFFLINE")

        return HealthStatus(
            status=HealthStatusEnum.HEALTHY if "OK" in "".join(results) else HealthStatusEnum.FAILED,
            response_time=0,
            message=" | ".join(results),
            timestamp=datetime.now(),
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Expose bridge runtime metrics without leaking the configured bearer token."""
        return {
            "source_type": self.source_type,
            "provider_count": len(self.providers),
            "provider_names": sorted(self.providers.keys()),
            "timeout_seconds": self.timeout,
            "bridge_contract_version": self.bridge_contract_version,
            "bridge_auth_configured": bool(self.bridge_token),
        }

    def _parse_endpoint(self, endpoint: str) -> tuple[str, str]:
        try:
            provider_name, method = endpoint.split("/")
        except ValueError as exc:
            raise ValueError(f"Invalid endpoint format: {endpoint}. Use 'provider/method'.") from exc
        return provider_name.strip().lower(), method.strip()

    def _build_contract_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"{BRIDGE_AUTH_SCHEME} {self.bridge_token}",
            BRIDGE_CONTRACT_VERSION_HEADER: self.bridge_contract_version,
        }

    def _validate_contract_configuration(
        self,
        *,
        provider_name: str,
        method: str,
        task_id: str | None = None,
    ) -> Dict[str, Any] | None:
        if self.bridge_token:
            return None
        return self._build_bridge_failure(
            provider_name=provider_name,
            method=method,
            task_id=task_id,
            reason_code=LIVE_BRIDGE_AUTH_FAILED,
            reason_detail="TRADING_QMT_BRIDGE_TOKEN is not configured",
        )

    def _validate_execute_target(self, provider_name: str, method: str) -> Dict[str, Any] | None:
        allowed_methods = _ALLOWED_PROVIDER_METHODS.get(provider_name)
        if allowed_methods and method in allowed_methods:
            return None
        return self._build_bridge_failure(
            provider_name=provider_name,
            method=method,
            reason_code=LIVE_BRIDGE_UNSUPPORTED_METHOD,
            reason_detail=f"Unsupported bridge execute target: {provider_name}/{method}",
        )

    def _validate_result_target(self, *, provider_name: str, task_id: str) -> Dict[str, Any] | None:
        if provider_name == QMT_PROVIDER_NAME:
            return None
        return self._build_bridge_failure(
            provider_name=provider_name,
            method="task_result",
            task_id=task_id,
            reason_code=LIVE_BRIDGE_UNSUPPORTED_METHOD,
            reason_detail=f"Unsupported bridge result target: {provider_name}",
        )

    def _normalize_execute_response(
        self,
        *,
        response: httpx.Response,
        provider_name: str,
        method: str,
    ) -> Dict[str, Any]:
        payload = _safe_json_body(response)
        if not isinstance(payload, Mapping):
            return self._build_bridge_failure(
                provider_name=provider_name,
                method=method,
                reason_code=LIVE_BRIDGE_INVALID_RESULT,
                reason_detail="Windows qmt execute response must be a JSON object",
                bridge_contract_version=_extract_bridge_contract_version(response, {}),
                raw_payload={"response_text": response.text},
            )

        actual_contract_version = _extract_bridge_contract_version(response, payload)
        classified_failure = self._classify_bridge_failure(
            status_code=response.status_code,
            payload=payload,
            provider_name=provider_name,
            method=method,
            task_id=_extract_str(payload, "task_id", "bridge_task_id", "receipt_id"),
            bridge_contract_version=actual_contract_version,
        )
        if classified_failure is not None:
            return classified_failure

        return {
            **dict(payload),
            "provider": provider_name,
            "method": method,
            "status": _extract_str(payload, "status", "transport_status") or "success",
            "task_id": _extract_str(payload, "task_id", "bridge_task_id", "receipt_id"),
            "source": _extract_str(payload, "source", "source_name") or provider_name,
            "source_name": _extract_str(payload, "source_name", "source") or f"{provider_name}/windows_bridge",
            "timestamp": _extract_str(payload, "timestamp", "receipt_timestamp", "updated_at", "occurred_at")
            or _utc_now().isoformat(),
            "bridge_contract_version": actual_contract_version,
        }

    def _normalize_result_response(
        self,
        *,
        response: httpx.Response,
        provider_name: str,
        task_id: str,
    ) -> Dict[str, Any]:
        payload = _safe_json_body(response)
        if not isinstance(payload, Mapping):
            return self._build_bridge_failure(
                provider_name=provider_name,
                method="task_result",
                task_id=task_id,
                reason_code=LIVE_BRIDGE_INVALID_RESULT,
                reason_detail="Windows qmt result response must be a JSON object",
                bridge_contract_version=_extract_bridge_contract_version(response, {}),
                raw_payload={"response_text": response.text},
            )

        actual_contract_version = _extract_bridge_contract_version(response, payload)
        classified_failure = self._classify_bridge_failure(
            status_code=response.status_code,
            payload=payload,
            provider_name=provider_name,
            method="task_result",
            task_id=task_id,
            bridge_contract_version=actual_contract_version,
        )
        if classified_failure is not None:
            return classified_failure

        return {
            **dict(payload),
            "provider": _extract_str(payload, "provider") or provider_name,
            "method": _extract_str(payload, "method") or "task_result",
            "task_id": _extract_str(payload, "task_id", "bridge_task_id", "receipt_id") or task_id,
            "bridge_contract_version": actual_contract_version,
        }

    def _classify_bridge_failure(
        self,
        *,
        status_code: int,
        payload: Mapping[str, Any],
        provider_name: str,
        method: str,
        task_id: str | None,
        bridge_contract_version: str | None,
    ) -> Dict[str, Any] | None:
        normalized_reason = _normalize_lookup_key(_extract_str(payload, "reason_code", "error_code", "failure_class"))
        reason_detail = _extract_str(payload, "reason_detail", "error_message", "message", "detail", "status_message")

        if status_code in _HTTP_AUTH_FAILURES or normalized_reason in {"auth_failed", "forbidden", "live_bridge_auth_failed", "unauthorized"}:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method=method,
                task_id=task_id,
                reason_code=LIVE_BRIDGE_AUTH_FAILED,
                reason_detail=reason_detail or "Windows qmt agent authentication failed",
                bridge_contract_version=bridge_contract_version,
                raw_payload=payload,
            )

        if status_code in _HTTP_UNSUPPORTED_METHOD_FAILURES or normalized_reason in {
            "live_bridge_unsupported_method",
            "method_not_allowed",
            "provider_not_allowed",
            "unsupported_method",
            "unsupported_provider",
        }:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method=method,
                task_id=task_id,
                reason_code=LIVE_BRIDGE_UNSUPPORTED_METHOD,
                reason_detail=reason_detail or f"Windows qmt agent rejected unsupported target {provider_name}/{method}",
                bridge_contract_version=bridge_contract_version,
                raw_payload=payload,
            )

        if status_code in _HTTP_VERSION_FAILURES or normalized_reason in {
            "bridge_contract_version_mismatch",
            "contract_version_mismatch",
            "live_bridge_unsupported_contract_version",
            "unsupported_contract_version",
        }:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method=method,
                task_id=task_id,
                reason_code=LIVE_BRIDGE_UNSUPPORTED_CONTRACT_VERSION,
                reason_detail=reason_detail or "Windows qmt agent rejected the requested contract version",
                bridge_contract_version=bridge_contract_version,
                raw_payload=payload,
            )

        if bridge_contract_version != self.bridge_contract_version:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method=method,
                task_id=task_id,
                reason_code=LIVE_BRIDGE_UNSUPPORTED_CONTRACT_VERSION,
                reason_detail=(
                    f"Windows qmt agent echoed contract version {bridge_contract_version or '<missing>'} "
                    f"but repository expects {self.bridge_contract_version}"
                ),
                bridge_contract_version=bridge_contract_version,
                raw_payload=payload,
            )

        if status_code >= 500:
            return self._build_bridge_failure(
                provider_name=provider_name,
                method=method,
                task_id=task_id,
                reason_code=LIVE_BRIDGE_UNAVAILABLE,
                reason_detail=reason_detail or f"Windows qmt agent returned HTTP {status_code}",
                bridge_contract_version=bridge_contract_version,
                raw_payload=payload,
            )

        return None

    def _build_bridge_failure(
        self,
        *,
        provider_name: str,
        method: str,
        reason_code: str,
        reason_detail: str,
        task_id: str | None = None,
        bridge_contract_version: str | None = None,
        raw_payload: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "status": "error",
            "provider": provider_name,
            "method": method,
            "task_id": task_id,
            "source": provider_name,
            "source_name": f"{provider_name}/windows_bridge",
            "timestamp": _utc_now().isoformat(),
            "reason_code": reason_code,
            "reason_detail": reason_detail,
            "failure_class": reason_code,
            "bridge_contract_version": bridge_contract_version,
            "raw_payload": dict(raw_payload) if isinstance(raw_payload, Mapping) else raw_payload,
        }

    def _resolve_provider_url(self, provider_name: str) -> str | None:
        return self.providers.get(provider_name)


def _extract_config_str(config: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = config.get(key)
        if value is None:
            continue
        normalized = str(value).strip()
        if normalized:
            return normalized
    return None


def _extract_str(payload: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        normalized = str(value).strip()
        if normalized:
            return normalized
    return None


def _extract_bridge_contract_version(response: httpx.Response, payload: Mapping[str, Any]) -> str | None:
    header_value = response.headers.get(BRIDGE_CONTRACT_VERSION_HEADER)
    if header_value:
        normalized = header_value.strip()
        if normalized:
            return normalized
    return _extract_str(payload, "bridge_contract_version", "contract_version")


def _normalize_lookup_key(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _safe_json_body(response: httpx.Response) -> Mapping[str, Any] | Any:
    try:
        return response.json()
    except ValueError:
        return None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
