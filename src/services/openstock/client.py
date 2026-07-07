"""OpenStock HTTP 客户端 - 单一外部数据网关.

只做轻量封装:
- 从环境变量读取 OPENSTOCK_BASE_URL + OPENSTOCK_API_KEY
- 统一 X-API-Key header
- 单次重试(provider_unavailable 时触发,其余 4xx/5xx 抛 OpenStockError)
- 不复刻 OpenStock 内置的 5 秒缓存、熔断器、failover

外部循环重试/调度由消费端自行决定。OpenStock 已内置上游 provider failover,
本项目不感知 provider 切换。
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from src.services.openstock.category_mapping import DataCategory

logger = logging.getLogger(__name__)

# 默认超时(秒)。OpenStock 内部已带 5s 缓存,大多数 category 应在 1s 内返回。
# 期货盲区、跨市场 K 线回溯等可能更慢,留 10s 余量。
_DEFAULT_TIMEOUT = 10.0

# provider_unavailable 时单次重试,其余错误不重试。
_MAX_ATTEMPTS = 2

# 错误 envelope 中的 code 字段值
_CODE_PROVIDER_UNAVAILABLE = "provider_unavailable"


class OpenStockError(Exception):
    """OpenStock 网关返回非 2xx 响应时的基类异常.

    Attributes:
        status_code: HTTP 状态码
        code: 错误 envelope 中的 `detail.code` 字段(可能为 None)
        message: 错误 envelope 中的 `detail` 字符串或 `detail.message`
        request_id: 请求追踪 ID(可能为 None)
    """

    def __init__(
        self,
        status_code: int,
        code: str | None,
        message: str,
        request_id: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.request_id = request_id
        super().__init__(f"OpenStock error {status_code} [{code}]: {message} (request_id={request_id})")


class OpenStockProviderUnavailable(OpenStockError):
    """provider_unavailable — 触发客户端单次重试的子类。"""


class OpenStockClient:
    """OpenStock 数据网关 HTTP 客户端.

    所有方法返回 OpenStock 响应 JSON(已 decode)。消费端按 `data` / `results` /
    `sources` 等字段自行 reshape。本项目不做字段逆向 reshape(决策 1:消费端按
    OpenStock `fields_typed` 自适应)。

    Usage::

        client = OpenStockClient()  # 从 .env 读取配置
        quote = client.fetch(DataCategory.REALTIME_QUOTES, {"symbol": "000001"})
        bars = client.bars(symbol="000001", period="day", count=100)
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._base_url = (base_url or os.environ.get("OPENSTOCK_BASE_URL", "")).rstrip("/")
        self._api_key = api_key or os.environ.get("OPENSTOCK_API_KEY", "")
        if not self._base_url:
            raise OpenStockError(0, None, "OPENSTOCK_BASE_URL not configured")
        if not self._api_key:
            raise OpenStockError(0, None, "OPENSTOCK_API_KEY not configured")
        self._timeout = timeout
        # transport 仅用于测试注入 mock; 生产路径使用默认 httpx.HTTPTransport
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={"X-API-Key": self._api_key, "Content-Type": "application/json"},
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OpenStockClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ---- 六个端点封装 -------------------------------------------------

    def fetch(
        self,
        category: DataCategory | str,
        params: dict[str, Any] | None = None,
        *,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """POST /data/fetch — 单条数据拉取."""
        body: dict[str, Any] = {
            "data_category": _category_value(category),
        }
        if params is not None:
            body["params"] = params
        if request_id is not None:
            body["request_id"] = request_id
        return self._post_with_retry("/data/fetch", body)

    def batch(
        self,
        requests: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """POST /data/batch — 批量拉取(最多 500 个子请求)."""
        if not isinstance(requests, list):
            raise TypeError("batch() expects a list of request objects")
        if len(requests) > 500:
            raise ValueError(f"OpenStock /data/batch accepts at most 500 sub-requests, got {len(requests)}")
        return self._post_with_retry("/data/batch", {"requests": requests})

    def bars(
        self,
        symbol: str,
        *,
        period: str = "day",
        count: int = 100,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """POST /data/bars — K 线/分钟线."""
        body: dict[str, Any] = {"symbol": symbol, "period": period, "count": count}
        if request_id is not None:
            body["request_id"] = request_id
        return self._post_with_retry("/data/bars", body)

    def snapshot(self, symbol: str) -> dict[str, Any]:
        """POST /data/snapshot — 实时快照(等价于 fetch REALTIME_QUOTES)."""
        return self.fetch(DataCategory.REALTIME_QUOTES, {"symbol": symbol})

    def routing_best(
        self,
        category: DataCategory | str,
        *,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """POST /routing/best — 查询最佳路由决策."""
        body: dict[str, Any] = {"data_category": _category_value(category)}
        if request_id is not None:
            body["request_id"] = request_id
        return self._post_with_retry("/routing/best", body)

    def sources(self) -> dict[str, Any]:
        """GET /sources — 列出已注册数据源与 category 注册表."""
        return self._get("/sources")

    # ---- 内部 HTTP 工具 ----------------------------------------------

    def _post_with_retry(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                response = self._client.post(path, json=body)
            except httpx.HTTPError as exc:
                last_exc = exc
                logger.warning(
                    "OpenStock %s transport error (attempt %d/%d): %s",
                    path, attempt, _MAX_ATTEMPTS, exc,
                )
                if attempt < _MAX_ATTEMPTS:
                    continue
                raise OpenStockError(0, None, f"transport error: {exc}") from exc

            if response.status_code == 200:
                return response.json()

            err = self._decode_error(response)
            # 只对 provider_unavailable 单次重试
            if err.code == _CODE_PROVIDER_UNAVAILABLE and attempt < _MAX_ATTEMPTS:
                logger.info(
                    "OpenStock %s provider_unavailable, retrying (attempt %d/%d)",
                    path, attempt, _MAX_ATTEMPTS,
                )
                last_exc = err
                continue
            raise err

        # 理论不可达:循环要么 return,要么 raise
        raise last_exc if last_exc else OpenStockError(0, None, "unknown failure")

    def _get(self, path: str) -> dict[str, Any]:
        try:
            response = self._client.get(path)
        except httpx.HTTPError as exc:
            raise OpenStockError(0, None, f"transport error: {exc}") from exc
        if response.status_code == 200:
            return response.json()
        raise self._decode_error(response)

    @staticmethod
    def _decode_error(response: httpx.Response) -> OpenStockError:
        status = response.status_code
        request_id: str | None = None
        code: str | None = None
        message = response.text or f"HTTP {status}"
        try:
            payload = response.json()
        except Exception:
            return OpenStockError(status, code, message, request_id)

        # OpenStock 错误 envelope: {"detail": "..."} 或 {"detail": {"code": "...", "message": "..."}}
        detail = payload.get("detail") if isinstance(payload, dict) else None
        if isinstance(detail, dict):
            code = detail.get("code")
            message = detail.get("message") or detail.get("detail") or message
            request_id = detail.get("request_id") or payload.get("request_id")
        elif isinstance(detail, str):
            message = detail
            request_id = payload.get("request_id") if isinstance(payload, dict) else None
        elif isinstance(payload, dict):
            code = payload.get("code")
            message = payload.get("message") or message
            request_id = payload.get("request_id")

        if code == _CODE_PROVIDER_UNAVAILABLE:
            return OpenStockProviderUnavailable(status, code, message, request_id)
        return OpenStockError(status, code, message, request_id)


def _category_value(category: DataCategory | str) -> str:
    """接受 DataCategory 枚举或裸字符串."""
    if isinstance(category, DataCategory):
        return category.value
    if isinstance(category, str):
        return category
    raise TypeError(f"data_category must be DataCategory or str, got {type(category).__name__}")


__all__ = [
    "OpenStockClient",
    "OpenStockError",
    "OpenStockProviderUnavailable",
]
