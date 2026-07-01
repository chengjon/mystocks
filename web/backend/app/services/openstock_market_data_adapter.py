"""
OpenStock 行情数据源适配器 (B4.014 S5 / M1k-2)

将 OpenStockClient 适配到 IDataSource 接口,以便注册到 data_source_factory。
factory 通过新增 source_type="openstock_market" 分支调用本类(见步骤 3)。

设计依据:
- docs/architecture/S5_OPENSTOCK_ADAPTER_DESIGN_2026-07-01.md §四
- docs/architecture/M1K_M1M_EXECUTION_PLAN_2026-07-01.md §三步骤 2
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, Mapping, Optional

import httpx

from app.services.data_source_interface import (
    HealthStatus,
    HealthStatusEnum,
    IDataSource,
)
from app.services.openstock_client import (
    OpenStockClient,
    OpenStockClientConfig,
    OpenStockClientError,
)

logger = logging.getLogger(__name__)


PERIOD_MAP: Mapping[str, str] = {
    "daily": "day",
    "weekly": "week",
    "monthly": "month",
}

ENDPOINT_ROUTES: Mapping[str, str] = {
    "quotes": "REALTIME_QUOTES",
}

DEFAULT_BASE_URL = "http://192.168.123.104:8040"
DEFAULT_TIMEOUT_SECONDS = 5.0
HEALTH_LIVE_PATH = "/health/live"
HEALTH_READY_TIMEOUT_SECONDS = 5.0


class OpenStockMarketDataSourceAdapter(IDataSource):
    """OpenStock 行情数据源适配器,实现 IDataSource 接口。

    通过 endpoint 路由表将 factory 的 endpoint 参数映射到 OpenStockClient 方法:
      - "quotes" → client.fetch("REALTIME_QUOTES")
      - "klines" → client.fetch_bars(symbol=..., period=..., count=...)

    config 期望字段(来自 config/data_sources.json):
      - base_url (str, default "http://192.168.123.104:8040")
      - timeout (float, default 5.0) — factory schema 用 "timeout",内部转 timeout_seconds
      - 其他字段(custom_headers 等)目前未消费,保留以兼容 factory schema
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        base_url = str(config.get("base_url") or DEFAULT_BASE_URL)
        timeout_seconds = float(config.get("timeout") or DEFAULT_TIMEOUT_SECONDS)
        self._client_config = OpenStockClientConfig(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        )
        self._client: Optional[OpenStockClient] = None
        self._metrics: Dict[str, Any] = {
            "total_requests": 0,
            "success_count": 0,
            "error_count": 0,
            "last_error": None,
            "last_latency_ms": None,
        }

    def _get_client(self) -> OpenStockClient:
        if self._client is None:
            self._client = OpenStockClient(self._client_config)
        return self._client

    async def get_data(
        self, endpoint: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        params = params or {}
        self._metrics["total_requests"] += 1
        started = time.monotonic()
        try:
            client = self._get_client()
            if endpoint == "klines":
                result = await self._fetch_klines(client, params)
            elif endpoint == "quotes":
                result = await self._fetch_quotes(client, params)
            else:
                raise ValueError(f"Unsupported endpoint: {endpoint}")
            elapsed_ms = (time.monotonic() - started) * 1000.0
            self._metrics["success_count"] += 1
            self._metrics["last_latency_ms"] = elapsed_ms
            return result
        except Exception as exc:
            elapsed_ms = (time.monotonic() - started) * 1000.0
            self._metrics["error_count"] += 1
            self._metrics["last_error"] = str(exc)
            self._metrics["last_latency_ms"] = elapsed_ms
            logger.warning(
                "OpenStock adapter get_data failed (endpoint=%(ep)s): %(exc)s",
                {"ep": endpoint, "exc": exc},
            )
            raise

    async def _fetch_klines(
        self, client: OpenStockClient, params: Mapping[str, Any]
    ) -> Dict[str, Any]:
        symbol = params.get("symbol") or params.get("code")
        if not symbol:
            raise ValueError("klines endpoint requires 'symbol' parameter")
        period_input = str(params.get("period") or "daily")
        period = PERIOD_MAP.get(period_input, period_input)
        count = int(params.get("count") or params.get("limit") or 100)
        fetch_result = await client.fetch_bars(
            symbol=symbol,
            period=period,
            count=count,
        )
        rows = self._coerce_rows(fetch_result.data)
        candles = [self._transform_kline_row(row) for row in rows]
        return {
            "status": "success",
            "data": candles,
            "candles": candles,
            "timestamp": datetime.utcnow().isoformat(),
            "source": fetch_result.source or "openstock",
            "endpoint": "klines",
            "data_category": fetch_result.data_category,
            "parameters": {
                "symbol": symbol,
                "period": period_input,
                "count": count,
            },
        }

    async def _fetch_quotes(
        self, client: OpenStockClient, params: Mapping[str, Any]
    ) -> Dict[str, Any]:
        symbols_value = params.get("symbols") or params.get("symbol")
        if isinstance(symbols_value, (list, tuple)):
            symbols_str = ",".join(str(s) for s in symbols_value)
        else:
            symbols_str = str(symbols_value) if symbols_value else ""
        fetch_params: Dict[str, Any] = {}
        if symbols_str:
            fetch_params["symbols"] = symbols_str
        fetch_result = await client.fetch(
            ENDPOINT_ROUTES["quotes"],
            params=fetch_params or None,
        )
        rows = self._coerce_rows(fetch_result.data)
        quotes = [self._transform_quote_row(row) for row in rows]
        return {
            "status": "success",
            "data": quotes,
            "quotes": quotes,
            "timestamp": datetime.utcnow().isoformat(),
            "source": fetch_result.source or "openstock",
            "endpoint": "quotes",
            "data_category": fetch_result.data_category,
            "parameters": {"symbols": symbols_str} if symbols_str else {},
        }

    @staticmethod
    def _coerce_rows(data: Any) -> list:
        if data is None:
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, Mapping):
            for key in ("rows", "data", "items", "quotes", "candles"):
                inner = data.get(key)
                if isinstance(inner, list):
                    return inner
            logger.warning(
                "OpenStock _coerce_rows: mapping shape unrecognized, "
                "returning empty list. keys=%(keys)s",
                {"keys": list(data.keys())},
            )
        return []

    @staticmethod
    def _transform_kline_row(row: Mapping[str, Any]) -> Dict[str, Any]:
        """将 OpenStock KLINES 行映射为前端 KLineRow 期望的 schema。

        前端 extractKlineRows 识别的字段:datetime/open/high/low/close/volume。
        OpenStock KLINES 返回的字段名以 time 为时间戳(实测),需要映射到 datetime。
        """
        if not isinstance(row, Mapping):
            return {}
        result: Dict[str, Any] = {}
        for key, value in row.items():
            key_lower = str(key).lower()
            if key_lower == "time":
                result["datetime"] = value
            elif key_lower == "date":
                result.setdefault("datetime", value)
            else:
                result[key_lower] = value
        return result

    @staticmethod
    def _transform_quote_row(row: Mapping[str, Any]) -> Dict[str, Any]:
        """将 OpenStock REALTIME_QUOTES 行映射为前端 quotes 期望的 schema。

        归一字段:symbol/price/volume/change/change_percent。
        OpenStock 返回字段名通常已是英文小写或 code/name/price/volume,
        这里只做大小写归一,不做强转。
        """
        if not isinstance(row, Mapping):
            return {}
        return {str(k).lower(): v for k, v in row.items()}

    async def health_check(self) -> HealthStatus:
        """调用 OpenStock /health/live 端点检查活性。

        优先用 /health/live(实测 9.9ms,200 OK);若 404 再降级用 OpenStockClient.ready()
        (内部打 /health)。
        """
        started = time.monotonic()
        try:
            async with httpx.AsyncClient(
                base_url=self._client_config.base_url.rstrip("/"),
                timeout=HEALTH_READY_TIMEOUT_SECONDS,
            ) as http_client:
                response = await http_client.get(HEALTH_LIVE_PATH)
            elapsed_ms = (time.monotonic() - started) * 1000.0
            if response.status_code < 500:
                return HealthStatus(
                    status=HealthStatusEnum.HEALTHY,
                    response_time=elapsed_ms,
                    message=f"/health/live {response.status_code}",
                    timestamp=datetime.utcnow(),
                )
            return HealthStatus(
                status=HealthStatusEnum.DEGRADED,
                response_time=elapsed_ms,
                message=f"/health/live {response.status_code}",
                timestamp=datetime.utcnow(),
            )
        except httpx.HTTPError as exc:
            elapsed_ms = (time.monotonic() - started) * 1000.0
            logger.warning(
                "OpenStock /health/live probe failed: %(exc)s", {"exc": exc}
            )
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=elapsed_ms,
                message=str(exc),
                timestamp=datetime.utcnow(),
            )
        except OpenStockClientError as exc:
            elapsed_ms = (time.monotonic() - started) * 1000.0
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=elapsed_ms,
                message=str(exc),
                timestamp=datetime.utcnow(),
            )

    def get_metrics(self) -> Dict[str, Any]:
        total = self._metrics["total_requests"]
        success = self._metrics["success_count"]
        availability = (success / total * 100.0) if total > 0 else 0.0
        return {
            **self._metrics,
            "availability": availability,
            "type": self.type,
            "base_url": self._client_config.base_url,
        }

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
