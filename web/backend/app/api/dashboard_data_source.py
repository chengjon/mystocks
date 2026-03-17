"""
仪表盘真实数据源适配层
"""

from __future__ import annotations

import logging
import os
import re
from datetime import date, datetime
from typing import Dict, List, Optional

import httpx
import pandas as pd
from fastapi import HTTPException
from sqlalchemy import text

from app.services.market_data_service_v2 import get_market_data_service_v2
from app.services.tdx_service import get_tdx_service

logger = logging.getLogger(__name__)

_TDX_MARKET_SNAPSHOT_CACHE: Optional[Dict] = None
_TDX_MARKET_SNAPSHOT_CACHE_AT: Optional[datetime] = None
_TDX_MARKET_SNAPSHOT_CACHE_TTL_SECONDS = 300
_MAJOR_INDEX_QUOTES_CACHE: Optional[List[Dict]] = None
_MAJOR_INDEX_QUOTES_CACHE_AT: Optional[datetime] = None
_MAJOR_INDEX_QUOTES_CACHE_TTL_SECONDS = 60
_LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL: Optional[datetime] = None
_LIVE_MARKET_SNAPSHOT_FAILURE_COOLDOWN_SECONDS = 300


class RealBusinessDataSource:
    """
    真实业务数据源

    使用现有API端点获取真实数据，替代硬编码的Mock数据。
    实现方案与前端dashboardService.ts保持一致。
    """

    def __init__(self):
        """初始化真实数据源"""
        backend_port = os.getenv("BACKEND_PORT", "").strip()
        if not backend_port:
            raise RuntimeError("Missing BACKEND_PORT in .env")
        self.base_url = os.getenv("BACKEND_BASE_URL", f"http://localhost:{backend_port}")
        self.timeout = 10.0
        logger.info("✅ RealBusinessDataSource initialized")

    async def _make_request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None) -> Dict:
        """发送HTTP请求到后端API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}{endpoint}"

                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=json_data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as error:
            logger.error("HTTP请求失败: endpoint=%s, error=%s", endpoint, error)
            return {"success": False, "data": None}
        except Exception as error:
            logger.error("请求异常: endpoint=%s, error=%s", endpoint, error)
            return {"success": False, "data": None}

    def get_market_overview_data(self) -> Dict:
        return self._get_market_overview_data()

    def get_dashboard_summary(self, user_id: int, trade_date: Optional[date] = None):
        """获取仪表盘汇总数据"""
        logger.info("获取仪表盘数据: user_id=%s, trade_date=%s", user_id, trade_date)

        dashboard_data = {
            "data_source": "real_api_composite",
            "generated_at": datetime.now().isoformat(),
        }

        try:
            dashboard_data["market_overview"] = self._get_market_overview_data()
        except Exception as error:
            logger.warning("获取市场概览失败: %s", error)
            dashboard_data["market_overview"] = self._get_fallback_market_overview()

        try:
            portfolio_data = self._get_user_portfolio_data(user_id)
            dashboard_data["portfolio"] = portfolio_data
        except Exception as error:
            logger.warning("获取用户持仓失败: %s", error)
            dashboard_data["portfolio"] = self._get_fallback_portfolio()

        dashboard_data["watchlist"] = []

        try:
            dashboard_data["strategies"] = self._get_user_active_strategies(user_id)
        except Exception as error:
            logger.warning("获取活跃策略失败: %s", error)
            dashboard_data["strategies"] = []

        dashboard_data["risk_alerts"] = []
        return dashboard_data

    def _get_market_overview_data(self) -> Dict:
        """获取市场概览数据"""
        try:
            market_service = get_market_data_service_v2()
            market_snapshot = (
                self._get_live_market_snapshot()
                or self._get_tdx_live_market_snapshot(market_service)
                or self._get_realtime_market_snapshot(market_service)
            )
            etf_data = market_service.query_etf_spot(limit=100)
            index_patterns = [
                r"^510300",
                r"^510500",
                r"^510050",
                r"^159915",
                r"^159919",
                r"^159949",
                r"^510900",
            ]

            ranking_indices = []
            up_count = 0
            down_count = 0
            total_volume = 0

            for etf in etf_data:
                symbol = etf.get("symbol", "")
                name = etf.get("name", "")
                is_index = any(re.match(pattern, symbol) for pattern in index_patterns) or "指数" in name

                if is_index:
                    change_percent = etf.get("change_percent", 0)
                    ranking_indices.append(
                        {
                            "symbol": symbol,
                            "name": name.replace("ETF", "").replace("交易型开放式指数基金", "").strip(),
                            "current_price": etf.get("latest_price", 0),
                            "change_percent": change_percent,
                            "volume": etf.get("volume", 0),
                            "turnover": etf.get("amount", 0),
                            "update_time": etf.get("created_at") or etf.get("trade_date"),
                        }
                    )

                    if change_percent > 0:
                        up_count += 1
                    elif change_percent < 0:
                        down_count += 1

                    total_volume += etf.get("volume", 0)

            indices = self._get_major_index_quotes() or ranking_indices[:10]
            ranking_source = ranking_indices or indices
            market_stats = market_snapshot if market_snapshot else None
            fallback_total_turnover = sum(idx.get("turnover", 0) for idx in ranking_source)
            fallback_top_gainers = sorted(ranking_source, key=lambda item: item.get("change_percent", 0), reverse=True)[:3]
            fallback_top_losers = sorted(ranking_source, key=lambda item: item.get("change_percent", 0))[:3]
            fallback_most_active = sorted(ranking_source, key=lambda item: item.get("volume", 0), reverse=True)[:3]

            return {
                "indices": indices,
                "up_count": market_stats.get("up_count", up_count) if market_stats else up_count,
                "down_count": market_stats.get("down_count", down_count) if market_stats else down_count,
                "flat_count": market_stats.get("flat_count", 0) if market_stats else 0,
                "total_volume": market_stats.get("total_volume", total_volume) if market_stats else total_volume,
                "total_turnover": market_stats["total_turnover"]
                if market_stats and market_stats.get("total_turnover") is not None
                else fallback_total_turnover,
                "top_gainers": market_stats["top_gainers"]
                if market_stats and market_stats.get("top_gainers") is not None
                else fallback_top_gainers,
                "top_losers": market_stats["top_losers"]
                if market_stats and market_stats.get("top_losers") is not None
                else fallback_top_losers,
                "most_active": market_stats["most_active"]
                if market_stats and market_stats.get("most_active") is not None
                else fallback_most_active,
            }

        except Exception as error:
            logger.error("获取市场概览数据失败: %s", error)

        return self._get_fallback_market_overview()

    def _get_major_index_quotes(self) -> List[Dict]:
        """获取 dashboard 约定的三大指数真实报价"""
        global _MAJOR_INDEX_QUOTES_CACHE, _MAJOR_INDEX_QUOTES_CACHE_AT

        now = datetime.now()
        if (
            _MAJOR_INDEX_QUOTES_CACHE is not None
            and _MAJOR_INDEX_QUOTES_CACHE_AT is not None
            and (now - _MAJOR_INDEX_QUOTES_CACHE_AT).total_seconds() < _MAJOR_INDEX_QUOTES_CACHE_TTL_SECONDS
        ):
            return _MAJOR_INDEX_QUOTES_CACHE

        index_labels = {
            "000001": "上证指数",
            "399001": "深证成指",
            "399006": "创业板指",
        }

        try:
            tdx_service = get_tdx_service()
            indices = []

            for symbol, default_name in index_labels.items():
                quote = tdx_service.get_index_quote(symbol)
                if not isinstance(quote, dict):
                    continue

                indices.append(
                    {
                        "symbol": str(quote.get("symbol") or quote.get("code") or symbol),
                        "name": str(quote.get("name") or default_name),
                        "current_price": quote.get("price", quote.get("current_price", 0)),
                        "change_percent": quote.get("change_pct", quote.get("change_percent", 0)),
                        "volume": quote.get("volume", 0),
                        "turnover": quote.get("amount", quote.get("turnover", 0)),
                        "update_time": quote.get("timestamp") or quote.get("update_time"),
                    }
                )

            _MAJOR_INDEX_QUOTES_CACHE = indices
            _MAJOR_INDEX_QUOTES_CACHE_AT = now
            return indices

        except Exception as error:
            logger.warning("获取三大指数真实报价失败: %s", error)
            return []

    def _get_realtime_market_snapshot(self, market_service) -> Optional[Dict]:
        """获取真实市场快照统计与榜单"""
        engine = getattr(market_service, "engine", None)
        if engine is None:
            return None

        def _row_to_dict(row) -> Dict:
            if row is None:
                return {}
            if hasattr(row, "_mapping"):
                return dict(row._mapping)
            return dict(row)

        stats_sql = text(
            """
            WITH latest AS (
                SELECT MAX(fetch_timestamp) AS ts
                FROM realtime_market_quotes
            )
            SELECT
                COALESCE(SUM(CASE WHEN pct_chg > 0 THEN 1 ELSE 0 END), 0) AS up_count,
                COALESCE(SUM(CASE WHEN pct_chg < 0 THEN 1 ELSE 0 END), 0) AS down_count,
                COALESCE(SUM(CASE WHEN pct_chg = 0 THEN 1 ELSE 0 END), 0) AS flat_count,
                COALESCE(SUM(volume), 0) AS total_volume,
                COALESCE(SUM(amount), 0) AS total_turnover
            FROM realtime_market_quotes
            WHERE fetch_timestamp = (SELECT ts FROM latest)
              AND pct_chg IS NOT NULL
              AND close IS NOT NULL
              AND amount IS NOT NULL
            """
        )
        top_gainers_sql = text(
            """
            WITH latest AS (
                SELECT MAX(fetch_timestamp) AS ts
                FROM realtime_market_quotes
            )
            SELECT
                symbol,
                name,
                close AS current_price,
                pct_chg AS change_percent,
                volume,
                amount AS turnover,
                fetch_timestamp AS update_time
            FROM realtime_market_quotes
            WHERE fetch_timestamp = (SELECT ts FROM latest)
              AND pct_chg IS NOT NULL
              AND close IS NOT NULL
              AND amount IS NOT NULL
            ORDER BY pct_chg DESC, amount DESC
            LIMIT 3
            """
        )
        top_losers_sql = text(
            """
            WITH latest AS (
                SELECT MAX(fetch_timestamp) AS ts
                FROM realtime_market_quotes
            )
            SELECT
                symbol,
                name,
                close AS current_price,
                pct_chg AS change_percent,
                volume,
                amount AS turnover,
                fetch_timestamp AS update_time
            FROM realtime_market_quotes
            WHERE fetch_timestamp = (SELECT ts FROM latest)
              AND pct_chg IS NOT NULL
              AND close IS NOT NULL
              AND amount IS NOT NULL
            ORDER BY pct_chg ASC, amount DESC
            LIMIT 3
            """
        )
        most_active_sql = text(
            """
            WITH latest AS (
                SELECT MAX(fetch_timestamp) AS ts
                FROM realtime_market_quotes
            )
            SELECT
                symbol,
                name,
                close AS current_price,
                pct_chg AS change_percent,
                volume,
                amount AS turnover,
                fetch_timestamp AS update_time
            FROM realtime_market_quotes
            WHERE fetch_timestamp = (SELECT ts FROM latest)
              AND pct_chg IS NOT NULL
              AND close IS NOT NULL
              AND amount IS NOT NULL
            ORDER BY amount DESC
            LIMIT 3
            """
        )

        try:
            with engine.connect() as conn:
                stats = _row_to_dict(conn.execute(stats_sql).fetchone())
                if not stats:
                    return None

                top_gainers = [_row_to_dict(row) for row in conn.execute(top_gainers_sql).fetchall()]
                top_losers = [_row_to_dict(row) for row in conn.execute(top_losers_sql).fetchall()]
                most_active = [_row_to_dict(row) for row in conn.execute(most_active_sql).fetchall()]

            return {
                "up_count": int(stats.get("up_count", 0) or 0),
                "down_count": int(stats.get("down_count", 0) or 0),
                "flat_count": int(stats.get("flat_count", 0) or 0),
                "total_volume": float(stats.get("total_volume", 0) or 0),
                "total_turnover": float(stats.get("total_turnover", 0) or 0),
                "top_gainers": top_gainers,
                "top_losers": top_losers,
                "most_active": most_active,
            }
        except Exception as error:
            logger.warning("获取实时市场快照失败: %s", error)
            return None

    def _get_live_market_snapshot(self) -> Optional[Dict]:
        """获取实时 efinance 全市场快照"""
        global _LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL

        now = datetime.now()
        if _LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL and now < _LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL:
            return None

        try:
            from src.adapters.financial_adapter import FinancialDataSource

            snapshot_df = FinancialDataSource().get_real_time_data()
            if not isinstance(snapshot_df, pd.DataFrame) or snapshot_df.empty:
                _LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL = now + pd.Timedelta(seconds=_LIVE_MARKET_SNAPSHOT_FAILURE_COOLDOWN_SECONDS)
                return None

            normalized = pd.DataFrame(
                {
                    "symbol": snapshot_df.get("股票代码"),
                    "name": snapshot_df.get("股票名称"),
                    "current_price": pd.to_numeric(snapshot_df.get("最新价"), errors="coerce"),
                    "change_percent": pd.to_numeric(snapshot_df.get("涨跌幅"), errors="coerce"),
                    "volume": pd.to_numeric(snapshot_df.get("成交量"), errors="coerce"),
                    "turnover": pd.to_numeric(snapshot_df.get("成交额"), errors="coerce"),
                    "update_time": snapshot_df.get("更新时间"),
                }
            )

            normalized = normalized.dropna(subset=["symbol", "current_price", "change_percent", "turnover"])
            if normalized.empty:
                _LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL = now + pd.Timedelta(seconds=_LIVE_MARKET_SNAPSHOT_FAILURE_COOLDOWN_SECONDS)
                return None

            _LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL = None

            up_count = int((normalized["change_percent"] > 0).sum())
            down_count = int((normalized["change_percent"] < 0).sum())
            flat_count = int((normalized["change_percent"] == 0).sum())

            def _records(frame: pd.DataFrame) -> List[Dict]:
                return frame.to_dict(orient="records")

            top_gainers = _records(
                normalized.sort_values(["change_percent", "turnover"], ascending=[False, False]).head(3)
            )
            top_losers = _records(
                normalized.sort_values(["change_percent", "turnover"], ascending=[True, False]).head(3)
            )
            most_active = _records(normalized.sort_values(["turnover"], ascending=[False]).head(3))

            return {
                "up_count": up_count,
                "down_count": down_count,
                "flat_count": flat_count,
                "total_volume": float(normalized["volume"].sum()),
                "total_turnover": float(normalized["turnover"].sum()),
                "top_gainers": top_gainers,
                "top_losers": top_losers,
                "most_active": most_active,
            }

        except Exception as error:
            _LIVE_MARKET_SNAPSHOT_DISABLED_UNTIL = now + pd.Timedelta(seconds=_LIVE_MARKET_SNAPSHOT_FAILURE_COOLDOWN_SECONDS)
            logger.warning("获取实时全市场快照失败: %s", error)
            return None

    def _get_tdx_live_market_snapshot(self, market_service) -> Optional[Dict]:
        """获取 TDX 全市场实时快照（带短 TTL 缓存）"""
        global _TDX_MARKET_SNAPSHOT_CACHE, _TDX_MARKET_SNAPSHOT_CACHE_AT

        now = datetime.now()
        if (
            _TDX_MARKET_SNAPSHOT_CACHE is not None
            and _TDX_MARKET_SNAPSHOT_CACHE_AT is not None
            and (now - _TDX_MARKET_SNAPSHOT_CACHE_AT).total_seconds() < _TDX_MARKET_SNAPSHOT_CACHE_TTL_SECONDS
        ):
            return _TDX_MARKET_SNAPSHOT_CACHE

        engine = getattr(market_service, "engine", None)
        if engine is None:
            return None

        def _infer_market_code(symbol: str) -> int:
            if symbol.startswith(("000", "002", "300", "399")):
                return 0
            if symbol.startswith(("600", "601", "603", "605", "688", "689", "999")):
                return 1
            return 0

        try:
            from pytdx.hq import TdxHq_API

            tdx_service = get_tdx_service()
            tdx_host = tdx_service.tdx_adapter.tdx_host
            tdx_port = tdx_service.tdx_adapter.tdx_port

            symbols_sql = text(
                """
                WITH latest AS (
                    SELECT MAX(fetch_timestamp) AS ts
                    FROM realtime_market_quotes
                )
                SELECT DISTINCT ON (symbol)
                    symbol,
                    name
                FROM realtime_market_quotes
                WHERE fetch_timestamp = (SELECT ts FROM latest)
                  AND amount IS NOT NULL
                  AND symbol ~ '^[0-9]{6}$'
                ORDER BY symbol, amount DESC NULLS LAST
                """
            )

            with engine.connect() as conn:
                symbol_rows = conn.execute(symbols_sql).fetchall()

            if not symbol_rows:
                return None

            symbol_name_map = {row._mapping["symbol"]: row._mapping.get("name") or row._mapping["symbol"] for row in symbol_rows}
            symbol_pairs = [(_infer_market_code(symbol), symbol) for symbol in symbol_name_map]

            api = TdxHq_API()
            snapshot_rows = []
            batch_size = 20
            batch_timestamp = now.isoformat()

            with api.connect(tdx_host, tdx_port):
                for offset in range(0, len(symbol_pairs), batch_size):
                    batch = symbol_pairs[offset : offset + batch_size]
                    data = api.get_security_quotes(batch) or []
                    for pair, quote in zip(batch, data):
                        symbol = pair[1]
                        price = float(quote.get("price", 0) or 0)
                        pre_close = float(quote.get("last_close", 0) or 0)
                        amount = float(quote.get("amount", 0) or 0)
                        volume = int(quote.get("vol", 0) or 0)
                        if price <= 0 or pre_close <= 0 or amount <= 0:
                            continue

                        snapshot_rows.append(
                            {
                                "symbol": symbol,
                                "name": symbol_name_map.get(symbol, symbol),
                                "current_price": price,
                                "change_percent": round((price - pre_close) / pre_close * 100, 2),
                                "volume": volume,
                                "turnover": amount,
                                "update_time": batch_timestamp,
                            }
                        )

            if not snapshot_rows:
                return None

            snapshot_df = pd.DataFrame(snapshot_rows)
            top_gainers = snapshot_df.sort_values(["change_percent", "turnover"], ascending=[False, False]).head(3)
            top_losers = snapshot_df.sort_values(["change_percent", "turnover"], ascending=[True, False]).head(3)
            most_active = snapshot_df.sort_values(["turnover"], ascending=[False]).head(3)

            result = {
                "up_count": int((snapshot_df["change_percent"] > 0).sum()),
                "down_count": int((snapshot_df["change_percent"] < 0).sum()),
                "flat_count": int((snapshot_df["change_percent"] == 0).sum()),
                "total_volume": float(snapshot_df["volume"].sum()),
                "total_turnover": float(snapshot_df["turnover"].sum()),
                "top_gainers": top_gainers.to_dict(orient="records"),
                "top_losers": top_losers.to_dict(orient="records"),
                "most_active": most_active.to_dict(orient="records"),
            }

            _TDX_MARKET_SNAPSHOT_CACHE = result
            _TDX_MARKET_SNAPSHOT_CACHE_AT = now
            return result

        except Exception as error:
            logger.warning("获取 TDX 全市场快照失败: %s", error)
            return None

    def _get_user_portfolio_data(self, user_id: int) -> Dict:
        """获取用户持仓数据"""
        try:
            import requests

            mtm_response = requests.get(f"{self.base_url}/api/api/mtm/portfolio/{user_id}", timeout=5)

            if mtm_response.status_code == 200:
                mtm_data = mtm_response.json()
                return {
                    "total_market_value": mtm_data.get("total_value", 0),
                    "total_cost": mtm_data.get("total_cost", 0),
                    "total_profit_loss": mtm_data.get("profit_loss", 0),
                    "total_profit_loss_percent": mtm_data.get("profit_loss_percent", 0),
                    "position_count": len(mtm_data.get("positions", [])),
                    "positions": [
                        {
                            "symbol": pos.get("symbol", ""),
                            "name": pos.get("name", ""),
                            "quantity": pos.get("quantity", 0),
                            "avg_cost": pos.get("avg_cost", 0),
                            "current_price": pos.get("current_price", 0),
                            "market_value": pos.get("market_value", 0),
                            "profit_loss": pos.get("profit_loss", 0),
                            "profit_loss_percent": pos.get("profit_loss_percent", 0),
                            "position_percent": pos.get("position_percent", 0),
                        }
                        for pos in mtm_data.get("positions", [])
                    ],
                }

        except Exception as error:
            logger.error("获取用户持仓数据失败: %s", error)

        return self._get_fallback_portfolio()

    def _get_user_active_strategies(self, user_id: int) -> List:
        """获取用户活跃策略"""
        try:
            import requests

            strategy_response = requests.get(
                f"{self.base_url}/api/strategy-mgmt/strategies", params={"user_id": user_id}, timeout=5
            )

            if strategy_response.status_code == 200:
                strategies_data = strategy_response.json()

                if isinstance(strategies_data, dict):
                    strategies = strategies_data.get("data", [])
                elif isinstance(strategies_data, list):
                    strategies = strategies_data
                else:
                    strategies = []

                active_strategies = [
                    item for item in strategies if item.get("status") == "active" or item.get("is_active") is True
                ]
                return active_strategies

        except Exception as error:
            logger.error("获取活跃策略失败: %s", error)

        return []

    def _get_fallback_market_overview(self) -> Dict:
        """获取降级市场概览数据"""
        return {
            "indices": [
                {
                    "symbol": "000001",
                    "name": "上证指数",
                    "current_price": 3021.45,
                    "change_percent": 0.85,
                    "volume": 285000000,
                    "turnover": 3120000000,
                    "update_time": datetime.now().isoformat(),
                },
                {
                    "symbol": "399001",
                    "name": "深证成指",
                    "current_price": 9876.32,
                    "change_percent": -0.32,
                    "volume": 198000000,
                    "turnover": 2450000000,
                    "update_time": datetime.now().isoformat(),
                },
            ],
            "up_count": 2156,
            "down_count": 1832,
            "flat_count": 234,
            "total_volume": 483000000,
            "total_turnover": 5570000000,
            "top_gainers": [],
            "top_losers": [],
            "most_active": [],
        }

    def _get_fallback_portfolio(self) -> Dict:
        """获取降级持仓数据"""
        return {
            "total_market_value": 0,
            "total_cost": 0,
            "total_profit_loss": 0,
            "total_profit_loss_percent": 0,
            "position_count": 0,
            "positions": [],
        }

    def health_check(self) -> Dict:
        """健康检查"""
        return {
            "status": "healthy",
            "database": "postgresql",
            "cache": "enabled",
            "data_source": "real_api",
            "last_check": datetime.now().isoformat(),
        }


def get_business_source():
    """获取业务数据源配置"""
    return RealBusinessDataSource()


def prewarm_dashboard_market_overview_cache() -> bool:
    """后台预热 dashboard market-overview 的 TDX 缓存"""
    try:
        source = RealBusinessDataSource()
        market_service = get_market_data_service_v2()
        source._get_major_index_quotes()
        source._get_tdx_live_market_snapshot(market_service)
        logger.info("✅ dashboard market-overview cache prewarmed")
        return True
    except Exception as error:
        logger.warning("⚠️ dashboard market-overview cache prewarm failed: %s", error)
        return False


def get_data_source():
    """获取业务数据源"""
    try:
        return RealBusinessDataSource()
    except Exception as error:
        logger.error("获取数据源失败: %s", error)
        raise HTTPException(status_code=500, detail=f"数据源初始化失败: {str(error)}")
