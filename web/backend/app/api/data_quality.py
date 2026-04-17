"""
数据质量监控API端点
提供数据源状态、健康检查、质量指标等监控信息
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Path, Query

from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.core.responses import create_error_response, create_success_response
from app.openapi_config import COMMON_RESPONSES
from app.services.data_quality_monitor import get_data_quality_monitor, monitor_data_quality
from app.services.data_source_factory import get_data_source_factory
from app.services.data_source_factory import get_data_source_mode as get_factory_mode
from app.services.data_source_factory import is_fallback_enabled

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data-quality", tags=["data-quality"])


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


@router.get(
    "/health",
    summary="获取数据源健康状态",
    description="汇总所有数据源的健康状态、响应时间和可用性指标，供运维与数据质量监控面板使用。",
    responses=DATA_QUALITY_HEALTH_RESPONSES,
)
async def get_sources_health():
    """获取所有数据源健康状态"""
    try:
        factory = await get_data_source_factory()
        health_results = await factory.health_check_all()

        # 格式化健康状态
        health_summary = {
            "timestamp": datetime.now().isoformat(),
            "total_sources": len(health_results),
            "healthy_sources": sum(1 for h in health_results.values() if h.status.value == "healthy"),
            "degraded_sources": sum(1 for h in health_results.values() if h.status.value == "degraded"),
            "failed_sources": sum(1 for h in health_results.values() if h.status.value == "failed"),
            "sources": {},
        }

        for source_name, health in health_results.items():
            metrics = factory.get_source_metrics(source_name)
            health_summary["sources"][source_name] = {
                "status": health.status.value,
                "response_time": health.response_time,
                "message": health.message,
                "last_check": health.timestamp.isoformat(),
                "metrics": (
                    {
                        "total_requests": metrics.total_requests,
                        "success_rate": metrics.success_rate,
                        "error_count": metrics.error_count,
                        "availability": metrics.availability,
                    }
                    if metrics
                    else None
                ),
            }

        return create_success_response(data=health_summary, message="Data sources health status retrieved successfully")

    except Exception as e:
        logger.error("Failed to get sources health: {str(e)}")
        return create_error_response(
            error_code="HEALTH_CHECK_FAILED",
            message="Failed to retrieve data sources health status",
            details={"error": str(e)},
        )


@router.get(
    "/metrics",
    summary="获取数据质量指标",
    description="返回指定数据源或全量数据源的数据质量评分、健康等级和关键指标摘要，供质量大盘和巡检脚本使用。",
    responses=DATA_QUALITY_METRICS_RESPONSES,
)
async def get_data_quality_metrics(source: Optional[str] = Query(None, description="Filter by specific data source")):
    """获取数据质量指标"""
    try:
        monitor = get_data_quality_monitor()

        if source:
            # 获取特定数据源的指标
            source_metrics = monitor.get_source_metrics(source)
            if not source_metrics:
                raise NotFoundException(resource="数据源", identifier=source)

            quality_score = source_metrics.get_overall_quality_score()
            active_alerts = source_metrics.get_active_alerts()

            metrics_data = {
                "source": source,
                "overall_quality_score": quality_score,
                "overall_health": (
                    "healthy" if quality_score >= 90 else "degraded" if quality_score >= 70 else "unhealthy"
                ),
                "active_alerts_count": len(active_alerts),
                "metrics": {
                    name: {
                        "value": metric.value,
                        "unit": metric.unit,
                        "description": metric.description,
                        "quality_level": metric.quality_level.value,
                        "severity": metric.get_severity().value,
                        "trend_direction": metric.get_trend_direction(),
                        "last_updated": metric.last_updated.isoformat(),
                        "threshold_warning": metric.threshold_warning,
                        "threshold_error": metric.threshold_error,
                        "threshold_critical": metric.threshold_critical,
                    }
                    for name, metric in source_metrics.metrics.items()
                },
            }

            return create_success_response(
                data=metrics_data, message=f"Data quality metrics for '{source}' retrieved successfully"
            )
        else:
            # 获取所有数据源的指标
            all_source_metrics = monitor.get_all_source_metrics()
            health_summary = monitor.get_overall_health_summary()

            all_metrics_data = {"timestamp": datetime.now().isoformat(), "summary": health_summary, "sources": {}}

            for source_name, source_metrics in all_source_metrics.items():
                quality_score = source_metrics.get_overall_quality_score()
                active_alerts = source_metrics.get_active_alerts()

                all_metrics_data["sources"][source_name] = {
                    "overall_quality_score": quality_score,
                    "overall_health": (
                        "healthy" if quality_score >= 90 else "degraded" if quality_score >= 70 else "unhealthy"
                    ),
                    "active_alerts_count": len(active_alerts),
                    "metrics_summary": {
                        name: {
                            "value": metric.value,
                            "unit": metric.unit,
                            "quality_level": metric.quality_level.value,
                            "severity": metric.get_severity().value,
                        }
                        for name, metric in source_metrics.metrics.items()
                    },
                }

            return create_success_response(
                data=all_metrics_data, message="All data quality metrics retrieved successfully"
            )

    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to get data quality metrics: {str(e)}")
        return create_error_response(
            error_code="METRICS_RETRIEVAL_FAILED",
            message="Failed to retrieve data quality metrics",
            details={"error": str(e)},
        )


@router.get(
    "/alerts",
    summary="获取活跃数据质量告警",
    description="按严重级别、数据源和数量上限返回当前活跃告警列表，供值班人员快速识别待处理的数据质量问题。",
    responses=DATA_QUALITY_ALERTS_RESPONSES,
)
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of alerts to return"),
):
    """获取活跃告警"""
    try:
        monitor = get_data_quality_monitor()
        all_alerts = monitor.get_all_alerts()

        # 应用过滤器
        filtered_alerts = []
        for alert in all_alerts:
            if severity and alert.severity.value != severity:
                continue
            if source and alert.source != source:
                continue
            filtered_alerts.append(alert)

        # 限制结果数量
        limited_alerts = filtered_alerts[:limit]

        alerts_data = {
            "timestamp": datetime.now().isoformat(),
            "total_alerts": len(filtered_alerts),
            "returned_alerts": len(limited_alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "metric_name": alert.metric_name,
                    "severity": alert.severity.value,
                    "source": alert.source,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "acknowledged": alert.acknowledged,
                    "resolved": alert.resolved,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "metadata": alert.metadata,
                }
                for alert in limited_alerts
            ],
        }

        return create_success_response(data=alerts_data, message="Active alerts retrieved successfully")

    except Exception as e:
        logger.error("Failed to get active alerts: {str(e)}")
        return create_error_response(
            error_code="ALERTS_RETRIEVAL_FAILED", message="Failed to retrieve active alerts", details={"error": str(e)}
        )


@router.post(
    "/alerts/{alert_id}/acknowledge",
    summary="确认数据质量告警",
    description="按告警ID确认一条数据质量告警，便于运维人员标记已知问题并避免重复处理。",
    responses=DATA_QUALITY_ALERT_ACK_RESPONSES,
)
async def acknowledge_alert(alert_id: str = Path(..., description="需要确认的数据质量告警ID。")):
    """确认告警"""
    try:
        monitor = get_data_quality_monitor()

        # 查找并确认告警
        acknowledged = False
        for source_metrics in monitor.get_all_source_metrics().values():
            if source_metrics.acknowledge_alert(alert_id):
                acknowledged = True
                break

        if not acknowledged:
            raise NotFoundException(resource="告警", identifier=alert_id)

        return create_success_response(message=f"Alert '{alert_id}' acknowledged successfully")

    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to acknowledge alert: {str(e)}")
        return create_error_response(
            error_code="ALERT_ACKNOWLEDGE_FAILED", message="Failed to acknowledge alert", details={"error": str(e)}
        )


@router.post(
    "/alerts/{alert_id}/resolve",
    summary="解决数据质量告警",
    description="按告警ID将一条数据质量告警标记为已解决，并保留后续审计与回溯所需状态。",
    responses=DATA_QUALITY_ALERT_RESOLVE_RESPONSES,
)
async def resolve_alert(alert_id: str = Path(..., description="需要标记为已解决的数据质量告警ID。")):
    """解决告警"""
    try:
        monitor = get_data_quality_monitor()

        # 查找并解决告警
        resolved = False
        for source_metrics in monitor.get_all_source_metrics().values():
            if source_metrics.resolve_alert(alert_id):
                resolved = True
                break

        if not resolved:
            raise NotFoundException(resource="告警", identifier=alert_id)

        return create_success_response(message=f"Alert '{alert_id}' resolved successfully")

    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to resolve alert: {str(e)}")
        return create_error_response(
            error_code="ALERT_RESOLVE_FAILED", message="Failed to resolve alert", details={"error": str(e)}
        )


@router.get(
    "/config/mode",
    summary="获取数据源模式配置",
    description="返回当前数据源运行模式、回退开关和环境变量快照，帮助确认实时环境配置状态。",
    responses=DATA_QUALITY_MODE_RESPONSES,
)
async def get_data_source_mode():
    """获取当前数据源模式配置"""
    try:
        mode = get_factory_mode()
        fallback_enabled = is_fallback_enabled()
        current_mode = mode.value if hasattr(mode, "value") else str(mode)

        config_data = {
            "current_mode": current_mode,
            "fallback_enabled": fallback_enabled,
            "available_modes": ["mock", "real", "hybrid"],
            "environment_variables": {
                "USE_MOCK_DATA": str(settings.use_mock_apis).lower(),
                "REAL_DATA_AVAILABLE": str(current_mode != "mock").lower(),
                "FALLBACK_ENABLED": str(fallback_enabled).lower(),
            },
            "mode_description": {
                "mock": "完全使用模拟数据",
                "real": "完全使用真实数据",
                "hybrid": "混合模式：优先Real，失败时fallback到Mock",
            },
        }

        return create_success_response(
            data=config_data, message="Data source mode configuration retrieved successfully"
        )

    except Exception as e:
        logger.error("Failed to get data source mode: {str(e)}")
        return create_error_response(
            error_code="MODE_RETRIEVAL_FAILED", message="Failed to retrieve data source mode", details={"error": str(e)}
        )


@router.get(
    "/status/overview",
    summary="获取系统状态概览",
    description="汇总数据源健康分、告警数量、运行模式和近期性能指标，用于数据质量总览面板展示。",
    responses=DATA_QUALITY_OVERVIEW_RESPONSES,
)
async def get_system_status_overview():
    """获取系统状态概览"""
    try:
        # 获取数据源工厂状态
        factory = await get_data_source_factory()
        health_results = await factory.health_check_all()
        available_sources = factory.get_available_sources()

        # 获取数据质量监控状态
        monitor = get_data_quality_monitor()
        health_summary = monitor.get_overall_health_summary()
        monitor.get_all_alerts()

        # 获取环境配置
        mode = get_factory_mode()
        fallback_enabled = is_fallback_enabled()

        # 计算系统健康分数
        health_score = 0
        if available_sources:
            healthy_ratio = health_summary["health_percentage"] / 100
            availability_score = healthy_ratio * 100
            quality_score = health_summary["average_quality_score"]
            health_score = (availability_score + quality_score) / 2

        overview_data = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {
                "overall_score": round(health_score, 2),
                "status": "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "unhealthy",
                "health_percentage": health_summary["health_percentage"],
            },
            "data_sources": {
                "total": len(available_sources),
                "healthy": health_summary["healthy_sources"],
                "degraded": len(available_sources) - health_summary["healthy_sources"],  # Calculate degraded sources
                "failed": 0,  # Currently no failed sources in the health summary
                "available_sources": available_sources,
            },
            "data_quality": {
                "average_score": health_summary["average_quality_score"],
                "total_alerts": health_summary["total_active_alerts"],
                "critical_alerts": health_summary["critical_alerts"],
            },
            "configuration": {
                "mode": mode.value if hasattr(mode, "value") else str(mode),
                "fallback_enabled": fallback_enabled,
                "monitoring_enabled": monitor.is_monitoring_enabled(),
            },
            "performance": {
                "last_24h_health": {
                    "avg_response_time": (
                        sum(h.response_time for h in health_results.values()) / len(health_results)
                        if health_results
                        else 0
                    ),
                    "total_requests": sum(
                        factory.get_source_metrics(s).total_requests
                        for s in available_sources
                        if factory.get_source_metrics(s)
                    ),
                }
            },
        }

        return create_success_response(data=overview_data, message="System status overview retrieved successfully")

    except Exception as e:
        logger.error("Failed to get system status overview: {str(e)}")
        return create_error_response(
            error_code="OVERVIEW_RETRIEVAL_FAILED",
            message="Failed to retrieve system status overview",
            details={"error": str(e)},
        )


@router.post(
    "/test/quality",
    summary="测试数据质量监控",
    description="向指定数据源提交一段测试数据并返回质量监控结果，验证质量评分和告警逻辑是否正常。",
    responses=DATA_QUALITY_TEST_RESPONSES,
)
async def test_data_quality(
    source: str = Query(..., description="需要执行数据质量测试的数据源名称。"),
    test_data: Optional[Dict[str, Any]] = Body(None, openapi_examples=DATA_QUALITY_TEST_REQUEST_EXAMPLES),
):
    """测试数据质量监控"""
    try:
        if test_data is None:
            # 创建测试数据
            test_data = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "test": True,
                "data": {"sample": "test data"},
            }

        # 模拟响应时间
        response_time = 150.0  # 模拟150ms响应时间

        # 执行数据质量监控
        quality_result = await monitor_data_quality(
            data=test_data, source=source, response_time=response_time, success=True
        )

        return create_success_response(data=quality_result, message=f"Data quality test completed for '{source}'")

    except Exception as e:
        logger.error("Failed to test data quality: {str(e)}")
        return create_error_response(
            error_code="QUALITY_TEST_FAILED", message="Failed to test data quality", details={"error": str(e)}
        )


@router.get(
    "/metrics/trends",
    summary="获取数据质量趋势",
    description="按数据源和时间窗口返回质量评分、响应时间与成功率趋势，供识别质量退化和波动周期使用。",
    responses=DATA_QUALITY_TRENDS_RESPONSES,
)
async def get_quality_trends(
    source: str = Query(..., description="Data source name"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
):
    """获取数据质量趋势"""
    try:
        import statistics

        monitor = get_data_quality_monitor()
        source_metrics = monitor.get_source_metrics(source)

        if not source_metrics:
            raise NotFoundException(resource="数据源", identifier=source)

        # 获取评估历史
        evaluation_history = monitor.evaluation_history.get(source, [])

        # 过滤时间范围
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_evaluations = [
            eval for eval in evaluation_history if datetime.fromisoformat(eval["timestamp"]) >= cutoff_time
        ]

        # 计算趋势数据
        if recent_evaluations:
            [datetime.fromisoformat(eval["timestamp"]) for eval in recent_evaluations]
            [eval["quality_score"] for eval in recent_evaluations]
            [eval.get("response_time", 0) for eval in recent_evaluations]

            # 按小时分组
            hourly_data = {}
            for eval in recent_evaluations:
                hour_key = datetime.fromisoformat(eval["timestamp"]).strftime("%Y-%m-%d %H:00")
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = {
                        "quality_scores": [],
                        "response_times": [],
                        "success_count": 0,
                        "total_count": 0,
                    }

                hourly_data[hour_key]["quality_scores"].append(eval["quality_score"])
                if eval.get("response_time"):
                    hourly_data[hour_key]["response_times"].append(eval["response_time"])
                hourly_data[hour_key]["total_count"] += 1
                if eval.get("success", False):
                    hourly_data[hour_key]["success_count"] += 1

            # 格式化趋势数据
            trend_data = {
                "source": source,
                "period_hours": hours,
                "total_evaluations": len(recent_evaluations),
                "hourly_trends": {},
            }

            for hour, data in hourly_data.items():
                trend_data["hourly_trends"][hour] = {
                    "avg_quality_score": statistics.mean(data["quality_scores"]) if data["quality_scores"] else 0,
                    "avg_response_time": statistics.mean(data["response_times"]) if data["response_times"] else 0,
                    "success_rate": (
                        (data["success_count"] / data["total_count"] * 100) if data["total_count"] > 0 else 0
                    ),
                    "total_evaluations": data["total_count"],
                }

        else:
            trend_data = {"source": source, "period_hours": hours, "total_evaluations": 0, "hourly_trends": {}}

        return create_success_response(data=trend_data, message=f"Quality trends for '{source}' retrieved successfully")

    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to get quality trends: {str(e)}")
        return create_error_response(
            error_code="TRENDS_RETRIEVAL_FAILED", message="Failed to retrieve quality trends", details={"error": str(e)}
        )
