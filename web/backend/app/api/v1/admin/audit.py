"""
审计日志API

提供系统审计和日志管理功能
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy import func

from app.core.database_factory import get_postgresql_session
from app.core.responses import UnifiedResponse
from app.models.rbac import AuditLog

from .runtime_state import runtime_store

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)

AuditSessionFactory = Callable[[], Any]


AUDIT_LOG_LIST_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Audit logs retrieved",
    "data": {
        "logs": [
            {
                "log_id": "audit_seed_001",
                "user_id": "admin",
                "action": "LOGIN",
                "resource_type": "auth",
                "resource_id": "session_admin",
                "details": {"status": "success"},
                "ip_address": "127.0.0.1",
                "user_agent": "seed/runtime",
                "timestamp": "2026-04-13T08:00:00+00:00",
            }
        ],
        "total": 1,
        "source": "runtime",
    },
}

AUDIT_LOG_DETAIL_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Audit log detail retrieved",
    "data": {
        "log_id": "audit_seed_001",
        "user_id": "admin",
        "action": "LOGIN",
        "resource_type": "auth",
        "resource_id": "session_admin",
        "details": {"status": "success"},
        "ip_address": "127.0.0.1",
        "user_agent": "seed/runtime",
        "timestamp": "2026-04-13T08:00:00+00:00",
    },
}

AUDIT_STATISTICS_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Audit statistics retrieved",
    "data": {
        "period": {
            "start": "2025-01-01",
            "end": "2025-01-20",
        },
        "total_logs": 2,
        "actions": {"LOGIN": 1, "UPDATE": 1},
        "resource_types": {"auth": 1, "configuration": 1},
        "source": "runtime",
    },
}

AUDIT_LOG_LIST_RESPONSES = {
    200: {
        "description": "审计日志列表结果。",
        "content": {
            "application/json": {
                "example": AUDIT_LOG_LIST_SUCCESS_EXAMPLE,
            }
        },
    },
    500: {
        "description": "审计日志服务不可用。",
        "content": {
            "application/json": {
                "example": {
                    "detail": "audit log query failed",
                }
            }
        },
    },
}

AUDIT_LOG_DETAIL_RESPONSES = {
    200: {
        "description": "审计日志详情结果。",
        "content": {
            "application/json": {
                "example": AUDIT_LOG_DETAIL_SUCCESS_EXAMPLE,
            }
        },
    },
    500: {
        "description": "审计日志详情服务不可用。",
        "content": {
            "application/json": {
                "example": {
                    "detail": "audit log detail lookup failed",
                }
            }
        },
    },
}

AUDIT_STATISTICS_RESPONSES = {
    200: {
        "description": "审计统计结果。",
        "content": {
            "application/json": {
                "example": AUDIT_STATISTICS_SUCCESS_EXAMPLE,
            }
        },
    },
    500: {
        "description": "审计统计服务不可用。",
        "content": {
            "application/json": {
                "example": {
                    "detail": "audit statistics query failed",
                }
            }
        },
    },
}


class AuditLogResponse(BaseModel):
    """审计日志响应"""

    log_id: str = Field(..., description="触发该审计事件的唯一ID。")
    user_id: Optional[str] = Field(None, description="触发该操作的用户ID。")
    action: str = Field(..., description="审计动作类型，例如 LOGIN 或 UPDATE。")
    resource_type: str = Field(..., description="被审计资源类型。")
    resource_id: str = Field(..., description="被审计资源ID。")
    details: Dict[str, Any] = Field(..., description="审计明细数据。")
    ip_address: str = Field(..., description="请求来源IP地址。")
    user_agent: str = Field(..., description="客户端 User-Agent。")
    timestamp: datetime = Field(..., description="审计事件发生时间。")


def _resolve_query_value(value: Any) -> Any:
    return getattr(value, "default", value)


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _serialize_row(row: AuditLog) -> Dict[str, Any]:
    details: Dict[str, Any] = {}
    if row.additional_data:
        try:
            details = json.loads(row.additional_data)
        except json.JSONDecodeError:
            details = {"raw": row.additional_data}
    return AuditLogResponse(
        log_id=str(row.id),
        user_id=str(row.user_id) if row.user_id else None,
        action=row.action,
        resource_type=row.resource_type,
        resource_id=row.resource_id or "",
        details=details,
        ip_address=row.ip_address,
        user_agent=row.user_agent or "",
        timestamp=row.created_at,
    ).model_dump()


def _runtime_logs() -> list[Dict[str, Any]]:
    runtime_store.seed()
    return [
        AuditLogResponse(
            log_id=item.log_id,
            user_id=item.user_id,
            action=item.action,
            resource_type=item.resource_type,
            resource_id=item.resource_id,
            details=item.details,
            ip_address=item.ip_address,
            user_agent=item.user_agent,
            timestamp=item.timestamp,
        ).model_dump()
        for item in sorted(runtime_store.audit_logs, key=lambda entry: entry.timestamp, reverse=True)
    ]


def get_admin_audit_postgresql_session_factory() -> AuditSessionFactory:
    return get_postgresql_session


def _load_audit_logs(
    *,
    user_id: Optional[str],
    action: Optional[str],
    resource_type: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    limit: int,
    session_factory: AuditSessionFactory = get_postgresql_session,
) -> tuple[list[Dict[str, Any]], str]:
    runtime_store.seed()
    try:
        session = session_factory()
        try:
            query = session.query(AuditLog)
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if action:
                query = query.filter(AuditLog.action == action)
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            if start_date:
                query = query.filter(AuditLog.created_at >= _parse_date(start_date))
            if end_date:
                query = query.filter(AuditLog.created_at <= _parse_date(end_date))
            rows = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
            if rows:
                return [_serialize_row(row) for row in rows], "database"
        finally:
            session.close()
    except Exception:
        pass

    items = _runtime_logs()
    if user_id:
        items = [item for item in items if item["user_id"] == user_id]
    if action:
        items = [item for item in items if item["action"] == action]
    if resource_type:
        items = [item for item in items if item["resource_type"] == resource_type]
    if start_date:
        start_dt = _parse_date(start_date)
        items = [item for item in items if item["timestamp"] >= start_dt]
    if end_date:
        end_dt = _parse_date(end_date)
        items = [item for item in items if item["timestamp"] <= end_dt]
    return items[:limit], "runtime"


@router.get(
    "/logs",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="List Audit Logs",
    description="按用户、动作、资源类型和日期范围筛选审计日志列表；当前实现优先查询真实 `audit_logs` 表，数据库不可用时降级到运行时审计记录。",
    responses=AUDIT_LOG_LIST_RESPONSES,
)
async def list_audit_logs(
    user_id: Optional[str] = Query(None, description="按用户ID筛选审计日志。"),
    action: Optional[str] = Query(None, description="按操作类型筛选审计日志。"),
    resource_type: Optional[str] = Query(None, description="按资源类型筛选审计日志。"),
    start_date: Optional[str] = Query(None, description="查询开始日期，格式为 YYYY-MM-DD。"),
    end_date: Optional[str] = Query(None, description="查询结束日期，格式为 YYYY-MM-DD。"),
    limit: int = Query(50, description="Maximum number of logs to return"),
    session_factory: AuditSessionFactory = Depends(get_admin_audit_postgresql_session_factory),
):
    """
    获取审计日志列表。
    """
    logs, source = _load_audit_logs(
        user_id=_resolve_query_value(user_id),
        action=_resolve_query_value(action),
        resource_type=_resolve_query_value(resource_type),
        start_date=_resolve_query_value(start_date),
        end_date=_resolve_query_value(end_date),
        limit=int(_resolve_query_value(limit)),
        session_factory=session_factory,
    )
    runtime_store.add_log(
        user_id="system",
        action="READ",
        resource_type="audit",
        resource_id="logs",
        details={"limit": len(logs), "source": source},
    )
    return UnifiedResponse(
        success=True,
        code=200,
        message="Audit logs retrieved",
        data={"logs": logs, "total": len(logs), "source": source},
    )


@router.get(
    "/logs/{log_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Audit Log",
    description="根据审计日志ID返回单条审计事件详情；当前实现优先从真实 `audit_logs` 表查询，查不到时回退到运行时记录。",
    responses=AUDIT_LOG_DETAIL_RESPONSES,
)
async def get_audit_log(
    log_id: str = Path(..., description="审计日志唯一标识。"),
    session_factory: AuditSessionFactory = Depends(get_admin_audit_postgresql_session_factory),
):
    """
    获取单个审计日志详情。
    """
    logs, source = _load_audit_logs(
        user_id=None,
        action=None,
        resource_type=None,
        start_date=None,
        end_date=None,
        limit=200,
        session_factory=session_factory,
    )
    entry = next((item for item in logs if item["log_id"] == log_id), None)
    if entry is None:
        runtime_store.seed()
        entry = next((item for item in _runtime_logs() if item["log_id"] == log_id), None)
        source = "runtime"
    if entry is None:
        entry = AuditLogResponse(
            log_id=log_id,
            user_id=None,
            action="UNKNOWN",
            resource_type="unknown",
            resource_id=log_id,
            details={"status": "not_found"},
            ip_address="127.0.0.1",
            user_agent="mystocks-v1-runtime",
            timestamp=datetime.now(timezone.utc),
        ).model_dump()
        source = "runtime"
    return UnifiedResponse(
        success=True,
        code=200,
        message="Audit log detail retrieved",
        data={**entry, "source": source},
    )


@router.get(
    "/statistics",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Audit Statistics",
    description="统计指定时间范围内的审计日志数量与操作分布；当前实现优先使用真实审计表聚合，数据库不可用时降级到运行时记录。",
    responses=AUDIT_STATISTICS_RESPONSES,
)
async def get_audit_statistics(
    start_date: Optional[str] = Query(None, description="统计开始日期，格式为 YYYY-MM-DD。"),
    end_date: Optional[str] = Query(None, description="统计结束日期，格式为 YYYY-MM-DD。"),
    session_factory: AuditSessionFactory = Depends(get_admin_audit_postgresql_session_factory),
):
    """
    获取审计统计信息。
    """
    resolved_start = _resolve_query_value(start_date)
    resolved_end = _resolve_query_value(end_date)
    try:
        session = session_factory()
        try:
            query = session.query(
                AuditLog.action,
                AuditLog.resource_type,
                func.count(AuditLog.id).label("count"),
            )
            if resolved_start:
                query = query.filter(AuditLog.created_at >= _parse_date(resolved_start))
            if resolved_end:
                query = query.filter(AuditLog.created_at <= _parse_date(resolved_end))
            rows = query.group_by(AuditLog.action, AuditLog.resource_type).all()
            if rows:
                actions: Dict[str, int] = {}
                resource_types: Dict[str, int] = {}
                total_logs = 0
                for action_name, resource_name, count in rows:
                    actions[action_name] = actions.get(action_name, 0) + int(count)
                    resource_types[resource_name] = resource_types.get(resource_name, 0) + int(count)
                    total_logs += int(count)
                source = "database"
            else:
                raise RuntimeError("empty audit table")
        finally:
            session.close()
    except Exception:
        logs, source = _load_audit_logs(
            user_id=None,
            action=None,
            resource_type=None,
            start_date=resolved_start,
            end_date=resolved_end,
            limit=500,
            session_factory=session_factory,
        )
        actions = {}
        resource_types = {}
        for item in logs:
            actions[item["action"]] = actions.get(item["action"], 0) + 1
            resource_types[item["resource_type"]] = resource_types.get(item["resource_type"], 0) + 1
        total_logs = len(logs)

    return UnifiedResponse(
        success=True,
        code=200,
        message="Audit statistics retrieved",
        data={
            "period": {"start": resolved_start, "end": resolved_end},
            "total_logs": total_logs,
            "actions": actions,
            "resource_types": resource_types,
            "source": source,
        },
    )
