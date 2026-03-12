from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text

from app.core.database import get_postgresql_engine
from app.core.config import settings


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
            "required": True,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }
    except Exception as exc:
        return {
            "status": "error",
            "detail": f"PostgreSQL readiness check failed: {exc}",
            "required": True,
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
                "required": True,
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            }

        return {
            "status": "error",
            "detail": "Redis health check returned unavailable",
            "required": True,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }
    except Exception as exc:
        return {
            "status": "error",
            "detail": f"Redis readiness check failed: {exc}",
            "required": True,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }


def check_mongodb_readiness() -> dict[str, Any]:
    """检查 MongoDB 运行时状态（默认可见但不阻塞就绪探针）。"""
    start_time = time.perf_counter()

    host = getattr(settings, "mongodb_runtime_host", "localhost")
    port = getattr(settings, "mongodb_runtime_port", 27017)
    username = getattr(settings, "mongodb_root_username", "") or None
    password = getattr(settings, "mongodb_root_password", "") or None
    auth_source = getattr(settings, "mongodb_auth_source", "admin")

    host_is_configured = bool(getattr(settings, "mongodb_host", "") or getattr(settings, "mongodb_ip", ""))
    credentials_are_configured = bool(username or password)

    if not host_is_configured and not credentials_are_configured:
        return {
            "status": "optional_unconfigured",
            "detail": "MongoDB runtime config not provided",
            "required": False,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }

    try:
        from pymongo import MongoClient

        client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            authSource=auth_source,
            serverSelectionTimeoutMS=5000,
        )
        client.admin.command({"ping": 1})
        client.close()

        return {
            "status": "ready",
            "detail": f"MongoDB ping verified ({host}:{port})",
            "required": False,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }
    except Exception as exc:
        return {
            "status": "optional_unavailable",
            "detail": f"MongoDB readiness check failed: {exc}",
            "required": False,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }


def collect_readiness_checks() -> tuple[bool, dict[str, dict[str, Any]]]:
    """收集就绪探针检查结果。"""
    checks = {
        "postgresql": check_postgresql_readiness(),
        "redis": check_redis_readiness(),
        "mongodb": check_mongodb_readiness(),
    }
    ready = all(item["status"] == "ready" for item in checks.values() if item.get("required", True))
    return ready, checks
