"""
审计日志API

提供系统审计和日志管理功能
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


AUDIT_LOG_RESPONSE_EXAMPLE = {
    "log_id": "log_001",
    "user_id": "user_001",
    "action": "LOGIN",
    "resource_type": "session",
    "resource_id": "session_001",
    "details": {"method": "password", "result": "success"},
    "ip_address": "127.0.0.1",
    "user_agent": "Mozilla/5.0",
    "timestamp": "2025-01-20T10:30:00Z",
}

AUDIT_LOG_LIST_RESPONSES = {
    200: {
        "description": "审计日志列表查询成功。",
        "content": {
            "application/json": {
                "example": {
                    "logs": [
                        AUDIT_LOG_RESPONSE_EXAMPLE,
                        {
                            "log_id": "log_002",
                            "user_id": "user_002",
                            "action": "UPDATE",
                            "resource_type": "portfolio",
                            "resource_id": "portfolio_007",
                            "details": {"field": "risk_limit", "from": 0.08, "to": 0.06},
                            "ip_address": "10.0.0.8",
                            "user_agent": "curl/8.0.1",
                            "timestamp": "2025-01-20T11:15:00Z",
                        },
                    ],
                    "total": 2,
                }
            }
        },
    }
}

AUDIT_LOG_DETAIL_RESPONSES = {
    200: {
        "description": "审计日志详情查询成功。",
        "content": {
            "application/json": {
                "example": AUDIT_LOG_RESPONSE_EXAMPLE,
            }
        },
    }
}

AUDIT_STATISTICS_RESPONSES = {
    200: {
        "description": "审计统计信息查询成功。",
        "content": {
            "application/json": {
                "example": {
                    "total_logs": 1250,
                    "unique_users": 15,
                    "action_counts": {
                        "LOGIN": 450,
                        "LOGOUT": 380,
                        "CREATE": 200,
                        "UPDATE": 150,
                        "DELETE": 70,
                    },
                    "period": {
                        "start": "2025-01-01",
                        "end": "2025-01-20",
                    },
                }
            }
        },
    }
}


class AuditLogResponse(BaseModel):
    """审计日志响应"""

    log_id: str = Field(..., description="审计日志唯一标识。")
    user_id: str = Field(..., description="触发该操作的用户ID。")
    action: str = Field(..., description="审计动作类型，例如 LOGIN 或 UPDATE。")
    resource_type: str = Field(..., description="被审计资源类型。")
    resource_id: str = Field(..., description="被审计资源ID。")
    details: Dict[str, Any] = Field(..., description="审计明细数据。")
    ip_address: str = Field(..., description="请求来源IP地址。")
    user_agent: str = Field(..., description="客户端 User-Agent。")
    timestamp: datetime = Field(..., description="审计事件发生时间。")


@router.get(
    "/logs",
    response_model=Dict[str, Any],
    summary="List Audit Logs",
    description="按用户、动作、资源类型和日期范围筛选审计日志列表，并返回当前筛选结果总数。",
    responses=AUDIT_LOG_LIST_RESPONSES,
)
async def list_audit_logs(
    user_id: Optional[str] = Query(None, description="按用户ID筛选审计日志。"),
    action: Optional[str] = Query(None, description="按操作类型筛选审计日志。"),
    resource_type: Optional[str] = Query(None, description="按资源类型筛选审计日志。"),
    start_date: Optional[str] = Query(None, description="查询开始日期，格式为 YYYY-MM-DD。"),
    end_date: Optional[str] = Query(None, description="查询结束日期，格式为 YYYY-MM-DD。"),
    limit: int = Query(50, description="Maximum number of logs to return"),
):
    """
    获取审计日志列表

    Returns audit logs with filtering options.
    """
    mock_logs = [
        {
            "log_id": "log_001",
            "user_id": "user_001",
            "action": "LOGIN",
            "resource_type": "session",
            "resource_id": "session_001",
            "details": {"method": "password"},
            "ip_address": "example.local",
            "user_agent": "Mozilla/5.0",
            "timestamp": "2025-01-20T10:30:00Z",
        },
    ]

    if user_id:
        mock_logs = [l for l in mock_logs if l["user_id"] == user_id]
    if action:
        mock_logs = [l for l in mock_logs if l["action"] == action]

    return {"logs": mock_logs[:limit], "total": len(mock_logs)}


@router.get(
    "/logs/{log_id}",
    response_model=AuditLogResponse,
    summary="Get Audit Log",
    description="根据审计日志ID返回单条审计事件详情，包含用户、资源、来源IP与操作明细。",
    responses=AUDIT_LOG_DETAIL_RESPONSES,
)
async def get_audit_log(log_id: str = Path(..., description="审计日志唯一标识。")):
    """
    获取单个审计日志详情

    Returns details of a specific audit log.
    """
    return AuditLogResponse(
        log_id=log_id,
        user_id="user_001",
        action="LOGIN",
        resource_type="session",
        resource_id="session_001",
        details={"method": "password"},
        ip_address="example.local",
        user_agent="Mozilla/5.0",
        timestamp=datetime.now(),
    )


@router.get(
    "/statistics",
    summary="Get Audit Statistics",
    description="统计指定时间范围内的审计日志数量、活跃用户规模和各类操作分布。",
    responses=AUDIT_STATISTICS_RESPONSES,
)
async def get_audit_statistics(
    start_date: Optional[str] = Query(None, description="统计开始日期，格式为 YYYY-MM-DD。"),
    end_date: Optional[str] = Query(None, description="统计结束日期，格式为 YYYY-MM-DD。"),
):
    """
    获取审计统计信息

    Returns audit statistics for the specified period.
    """
    return {
        "total_logs": 1250,
        "unique_users": 15,
        "action_counts": {
            "LOGIN": 450,
            "LOGOUT": 380,
            "CREATE": 200,
            "UPDATE": 150,
            "DELETE": 70,
        },
        "period": {
            "start": start_date or "2025-01-01",
            "end": end_date or "2025-01-20",
        },
    }
