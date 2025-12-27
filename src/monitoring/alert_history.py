"""
Alert History and Analytics Database Layer
Provides comprehensive alert tracking, analytics, and reporting capabilities
"""

import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertStatus(str, Enum):
    """Alert lifecycle status"""

    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"


@dataclass
class AlertHistoryRecord:
    """Individual alert history record"""

    id: Optional[int] = None
    alert_name: str = ""
    severity: str = ""
    service: str = ""
    category: str = ""
    instance: str = ""
    status: AlertStatus = AlertStatus.FIRING
    summary: str = ""
    description: str = ""
    start_time: datetime = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    resolution_time_seconds: Optional[float] = None
    acknowledgment_time_seconds: Optional[float] = None
    escalation_level: int = 1
    notification_channels: str = ""  # JSON list of channels
    notification_count: int = 0
    labels: str = ""  # JSON dict of labels
    annotations: str = ""  # JSON dict of annotations
    root_cause: Optional[str] = None
    related_alerts: str = ""  # JSON list of related alert IDs
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class AlertHistoryDatabase:
    """Manages alert history and analytics"""

    def __init__(self, db_path: str = "alert_history.db"):
        self.db_path = db_path
        self.connection = None
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        # Main alert history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                service TEXT NOT NULL,
                category TEXT NOT NULL,
                instance TEXT NOT NULL,
                status TEXT DEFAULT 'firing',
                summary TEXT,
                description TEXT,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                duration_seconds REAL,
                resolution_time_seconds REAL,
                acknowledgment_time_seconds REAL,
                escalation_level INTEGER DEFAULT 1,
                notification_channels TEXT,
                notification_count INTEGER DEFAULT 0,
                labels TEXT,
                annotations TEXT,
                root_cause TEXT,
                related_alerts TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Indices for common queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_alert_name
            ON alert_history(alert_name)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_severity
            ON alert_history(severity)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_service
            ON alert_history(service)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_status
            ON alert_history(status)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_start_time
            ON alert_history(start_time)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_alert_service_time
            ON alert_history(alert_name, service, start_time)
        """
        )

        # Alert metrics summary table (for performance)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alert_metrics_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                alert_name TEXT NOT NULL,
                severity TEXT,
                total_occurrences INTEGER,
                total_duration_seconds REAL,
                avg_resolution_time_seconds REAL,
                avg_escalation_level REAL,
                total_notifications INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, alert_name)
            )
        """
        )

        # Alert correlation table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alert_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert1_id INTEGER NOT NULL,
                alert2_id INTEGER NOT NULL,
                correlation_score REAL,
                correlation_type TEXT,
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(alert1_id) REFERENCES alert_history(id),
                FOREIGN KEY(alert2_id) REFERENCES alert_history(id)
            )
        """
        )

        # Escalation history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS escalation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER NOT NULL,
                from_level INTEGER,
                to_level INTEGER,
                reason TEXT,
                escalated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                escalated_by TEXT,
                FOREIGN KEY(alert_id) REFERENCES alert_history(id)
            )
        """
        )

        # Acknowledgment history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS acknowledgments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER NOT NULL,
                acknowledged_by TEXT NOT NULL,
                acknowledgment_comment TEXT,
                acknowledged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME,
                FOREIGN KEY(alert_id) REFERENCES alert_history(id)
            )
        """
        )

        self.connection.commit()
        logger.info("Alert history database initialized")

    def save_alert(self, record: AlertHistoryRecord) -> int:
        """Save alert history record, return record ID"""
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO alert_history (
                alert_name, severity, service, category, instance,
                status, summary, description, start_time, end_time,
                duration_seconds, resolution_time_seconds,
                acknowledgment_time_seconds, escalation_level,
                notification_channels, notification_count,
                labels, annotations, root_cause, related_alerts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.alert_name,
                record.severity,
                record.service,
                record.category,
                record.instance,
                record.status.value,
                record.summary,
                record.description,
                record.start_time,
                record.end_time,
                record.duration_seconds,
                record.resolution_time_seconds,
                record.acknowledgment_time_seconds,
                record.escalation_level,
                record.notification_channels,
                record.notification_count,
                record.labels,
                record.annotations,
                record.root_cause,
                record.related_alerts,
            ),
        )

        self.connection.commit()
        return cursor.lastrowid

    def update_alert(self, alert_id: int, **updates) -> bool:
        """Update alert history record"""
        cursor = self.connection.cursor()

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"

        cursor.execute(
            f"""
            UPDATE alert_history
            SET {set_clause}
            WHERE id = ?
        """,
            (*updates.values(), alert_id),
        )

        self.connection.commit()
        return cursor.rowcount > 0

    def resolve_alert(self, alert_id: int, resolution_time_seconds: float = None) -> bool:
        """Mark alert as resolved"""
        end_time = datetime.now()
        return self.update_alert(
            alert_id,
            status=AlertStatus.RESOLVED.value,
            end_time=end_time,
            resolution_time_seconds=resolution_time_seconds,
        )

    def acknowledge_alert(self, alert_id: int, acknowledged_by: str, comment: str = None) -> int:
        """Record alert acknowledgment"""
        cursor = self.connection.cursor()

        # Update alert status
        self.update_alert(alert_id, status=AlertStatus.ACKNOWLEDGED.value)

        # Record acknowledgment
        cursor.execute(
            """
            INSERT INTO acknowledgments (
                alert_id, acknowledged_by, acknowledgment_comment
            ) VALUES (?, ?, ?)
        """,
            (alert_id, acknowledged_by, comment),
        )

        self.connection.commit()
        return cursor.lastrowid

    def escalate_alert(
        self,
        alert_id: int,
        to_level: int,
        reason: str = None,
        escalated_by: str = "system",
    ) -> int:
        """Record alert escalation"""
        cursor = self.connection.cursor()

        # Get current level
        current = cursor.execute("SELECT escalation_level FROM alert_history WHERE id = ?", (alert_id,)).fetchone()

        from_level = current["escalation_level"] if current else 1

        # Record escalation
        cursor.execute(
            """
            INSERT INTO escalation_history (
                alert_id, from_level, to_level, reason, escalated_by
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (alert_id, from_level, to_level, reason, escalated_by),
        )

        # Update alert
        self.update_alert(alert_id, escalation_level=to_level, status=AlertStatus.ESCALATED.value)

        self.connection.commit()
        return cursor.lastrowid

    def get_alert(self, alert_id: int) -> Optional[Dict]:
        """Get alert history record by ID"""
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT * FROM alert_history WHERE id = ?", (alert_id,)).fetchone()

        return dict(row) if row else None

    def get_alerts(
        self,
        alert_name: Optional[str] = None,
        severity: Optional[str] = None,
        service: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict]:
        """Query alerts with filters"""
        query = "SELECT * FROM alert_history WHERE 1=1"
        params = []

        if alert_name:
            query += " AND alert_name = ?"
            params.append(alert_name)

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        if service:
            query += " AND service = ?"
            params.append(service)

        if status:
            query += " AND status = ?"
            params.append(status)

        if start_time:
            query += " AND start_time >= ?"
            params.append(start_time)

        if end_time:
            query += " AND start_time <= ?"
            params.append(end_time)

        query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.connection.cursor()
        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_alert_statistics(self, alert_name: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Get alert statistics for time period"""
        start_time = datetime.now() - timedelta(days=days)
        cursor = self.connection.cursor()

        # Total alerts by severity
        query = """
            SELECT severity, COUNT(*) as count
            FROM alert_history
            WHERE start_time >= ?
        """
        params = [start_time]

        if alert_name:
            query += " AND alert_name = ?"
            params.append(alert_name)

        query += " GROUP BY severity"

        severity_stats = {}
        for row in cursor.execute(query, params).fetchall():
            severity_stats[row["severity"]] = row["count"]

        # Resolution time statistics
        query = """
            SELECT
                AVG(resolution_time_seconds) as avg_resolution,
                MIN(resolution_time_seconds) as min_resolution,
                MAX(resolution_time_seconds) as max_resolution
            FROM alert_history
            WHERE start_time >= ? AND resolution_time_seconds IS NOT NULL
        """
        params = [start_time]

        if alert_name:
            query += " AND alert_name = ?"
            params.append(alert_name)

        resolution_row = cursor.execute(query, params).fetchone()

        # Escalation statistics
        query = """
            SELECT AVG(escalation_level) as avg_escalation
            FROM alert_history
            WHERE start_time >= ?
        """
        params = [start_time]

        if alert_name:
            query += " AND alert_name = ?"
            params.append(alert_name)

        escalation_row = cursor.execute(query, params).fetchone()

        # Alert frequency by service
        query = """
            SELECT service, COUNT(*) as count
            FROM alert_history
            WHERE start_time >= ?
            GROUP BY service
            ORDER BY count DESC
            LIMIT 10
        """
        params = [start_time]

        if alert_name:
            query += " AND alert_name = ?"
            params.append(alert_name)

        service_stats = {}
        for row in cursor.execute(query, params).fetchall():
            service_stats[row["service"]] = row["count"]

        return {
            "time_period_days": days,
            "severity_distribution": severity_stats,
            "average_resolution_time_seconds": resolution_row["avg_resolution"],
            "min_resolution_time_seconds": resolution_row["min_resolution"],
            "max_resolution_time_seconds": resolution_row["max_resolution"],
            "average_escalation_level": escalation_row["avg_escalation"],
            "top_services_by_alert_count": service_stats,
        }

    def get_top_alerts(
        self,
        limit: int = 10,
        days: int = 7,
        order_by: str = "count",  # count, resolution_time, escalation_level
    ) -> List[Dict]:
        """Get most impactful alerts"""
        start_time = datetime.now() - timedelta(days=days)

        if order_by == "resolution_time":
            query = """
                SELECT
                    alert_name,
                    COUNT(*) as count,
                    AVG(resolution_time_seconds) as avg_resolution_time,
                    AVG(escalation_level) as avg_escalation
                FROM alert_history
                WHERE start_time >= ?
                GROUP BY alert_name
                ORDER BY avg_resolution_time DESC
                LIMIT ?
            """
        elif order_by == "escalation_level":
            query = """
                SELECT
                    alert_name,
                    COUNT(*) as count,
                    AVG(resolution_time_seconds) as avg_resolution_time,
                    AVG(escalation_level) as avg_escalation
                FROM alert_history
                WHERE start_time >= ?
                GROUP BY alert_name
                ORDER BY avg_escalation DESC
                LIMIT ?
            """
        else:  # Default: by count
            query = """
                SELECT
                    alert_name,
                    COUNT(*) as count,
                    AVG(resolution_time_seconds) as avg_resolution_time,
                    AVG(escalation_level) as avg_escalation
                FROM alert_history
                WHERE start_time >= ?
                GROUP BY alert_name
                ORDER BY count DESC
                LIMIT ?
            """

        cursor = self.connection.cursor()
        rows = cursor.execute(query, (start_time, limit)).fetchall()
        return [dict(row) for row in rows]

    def get_alert_trends(
        self,
        alert_name: Optional[str] = None,
        days: int = 30,
        granularity: str = "day",  # day, hour
    ) -> List[Dict]:
        """Get alert trend data for charting"""
        start_time = datetime.now() - timedelta(days=days)
        cursor = self.connection.cursor()

        if granularity == "hour":
            date_format = "strftime('%Y-%m-%d %H:00', start_time)"
        else:  # day
            date_format = "DATE(start_time)"

        query = f"""
            SELECT
                {date_format} as time_bucket,
                severity,
                COUNT(*) as count,
                AVG(resolution_time_seconds) as avg_resolution_time
            FROM alert_history
            WHERE start_time >= ?
        """
        params = [start_time]

        if alert_name:
            query += " AND alert_name = ?"
            params.append(alert_name)

        query += f" GROUP BY {date_format}, severity ORDER BY time_bucket DESC"

        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_related_alerts(self, alert_id: int, min_correlation: float = 0.5) -> List[Dict]:
        """Get alerts correlated with given alert"""
        cursor = self.connection.cursor()

        query = """
            SELECT
                c.alert2_id,
                c.correlation_score,
                c.correlation_type,
                ah.alert_name,
                ah.severity,
                ah.service,
                ah.summary
            FROM alert_correlations c
            JOIN alert_history ah ON c.alert2_id = ah.id
            WHERE c.alert1_id = ? AND c.correlation_score >= ?
            ORDER BY c.correlation_score DESC
        """

        rows = cursor.execute(query, (alert_id, min_correlation)).fetchall()
        return [dict(row) for row in rows]

    def record_correlation(
        self,
        alert1_id: int,
        alert2_id: int,
        correlation_score: float,
        correlation_type: str = "temporal",
    ) -> int:
        """Record correlation between two alerts"""
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO alert_correlations (
                alert1_id, alert2_id, correlation_score, correlation_type
            ) VALUES (?, ?, ?, ?)
        """,
            (alert1_id, alert2_id, correlation_score, correlation_type),
        )

        self.connection.commit()
        return cursor.lastrowid

    def get_service_health(self, service: str, days: int = 7) -> Dict[str, Any]:
        """Get health metrics for a service"""
        start_time = datetime.now() - timedelta(days=days)
        cursor = self.connection.cursor()

        query = """
            SELECT
                COUNT(*) as total_alerts,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN severity = 'warning' THEN 1 ELSE 0 END) as warning_count,
                SUM(CASE WHEN severity = 'info' THEN 1 ELSE 0 END) as info_count,
                AVG(resolution_time_seconds) as avg_resolution_time,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_count
            FROM alert_history
            WHERE service = ? AND start_time >= ?
        """

        row = cursor.execute(query, (service, start_time)).fetchone()

        if not row or row["total_alerts"] == 0:
            return {
                "service": service,
                "days": days,
                "total_alerts": 0,
                "health_score": 100.0,
                "critical_count": 0,
                "warning_count": 0,
                "info_count": 0,
            }

        # Calculate health score (0-100)
        # Based on: resolved rate, resolution time, severity distribution
        resolved_rate = (row["resolved_count"] / row["total_alerts"]) * 100
        critical_weight = (row["critical_count"] / row["total_alerts"]) * 100 if row["total_alerts"] > 0 else 0

        health_score = (resolved_rate * 0.5) - (critical_weight * 0.3)
        health_score = max(0, min(100, health_score))

        return {
            "service": service,
            "days": days,
            "total_alerts": row["total_alerts"],
            "resolved_count": row["resolved_count"],
            "resolved_rate_percent": resolved_rate,
            "critical_count": row["critical_count"],
            "warning_count": row["warning_count"],
            "info_count": row["info_count"],
            "average_resolution_time_seconds": row["avg_resolution_time"],
            "health_score": health_score,
        }

    def cleanup_old_records(self, days: int = 90) -> int:
        """Delete alert records older than specified days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        cursor = self.connection.cursor()

        cursor.execute("DELETE FROM alert_history WHERE start_time < ?", (cutoff_time,))

        self.connection.commit()
        deleted_count = cursor.rowcount

        logger.info(f"Deleted {deleted_count} alert records older than {days} days")
        return deleted_count

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global singleton instance
_alert_history_db: Optional[AlertHistoryDatabase] = None


def get_alert_history_db() -> AlertHistoryDatabase:
    """Get global alert history database instance"""
    global _alert_history_db
    if _alert_history_db is None:
        _alert_history_db = AlertHistoryDatabase()
    return _alert_history_db
