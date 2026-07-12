from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Tuple


try:
    from .kline_fallback import build_fallback_kline
    from .parse_datetime_to_timestamp import normalize_stock_code, parse_datetime_to_timestamp
except ImportError:
    from app.services.stock_search_service.kline_fallback import build_fallback_kline  # type: ignore
    from app.services.stock_search_service.parse_datetime_to_timestamp import (  # type: ignore
        normalize_stock_code,
        parse_datetime_to_timestamp,
    )


@lru_cache(maxsize=1000)
def search_a_stocks(self, query: str) -> List[Dict]:
    """搜索 A 股股票（带缓存）。"""
    if not self.akshare_available:
        self._log_warning("A股搜索失败: AKShare 未安装")
        return []

    try:
        ak_module = self._get_akshare_module()
        stock_info_df = ak_module.stock_info_a_code_name()
        query_upper = query.upper()
        matched_stocks = stock_info_df[
            (stock_info_df["code"].str.contains(query_upper, case=False))
            | (stock_info_df["name"].str.contains(query, case=False))
        ]

        results = []
        for _, row in matched_stocks.head(20).iterrows():
            results.append(
                {
                    "symbol": row["code"],
                    "description": row["name"],
                    "displaySymbol": row["code"],
                    "type": "A股",
                    "exchange": self._get_a_stock_exchange(row["code"]),
                    "market": "CN",
                },
            )
        return results
    except Exception as error:
        self._log_exception("搜索 A 股时发生错误", error)
        return []


def _get_a_stock_exchange(self, code: str) -> str:
    """根据股票代码判断交易所。"""
    if code.startswith("6"):
        return "上海证券交易所"
    if code.startswith("0") or code.startswith("3"):
        return "深圳证券交易所"
    if code.startswith("8") or code.startswith("4"):
        return "北京证券交易所"
    return "未知"


def get_a_stock_realtime(self, symbol: str) -> Optional[Dict]:
    """获取 A 股实时行情。"""
    if not self.akshare_available:
        self._log_warning("获取 A 股行情失败: AKShare 未安装")
        return None

    try:
        try:
            normalized_code = normalize_stock_code(symbol, market="cn")
        except ValueError as error:
            self._log_warning("股票代码格式错误: %s", error)
            return None

        code_for_query = normalized_code.split(".")[0]
        ak_module = self._get_akshare_module()
        df = ak_module.stock_zh_a_spot_em()
        stock_data = df[df["代码"] == code_for_query]
        if stock_data.empty:
            return None

        row = stock_data.iloc[0]
        return {
            "symbol": normalized_code,
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
            "turnover_rate": float(row["换手率"]) if "换手率" in row else None,
            "timestamp": datetime.now().timestamp(),
        }
    except Exception as error:
        self._log_exception("获取 A 股实时行情时发生错误", error)
        return None


def get_a_stock_news(self, symbol: str = None, days: int = 7) -> List[Dict]:
    """获取 A 股新闻。"""
    if not self.akshare_available:
        self._log_warning("获取 A 股新闻失败: AKShare 未安装")
        return []

    try:
        ak_module = self._get_akshare_module()
        if symbol:
            try:
                news_df = ak_module.stock_news_em(symbol=symbol)
            except Exception as error:
                self._log_warning("无法获取股票 %s 的新闻: %s", symbol, error)
                return []
        else:
            news_df = ak_module.stock_news_em()

        news_list = []
        for _, row in news_df.head(30).iterrows():
            news_list.append(
                {
                    "headline": row.get("新闻标题", ""),
                    "summary": row.get("新闻内容", "")[:200] if "新闻内容" in row else "",
                    "source": row.get("新闻来源", "东方财富"),
                    "datetime": parse_datetime_to_timestamp(row.get("发布时间")),
                    "url": row.get("新闻链接", ""),
                    "category": "A股新闻",
                },
            )
        return news_list
    except Exception as error:
        self._log_exception("获取 A 股新闻时发生错误", error)
        return []


def _resolve_kline_date_range(start_date: str = None, end_date: str = None) -> Tuple[str, str]:
    """格式化 AKShare K 线查询日期。"""
    if start_date:
        start_date_formatted = start_date.replace("-", "")
    else:
        start_date_formatted = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")

    if end_date:
        end_date_formatted = end_date.replace("-", "")
    else:
        end_date_formatted = datetime.now().strftime("%Y%m%d")

    return start_date_formatted, end_date_formatted


