from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
import os
import socket
from typing import Any

import psutil

from app.api.v1.pool_monitoring import connection_pools_health_check


POLL_INTERVAL_SECONDS = 15
MAX_WINDOW_MINUTES = 60
_HISTORY_LIMIT = int((MAX_WINDOW_MINUTES * 60) / POLL_INTERVAL_SECONDS) + 4

_HOST_THRESHOLDS = {
    "cpu_percent": {"warning": 70.0, "critical": 90.0, "unit": "%"},
    "memory_percent": {"warning": 75.0, "critical": 90.0, "unit": "%"},
    "disk_percent": {"warning": 80.0, "critical": 90.0, "unit": "%"},
    "load_percent": {"warning": 70.0, "critical": 90.0, "unit": "%"},
}

_PROCESS_THRESHOLDS = {
    "cpu_percent": {"warning": 70.0, "critical": 90.0, "unit": "%"},
    "memory_percent": {"warning": 60.0, "critical": 80.0, "unit": "%"},
}

_DEPENDENCY_USAGE_THRESHOLDS = {"warning": 70.0, "critical": 90.0, "unit": "%"}

_HOST_HISTORY: dict[str, deque[dict[str, Any]]] = {
    metric_key: deque(maxlen=_HISTORY_LIMIT)
    for metric_key in _HOST_THRESHOLDS
}

_SEVERITY = {"normal": 0, "warning": 1, "critical": 2}


def _status_for_threshold(value: float, warning: float, critical: float) -> str:
    if value >= critical:
        return "critical"
    if value >= warning:
        return "warning"
    return "normal"


def _max_status(*statuses: str) -> str:
    return max(statuses, key=lambda status: _SEVERITY.get(status, 0), default="normal")


def _to_gb(value: float | int | None) -> float | None:
    if value is None:
        return None
    return round(float(value) / 1024**3, 2)


def _append_history(metric_key: str, sampled_at: datetime, value: float) -> None:
    _HOST_HISTORY[metric_key].append(
        {
            "timestamp": sampled_at.isoformat(),
            "value": round(float(value), 2),
        }
    )


def _build_series(metric_key: str, sampled_at: datetime, window_minutes: int) -> list[dict[str, Any]]:
    cutoff = sampled_at - timedelta(minutes=window_minutes)
    series = []
    for point in _HOST_HISTORY[metric_key]:
        timestamp = datetime.fromisoformat(point["timestamp"])
        if timestamp >= cutoff:
            series.append(point)
    return series


