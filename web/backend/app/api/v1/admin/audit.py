"""
审计日志API

提供系统审计和日志管理功能
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


class AuditLogResponse(BaseModel):
    """审计日志响应"""

    log_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime


@router.get("/logs", response_model=Dict[str, Any], summary="List Audit Logs")
async def list_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
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
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "timestamp": "2025-01-20T10:30:00Z",
        },
    ]

    if user_id:
        mock_logs = [l for l in mock_logs if l["user_id"] == user_id]
    if action:
        mock_logs = [l for l in mock_logs if l["action"] == action]

    return {"logs": mock_logs[:limit], "total": len(mock_logs)}


@router.get("/logs/{log_id}", response_model=AuditLogResponse, summary="Get Audit Log")
async def get_audit_log(log_id: str):
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
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        timestamp=datetime.now(),
    )


@router.get("/statistics", summary="Get Audit Statistics")
async def get_audit_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
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
