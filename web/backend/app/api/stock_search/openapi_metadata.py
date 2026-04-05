"""OpenAPI metadata for stock-search routes."""

from typing import Any

from app.openapi_config import COMMON_RESPONSES


def _success_response_spec(description: str, example: Any) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _error_response_spec(status_code: int, description: str, example: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


STOCK_SEARCH_RESPONSES = {
    400: COMMON_RESPONSES[400],
    401: COMMON_RESPONSES[401],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_error_response_spec(
        429,
        "搜索频率超限",
        {"code": "RATE_LIMIT_EXCEEDED", "message": "搜索频率过高，请稍后再试", "data": None, "path": "/api/stock-search/search", "timestamp": None},
    ),
    **_error_response_spec(
        503,
        "股票搜索服务暂不可用",
        {"code": "SERVICE_UNAVAILABLE", "message": "股票搜索服务暂时不可用，请稍后重试", "data": None, "path": "/api/stock-search/search", "timestamp": None},
    ),
    **_success_response_spec(
        "A股与港股股票搜索结果",
        [
            {"symbol": "600519", "description": "贵州茅台", "displaySymbol": "600519.SH", "type": "Common Stock", "exchange": "SSE", "market": "cn"},
            {"symbol": "00700", "description": "腾讯控股", "displaySymbol": "00700.HK", "type": "Common Stock", "exchange": "HKEX", "market": "hk"},
        ],
    ),
}

STOCK_QUOTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    401: COMMON_RESPONSES[401],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_error_response_spec(
        429,
        "行情访问频率超限",
        {"code": "RATE_LIMIT_EXCEEDED", "message": "访问频率过高，请稍后再试", "data": None, "path": "/api/stock-search/quote/600519", "timestamp": None},
    ),
    **_error_response_spec(
        503,
        "实时行情服务暂不可用",
        {"code": "SERVICE_UNAVAILABLE", "message": "数据源暂时不可用，请稍后重试", "data": None, "path": "/api/stock-search/quote/600519", "timestamp": None},
    ),
    **_success_response_spec(
        "A股或港股实时行情",
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "current": 1710.88,
            "change": 12.31,
            "percent_change": 0.72,
            "high": 1718.6,
            "low": 1688.0,
            "open": 1695.0,
            "previous_close": 1698.57,
            "volume": 325800.0,
            "amount": 556000000.0,
            "timestamp": 1775351400.0,
        },
    ),
}

STOCK_PROFILE_RESPONSES = {
    401: COMMON_RESPONSES[401],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_error_response_spec(
        501,
        "当前环境未启用公司资料服务",
        {"code": "FEATURE_NOT_SUPPORTED", "message": "公司基本信息功能暂不支持，本系统仅支持 A 股和 H 股（港股），不支持美股", "data": None, "path": "/api/stock-search/profile/600519", "timestamp": None},
    ),
    **_error_response_spec(
        503,
        "公司资料服务暂不可用",
        {"code": "COMPANY_INFO_SERVICE_UNAVAILABLE", "message": "公司信息服务暂时不可用，请稍后重试", "data": None, "path": "/api/stock-search/profile/600519", "timestamp": None},
    ),
    **_success_response_spec(
        "A股或港股公司资料",
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "industry": "酿酒行业",
            "market_cap": 2148000000000.0,
            "listing_date": "2001-08-27",
            "description": "贵州茅台酒股份有限公司，主营高端白酒生产与销售。",
        },
    ),
}

STOCK_NEWS_RESPONSES = {
    401: COMMON_RESPONSES[401],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_error_response_spec(
        503,
        "个股新闻服务暂不可用",
        {"code": "NEWS_SERVICE_UNAVAILABLE", "message": "新闻服务暂时不可用，请稍后重试", "data": None, "path": "/api/stock-search/news/600519", "timestamp": None},
    ),
    **_success_response_spec(
        "A股或港股个股新闻列表",
        [
            {
                "headline": "贵州茅台披露最新经营数据",
                "summary": "公司公告显示主营产品销售保持稳健增长。",
                "source": "上证报",
                "datetime": 1775351400.0,
                "url": "https://example.com/news/600519",
                "image": None,
                "category": "company",
            }
        ],
    ),
}