def _build_host_metric(
    *,
    metric_key: str,
    label: str,
    current_value: float,
    sampled_at: datetime,
    window_minutes: int,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    threshold = _HOST_THRESHOLDS[metric_key]
    status = _status_for_threshold(current_value, threshold["warning"], threshold["critical"])
    _append_history(metric_key, sampled_at, current_value)
    return {
        "metric_key": metric_key,
        "label": label,
        "unit": threshold["unit"],
        "current_value": round(float(current_value), 2),
        "status": status,
        "warning_threshold": threshold["warning"],
        "critical_threshold": threshold["critical"],
        "series": _build_series(metric_key, sampled_at, window_minutes),
        "meta": meta or {},
    }


def _sample_backend_process(sampled_at: str) -> dict[str, Any]:
    return _serialize_process_snapshot(
        process_key="mystocks-backend",
        display_name="mystocks-backend",
        process=psutil.Process(os.getpid()),
        sampled_at=sampled_at,
    )


def _find_frontend_process() -> psutil.Process | None:
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            info = process.info
            cmdline = " ".join(info.get("cmdline") or [])
            name = (info.get("name") or "").lower()
            haystack = f"{name} {cmdline}".lower()
            if "mystocks-frontend" in haystack or "web/frontend" in haystack or "vite" in haystack:
                return process
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    return None


def _serialize_process_snapshot(
    *,
    process_key: str,
    display_name: str,
    process: psutil.Process | None,
    sampled_at: str,
) -> dict[str, Any]:
    if process is None:
        return {
            "process_key": process_key,
            "display_name": display_name,
            "status": "critical",
            "pid": None,
            "cpu_percent": None,
            "memory_mb": None,
            "memory_percent": None,
            "sampled_at": sampled_at,
            "started_at": None,
            "thresholds": _PROCESS_THRESHOLDS,
            "summary": "process not detected",
        }

    cpu_percent = round(float(process.cpu_percent(interval=None)), 2)
    memory_percent = round(float(process.memory_percent()), 2)
    memory_mb = round(float(process.memory_info().rss) / 1024**2, 2)
    cpu_status = _status_for_threshold(
        cpu_percent,
        _PROCESS_THRESHOLDS["cpu_percent"]["warning"],
        _PROCESS_THRESHOLDS["cpu_percent"]["critical"],
    )
    memory_status = _status_for_threshold(
        memory_percent,
        _PROCESS_THRESHOLDS["memory_percent"]["warning"],
        _PROCESS_THRESHOLDS["memory_percent"]["critical"],
    )
    started_at = datetime.fromtimestamp(process.create_time(), timezone.utc).isoformat()
    return {
        "process_key": process_key,
        "display_name": display_name,
        "status": _max_status(cpu_status, memory_status),
        "pid": process.pid,
        "cpu_percent": cpu_percent,
        "memory_mb": memory_mb,
        "memory_percent": memory_percent,
        "sampled_at": sampled_at,
        "started_at": started_at,
        "thresholds": _PROCESS_THRESHOLDS,
        "summary": f"cpu={cpu_percent}% memory={memory_percent}%",
    }


def _sample_processes(sampled_at: str) -> list[dict[str, Any]]:
    return [
        _sample_backend_process(sampled_at),
        _serialize_process_snapshot(
            process_key="mystocks-frontend",
            display_name="mystocks-frontend",
            process=_find_frontend_process(),
            sampled_at=sampled_at,
        ),
    ]


def _map_dependency_status(raw_status: str, usage_percentage: float | None) -> str:
    raw = raw_status.lower()
    base_status = "critical"
    if raw in {"healthy", "up", "ready", "available"}:
        base_status = "normal"
    elif raw in {"degraded", "not_initialized", "unknown"}:
        base_status = "warning"
    if usage_percentage is None:
        return base_status
    usage_status = _status_for_threshold(
        usage_percentage,
        _DEPENDENCY_USAGE_THRESHOLDS["warning"],
        _DEPENDENCY_USAGE_THRESHOLDS["critical"],
    )
    return _max_status(base_status, usage_status)


def _serialize_pool_dependency(
    *,
    dependency_key: str,
    display_name: str,
    payload: dict[str, Any],
    sampled_at: str,
) -> dict[str, Any]:
    details = payload.get("details", {})
    usage_percentage = details.get("usage_percentage")
    usage_value = round(float(usage_percentage), 2) if usage_percentage is not None else None
    return {
        "dependency_key": dependency_key,
        "display_name": display_name,
        "status": _map_dependency_status(payload.get("status", "unknown"), usage_value),
        "summary": payload.get("error") or payload.get("status", "unknown"),
        "sampled_at": sampled_at,
        "warning_threshold": _DEPENDENCY_USAGE_THRESHOLDS["warning"] if usage_value is not None else None,
        "critical_threshold": _DEPENDENCY_USAGE_THRESHOLDS["critical"] if usage_value is not None else None,
        "metrics": {
            "active_connections": details.get("active_connections"),
            "idle_connections": details.get("idle_connections"),
            "usage_percentage": usage_value,
            "error_rate": details.get("error_rate"),
        },
    }


def _sample_redis_dependency(sampled_at: str) -> dict[str, Any]:
    try:
        from app.core.redis_client import get_redis_client

        client = get_redis_client()
        client.ping()
        info = client.info()
        used_memory = float(info.get("used_memory", 0))
        max_memory = float(info.get("maxmemory", 0))
        usage_percentage = round((used_memory / max_memory) * 100, 2) if max_memory > 0 else None
        return {
            "dependency_key": "redis",
            "display_name": "Redis",
            "status": _map_dependency_status("healthy", usage_percentage),
            "summary": "redis reachable",
            "sampled_at": sampled_at,
            "warning_threshold": _DEPENDENCY_USAGE_THRESHOLDS["warning"] if usage_percentage is not None else None,
            "critical_threshold": _DEPENDENCY_USAGE_THRESHOLDS["critical"] if usage_percentage is not None else None,
            "metrics": {
                "connected_clients": info.get("connected_clients"),
                "used_memory_mb": round(used_memory / 1024**2, 2),
                "usage_percentage": usage_percentage,
            },
        }
    except Exception as exc:  # pragma: no cover - runtime variability
        return {
            "dependency_key": "redis",
            "display_name": "Redis",
            "status": "critical",
            "summary": str(exc),
            "sampled_at": sampled_at,
            "warning_threshold": None,
            "critical_threshold": None,
            "metrics": {},
        }


async def _sample_dependencies(sampled_at: str) -> list[dict[str, Any]]:
    pool_health = await connection_pools_health_check()
    return [
        _serialize_pool_dependency(
            dependency_key="postgresql",
            display_name="PostgreSQL",
            payload=pool_health.get("postgresql", {}),
            sampled_at=sampled_at,
        ),
        _serialize_pool_dependency(
            dependency_key="tdengine",
            display_name="TDengine",
            payload=pool_health.get("tdengine", {}),
            sampled_at=sampled_at,
        ),
        _sample_redis_dependency(sampled_at),
    ]


async def collect_resource_metrics(
    *,
    window_minutes: int,
    include_processes: bool,
    include_dependencies: bool,
) -> dict[str, Any]:
    sampled_at = datetime.now(timezone.utc)
    sampled_at_iso = sampled_at.isoformat()

    cpu_percent = round(float(psutil.cpu_percent(interval=None)), 2)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    load_average = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
    cpu_count = max(os.cpu_count() or 1, 1)
    load_percent = round(float(load_average / cpu_count) * 100, 2)

    host = {
        "cpu": _build_host_metric(
            metric_key="cpu_percent",
            label="CPU",
            current_value=cpu_percent,
            sampled_at=sampled_at,
            window_minutes=window_minutes,
            meta={"cpu_count": cpu_count},
        ),
        "memory": _build_host_metric(
            metric_key="memory_percent",
            label="内存",
            current_value=round(float(memory.percent), 2),
            sampled_at=sampled_at,
            window_minutes=window_minutes,
            meta={"used_gb": _to_gb(memory.used), "total_gb": _to_gb(memory.total)},
        ),
        "disk": _build_host_metric(
            metric_key="disk_percent",
            label="磁盘",
            current_value=round(float(disk.percent), 2),
            sampled_at=sampled_at,
            window_minutes=window_minutes,
            meta={"used_gb": _to_gb(disk.used), "total_gb": _to_gb(disk.total)},
        ),
        "load": _build_host_metric(
            metric_key="load_percent",
            label="负载",
            current_value=load_percent,
            sampled_at=sampled_at,
            window_minutes=window_minutes,
            meta={"load_average_1m": round(float(load_average), 2), "cpu_count": cpu_count},
        ),
    }

    processes = _sample_processes(sampled_at_iso) if include_processes else []
    dependencies = await _sample_dependencies(sampled_at_iso) if include_dependencies else []
    overall_status = _max_status(
        *(metric["status"] for metric in host.values()),
        *(entry["status"] for entry in processes),
        *(entry["status"] for entry in dependencies),
    )

    return {
        "node": {
            "node_id": socket.gethostname(),
            "scope": "single-node",
            "sampled_at": sampled_at_iso,
            "window_minutes": window_minutes,
            "polling_interval_seconds": POLL_INTERVAL_SECONDS,
            "overall_status": overall_status,
        },
        "host": host,
        "processes": processes,
        "dependencies": dependencies,
        "thresholds": {
            f"host.{metric_key}": threshold
            for metric_key, threshold in _HOST_THRESHOLDS.items()
        },
    }
