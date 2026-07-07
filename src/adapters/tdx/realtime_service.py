"""
TDX 实时数据服务 — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Class name (RealtimeService), constructor signature, and all public method
signatures are retained for backward compatibility.

迁移前: 通过 BaseTdxAdapter._get_tdx_connection() 拿到 tdx_api,调用
        tdx_api.get_security_quotes / get_security_list / get_block_info —
        依赖原生 TDX 协议(socket + pytdx),需要本机可访问 TDX 服务器。
迁移后: 通过 OpenStockClient.fetch() 调用 OpenStock 的 REALTIME_QUOTES /
        MARKET_DEPTH / STOCK_INDUSTRY / TOPICS_CONCEPTS / SECTOR_QUOTES category。
        OpenStock 后端用 eltdx/baostock failover,不再依赖本地 TDX 协议栈。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.2.2)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from .base_tdx_adapter import BaseTdxAdapter
from src.services.openstock import (
    DataCategory,
    OpenStockClient,
    OpenStockError,
)


def _normalize_symbol_to_baostock(symbol: str) -> str:
    """归一化到 baostock 风格 sh.600000 / sz.000001."""
    s = str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()
    if s.startswith("6"):
        return f"sh.{s}"
    if s.startswith(("0", "3")):
        return f"sz.{s}"
    return symbol


def _normalize_symbol_to_bare(symbol: str) -> str:
    """归一化到纯数字(eltdx 后端要求)."""
    return str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()


class RealtimeService(BaseTdxAdapter):
    """TDX 实时数据服务 — OpenStock 网关外观.

    保留类名、构造签名、所有公开方法签名。内部实现切换为 OpenStockClient,
    不再走 pytdx 原生协议。
    """

    def __init__(self):
        super().__init__()
        try:
            self._client = OpenStockClient()
            self._available = True
        except OpenStockError as exc:
            logger.error("RealtimeService OpenStock 初始化失败: %s", exc)
            self._client = None  # type: ignore[assignment]
            self._available = False
        logger.info("RealtimeService(OpenStock facade)初始化完成")

    # ---- 内部辅助 ----------------------------------------------------

    def _normalize_symbol(self, symbol: str) -> str:
        """保留 BaseTdxAdapter 兼容签名,实际归一化到 baostock 风格."""
        return _normalize_symbol_to_baostock(symbol)

    def _get_market_code(self, symbol: str) -> int:
        """保留 BaseTdxAdapter 兼容签名,OpenStock 不需要 market_code."""
        std = _normalize_symbol_to_baostock(symbol)
        return 1 if std.startswith("sh.") else 0

    def _get_tdx_connection(self):  # type: ignore[no-untyped-def]
        """保留 BaseTdxAdapter 兼容签名,facade 模式下不再使用 TDX 连接."""
        return None

    # ---- 实时行情 ----------------------------------------------------

    def get_real_time_data(self, symbol: str) -> Optional[Dict]:
        """获取实时行情数据 — OpenStock REALTIME_QUOTES(客户端过滤)."""
        try:
            if not symbol:
                raise ValueError("股票代码不能为空")
            if not self._available:
                return None

            std_symbol = _normalize_symbol_to_baostock(symbol)
            response = self._client.fetch(
                DataCategory.REALTIME_QUOTES,
                {"symbols": std_symbol},
            )
            rows = response.get("data") or []
            # REALTIME_QUOTES 返回前 N 条,需要客户端按 symbol 过滤
            row = next(
                (r for r in rows if r.get("symbol") == std_symbol.replace(".", "") or r.get("symbol") == std_symbol),
                None,
            )
            if not row:
                logger.warning("OpenStock REALTIME_QUOTES 未找到股票 %s", std_symbol)
                return None

            return {
                "symbol": symbol,
                "name": row.get("name", ""),
                "price": float(row.get("price") or 0),
                "open": float(row.get("open") or 0),
                "high": float(row.get("high") or 0),
                "low": float(row.get("low") or 0),
                "pre_close": float(row.get("prev_close") or 0),
                "change": float(row.get("change") or 0),
                "change_pct": float(row.get("pct_chg") or 0),
                "volume": float(row.get("volume") or 0),
                "amount": float(row.get("amount") or 0),
                "turnover": float(row.get("turnover_rate") or 0),
                "pe": float(row.get("pe_dynamic") or 0),
                "pb": float(row.get("pb") or 0),
                "market": "上交所" if std_symbol.startswith("sh.") else "深交所",
                "timestamp": datetime.now().isoformat(),
                "source": "openstock",
            }
        except OpenStockError as exc:
            logger.error("OpenStock 获取实时行情失败 %s: %s", symbol, exc)
            return None
        except Exception as exc:
            logger.error("获取实时行情数据失败: %s", exc)
            return None

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息 — OpenStock ALL_STOCKS(客户端过滤)."""
        try:
            if not symbol:
                raise ValueError("股票代码不能为空")
            if not self._available:
                return {}

            std_symbol = _normalize_symbol_to_baostock(symbol)
            response = self._client.fetch(DataCategory.ALL_STOCKS, {})
            rows = response.get("data") or []
            row = next(
                (r for r in rows if r.get("code") == std_symbol or r.get("symbol") == std_symbol),
                None,
            )
            if not row:
                return {}

            return {
                "symbol": symbol,
                "name": row.get("code_name") or row.get("name") or "",
                "market": "上交所" if std_symbol.startswith("sh.") else "深交所",
                "industry": "",
                "area": "",
                "pe": 0,
                "outstanding": 0,
                "total_shares": 0,
                "float_shares": 0,
                "asset_per_share": 0,
                "bv_per_share": 0,
                "pb": 0,
                "time_to_market": "",
                "listing_date": str(row.get("list_date") or ""),
                "is_st": False,
                "timestamp": datetime.now().isoformat(),
                "source": "openstock",
            }
        except OpenStockError as exc:
            logger.error("OpenStock 获取股票基本信息失败 %s: %s", symbol, exc)
            return {}
        except Exception as exc:
            logger.error("获取股票基本信息失败: %s", exc)
            return {}

    def get_industry_classify(self) -> pd.DataFrame:
        """获取行业分类数据 — OpenStock SECTOR_QUOTES(industry).

        上游 akshare provider 当前不稳定,返回空 DataFrame + warning。
        """
        if not self._available:
            return pd.DataFrame()
        try:
            response = self._client.fetch(
                DataCategory.SECTOR_QUOTES,
                {"sector_type": "industry"},
            )
            rows = response.get("data") or []
            if not rows:
                logger.warning("[OpenStock] SECTOR_QUOTES(industry) 上游返回空")
                return pd.DataFrame()
            return pd.DataFrame(rows)
        except OpenStockError as exc:
            logger.warning(
                "[OpenStock] SECTOR_QUOTES(industry) 上游不可用: %s "
                "(详见 docs/reports/openstock-coverage-gaps.md)", exc,
            )
            return pd.DataFrame()
        except Exception as exc:
            logger.error("获取行业分类数据失败: %s", exc)
            return pd.DataFrame()

    def get_concept_classify(self) -> pd.DataFrame:
        """获取概念分类数据 — OpenStock SECTOR_QUOTES(concept).

        上游 akshare provider 当前不稳定,返回空 DataFrame + warning。
        """
        if not self._available:
            return pd.DataFrame()
        try:
            response = self._client.fetch(
                DataCategory.SECTOR_QUOTES,
                {"sector_type": "concept"},
            )
            rows = response.get("data") or []
            if not rows:
                logger.warning("[OpenStock] SECTOR_QUOTES(concept) 上游返回空")
                return pd.DataFrame()
            return pd.DataFrame(rows)
        except OpenStockError as exc:
            logger.warning(
                "[OpenStock] SECTOR_QUOTES(concept) 上游不可用: %s "
                "(详见 docs/reports/openstock-coverage-gaps.md)", exc,
            )
            return pd.DataFrame()
        except Exception as exc:
            logger.error("获取概念分类数据失败: %s", exc)
            return pd.DataFrame()

    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """获取股票的行业和概念信息 — OpenStock STOCK_INDUSTRY + TOPICS_CONCEPTS."""
        try:
            if not symbol:
                raise ValueError("股票代码不能为空")
            if not self._available:
                return {
                    "symbol": symbol,
                    "industry": {},
                    "concepts": {},
                    "timestamp": datetime.now().isoformat(),
                }

            std_symbol = _normalize_symbol_to_baostock(symbol)
            bare_symbol = _normalize_symbol_to_bare(symbol)

            industry_resp = self._client.fetch(DataCategory.STOCK_INDUSTRY, {})
            industry_match = next(
                (r for r in (industry_resp.get("data") or [])
                 if r.get("symbol") == std_symbol or r.get("code") == std_symbol),
                None,
            )
            industry_name = ""
            if industry_match:
                industry_name = str(industry_match.get("industry") or "").strip()

            topics_resp = self._client.fetch(
                DataCategory.TOPICS_CONCEPTS,
                {"symbol": bare_symbol},
            )
            topic_names = [
                str(r.get("topic_name") or "").strip()
                for r in (topics_resp.get("data") or [])
                if r.get("topic_name")
            ]

            return {
                "symbol": symbol,
                "industry": {"name": industry_name, "code": ""},
                "concepts": {"name": ", ".join(topic_names)},
                "timestamp": datetime.now().isoformat(),
            }
        except OpenStockError as exc:
            logger.error("OpenStock 获取行业概念失败 %s: %s", symbol, exc)
            return {
                "symbol": symbol,
                "industry": {},
                "concepts": {},
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            logger.error("获取股票行业概念信息失败: %s", exc)
            return {
                "symbol": symbol,
                "error": str(exc),
                "timestamp": datetime.now().isoformat(),
            }

    def get_batch_real_time_data(self, symbols: List[str]) -> List[Dict]:
        """批量获取实时行情数据 — OpenStock REALTIME_QUOTES(客户端过滤)."""
        try:
            if not symbols or not self._available:
                return []

            # OpenStock REALTIME_QUOTES 当前忽略 symbols filter,返回前 N 条
            # 我们拉一次,然后按需过滤
            response = self._client.fetch(
                DataCategory.REALTIME_QUOTES,
                {"symbols": ",".join(_normalize_symbol_to_baostock(s) for s in symbols[:50])},
            )
            rows = response.get("data") or []

            results: list[Dict] = []
            for sym in symbols:
                std = _normalize_symbol_to_baostock(sym)
                bare = std.replace(".", "")
                row = next(
                    (r for r in rows if r.get("symbol") == std or r.get("symbol") == bare),
                    None,
                )
                if not row:
                    continue
                results.append({
                    "symbol": sym,
                    "name": row.get("name", ""),
                    "price": float(row.get("price") or 0),
                    "open": float(row.get("open") or 0),
                    "high": float(row.get("high") or 0),
                    "low": float(row.get("low") or 0),
                    "pre_close": float(row.get("prev_close") or 0),
                    "change": float(row.get("change") or 0),
                    "change_pct": float(row.get("pct_chg") or 0),
                    "volume": float(row.get("volume") or 0),
                    "amount": float(row.get("amount") or 0),
                    "market": "上交所" if std.startswith("sh.") else "深交所",
                    "timestamp": datetime.now().isoformat(),
                    "source": "openstock",
                })
            logger.info("OpenStock 批量实时行情: 请求 %d 命中 %d", len(symbols), len(results))
            return results
        except OpenStockError as exc:
            logger.error("OpenStock 批量实时行情失败: %s", exc)
            return []
        except Exception as exc:
            logger.error("批量获取实时行情数据失败: %s", exc)
            return []

    # ==================== IDataSource接口补全(保留 no-op 占位) ====================

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """RealtimeService 专注实时数据,不支持历史 K 线."""
        logger.warning("RealtimeService 不支持获取历史日线数据: %s", symbol)
        return pd.DataFrame()

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """RealtimeService 专注实时数据,不支持历史指数."""
        logger.warning("RealtimeService 不支持获取历史指数数据: %s", symbol)
        return pd.DataFrame()

    def get_index_components(self, symbol: str) -> list:
        """RealtimeService 专注实时数据,不支持指数成分股."""
        logger.warning("RealtimeService 不支持获取指数成分股: %s", symbol)
        return []

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """RealtimeService 专注实时数据,不支持交易日历."""
        logger.warning("RealtimeService 不支持获取交易日历")
        return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """RealtimeService 专注实时数据,不支持财务数据."""
        logger.warning("RealtimeService 不支持获取财务数据: %s", symbol)
        return pd.DataFrame()

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> list:
        """RealtimeService 专注实时行情,不支持新闻数据."""
        logger.warning("RealtimeService 不支持获取新闻数据")
        return []
