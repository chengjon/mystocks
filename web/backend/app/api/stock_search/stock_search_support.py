"""
股票搜索 API 的审计与限流辅助。
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from app.api.auth import User

logger = logging.getLogger(__name__)

search_operation_count: dict[int, dict[int, int]] = {}
search_analytics: list[dict[str, Any]] = []


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
