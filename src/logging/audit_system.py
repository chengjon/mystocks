"""
统一日志和审计管理系统
Unified Logging and Audit Management System

提供结构化日志记录、审计追踪、日志轮转、安全事件监控等功能。
Provides structured logging, audit trails, log rotation, security event monitoring, etc.
"""

from src.core.database import DatabaseConnectionManager
import json
import logging
import logging.handlers
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import structlog
import asyncio
from contextvars import ContextVar

# Setup project path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar("session_id", default=None)


@dataclass
class LogConfig:
    """日志配置"""

    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_structured: bool = True


@dataclass
class AuditEvent:
    """审计事件"""

    event_type: str
    user_id: Optional[str] = None
    action: str = ""
    resource_type: str = ""
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = "success"
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


def to_dict(self) -> Dict[str, Any]:
    """转换为字典"""
    return {
        "event_type": self.event_type,
        "user_id": self.user_id,
        "action": self.action,
        "resource_type": self.resource_type,
        "resource_id": self.resource_id,
        "ip_address": self.ip_address,
        "user_agent": self.user_agent,
        "status": self.status,
        "details": self.details,
        "timestamp": self.timestamp.isoformat(),
    }


class StructuredLogger:
    """结构化日志记录器"""


def __init__(self, config: LogConfig):
    self.config = config
    self.logger = self._setup_logger()


def _setup_logger(self) -> logging.Logger:
    """设置结构化日志记录器"""
    logger = logging.getLogger("mystocks")
    logger.setLevel(getattr(logging, self.config.log_level))

    # 清除现有处理器
    logger.handlers.clear()

    # 创建格式化器
    if self.config.enable_structured:
        # 使用structlog进行结构化日志
        formatter = structlog.WriteASJSON()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # 控制台处理器
    if self.config.enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件处理器
    if self.config.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            self.config.log_file,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_request(
    self,
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: Optional[str] = None,
):
    """记录HTTP请求"""
    request_id = request_id_var.get()
    session_id = session_id_var.get()

    self.logger.info(
        "HTTP Request",
        method=method,
        path=path,
        status_code=status_code,
        duration=duration,
        user_id=user_id or user_id_var.get(),
        request_id=request_id,
        session_id=session_id,
        extra={
            "http": {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration,
            },
            "user": {"id": user_id},
            "request": {"id": request_id},
            "session": {"id": session_id},
        },
    )


def log_database_operation(
    self,
    operation: str,
    table: str,
    record_count: int,
    duration: float,
    user_id: Optional[str] = None,
):
    """记录数据库操作"""
    request_id = request_id_var.get()

    self.logger.info(
        "Database Operation",
        operation=operation,
        table=table,
        record_count=record_count,
        duration=duration,
        user_id=user_id or user_id_var.get(),
        request_id=request_id,
        extra={
            "database": {
                "operation": operation,
                "table": table,
                "record_count": record_count,
                "duration_ms": duration,
            },
            "user": {"id": user_id},
            "request": {"id": request_id},
        },
    )


def log_security_event(
    self,
    event_type: str,
    severity: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None,
):
    """记录安全事件"""
    request_id = request_id_var.get()
    ip_address = details.get("ip_address")

    self.logger.warning(
        "Security Event",
        event_type=event_type,
        severity=severity,
        user_id=user_id or user_id_var.get(),
        ip_address=ip_address,
        request_id=request_id,
        extra={
            "security": {"event_type": event_type, "severity": severity, **details},
            "user": {"id": user_id},
            "request": {"id": request_id},
        },
    )


def log_business_event(
    self, event_type: str, details: Dict[str, Any], user_id: Optional[str] = None
):
    """记录业务事件"""
    request_id = request_id_var.get()

    self.logger.info(
        "Business Event",
        event_type=event_type,
        user_id=user_id or user_id_var.get(),
        request_id=request_id,
        extra={
            "business": {"event_type": event_type, **details},
            "user": {"id": user_id},
            "request": {"id": request_id},
        },
    )


class AuditManager:
    """审计管理器"""

    def __init__(self, db_manager: DatabaseConnectionManager):
        self.db_manager = db_manager
        self.audit_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        self.worker_task: Optional[asyncio.Task] = None


async def start_audit_worker(self):
    """启动审计工作进程"""
    if self.is_running:
        return

    self.is_running = True
    self.worker_task = asyncio.create_task(self._audit_worker())
    logger.info("Audit worker started")


