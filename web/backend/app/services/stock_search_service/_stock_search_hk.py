from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional


@lru_cache(maxsize=1000)
def search_hk_stocks(self, query: str) -> List[Dict]:
    """搜索港股股票（带缓存）。"""
    if not self.akshare_available:
        self._log_warning("港股搜索失败: AKShare 未安装")
        return []

    try:
        ak_module = self._get_akshare_module()
        hk_stock_df = ak_module.stock_hk_spot_em()
        query_upper = query.upper()
        matched_stocks = hk_stock_df[
            (hk_stock_df["代码"].astype(str).str.contains(query_upper, case=False))
            | (hk_stock_df["名称"].str.contains(query, case=False))
        ]

        results = []
        for _, row in matched_stocks.head(20).iterrows():
            results.append(
                {
                    "symbol": str(row["代码"]),
                    "description": row["名称"],
                    "displaySymbol": str(row["代码"]),
                    "type": "H股",
                    "exchange": "香港证券交易所",
                    "market": "HK",
                }
            )
        return results
    except Exception as error:
        self._log_exception("搜索港股时发生错误", error)
        return []


def get_hk_stock_realtime(self, symbol: str) -> Optional[Dict]:
    """获取港股实时行情。"""
    if not self.akshare_available:
        self._log_warning("获取港股行情失败: AKShare 未安装")
        return None

    try:
        ak_module = self._get_akshare_module()
        df = ak_module.stock_hk_spot_em()
        stock_data = df[df["代码"].astype(str) == symbol]
        if stock_data.empty:
            return None

        row = stock_data.iloc[0]
        return {
            "symbol": symbol,
            "name": row["名称"],
            "current": float(row["最新价"]),
            "change": float(row["涨跌额"]),
            "percent_change": float(row["涨跌幅"]),
            "open": float(row["今开"]),
            "high": float(row["最高"]),
            "low": float(row["最低"]),
            "previous_close": float(row["昨收"]),
            "volume": float(row["成交量"]),
            "amount": float(row["成交额"]),
            "timestamp": datetime.now().timestamp(),
        }
    except Exception as error:
        self._log_exception("获取港股实时行情时发生错误", error)
        return None


def get_hk_stock_news(self, symbol: str = None) -> List[Dict]:
    """获取港股新闻。"""
    if not self.akshare_available:
        self._log_warning("获取港股新闻失败: AKShare 未安装")
        return []

    try:
        return []
    except Exception as error:
        self._log_exception("获取港股新闻时发生错误", error)
        return []
