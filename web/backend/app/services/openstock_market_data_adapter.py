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
        # B4.014-M1n 修复:OpenStock REALTIME_QUOTES 用单数 symbol(字符串)。
        # 多 symbol 不支持逗号分隔(provider 会把整串当 1 个非法代码 → 503),
        # 必须循环调用每次单 symbol 后合并。
        symbols_value = params.get("symbols") or params.get("symbol")
        if isinstance(symbols_value, (list, tuple)):
            symbols_list = [str(s) for s in symbols_value if s]
        elif symbols_value:
            symbols_list = [str(symbols_value)]
        else:
            symbols_list = []

        all_rows: list = []
        fetch_category: Optional[str] = None
        source: Optional[str] = None
        last_request_id: Optional[str] = None
        for sym in symbols_list:
            fetch_result = await client.fetch(
                ENDPOINT_ROUTES["quotes"],
                params={"symbol": sym},
            )
            all_rows.extend(self._coerce_rows(fetch_result.data))
            fetch_category = fetch_result.data_category or fetch_category
            source = fetch_result.source or source
            last_request_id = fetch_result.request_id or last_request_id

        quotes = [self._transform_quote_row(row) for row in all_rows]
        return {
            "status": "success",
            "data": quotes,
            "quotes": quotes,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source or "openstock",
            "endpoint": "quotes",
            "data_category": fetch_category,
            "parameters": {"symbols": ",".join(symbols_list)} if symbols_list else {},
            "request_id": last_request_id,
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
        OpenStock KLINES 返回字段:`time`(ISO8601 全时间戳)、`symbol`(带 sz/sh 前缀)。
        修复:
        - time(ISO8601 "2026-06-30T15:00:00+08:00") → datetime 截断到日期 "2026-06-30"
        - symbol "sz000001" → "000001"(去交易所前缀)
        """
        if not isinstance(row, Mapping):
            return {}
        result: Dict[str, Any] = {}
        for key, value in row.items():
            key_lower = str(key).lower()
            if key_lower == "time":
                sval = str(value) if value is not None else ""
                result["datetime"] = sval[:10] if sval else sval
            elif key_lower == "date":
                sval = str(value) if value is not None else ""
                result.setdefault("datetime", sval[:10] if sval else sval)
            elif key_lower == "symbol":
                result["symbol"] = OpenStockMarketDataSourceAdapter._strip_exchange_prefix(value)
            else:
                result[key_lower] = value
        return result

    @staticmethod
    def _transform_quote_row(row: Mapping[str, Any]) -> Dict[str, Any]:
        """将 OpenStock REALTIME_QUOTES 行映射为前端 quotes 期望的 schema。

        前端消费者(build_quotes_response_payload / marketAdapter / Realtime.vue):
        symbol, name, price, change, change_percent, volume, amount

        OpenStock 真实字段:pct_chg, symbol(sz000001), bid1_price, pe_dynamic 等 20 字段。

        修复:
        - pct_chg → change_percent(前端期望)
        - symbol "sz000001" → "000001"(去交易所前缀)
        - 其他字段透传(无害,但保留以备未来消费者使用)
        """
        if not isinstance(row, Mapping):
            return {}
        lowered: Dict[str, Any] = {str(k).lower(): v for k, v in row.items()}
        if "pct_chg" in lowered and "change_percent" not in lowered:
            lowered["change_percent"] = lowered["pct_chg"]
        if "symbol" in lowered:
            lowered["symbol"] = OpenStockMarketDataSourceAdapter._strip_exchange_prefix(
                lowered["symbol"]
            )
        return lowered

    @staticmethod
    def _strip_exchange_prefix(symbol_value: Any) -> Any:
        """去掉 sz/sh/bj 前缀,带校验。

        用确定的 2 字符前缀剥离 + 剩余 6 位数字校验,避免 lstrip 误剥
        (lstrip("sh") 会把 "sh600519" 当成连续字符集剥离,行为不可预测)。
        """
        if not isinstance(symbol_value, str) or not symbol_value:
            return symbol_value
        if (
            len(symbol_value) >= 8
            and symbol_value[:2] in ("sz", "sh", "bj")
            and symbol_value[2:].isdigit()
        ):
            return symbol_value[2:]
        return symbol_value

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
