"""Data quality route response examples and OpenAPI response specs."""

from typing import Any

from app.openapi_config import COMMON_RESPONSES


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


DATA_QUALITY_ERROR_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

DATA_QUALITY_ALERT_ACTION_RESPONSES = {
    404: COMMON_RESPONSES[404],
    500: COMMON_RESPONSES[500],
}

DATA_QUALITY_TEST_REQUEST_EXAMPLES = {
    "test_realtime_feed_payload": {
        "summary": "测试实时行情数据质量",
        "description": "提交一段模拟数据，验证指定数据源的质量监控与评分逻辑。",
        "value": {
            "status": "success",
            "timestamp": "2026-04-04T09:35:00Z",
            "test": True,
            "data": {
                "symbol": "600519.SH",
                "price": 1710.88,
                "volume": 126500,
            },
        },
    }
}

DATA_QUALITY_HEALTH_RESPONSES = {
    **DATA_QUALITY_ERROR_RESPONSES,
    **_success_response_spec(
        "数据源健康状态汇总",
        {
            "success": True,
            "message": "Data sources health status retrieved successfully",
            "data": {
                "timestamp": "2026-04-04T09:35:00Z",
                "total_sources": 3,
                "healthy_sources": 2,
                "degraded_sources": 1,
                "failed_sources": 0,
                "sources": {
                    "akshare": {
                        "status": "healthy",
                        "response_time": 120.5,
                        "message": "source reachable",
                        "last_check": "2026-04-04T09:34:58Z",
                        "metrics": {
                            "total_requests": 480,
                            "success_rate": 0.98,
                            "error_count": 8,
                            "availability": 0.995,
                        },
                    }
                },
            },
            "timestamp": "2026-04-04T09:35:00Z",
        },
    ),
}

DATA_QUALITY_ALERT_ACK_RESPONSES = {
    **DATA_QUALITY_ALERT_ACTION_RESPONSES,
    **_success_response_spec(
        "告警确认结果",
        {
            "success": True,
            "message": "Alert 'alert_001' acknowledged successfully",
            "data": None,
            "timestamp": "2026-04-04T09:35:00Z",
        },
    ),
}

DATA_QUALITY_ALERT_RESOLVE_RESPONSES = {
    **DATA_QUALITY_ALERT_ACTION_RESPONSES,
    **_success_response_spec(
        "告警处理结果",
        {
            "success": True,
            "message": "Alert 'alert_001' resolved successfully",
            "data": None,
            "timestamp": "2026-04-04T09:35:00Z",
        },
    ),
}

DATA_QUALITY_METRICS_RESPONSES = {
    **DATA_QUALITY_ERROR_RESPONSES,
    **_success_response_spec(
        "数据质量指标",
        {
            "success": True,
            "message": "All data quality metrics retrieved successfully",
            "data": {
                "timestamp": "2026-04-05T08:00:00Z",
                "summary": {
                    "average_quality_score": 93.2,
                    "health_percentage": 96.7,
                    "healthy_sources": 3,
                    "total_active_alerts": 1,
                    "critical_alerts": 0,
                },
                "sources": {
                    "akshare": {
                        "overall_quality_score": 95.6,
                        "overall_health": "healthy",
                        "active_alerts_count": 0,
                        "metrics_summary": {
                            "freshness": {
                                "value": 99.2,
                                "unit": "%",
                                "quality_level": "excellent",
                                "severity": "info",
                            }
                        },
                    }
                },
            },
            "timestamp": "2026-04-05T08:00:00Z",
        },
    ),
}

DATA_QUALITY_ALERTS_RESPONSES = {
    **DATA_QUALITY_ERROR_RESPONSES,
    **_success_response_spec(
        "活跃数据质量告警",
        {
            "success": True,
            "message": "Active alerts retrieved successfully",
            "data": {
                "timestamp": "2026-04-05T08:00:00Z",
                "total_alerts": 1,
                "returned_alerts": 1,
                "alerts": [
                    {
                        "id": "alert_001",
                        "metric_name": "freshness",
                        "severity": "warning",
                        "source": "akshare",
                        "message": "Data freshness exceeded threshold",
                        "timestamp": "2026-04-05T07:58:00Z",
                        "acknowledged": False,
                        "resolved": False,
                        "resolved_at": None,
                        "metadata": {"threshold_minutes": 15},
                    }
                ],
            },
            "timestamp": "2026-04-05T08:00:00Z",
        },
    ),
}

DATA_QUALITY_TRENDS_RESPONSES = {
    404: COMMON_RESPONSES[404],
    **DATA_QUALITY_ERROR_RESPONSES,
    **_success_response_spec(
        "数据质量趋势",
        {
            "success": True,
            "message": "Quality trends for 'akshare' retrieved successfully",
            "data": {
                "source": "akshare",
                "period_hours": 24,
                "total_evaluations": 12,
                "hourly_trends": {
                    "2026-04-05 08:00": {
                        "avg_quality_score": 94.5,
                        "avg_response_time": 132.4,
                        "success_rate": 100.0,
                        "total_evaluations": 3,
                    }
                },
            },
            "timestamp": "2026-04-05T08:00:00Z",
        },
    ),
}

DATA_QUALITY_MODE_RESPONSES = {
    **DATA_QUALITY_ERROR_RESPONSES,
    **_success_response_spec(
        "数据源模式配置",
        {
            "success": True,
            "message": "Data source mode configuration retrieved successfully",
            "data": {
                "current_mode": "hybrid",
                "fallback_enabled": True,
                "available_modes": ["mock", "real", "hybrid"],
                "environment_variables": {
                    "USE_MOCK_DATA": "true",
                    "REAL_DATA_AVAILABLE": "false",
                    "FALLBACK_ENABLED": "true",
                },
                "mode_description": {
                    "mock": "完全使用模拟数据",
                    "real": "完全使用真实数据",
                    "hybrid": "混合模式：优先Real，失败时fallback到Mock",
                },
            },
            "timestamp": "2026-04-04T09:35:00Z",
        },
    ),
}

DATA_QUALITY_OVERVIEW_RESPONSES = {
    **DATA_QUALITY_ERROR_RESPONSES,
    **_success_response_spec(
        "系统数据质量概览",
        {
            "success": True,
            "message": "System status overview retrieved successfully",
            "data": {
                "timestamp": "2026-04-04T09:35:00Z",
                "system_health": {"overall_score": 92.4, "status": "healthy", "health_percentage": 96.0},
                "data_sources": {
                    "total": 3,
                    "healthy": 2,
                    "degraded": 1,
                    "failed": 0,
                    "available_sources": ["akshare", "baostock", "tushare"],
                },
                "data_quality": {"average_score": 91.3, "total_alerts": 2, "critical_alerts": 0},
                "configuration": {
                    "mode": "hybrid",
                    "fallback_enabled": True,
                    "monitoring_enabled": True,
                },
                "performance": {"last_24h_health": {"avg_response_time": 145.2, "total_requests": 1280}},
            },
            "timestamp": "2026-04-04T09:35:00Z",
        },
    ),
}

DATA_QUALITY_TEST_RESPONSES = {
    **DATA_QUALITY_ERROR_RESPONSES,
    **_success_response_spec(
        "数据质量测试结果",
        {
            "success": True,
            "message": "Data quality test completed for 'akshare'",
            "data": {
                "source": "akshare",
                "quality_score": 96.5,
                "alerts_generated": 0,
                "metrics": {"latency_ms": 150.0, "completeness": 1.0, "freshness": 0.99},
            },
            "timestamp": "2026-04-04T09:35:00Z",
        },
    ),
}
