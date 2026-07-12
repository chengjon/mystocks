from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional


try:
    from .parse_datetime_to_timestamp import FinnhubAPIError
except ImportError:
    from app.services.stock_search_service.parse_datetime_to_timestamp import FinnhubAPIError  # type: ignore


@lru_cache(maxsize=1000)
def search_stocks(self, query: str) -> List[Dict]:
    """搜索股票（带缓存）。"""
    try:
        data = self._make_request("search", {"q": query})
        results = []
        for item in data.get("result", [])[:20]:
            results.append(
                {
                    "symbol": item.get("symbol"),
                    "description": item.get("description"),
                    "displaySymbol": item.get("displaySymbol"),
                    "type": item.get("type"),
                    "exchange": item.get("exchange"),
                },
            )
        return results
    except FinnhubAPIError as error:
        self._log_exception("搜索股票时发生错误", error)
        return []


def get_stock_quote(self, symbol: str) -> Optional[Dict]:
    """获取股票实时报价。"""
    try:
        data = self._make_request("quote", {"symbol": symbol})
        if not data or data.get("c") is None:
            return None

        return {
            "current": data.get("c"),
            "change": data.get("d"),
            "percent_change": data.get("dp"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "previous_close": data.get("pc"),
            "timestamp": data.get("t"),
        }
    except FinnhubAPIError as error:
        self._log_exception("获取股票报价时发生错误", error)
        return None


def get_company_profile(self, symbol: str) -> Optional[Dict]:
    """获取公司基本信息。"""
    try:
        data = self._make_request("stock/profile2", {"symbol": symbol})
        if not data:
            return None

        return {
            "country": data.get("country"),
            "currency": data.get("currency"),
            "exchange": data.get("exchange"),
            "ipo": data.get("ipo"),
            "market_cap": data.get("marketCapitalization"),
            "name": data.get("name"),
            "phone": data.get("phone"),
            "share_outstanding": data.get("shareOutstanding"),
            "ticker": data.get("ticker"),
            "weburl": data.get("weburl"),
            "logo": data.get("logo"),
            "industry": data.get("finnhubIndustry"),
        }
    except FinnhubAPIError as error:
        self._log_exception("获取公司信息时发生错误", error)
        return None


def get_company_news(self, symbol: str, from_date: str = None, to_date: str = None) -> List[Dict]:
    """获取公司新闻。"""
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    if not from_date:
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        data = self._make_request("company-news", {"symbol": symbol, "from": from_date, "to": to_date})
        news_list = []
        for item in data[:50]:
            news_list.append(
                {
                    "headline": item.get("headline"),
                    "summary": item.get("summary"),
                    "source": item.get("source"),
                    "datetime": item.get("datetime"),
                    "url": item.get("url"),
                    "image": item.get("image"),
                    "related": item.get("related"),
                    "category": item.get("category"),
                },
            )
        return news_list
    except FinnhubAPIError as error:
        self._log_exception("获取公司新闻时发生错误", error)
        return []


def get_market_news(self, category: str = "general") -> List[Dict]:
    """获取市场新闻。"""
    try:
        data = self._make_request("news", {"category": category})
        news_list = []
        for item in data[:30]:
            news_list.append(
                {
                    "headline": item.get("headline"),
                    "summary": item.get("summary"),
                    "source": item.get("source"),
                    "datetime": item.get("datetime"),
                    "url": item.get("url"),
                    "image": item.get("image"),
                    "category": item.get("category"),
                },
            )
        return news_list
    except FinnhubAPIError as error:
        self._log_exception("获取市场新闻时发生错误", error)
        return []


def get_recommendation_trends(self, symbol: str) -> List[Dict]:
    """获取分析师推荐趋势。"""
    try:
        data = self._make_request("stock/recommendation", {"symbol": symbol})
        return [
            {
                "period": item.get("period"),
                "strong_buy": item.get("strongBuy"),
                "buy": item.get("buy"),
                "hold": item.get("hold"),
                "sell": item.get("sell"),
                "strong_sell": item.get("strongSell"),
            }
            for item in data
        ]
    except FinnhubAPIError as error:
        self._log_exception("获取推荐趋势时发生错误", error)
        return []
