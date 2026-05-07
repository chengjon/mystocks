"""
系统资源使用API

提供单节点 host / process / dependency 资源快照与短窗口趋势。
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Query

from app.core.responses import UnifiedResponse
from app.services.system_resource_metrics import collect_resource_metrics

router = APIRouter(
    prefix="/system",
    tags=["System Resources"],
)


RESOURCE_USAGE_ERROR_RESPONSE = {
    500: {
        "description": "System resource metrics are temporarily unavailable.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "system resource metrics unavailable",
                }
            }
        },
    }
}

RESOURCE_USAGE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "System resource metrics retrieved",
    "data": {
        "node": {
            "node_id": "mystocks-local",
            "scope": "single-node",
            "sampled_at": "2026-05-07T00:00:00+00:00",
            "window_minutes": 60,
            "polling_interval_seconds": 15,
            "overall_status": "normal",
        },
        "host": {
            "cpu": {
                "metric_key": "cpu_percent",
                "label": "CPU",
                "unit": "%",
                "current_value": 35.0,
                "status": "normal",
                "warning_threshold": 70.0,
                "critical_threshold": 90.0,
                "series": [{"timestamp": "2026-05-07T00:00:00+00:00", "value": 35.0}],
                "meta": {"cpu_count": 8},
            }
        },
        "processes": [],
        "dependencies": [],
        "thresholds": {
            "host.cpu_percent": {
                "warning": 70.0,
                "critical": 90.0,
                "unit": "%",
            }
        },
    },
}


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
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


RESOURCE_USAGE_RESPONSES = {
    **RESOURCE_USAGE_ERROR_RESPONSE,
    **_success_response_spec(
        "Runtime-backed single-node resource metrics, including host snapshots, process metrics, dependency summaries, and short-window trend series.",
        RESOURCE_USAGE_SUCCESS_EXAMPLE,
    ),
}


@router.get(
    "/resources",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="System Resource Usage Snapshot",
    description="返回当前运行节点的 host / process / dependency 资源快照、后端阈值状态，以及最近短窗口趋势序列，供独立的资源使用工作台轮询展示。",
    responses=RESOURCE_USAGE_RESPONSES,
)
async def get_system_resource_metrics(
    window_minutes: int = Query(60, ge=5, le=60, description="短窗口趋势长度，单位分钟"),
    include_processes: bool = Query(True, description="是否返回 mystocks-backend / mystocks-frontend 进程资源快照"),
    include_dependencies: bool = Query(True, description="是否返回 PostgreSQL / TDengine / Redis 依赖摘要"),
):
    payload = await collect_resource_metrics(
        window_minutes=window_minutes,
        include_processes=include_processes,
        include_dependencies=include_dependencies,
    )
    return UnifiedResponse(
        success=True,
        code=200,
        message="System resource metrics retrieved",
        data=payload,
    )
