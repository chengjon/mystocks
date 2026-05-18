"""System health route response examples and OpenAPI response specs."""

from typing import Any, Dict

SYSTEM_MANAGEMENT_ERROR_RESPONSE = {
    500: {
        "description": "System management request failed because a backend dependency, adapter probe, or log source is unavailable.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "获取日志统计失败: monitoring database unavailable",
                }
            }
        },
    }
}

CONNECTION_TEST_REQUEST_EXAMPLES = {
    "postgres_connection_probe": {
        "summary": "Probe a PostgreSQL instance",
        "value": {
            "db_type": "postgresql",
            "host": "127.0.0.1",
            "port": 5432,
        },
    }
}


def _success_response_spec(description: str, example: Any) -> Dict[int, Dict[str, Any]]:
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


SYSTEM_HEALTH_RESPONSES = {
    **SYSTEM_MANAGEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "系统健康检查结果",
        {
            "status": "healthy",
            "timestamp": "2026-04-07T08:00:00",
            "databases": {
                "postgresql": "healthy",
                "tdengine": "healthy",
            },
            "service": "mystocks-web-api",
            "version": "2.2.0",
            "architecture": "dual-database",
        },
    ),
}

SYSTEM_ADAPTER_HEALTH_RESPONSES = {
    **SYSTEM_MANAGEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "数据适配器健康检查结果",
        {
            "overall_status": "healthy",
            "healthy_count": 3,
            "total_count": 3,
            "adapters": {
                "akshare": {
                    "healthy": True,
                    "status": "healthy",
                    "error": None,
                    "last_check": "2026-04-07T08:00:00",
                },
                "tdx": {
                    "healthy": True,
                    "status": "healthy",
                    "error": None,
                    "last_check": "2026-04-07T08:00:00",
                },
            },
            "timestamp": "2026-04-07T08:00:00",
            "message": "3/3 适配器正常运行",
        },
    ),
}

SYSTEM_DATASOURCES_RESPONSES = {
    **SYSTEM_MANAGEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "系统已配置数据源列表",
        {
            "success": True,
            "data": [
                {
                    "id": "tdx",
                    "name": "通达信(TDX)",
                    "type": "realtime",
                    "status": "active",
                    "description": "实时行情和多周期K线数据",
                    "features": ["实时行情", "分钟K线", "日K线"],
                }
            ],
            "total": 1,
            "timestamp": "2026-04-07T08:00:00",
        },
    ),
}

SYSTEM_CONNECTION_TEST_RESPONSES = {
    **SYSTEM_MANAGEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "数据库连接测试结果",
        {
            "success": True,
            "message": "PostgreSQL 连接成功 (PostgreSQL 15.5)，发现数据库: mystocks",
            "error": None,
        },
    ),
}

SYSTEM_LOGS_RESPONSES = {
    **SYSTEM_MANAGEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "系统运行日志列表",
        {
            "success": True,
            "data": [
                {
                    "id": 8,
                    "timestamp": "2026-04-07T07:59:30",
                    "level": "WARNING",
                    "category": "api",
                    "operation": "API请求",
                    "message": "API请求频率过高",
                    "details": {"endpoint": "/api/market/quotes", "rate": "120 req/min"},
                    "duration_ms": 0,
                    "has_error": True,
                }
            ],
            "total": 1,
            "filtered": 1,
            "timestamp": "2026-04-07T08:00:00",
        },
    ),
}

SYSTEM_LOG_SUMMARY_RESPONSES = {
    **SYSTEM_MANAGEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "系统日志摘要",
        {
            "success": True,
            "data": {
                "total_logs": 128,
                "level_counts": {
                    "INFO": 96,
                    "WARNING": 20,
                    "ERROR": 10,
                    "CRITICAL": 2,
                },
                "category_counts": {
                    "database": 48,
                    "api": 32,
                    "adapter": 28,
                    "system": 20,
                },
                "recent_errors_1h": 4,
                "last_update": "2026-04-07T08:00:00",
            },
            "timestamp": "2026-04-07T08:00:00",
        },
    ),
}