async def stop_audit_worker(self):
    """停止审计工作进程"""
    if not self.is_running:
        return

    self.is_running = False
    if self.worker_task:
        self.worker_task.cancel()
        try:
            await self.worker_task
        except asyncio.CancelledError:
            pass
    logger.info("Audit worker stopped")


async def log_audit_event(self, event: AuditEvent):
    """记录审计事件"""
    await self.audit_queue.put(event)


async def _audit_worker(self):
    """审计工作进程"""
    try:
        while self.is_running:
            try:
                # 批量处理审计事件
                events = []
                try:
                    # 尝试获取多个事件进行批量处理
                    while len(events) < 10:  # 最多批量处理10个事件
                        event = await asyncio.wait_for(
                            self.audit_queue.get(), timeout=1.0
                        )
                        events.append(event)
                except asyncio.TimeoutError:
                    pass

                if events:
                    await self._batch_insert_audit_events(events)

            except Exception as e:
                logger.error(f"Audit worker error: {e}")

    except asyncio.CancelledError:
        logger.info("Audit worker cancelled")


async def _batch_insert_audit_events(self, events: List[AuditEvent]):
    """批量插入审计事件"""
    try:
        async with self.db_manager.get_connection() as conn:
            # 构建批量插入SQL
            values = []
            for event in events:
                values.append(
                    (
                        event.user_id,
                        event.action,
                        event.resource_type,
                        event.resource_id,
                        event.ip_address,
                        event.user_agent,
                        "POST"
                        if event.details.get("method") == "POST"
                        else "GET",  # 简化
                        event.details.get("path", ""),
                        event.status,
                        None,  # error_message
                        json.dumps(event.details) if event.details else None,
                    )
                )

            # 批量插入
            await conn.executemany(
                """
                    INSERT INTO audit_logs (
                        user_id, action, resource_type, resource_id,
                        ip_address, user_agent, request_method, request_path,
                        status, error_message, additional_data, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                """,
                values,
            )

            logger.debug(f"Batch inserted {len(events)} audit events")

    except Exception as e:
        logger.error(f"Failed to batch insert audit events: {e}")


