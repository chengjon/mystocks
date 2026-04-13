"""
数据库优化API

提供数据库优化和维护功能
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_postgresql_session
from app.core.database_metrics import get_metrics_collector, get_performance_logger
from app.core.database_performance_monitor import get_performance_monitor
from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES

OPTIMIZATION_ROUTE_RESPONSES = {
    500: COMMON_RESPONSES[500],
}


def _success_response_spec(description: str, example: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
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


router = APIRouter(
    prefix="/optimization",
    tags=["Database Optimization"],
    responses=OPTIMIZATION_ROUTE_RESPONSES,
)


class OptimizationResponse(BaseModel):
    """优化响应"""

    operation: str = Field(..., description="执行的数据库优化操作名称。")
    status: str = Field(..., description="优化操作执行状态。")
    duration_ms: int = Field(..., description="本次操作耗时，单位毫秒。")
    result: Dict[str, Any] = Field(..., description="优化执行结果详情。")


VACUUM_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Database vacuum completed",
    "data": {
        "operation": "vacuum",
        "status": "completed",
        "duration_ms": 145,
        "result": {
            "task_id": "opt_demo_vacuum",
            "executed_sql": "VACUUM",
            "started_at": "2026-04-13T08:00:00+00:00",
            "finished_at": "2026-04-13T08:00:00+00:00",
        },
    },
}

ANALYZE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Database analyze completed",
    "data": {
        "operation": "analyze",
        "status": "completed",
        "duration_ms": 122,
        "result": {
            "task_id": "opt_demo_analyze",
            "executed_sql": "ANALYZE",
            "started_at": "2026-04-13T08:00:00+00:00",
            "finished_at": "2026-04-13T08:00:00+00:00",
        },
    },
}

REINDEX_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Database reindex completed",
    "data": {
        "operation": "reindex",
        "status": "completed",
        "duration_ms": 210,
        "result": {
            "task_id": "opt_demo_reindex",
            "executed_sql": "REINDEX DATABASE current_database()",
            "started_at": "2026-04-13T08:00:00+00:00",
            "finished_at": "2026-04-13T08:00:00+00:00",
        },
    },
}

DATABASE_STATUS_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Database optimization status retrieved",
    "data": {
        "database": "mystocks",
        "pool": {"size": 20, "in_use": 0, "idle": 20, "status": "Pool size: 20  Connections in pool: 20"},
        "performance_monitor": {"total_queries": 0, "total_slow_queries": 0},
        "recent_operations": [],
        "updated_at": "2026-04-13T08:00:00+00:00",
    },
}

SLOW_QUERIES_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Slow queries retrieved",
    "data": {
        "limit": 10,
        "queries": [
            {
                "query": "SELECT * FROM daily_kline WHERE symbol = ?",
                "duration": 0.21,
                "type": "select",
                "timestamp": "2026-04-13T08:00:00+00:00",
                "params": None,
            }
        ],
        "summary": {"logged": 1, "aggregated": 0},
    },
}

VACUUM_RESPONSES = _success_response_spec("Vacuum 操作结果。", VACUUM_SUCCESS_EXAMPLE)
ANALYZE_RESPONSES = _success_response_spec("Analyze 操作结果。", ANALYZE_SUCCESS_EXAMPLE)
REINDEX_RESPONSES = _success_response_spec("Reindex 操作结果。", REINDEX_SUCCESS_EXAMPLE)
DATABASE_STATUS_RESPONSES = _success_response_spec("数据库优化状态结果。", DATABASE_STATUS_SUCCESS_EXAMPLE)
SLOW_QUERIES_RESPONSES = _success_response_spec("慢查询检查结果。", SLOW_QUERIES_SUCCESS_EXAMPLE)

_OPERATION_SQL = {
    "vacuum": "VACUUM",
    "analyze": "ANALYZE",
    "reindex": "REINDEX DATABASE current_database()",
}
_OPERATION_HISTORY: list[dict[str, Any]] = []


def _record_operation(entry: dict[str, Any]) -> None:
    _OPERATION_HISTORY.append(entry)
    del _OPERATION_HISTORY[:-20]


async def _run_maintenance(operation: str) -> OptimizationResponse:
    sql = _OPERATION_SQL[operation]
    task_id = f"opt_{uuid4().hex[:12]}"
    started_at = datetime.now(timezone.utc)
    start = time.perf_counter()
    session = None
    status = "completed"
    error = None
    try:
        session = get_postgresql_session()
        connection = session.connection().execution_options(isolation_level="AUTOCOMMIT")
        connection.execute(text(sql))
    except Exception as exc:
        status = "failed"
        error = str(exc)
    finally:
        if session is not None:
            session.close()
    duration_ms = int((time.perf_counter() - start) * 1000)
    finished_at = datetime.now(timezone.utc)
    entry = {
        "task_id": task_id,
        "operation": operation,
        "status": status,
        "executed_sql": sql,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "error": error,
    }
    _record_operation(entry)
    return OptimizationResponse(operation=operation, status=status, duration_ms=duration_ms, result=entry)


def _database_status_payload() -> dict[str, Any]:
    collector = get_metrics_collector("mystocks")
    monitor = get_performance_monitor()
    session = None
    try:
        session = get_postgresql_session()
        pool = session.get_bind().pool
        pool_status = pool.status()
        pool_metrics = collector.get_pool_metrics()
        monitor_stats = monitor.get_monitoring_stats()
        return {
            "database": "mystocks",
            "pool": {
                "size": pool_metrics.pool_size,
                "in_use": pool_metrics.connections_in_use,
                "idle": pool_metrics.connections_idle,
                "status": pool_status,
            },
            "performance_monitor": monitor_stats,
            "recent_operations": list(reversed(_OPERATION_HISTORY[-5:])),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        if session is not None:
            session.close()


def _slow_queries_payload(limit: int) -> dict[str, Any]:
    logger = get_performance_logger("mystocks")
    collector = get_metrics_collector("mystocks")
    logged_queries = logger.get_slow_queries(limit)
    aggregated_queries = collector.get_slow_queries(limit)
    return {
        "limit": limit,
        "queries": logged_queries,
        "aggregated": aggregated_queries,
        "summary": {"logged": len(logged_queries), "aggregated": len(aggregated_queries)},
    }


def _resolve_query_value(value: Any) -> Any:
    return getattr(value, "default", value)


@router.post(
    "/vacuum",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Vacuum Database",
    description="执行数据库 Vacuum 操作，当前实现会尝试对 PostgreSQL 连接执行真实维护命令并记录任务结果。",
    responses=VACUUM_RESPONSES,
)
async def vacuum_database():
    response = await _run_maintenance("vacuum")
    return UnifiedResponse(
        success=response.status == "completed",
        code=200 if response.status == "completed" else 503,
        message="Database vacuum completed" if response.status == "completed" else "Database vacuum failed",
        data=response.model_dump(),
    )


@router.post(
    "/analyze",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Analyze Database",
    description="执行数据库 Analyze 操作，当前实现会尝试刷新 PostgreSQL 统计信息并记录执行状态。",
    responses=ANALYZE_RESPONSES,
)
async def analyze_database():
    response = await _run_maintenance("analyze")
    return UnifiedResponse(
        success=response.status == "completed",
        code=200 if response.status == "completed" else 503,
        message="Database analyze completed" if response.status == "completed" else "Database analyze failed",
        data=response.model_dump(),
    )


@router.post(
    "/reindex",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Reindex Database",
    description="执行数据库 Reindex 操作，当前实现会尝试对 PostgreSQL 执行真实索引重建命令并记录结果。",
    responses=REINDEX_RESPONSES,
)
async def reindex_database():
    response = await _run_maintenance("reindex")
    return UnifiedResponse(
        success=response.status == "completed",
        code=200 if response.status == "completed" else 503,
        message="Database reindex completed" if response.status == "completed" else "Database reindex failed",
        data=response.model_dump(),
    )


@router.get(
    "/status",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Database Status",
    description="获取数据库优化状态，当前实现返回连接池状态、性能监控摘要和最近维护任务。",
    responses=DATABASE_STATUS_RESPONSES,
)
async def get_database_status():
    return UnifiedResponse(
        success=True,
        code=200,
        message="Database optimization status retrieved",
        data=_database_status_payload(),
    )


@router.get(
    "/slow-queries",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Slow Queries",
    description="返回数据库慢查询概览，当前实现聚合 QueryPerformanceLogger 与指标收集器中的慢查询数据。",
    responses=SLOW_QUERIES_RESPONSES,
)
async def get_slow_queries(limit: int = Query(10, ge=1, le=100, description="返回的慢查询条数上限。")):
    resolved_limit = _resolve_query_value(limit)
    return UnifiedResponse(
        success=True,
        code=200,
        message="Slow queries retrieved",
        data=_slow_queries_payload(resolved_limit),
    )
