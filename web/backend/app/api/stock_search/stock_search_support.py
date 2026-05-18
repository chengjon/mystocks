"""
股票搜索 API 的审计、限流与输入校验辅助。
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Optional

from app.api.auth import User
from app.core.config import settings

logger = logging.getLogger(__name__)

search_operation_count: dict[int, dict[int, int]] = {}
search_analytics: list[dict[str, Any]] = []


def _is_stock_search_mock_enabled() -> bool:
    """股票搜索 mock 模式由统一配置显式控制。"""
    return settings.stock_search_mock_enabled or settings.use_mock_apis


def _is_stock_search_mock_fallback_enabled() -> bool:
    """真实搜索失败后的 mock 回退必须显式开启。"""
    return settings.stock_search_mock_fallback_enabled


def _get_mock_stock_search_results(keyword: str, *, market: str, limit: int) -> List[Dict[str, Any]]:
    from app.mock.unified_mock_data import get_mock_data_manager

    mock_manager = get_mock_data_manager()
    mock_data = mock_manager.get_data("stock_search", keyword=keyword, market=market, limit=limit)
    return mock_data.get("data", [])


def _get_mock_stock_data(data_type: str, **kwargs: Any) -> Any:
    from app.mock.unified_mock_data import get_mock_data_manager

    mock_manager = get_mock_data_manager()
    mock_data = mock_manager.get_data(data_type, **kwargs)
    return mock_data.get("data")


def validate_stock_symbol(symbol: str, market: str) -> str:
    """验证股票代码格式。"""
    if not symbol:
        raise ValueError("股票代码不能为空")

    symbol = symbol.strip().upper()

    if market.lower() == "cn":
        if not re.match(r"^\d{6}$", symbol):
            raise ValueError("A股代码格式错误，应为6位数字")
    elif market.lower() == "hk":
        if not re.match(r"^\d{4,5}$|^\d{4}[A-Z]$", symbol):
            raise ValueError("港股代码格式错误，应为4-5位数字或4位数字+字母")

    return symbol


def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """清理查询参数，移除潜在的SQL注入和XSS攻击字符。"""
    sanitized = {}
    for key, value in params.items():
        if isinstance(value, str):
            value = re.sub(r'[<>"\'/\\;]', "", value)
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    return sanitized


def check_search_rate_limit(user_id: int, max_searches_per_minute: int = 30) -> bool:
    """检查搜索操作频率限制。"""
    current_time = int(time.time() / 60)

    if user_id not in search_operation_count:
        search_operation_count[user_id] = {}

    if current_time not in search_operation_count[user_id]:
        search_operation_count[user_id][current_time] = 0

    search_operation_count[user_id][current_time] += 1

    for old_time in list(search_operation_count[user_id].keys()):
        if current_time - old_time > 5:
            del search_operation_count[user_id][old_time]

    return search_operation_count[user_id][current_time] <= max_searches_per_minute


def check_admin_privileges(user: User) -> bool:
    """检查管理员权限。"""
    return user.role in ["admin", "backup_operator"]


def log_search_operation(
    user: User,
    operation: str,
    query: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> None:
    """记录搜索操作分析。"""
    analytics_entry = {
        "timestamp": time.time(),
        "user_id": user.id,
        "username": user.username,
        "operation": operation,
        "query": query,
        "details": details,
        "ip_address": getattr(user, "ip_address", "unknown"),
    }

    search_analytics.append(analytics_entry)
    if len(search_analytics) > 1000:
        search_analytics.pop(0)

    logger.info("Search operation logged: %s by %s", operation, user.username)