async def get_audit_logs(
    self,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """查询审计日志"""
    try:
        query = """
                SELECT
                    id, user_id, action, resource_type, resource_id,
                    ip_address, user_agent, request_method, request_path,
                    status, error_message, additional_data, created_at
                FROM audit_logs
                WHERE 1=1
            """
        params = []

        if user_id:
            query += " AND user_id = $1"
            params.append(user_id)

        if action:
            query += f" AND action = ${len(params) + 1}"
            params.append(action)

        if resource_type:
            query += f" AND resource_type = ${len(params) + 1}"
            params.append(resource_type)

        if start_date:
            query += f" AND created_at >= ${len(params) + 1}"
            params.append(start_date)

        if end_date:
            query += f" AND created_at <= ${len(params) + 1}"
            params.append(end_date)

        query += f" ORDER BY created_at DESC LIMIT {limit}"

        async with self.db_manager.get_connection() as conn:
            rows = await conn.fetch(query, *params)

            return [
                {
                    "id": str(row["id"]),
                    "user_id": str(row["user_id"]) if row["user_id"] else None,
                    "action": row["action"],
                    "resource_type": row["resource_type"],
                    "resource_id": row["resource_id"],
                    "ip_address": row["ip_address"],
                    "user_agent": row["user_agent"],
                    "request_method": row["request_method"],
                    "request_path": row["request_path"],
                    "status": row["status"],
                    "error_message": row["error_message"],
                    "additional_data": json.loads(row["additional_data"])
                    if row["additional_data"]
                    else None,
                    "created_at": row["created_at"].isoformat()
                    if row["created_at"]
                    else None,
                }
                for row in rows
            ]

    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        return []


async def cleanup_old_audit_logs(self, days_to_keep: int = 90):
    """清理旧的审计日志"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        async with self.db_manager.get_connection() as conn:
            deleted_count = await conn.execute(
                "DELETE FROM audit_logs WHERE created_at < $1", cutoff_date
            )

            logger.info(
                f"Cleaned up {deleted_count} old audit log entries older than {
                    days_to_keep
                } days"
            )
            return int(deleted_count)

    except Exception as e:
        logger.error(f"Failed to cleanup audit logs: {e}")
        return 0


class SecurityMonitor:
    """安全监控器"""


def __init__(self, audit_manager: AuditManager):
    self.audit_manager = audit_manager
    self.failed_login_attempts: Dict[str, List[datetime]] = {}
    self.suspicious_activities: List[Dict[str, Any]] = []


def record_failed_login(self, ip_address: str, username: str):
    """记录失败的登录尝试"""
    if ip_address not in self.failed_login_attempts:
        self.failed_login_attempts[ip_address] = []

    self.failed_login_attempts[ip_address].append(datetime.now())

    # 清理旧的记录（1小时前）
    cutoff = datetime.now() - timedelta(hours=1)
    self.failed_login_attempts[ip_address] = [
        attempt
        for attempt in self.failed_login_attempts[ip_address]
        if attempt > cutoff
    ]

    # 检查是否达到阈值（5次失败）
    if len(self.failed_login_attempts[ip_address]) >= 5:
        self._detect_brute_force_attack(ip_address, username)


def _detect_brute_force_attack(self, ip_address: str, username: str):
    """检测暴力破解攻击"""
    self.suspicious_activities.append(
        {
            "type": "brute_force_attack",
            "ip_address": ip_address,
            "username": username,
            "timestamp": datetime.now(),
            "details": {
                "failed_attempts": len(self.failed_login_attempts[ip_address]),
                "time_window": "1_hour",
            },
        }
    )

    logger.warning(
        f"Brute force attack detected from IP {ip_address} targeting user {username}"
    )


def record_suspicious_activity(
    self,
    activity_type: str,
    details: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_id: Optional[str] = None,
):
    """记录可疑活动"""
    self.suspicious_activities.append(
        {
            "type": activity_type,
            "ip_address": ip_address,
            "user_id": user_id,
            "timestamp": datetime.now(),
            "details": details,
        }
    )

    logger.warning(
        f"Suspicious activity detected: {activity_type} from IP {ip_address}"
    )


def get_security_report(self) -> Dict[str, Any]:
    """获取安全报告"""
    # 清理过期记录
    cutoff = datetime.now() - timedelta(hours=24)
    self.suspicious_activities = [
        activity
        for activity in self.suspicious_activities
        if activity["timestamp"] > cutoff
    ]

    return {
        "failed_login_attempts": {
            ip: len(attempts) for ip, attempts in self.failed_login_attempts.items()
        },
        "suspicious_activities": self.suspicious_activities,
        "total_suspicious_events": len(self.suspicious_activities),
        "report_generated_at": datetime.now().isoformat(),
    }


# 全局日志记录器实例
_logger_instance: Optional[StructuredLogger] = None
_audit_manager_instance: Optional[AuditManager] = None
_security_monitor_instance: Optional[SecurityMonitor] = None


def get_structured_logger(config: Optional[LogConfig] = None) -> StructuredLogger:
    """获取结构化日志记录器实例（单例模式）"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = StructuredLogger(config or LogConfig())
    return _logger_instance


def get_audit_manager(
    db_manager: Optional[DatabaseConnectionManager] = None,
) -> AuditManager:
    """获取审计管理器实例（单例模式）"""
    global _audit_manager_instance
    if _audit_manager_instance is None:
        if db_manager is None:
            # TODO: Pass proper database manager instance
            db_manager = None
        _audit_manager_instance = AuditManager(db_manager)
    return _audit_manager_instance


def get_security_monitor(
    audit_manager: Optional[AuditManager] = None,
) -> SecurityMonitor:
    """获取安全监控器实例（单例模式）"""
    global _security_monitor_instance
    if _security_monitor_instance is None:
        if audit_manager is None:
            audit_manager = get_audit_manager()
        _security_monitor_instance = SecurityMonitor(audit_manager)
    return _security_monitor_instance


# 初始化日志记录器
logger = logging.getLogger(__name__)


# 便捷函数
async def log_audit_event(event: AuditEvent):
    """便捷函数：记录审计事件"""
    audit_manager = get_audit_manager()
    await audit_manager.log_audit_event(event)


def log_security_event(
    event_type: str,
    severity: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None,
):
    """便捷函数：记录安全事件"""
    logger = get_structured_logger()
    logger.log_security_event(event_type, severity, details, user_id)


def log_business_event(
    event_type: str, details: Dict[str, Any], user_id: Optional[str] = None
):
    """便捷函数：记录业务事件"""
    logger = get_structured_logger()
    logger.log_business_event(event_type, details, user_id)
