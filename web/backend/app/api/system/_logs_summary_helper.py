"""Helpers for system log summary responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def build_logs_summary_payload(logs: list[Any], total: int) -> dict[str, Any]:
    """Build the response payload for `/logs/summary`."""
    level_counts = {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
    for log in logs:
        if log.level in level_counts:
            level_counts[log.level] += 1

    category_counts: dict[str, int] = {}
    for log in logs:
        category_counts[log.category] = category_counts.get(log.category, 0) + 1

    recent_errors = sum(1 for log in logs if log.has_error)
    timestamp = datetime.now().isoformat()

    return {
        "success": True,
        "data": {
            "total_logs": total,
            "level_counts": level_counts,
            "category_counts": category_counts,
            "recent_errors_1h": recent_errors,
            "last_update": timestamp,
        },
        "timestamp": timestamp,
    }
