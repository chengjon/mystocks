"""
股票搜索服务模块
支持多数据源：
- AKShare: A股数据和港股数据
- 统一搜索接口

迁移自 OpenStock 项目
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import Request
import requests

try:
    import akshare as ak

    AKSHARE_AVAILABLE = True
except ImportError:
    ak = None
    AKSHARE_AVAILABLE = False

try:
    from ._stock_search_cn import (
        _get_a_stock_exchange as _resolve_a_stock_exchange,
    )
    from ._stock_search_cn import get_a_stock_kline as _get_a_stock_kline
    from ._stock_search_cn import get_a_stock_news as _get_a_stock_news
    from ._stock_search_cn import get_a_stock_realtime as _get_a_stock_realtime
    from ._stock_search_cn import search_a_stocks as _search_a_stocks
    from ._stock_search_finnhub import get_company_news as _get_company_news
    from ._stock_search_finnhub import get_company_profile as _get_company_profile
    from ._stock_search_finnhub import get_market_news as _get_market_news
    from ._stock_search_finnhub import get_recommendation_trends as _get_recommendation_trends
    from ._stock_search_finnhub import get_stock_quote as _get_stock_quote
    from ._stock_search_finnhub import search_stocks as _search_stocks
    from ._stock_search_hk import get_hk_stock_news as _get_hk_stock_news
    from ._stock_search_hk import get_hk_stock_realtime as _get_hk_stock_realtime
    from ._stock_search_hk import search_hk_stocks as _search_hk_stocks
    from .parse_datetime_to_timestamp import FinnhubAPIError
except ImportError:
    from app.services.stock_search_service._stock_search_cn import (  # type: ignore
        _get_a_stock_exchange as _resolve_a_stock_exchange,
    )
    from app.services.stock_search_service._stock_search_cn import get_a_stock_kline as _get_a_stock_kline  # type: ignore
    from app.services.stock_search_service._stock_search_cn import get_a_stock_news as _get_a_stock_news  # type: ignore
    from app.services.stock_search_service._stock_search_cn import get_a_stock_realtime as _get_a_stock_realtime  # type: ignore
    from app.services.stock_search_service._stock_search_cn import search_a_stocks as _search_a_stocks  # type: ignore
    from app.services.stock_search_service._stock_search_finnhub import get_company_news as _get_company_news  # type: ignore
    from app.services.stock_search_service._stock_search_finnhub import get_company_profile as _get_company_profile  # type: ignore
    from app.services.stock_search_service._stock_search_finnhub import get_market_news as _get_market_news  # type: ignore
    from app.services.stock_search_service._stock_search_finnhub import (  # type: ignore
        get_recommendation_trends as _get_recommendation_trends,
    )
    from app.services.stock_search_service._stock_search_finnhub import get_stock_quote as _get_stock_quote  # type: ignore
    from app.services.stock_search_service._stock_search_finnhub import search_stocks as _search_stocks  # type: ignore
    from app.services.stock_search_service._stock_search_hk import get_hk_stock_news as _get_hk_stock_news  # type: ignore
    from app.services.stock_search_service._stock_search_hk import (  # type: ignore
        get_hk_stock_realtime as _get_hk_stock_realtime,
    )
    from app.services.stock_search_service._stock_search_hk import search_hk_stocks as _search_hk_stocks  # type: ignore
    from app.services.stock_search_service.parse_datetime_to_timestamp import FinnhubAPIError  # type: ignore

logger = logging.getLogger(__name__)
if not AKSHARE_AVAILABLE:
    logger.warning("AKShare library not available, A/H share search features are disabled")


_stock_search_service = None
STOCK_SEARCH_SERVICE_STATE_KEY = "stock_search_service"


class StockSearchService:
    """统一股票搜索服务。"""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://finnhub.io/api/v1"):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MyStocks/1.0"})
        self.akshare_available = AKSHARE_AVAILABLE
        self.kline_fallback_enabled = os.getenv("KLINE_FALLBACK_ENABLED", "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self.api_key = api_key
        self.base_url = base_url

    @staticmethod
    def _log_exception(action: str, error: Exception) -> None:
        logger.exception("%s: %s", action, error)

    @staticmethod
    def _log_warning(message: str, *args) -> None:
        logger.warning(message, *args)

    @staticmethod
    def _get_akshare_module():
        return ak

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发起 Finnhub API 请求。"""
        url = f"{self.base_url}/{endpoint}"
        request_params = params or {}
        request_params["token"] = self.api_key

        try:
            response = self.session.get(url, params=request_params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            raise FinnhubAPIError(f"API request failed: {error}")
        except json.JSONDecodeError as error:
            raise FinnhubAPIError(f"Failed to parse API response: {error}")

    search_stocks = _search_stocks
    get_stock_quote = _get_stock_quote
    get_company_profile = _get_company_profile
    get_company_news = _get_company_news
    get_market_news = _get_market_news
    get_recommendation_trends = _get_recommendation_trends
    search_a_stocks = _search_a_stocks
    _get_a_stock_exchange = _resolve_a_stock_exchange
    search_hk_stocks = _search_hk_stocks
    get_hk_stock_realtime = _get_hk_stock_realtime
    get_hk_stock_news = _get_hk_stock_news
    get_a_stock_realtime = _get_a_stock_realtime
    get_a_stock_news = _get_a_stock_news
    get_a_stock_kline = _get_a_stock_kline

    def clear_cache(self):
        """清除搜索缓存。"""
        if hasattr(self, "search_a_stocks"):
            self.search_a_stocks.cache_clear()
        if hasattr(self, "search_hk_stocks"):
            self.search_hk_stocks.cache_clear()

    def unified_search(self, query: str, market: str = "auto") -> List[Dict]:
        """统一搜索接口，根据市场类型自动选择数据源。"""
        results = []

        if market == "auto":
            if any("\u4e00" <= char <= "\u9fff" for char in query):
                market = "cn"
            elif query.isdigit() and len(query) == 6:
                market = "cn"
            elif query.isdigit() and len(query) == 5:
                market = "hk"
            else:
                market = "all"

        if market == "cn" and self.akshare_available:
            results = self.search_a_stocks(query)
        elif market == "hk" and self.akshare_available:
            results = self.search_hk_stocks(query)
        elif market == "all" and self.akshare_available:
            results.extend(self.search_a_stocks(query))
            results.extend(self.search_hk_stocks(query))
        elif self.akshare_available:
            results.extend(self.search_a_stocks(query))
            results.extend(self.search_hk_stocks(query))

        return results


def get_stock_search_service() -> StockSearchService:
    """获取股票搜索服务实例（单例模式）。"""
    global _stock_search_service
    if _stock_search_service is None:
        _stock_search_service = StockSearchService()
    return _stock_search_service


def install_stock_search_service(app: Any, service: StockSearchService | None = None) -> StockSearchService:
    selected_service = service if service is not None else get_stock_search_service()
    setattr(app.state, STOCK_SEARCH_SERVICE_STATE_KEY, selected_service)
    return selected_service


def get_stock_search_service_dependency(request: Request) -> StockSearchService:
    service = getattr(request.app.state, STOCK_SEARCH_SERVICE_STATE_KEY, None)
    if service is None:
        service = install_stock_search_service(request.app)
    return service