MARKET_NEWS_RESPONSES = {
    401: COMMON_RESPONSES[401],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_error_response_spec(
        503,
        "市场新闻服务暂不可用",
        {"code": "MARKET_NEWS_SERVICE_UNAVAILABLE", "message": "市场新闻服务暂时不可用，请稍后重试", "data": None, "path": "/api/stock-search/news/market/general", "timestamp": None},
    ),
    **_success_response_spec(
        "A股或港股市场新闻列表",
        [
            {
                "headline": "港股科技板块早盘走强",
                "summary": "恒生科技指数成分股普遍上涨，市场风险偏好回暖。",
                "source": "财联社",
                "datetime": 1775351400.0,
                "url": "https://example.com/news/market/general",
                "image": None,
                "category": "macro",
            }
        ],
    ),
}

RECOMMENDATION_RESPONSES = {
    401: COMMON_RESPONSES[401],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_error_response_spec(
        501,
        "当前环境未启用分析师推荐服务",
        {"code": "FEATURE_NOT_SUPPORTED", "message": "分析师推荐功能暂不支持，本系统仅支持 A 股和 H 股（港股），不支持美股", "data": None, "path": "/api/stock-search/recommendation/600519", "timestamp": None},
    ),
    **_error_response_spec(
        503,
        "推荐分析服务暂不可用",
        {"code": "RECOMMENDATION_SERVICE_UNAVAILABLE", "message": "推荐分析服务暂时不可用，请稍后重试", "data": None, "path": "/api/stock-search/recommendation/600519", "timestamp": None},
    ),
    **_success_response_spec(
        "个股分析师推荐趋势",
        {"symbol": "600519", "rating": "buy", "target_price": 1888.0, "analyst_count": 12, "as_of": "2026-04-05"},
    ),
}

CACHE_CLEAR_RESPONSES = {
    401: COMMON_RESPONSES[401],
    403: COMMON_RESPONSES[403],
    500: COMMON_RESPONSES[500],
    **_success_response_spec(
        "搜索缓存清理结果",
        {"success": True, "data": {"cleared_by": "admin"}, "message": "搜索缓存已清除"},
    ),
}

SEARCH_ANALYTICS_RESPONSES = {
    401: COMMON_RESPONSES[401],
    403: COMMON_RESPONSES[403],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_success_response_spec(
        "搜索分析数据查询结果",
        {
            "analytics": [{"operation": "search_stocks", "username": "alice", "query": "腾讯", "timestamp": 1775351400.0}],
            "total_count": 1,
            "statistics": {"operation_counts": {"search_stocks": 1}, "user_counts": {"alice": 1}},
            "filter_applied": {"operation": "search_stocks", "username": None},
            "returned_count": 1,
        },
    ),
}

SEARCH_ANALYTICS_CLEANUP_RESPONSES = {
    401: COMMON_RESPONSES[401],
    403: COMMON_RESPONSES[403],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_success_response_spec(
        "搜索分析清理结果",
        {"success": True, "data": {"cleaned_count": 12, "remaining_count": 35, "cutoff_days": 7}, "message": "已清理 12 条旧搜索分析数据"},
    ),
}

RATE_LIMIT_STATUS_RESPONSES = {
    401: COMMON_RESPONSES[401],
    403: COMMON_RESPONSES[403],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_success_response_spec(
        "访问频率限制状态查询结果",
        {
            "success": True,
            "data": {
                "total_users": 2,
                "user_limits": {
                    "101": {
                        "rate_limits": {"29589240": 12, "29589241": 4},
                        "total_minutes": 2,
                        "current_minute_requests": 4,
                    }
                },
            },
            "message": "所有用户的频率限制状态",
        },
    ),
}