def _parse_kline_date(date_str: str) -> datetime:
    """解析 K 线日期。"""
    if len(date_str) == 8:
        return datetime.strptime(date_str, "%Y%m%d")
    return datetime.strptime(date_str.split(" ", maxsplit=1)[0], "%Y-%m-%d")


def _build_kline_data_points(df) -> List[Dict]:
    """将 AKShare DataFrame 转为标准 K 线列表。"""
    data_points = []
    previous_close = None

    for _, row in df.iterrows():
        date_obj = _parse_kline_date(str(row["日期"]))
        open_price = float(row["开盘"])
        high_price = float(row["最高"])
        low_price = float(row["最低"])
        close_price = float(row["收盘"])
        volume = int(row["成交量"]) if "成交量" in row else 0
        amount = float(row["成交额"]) if "成交额" in row else 0.0

        if previous_close and previous_close > 0:
            amplitude = ((high_price - low_price) / previous_close) * 100
            change_percent = ((close_price - previous_close) / previous_close) * 100
        else:
            amplitude = 0.0
            change_percent = 0.0

        data_points.append(
            {
                "date": date_obj.strftime("%Y-%m-%d"),
                "timestamp": int(date_obj.timestamp()),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume,
                "amount": round(amount, 2),
                "amplitude": round(amplitude, 2),
                "change_percent": round(change_percent, 2),
            },
        )
        previous_close = close_price

    data_points.reverse()
    return data_points


def get_a_stock_kline(
    self,
    symbol: str,
    period: str = "daily",
    adjust: str = "qfq",
    start_date: str = None,
    end_date: str = None,
) -> Optional[Dict]:
    """获取 A 股 K 线数据。"""
    try:
        try:
            normalized_code = normalize_stock_code(symbol, market="cn")
        except ValueError as error:
            self._log_warning("股票代码格式错误: %s", error)
            return None

        if period not in ["daily", "weekly", "monthly"]:
            self._log_warning("无效的时间周期: %s。支持的值: daily, weekly, monthly", period)
            return None

        if adjust not in ["qfq", "hfq", ""]:
            self._log_warning("无效的复权类型: %s。支持的值: qfq, hfq, 或空字符串", adjust)
            return None

        if not self.akshare_available:
            if self.kline_fallback_enabled:
                self._log_warning("AKShare unavailable, returning fallback kline data for %s", normalized_code)
                return build_fallback_kline(normalized_code, period, adjust, end_date=end_date)
            self._log_warning("AKShare unavailable and fallback disabled for %s", normalized_code)
            return None

        code_for_query = normalized_code.split(".")[0]
        start_date_formatted, end_date_formatted = _resolve_kline_date_range(start_date, end_date)

        ak_module = self._get_akshare_module()
        df = ak_module.stock_zh_a_hist(
            symbol=code_for_query,
            period=period,
            start_date=start_date_formatted,
            end_date=end_date_formatted,
            adjust=adjust,
        )

        if df.empty:
            if self.kline_fallback_enabled:
                self._log_warning("No kline data from AKShare for %s, using fallback", code_for_query)
                return build_fallback_kline(normalized_code, period, adjust, end_date=end_date)
            self._log_warning("No kline data from AKShare for %s and fallback disabled", code_for_query)
            return None

        stock_name = df["股票名称"].iloc[0] if "股票名称" in df.columns else code_for_query
        data_points = _build_kline_data_points(df)

        return {
            "stock_code": normalized_code,
            "stock_name": stock_name,
            "period": period,
            "adjust": adjust,
            "data": data_points,
            "count": len(data_points),
        }
    except Exception as error:
        normalized_code = normalize_stock_code(symbol, market="cn")
        if self.kline_fallback_enabled:
            self._log_warning("Kline upstream fetch failed for %s: %s. Using fallback data.", symbol, error)
            return build_fallback_kline(normalized_code, period, adjust, end_date=end_date)
        self._log_warning("Kline upstream fetch failed for %s and fallback disabled: %s", symbol, error)
        return None
