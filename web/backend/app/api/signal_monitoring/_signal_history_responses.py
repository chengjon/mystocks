"""Signal history response examples and OpenAPI response specs."""

from typing import Any

from app.openapi_config import COMMON_RESPONSES


SIGNAL_MONITORING_HEALTH_RESPONSE_EXAMPLE = {
    "status": "healthy",
    "service": "signal-monitoring-api",
    "version": "v1.0",
    "database": "connected",
}

SIGNAL_MONITORING_HEALTH_ERROR_RESPONSE_EXAMPLE = {
    "status": "unhealthy",
    "service": "signal-monitoring-api",
    "version": "v1.0",
    "database": "error",
    "error": "database unavailable",
}


def _success_response_spec(description: str, example: Any) -> dict[int, dict[str, Any]]:
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


SIGNAL_MONITORING_ERROR_RESPONSES = {
    401: COMMON_RESPONSES[401],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    503: {
        "description": "监控数据库不可用",
        "content": {
            "application/json": {
                "example": {
                    "detail": "监控数据库未连接",
                }
            }
        },
    },
}

SIGNAL_HISTORY_RESPONSES = {
    **SIGNAL_MONITORING_ERROR_RESPONSES,
    **_success_response_spec(
        "信号历史记录列表",
        [
            {
                "id": 12345,
                "strategy_id": "macd_strategy",
                "symbol": "600519.SH",
                "signal_type": "BUY",
                "generated_at": "2026-01-08T10:30:00",
                "status": "executed",
                "execution_time_ms": 45.5,
                "gpu_used": True,
                "gpu_latency_ms": 12.3,
                "executed": True,
                "executed_at": "2026-01-08T10:30:05",
                "profit_loss": 125.5,
                "profit_loss_percent": 2.5,
            }
        ],
    ),
}

SIGNAL_QUALITY_REPORT_RESPONSES = {
    **SIGNAL_MONITORING_ERROR_RESPONSES,
    **_success_response_spec(
        "信号质量分析报告",
        {
            "strategy_id": "macd_strategy",
            "period_start": "2026-01-01",
            "period_end": "2026-01-08",
            "total_signals": 150,
            "buy_signals": 75,
            "sell_signals": 60,
            "hold_signals": 15,
            "executed_signals": 120,
            "execution_rate": 80.0,
            "signal_accuracy": 78.5,
            "signal_success_rate": 85.0,
            "avg_profit_loss": 25.5,
            "total_profit_loss": 3060.0,
            "avg_execution_time_ms": 45.2,
            "gpu_usage_rate": 65.0,
            "profitable_signals": 95,
            "losing_signals": 25,
            "win_rate": 79.17,
        },
    ),
}

STRATEGY_REALTIME_RESPONSES = {
    **SIGNAL_MONITORING_ERROR_RESPONSES,
    **_success_response_spec(
        "策略实时监控快照",
        {
            "strategy_id": "macd_strategy",
            "timestamp": "2026-01-08T15:30:45",
            "health_status": 1,
            "active_signals_count": 5,
            "signal_generation_rate": 2.5,
            "avg_latency_ms": 45.2,
            "p95_latency_ms": 68.5,
            "p99_latency_ms": 92.3,
            "gpu_enabled": True,
            "gpu_utilization": 75.5,
            "recent_signals": [
                {
                    "id": 12345,
                    "symbol": "600519.SH",
                    "signal_type": "BUY",
                    "generated_at": "2026-01-08T15:30:00",
                }
            ],
        },
    ),
}
