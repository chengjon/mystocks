"""任务 API 安全与审计辅助函数。
"""

import time
from datetime import datetime, timezone
from typing import Dict, Optional

from app.api.auth import User


task_operation_count: dict[int, dict[int, int]] = {}
task_audit_log: list[dict] = []


def check_task_rate_limit(user_id: int, max_operations_per_minute: int = 10) -> bool:
    """检查任务操作频率限制。"""
    current_time = int(time.time() / 60)

    if user_id not in task_operation_count:
        task_operation_count[user_id] = {}

    if current_time not in task_operation_count[user_id]:
        task_operation_count[user_id][current_time] = 0

    task_operation_count[user_id][current_time] += 1

    for old_time in list(task_operation_count[user_id].keys()):
        if current_time - old_time > 5:
            del task_operation_count[user_id][old_time]

    return task_operation_count[user_id][current_time] <= max_operations_per_minute


def check_admin_privileges(user: User) -> bool:
    """检查管理员权限。"""
    return user.role in ["admin", "backup_operator"]


def log_task_operation(
    user: User,
    operation: str,
    task_id: Optional[str] = None,
    details: Optional[Dict] = None,
) -> None:
    """记录任务操作审计日志。"""
    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user.id,
        "username": user.username,
        "operation": operation,
        "task_id": task_id,
        "details": details,
        "ip_address": getattr(user, "ip_address", "unknown"),
    }

    task_audit_log.append(audit_entry)

    if len(task_audit_log) > 1000:
        task_audit_log.pop(0)
