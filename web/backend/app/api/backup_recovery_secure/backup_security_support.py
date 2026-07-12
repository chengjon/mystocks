"""备份恢复安全辅助函数"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.core.security import User
from app.models.backup_schemas import require_admin_role, require_backup_permission, require_recovery_permission


security_logger = logging.getLogger("backup_security")
security_logger.setLevel(logging.INFO)

handler = logging.FileHandler("/tmp/backup_security.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

if not any(
    getattr(existing_handler, "baseFilename", None) == handler.baseFilename
    for existing_handler in security_logger.handlers
):
    security_logger.addHandler(handler)

_backup_operation_cache: dict[Any, list[float]] = {}
_recovery_operation_cache: dict[Any, list[float]] = {}
_rate_limit_window = 300
_max_backup_operations = 3
_max_recovery_operations = 1


def log_security_event(
    event_type: str,
    user: User,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    success: bool = True,
) -> None:
    """记录安全审计日志。"""
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "user_id": user.id,
        "username": user.username,
        "user_role": user.role,
        "action": action,
        "ip_address": "client",
        "success": success,
        "details": details or {},
    }

    security_logger.info("SECURITY_EVENT: %(log_data)s")


def check_backup_rate_limit(user: User) -> bool:
    """检查备份操作速率限制。"""
    current_time = time.time()
    user_id = user.id
    cutoff_time = current_time - _rate_limit_window

    if user_id in _backup_operation_cache:
        _backup_operation_cache[user_id] = [
            timestamp for timestamp in _backup_operation_cache[user_id] if timestamp > cutoff_time
        ]

    user_operations = _backup_operation_cache.get(user_id, [])
    if len(user_operations) >= _max_backup_operations:
        return False

    user_operations.append(current_time)
    _backup_operation_cache[user_id] = user_operations
    return True


def check_recovery_rate_limit(user: User) -> bool:
    """检查恢复操作速率限制。"""
    current_time = time.time()
    user_id = user.id
    cutoff_time = current_time - _rate_limit_window

    if user_id in _recovery_operation_cache:
        _recovery_operation_cache[user_id] = [
            timestamp for timestamp in _recovery_operation_cache[user_id] if timestamp > cutoff_time
        ]

    user_operations = _recovery_operation_cache.get(user_id, [])
    if len(user_operations) >= _max_recovery_operations:
        return False

    user_operations.append(current_time)
    _recovery_operation_cache[user_id] = user_operations
    return True


def verify_admin_permission(user: User) -> None:
    """验证管理员权限。"""
    if require_admin_role(user.role):
        return

    log_security_event(
        "AUTHORIZATION_FAILED",
        user,
        "admin_access_denied",
        {"required_role": "admin", "user_role": user.role},
        success=False,
    )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限执行此操作")


def verify_backup_permission(user: User) -> None:
    """验证备份操作权限。"""
    if require_backup_permission(user.role):
        return

    log_security_event(
        "AUTHORIZATION_FAILED",
        user,
        "backup_access_denied",
        {"required_permission": "backup", "user_role": user.role},
        success=False,
    )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要备份操作权限")


def verify_recovery_permission(user: User) -> None:
    """验证恢复操作权限。"""
    if require_recovery_permission(user.role):
        return

    log_security_event(
        "AUTHORIZATION_FAILED",
        user,
        "recovery_access_denied",
        {"required_permission": "recovery", "user_role": user.role},
        success=False,
    )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限执行恢复操作")
