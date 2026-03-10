from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text

from app.core.database import get_postgresql_engine


def check_postgresql_readiness() -> dict[str, Any]:
    """检查 PostgreSQL 就绪状态。"""
    start_time = time.perf_counter()

    try:
        engine = get_postgresql_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "detail": "PostgreSQL connection verified",
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }
    except Exception as exc:
        return {
            "status": "error",
            "detail": f"PostgreSQL readiness check failed: {exc}",
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }


def check_redis_readiness() -> dict[str, Any]:
    """检查 Redis 就绪状态。"""
    start_time = time.perf_counter()

    try:
        from app.core.redis_client import redis_manager

        if redis_manager.health_check():
            return {
                "status": "ready",
                "detail": "Redis ping verified",
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            }

        return {
            "status": "error",
            "detail": "Redis health check returned unavailable",
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }
    except Exception as exc:
        return {
            "status": "error",
            "detail": f"Redis readiness check failed: {exc}",
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }


def collect_readiness_checks() -> tuple[bool, dict[str, dict[str, Any]]]:
    """收集就绪探针检查结果。"""
    checks = {
        "postgresql": check_postgresql_readiness(),
        "redis": check_redis_readiness(),
    }
    ready = all(item["status"] == "ready" for item in checks.values())
    return ready, checks

