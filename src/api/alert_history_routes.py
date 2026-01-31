"""
FastAPI routes for alert history and analytics
Provides API endpoints for alert query, reporting, and analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.monitoring.alert_history import (
    AlertHistoryDatabase,
    AlertHistoryRecord,
    get_alert_history_db,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/history")
async def get_alert_history(
    alert_name: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """
    Retrieve alert history with optional filtering

    Query Parameters:
    - alert_name: Filter by alert name
    - severity: Filter by severity (critical, warning, info)
    - service: Filter by service
    - status: Filter by status (firing, resolved, acknowledged, suppressed, escalated)
    - days: Days to look back (default: 7)
    - limit: Maximum results (default: 1000)
    - offset: Pagination offset (default: 0)
    """
    start_time = datetime.now() - timedelta(days=days)

    alerts = db.get_alerts(
        alert_name=alert_name,
        severity=severity,
        service=service,
        status=status,
        start_time=start_time,
        limit=limit,
        offset=offset,
    )

    return {
        "success": True,
        "count": len(alerts),
        "total_returned": limit,
        "data": alerts,
    }


@router.get("/history/{alert_id}")
async def get_alert_by_id(alert_id: int, db: AlertHistoryDatabase = Depends(get_alert_history_db)):
    """Get specific alert record by ID"""
    alert = db.get_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"success": True, "data": alert}


@router.get("/statistics")
async def get_alert_statistics(
    alert_name: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """
    Get alert statistics for time period

    Returns:
    - Severity distribution
    - Resolution time statistics
    - Escalation statistics
    - Top services by alert count
    """
    stats = db.get_alert_statistics(alert_name=alert_name, days=days)

    return {"success": True, "data": stats}


@router.get("/top-alerts")
async def get_top_alerts(
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(7, ge=1, le=365),
    order_by: str = Query("count", regex="^(count|resolution_time|escalation_level)$"),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """
    Get most impactful alerts

    Order by:
    - count: Total occurrences
    - resolution_time: Average resolution time (slowest)
    - escalation_level: Average escalation level (highest)
    """
    alerts = db.get_top_alerts(limit=limit, days=days, order_by=order_by)

    return {"success": True, "count": len(alerts), "order_by": order_by, "data": alerts}


@router.get("/trends")
async def get_alert_trends(
    alert_name: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    granularity: str = Query("day", regex="^(day|hour)$"),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """
    Get alert trend data for charting

    Granularity:
    - day: Daily buckets
    - hour: Hourly buckets
    """
    trends = db.get_alert_trends(alert_name=alert_name, days=days, granularity=granularity)

    return {
        "success": True,
        "count": len(trends),
        "granularity": granularity,
        "data": trends,
    }


@router.get("/service-health/{service}")
async def get_service_health(
    service: str,
    days: int = Query(7, ge=1, le=365),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """
    Get health metrics for a service

    Metrics:
    - Total alerts
    - Resolved count and rate
    - Severity distribution
    - Average resolution time
    - Health score (0-100)
    """
    health = db.get_service_health(service=service, days=days)

    return {"success": True, "data": health}


@router.post("/history")
async def save_alert_history(alert_data: dict, db: AlertHistoryDatabase = Depends(get_alert_history_db)):
    """
    Save new alert history record

    Request body:
    {
        "alert_name": "HighAPIResponseTime",
        "severity": "warning",
        "service": "api",
        "category": "performance",
        "instance": "api-prod-1",
        "summary": "API response time high",
        "description": "p95 response time exceeded 1s",
        "labels": {"environment": "prod"},
        "annotations": {"runbook": "..."}
    }
    """
    try:
        record = AlertHistoryRecord(
            alert_name=alert_data.get("alert_name"),
            severity=alert_data.get("severity"),
            service=alert_data.get("service"),
            category=alert_data.get("category"),
            instance=alert_data.get("instance"),
            summary=alert_data.get("summary"),
            description=alert_data.get("description"),
            labels=alert_data.get("labels", {}),
            annotations=alert_data.get("annotations", {}),
            start_time=(
                datetime.fromisoformat(alert_data.get("start_time")) if alert_data.get("start_time") else datetime.now()
            ),
        )

        alert_id = db.save_alert(record)

        return {
            "success": True,
            "alert_id": alert_id,
            "message": "Alert history record created",
        }
    except Exception as e:
        logger.error("Error saving alert: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/history/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    resolution_time_seconds: Optional[float] = Query(None),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """Mark alert as resolved"""
    success = db.resolve_alert(alert_id, resolution_time_seconds)

    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {
        "success": True,
        "alert_id": alert_id,
        "message": "Alert marked as resolved",
    }


@router.put("/history/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    acknowledged_by: str = Query(...),
    comment: Optional[str] = Query(None),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """Acknowledge alert"""
    try:
        ack_id = db.acknowledge_alert(alert_id, acknowledged_by, comment)

        return {
            "success": True,
            "alert_id": alert_id,
            "acknowledgment_id": ack_id,
            "message": "Alert acknowledged",
        }
    except Exception as e:
        logger.error("Error acknowledging alert: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/history/{alert_id}/escalate")
async def escalate_alert(
    alert_id: int,
    to_level: int = Query(..., ge=1, le=3),
    reason: Optional[str] = Query(None),
    escalated_by: str = Query("system"),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """Escalate alert to higher level"""
    try:
        escalation_id = db.escalate_alert(alert_id, to_level, reason, escalated_by)

        return {
            "success": True,
            "alert_id": alert_id,
            "escalation_id": escalation_id,
            "to_level": to_level,
            "message": "Alert escalated",
        }
    except Exception as e:
        logger.error("Error escalating alert: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/related/{alert_id}")
async def get_related_alerts(
    alert_id: int,
    min_correlation: float = Query(0.5, ge=0.0, le=1.0),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """Get alerts correlated with given alert"""
    related = db.get_related_alerts(alert_id, min_correlation)

    return {
        "success": True,
        "count": len(related),
        "min_correlation": min_correlation,
        "data": related,
    }


@router.post("/correlations")
async def record_alert_correlation(
    alert1_id: int = Query(...),
    alert2_id: int = Query(...),
    correlation_score: float = Query(..., ge=0.0, le=1.0),
    correlation_type: str = Query("temporal"),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """Record correlation between two alerts"""
    try:
        correlation_id = db.record_correlation(alert1_id, alert2_id, correlation_score, correlation_type)

        return {
            "success": True,
            "correlation_id": correlation_id,
            "message": "Correlation recorded",
        }
    except Exception as e:
        logger.error("Error recording correlation: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/history/cleanup")
async def cleanup_old_records(
    days: int = Query(90, ge=30, le=365),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """
    Delete alert records older than specified days

    Warning: This operation cannot be undone
    """
    deleted_count = db.cleanup_old_records(days)

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} records older than {days} days",
    }


@router.get("/report/daily")
async def get_daily_report(
    service: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """
    Get comprehensive daily alert report

    Includes:
    - Alert count by severity
    - Top alerts
    - Service health metrics
    - Trends
    """
    stats = db.get_alert_statistics(days=days)
    top_alerts = db.get_top_alerts(limit=5, days=days)

    services_to_check = [service] if service else ["api", "database", "cache", "notification"]
    service_health = {}
    for svc in services_to_check:
        service_health[svc] = db.get_service_health(svc, days=days)

    return {
        "success": True,
        "report_date": datetime.now().isoformat(),
        "days": days,
        "statistics": stats,
        "top_alerts": top_alerts,
        "service_health": service_health,
    }


@router.get("/export/csv")
async def export_alerts_csv(
    alert_name: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365),
    db: AlertHistoryDatabase = Depends(get_alert_history_db),
):
    """
    Export alerts as CSV

    Returns CSV format suitable for spreadsheet imports
    """
    import csv
    import io

    start_time = datetime.now() - timedelta(days=days)
    alerts = db.get_alerts(
        alert_name=alert_name,
        severity=severity,
        service=service,
        start_time=start_time,
        limit=100000,
    )

    # Create CSV
    output = io.StringIO()
    if alerts:
        writer = csv.DictWriter(output, fieldnames=alerts[0].keys())
        writer.writeheader()
        writer.writerows(alerts)

    return {"success": True, "count": len(alerts), "csv_data": output.getvalue()}
