"""
系统管理API端点
提供系统设置、数据库连接测试、运行日志查询等功能
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psycopg2
from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.system._logs_summary_helper import build_logs_summary_payload
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def _is_system_health_mock_enabled() -> bool:
    return settings.use_mock_apis

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


def _required_env(env_name: str) -> str:
    value = os.getenv(env_name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {env_name}")
    return value


def _close_resource_quietly(resource_name: str, resource: Any) -> None:
    if resource is None:
        return

    try:
        resource.close()
    except Exception as exc:
        logger.debug("Failed to close %s cleanly: %s", resource_name, exc)


@router.get("/health", responses=SYSTEM_HEALTH_RESPONSES)
async def system_health():
    """
    系统健康检查端点 (双数据库架构: TDengine + PostgreSQL)

    返回:
    - 数据库连接状态
    - 系统运行时间
    - 服务状态
    """
    if _is_system_health_mock_enabled():
        # Mock数据：返回模拟健康状态
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "databases": {"postgresql": "healthy", "tdengine": "healthy"},
            "service": "mystocks-web-api",
            "version": "2.2.0",
            "mock_mode": True,
            "architecture": "dual-database",
            "uptime": "2天 14小时 23分钟",
        }

    try:
        from app.core.database import db_service

        # 检查数据库连接 (仅 PostgreSQL 和 TDengine)
        db_status = {
            "postgresql": "unknown",
            "tdengine": "unknown",
        }

        # 简单检查 - 尝试查询
        try:
            db_service.query_stocks_basic(limit=1)
            db_status["postgresql"] = "healthy"
        except Exception as exc:
            logger.debug("PostgreSQL health probe degraded: %s", exc)

        # TDengine 目前仍走轻量占位探针，避免可选驱动在健康检查阶段放大失败面。
        try:
            db_status["tdengine"] = "healthy"
        except Exception as exc:
            logger.debug("TDengine health probe degraded: %s", exc)

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "databases": db_status,
            "service": "mystocks-web-api",
            "version": "2.2.0",
            "architecture": "dual-database",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"系统健康检查失败: {str(e)}")


@router.get("/adapters/health", responses=SYSTEM_ADAPTER_HEALTH_RESPONSES)
async def get_adapters_health():
    """
    🚀 适配器健康检查端点（新增）

    检查所有数据适配器的健康状态：
    - akshare: AkShare适配器
    - tdx: 通达信适配器
    - financial: 财务数据适配器

    返回:
    - 每个适配器的健康状态
    - 最后检查时间
    - 错误信息（如果有）

    用于监控和自动降级
    """
    try:
        from datetime import datetime

        from app.core.adapter_loader import check_all_adapters, get_adapter_health_status

        # 执行健康检查
        health_results = check_all_adapters()

        # 获取详细状态
        detailed_status = {}
        for adapter_name, is_healthy in health_results.items():
            status_info = get_adapter_health_status(adapter_name)
            detailed_status[adapter_name] = {
                "healthy": is_healthy,
                "status": status_info.get("status", "unknown"),
                "error": status_info.get("error"),
                "last_check": datetime.now().isoformat(),
            }

        # 计算总体健康度
        total_adapters = len(health_results)
        healthy_adapters = sum(1 for h in health_results.values() if h)
        overall_healthy = healthy_adapters == total_adapters

        return {
            "overall_status": "healthy" if overall_healthy else "degraded",
            "healthy_count": healthy_adapters,
            "total_count": total_adapters,
            "adapters": detailed_status,
            "timestamp": datetime.now().isoformat(),
            "message": f"{healthy_adapters}/{total_adapters} 适配器正常运行",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"适配器健康检查失败: {str(e)}")


@router.get("/datasources", responses=SYSTEM_DATASOURCES_RESPONSES)
async def get_datasources():
    """
    获取已配置的数据源列表

    返回所有可用的数据源配置信息
    """
    datasources = [
        {
            "id": "tdx",
            "name": "通达信(TDX)",
            "type": "realtime",
            "status": "active",
            "description": "实时行情和多周期K线数据",
            "features": ["实时行情", "分钟K线", "日K线"],
        },
        {
            "id": "akshare",
            "name": "AkShare",
            "type": "historical",
            "status": "active",
            "description": "历史数据和财务数据",
            "features": ["历史行情", "财务报表", "宏观数据"],
        },
        {
            "id": "financial",
            "name": "Financial Adapter",
            "type": "comprehensive",
            "status": "active",
            "description": "综合财务数据适配器",
            "features": ["实时行情", "财务数据", "指数数据"],
        },
        {
            "id": "baostock",
            "name": "BaoStock",
            "type": "historical",
            "status": "available",
            "description": "历史数据备用数据源",
            "features": ["历史行情", "复权数据"],
        },
    ]

    return {
        "success": True,
        "data": datasources,
        "total": len(datasources),
        "timestamp": datetime.now().isoformat(),
    }


class ConnectionTestRequest(BaseModel):
    """数据库连接测试请求"""

    db_type: str = Field(..., description="待测试的数据库类型，例如 postgresql 或 tdengine。")
    host: str = Field(..., description="数据库服务主机地址。")
    port: int = Field(..., description="数据库服务端口。")


class ConnectionTestResponse(BaseModel):
    """数据库连接测试响应"""

    success: bool = Field(..., description="连接测试是否成功。")
    message: Optional[str] = Field(None, description="连接测试结果说明。")
    error: Optional[str] = Field(None, description="连接失败时的错误详情。")


@router.post(
    "/test-connection",
    response_model=ConnectionTestResponse,
    responses=SYSTEM_CONNECTION_TEST_RESPONSES,
)
async def test_database_connection(
    request: ConnectionTestRequest = Body(..., openapi_examples=CONNECTION_TEST_REQUEST_EXAMPLES),
):
    """
    测试数据库连接 (双数据库架构)

    支持的数据库类型:
    - postgresql: PostgreSQL (主数据库)
    - tdengine: TDengine (时序数据库)
    """
    db_type = request.db_type.lower()
    host = request.host
    port = request.port

    try:
        pg_user = os.getenv("POSTGRESQL_USER", "postgres")
        pg_password = _required_env("POSTGRESQL_PASSWORD")
        td_user = os.getenv("TDENGINE_USER", "root")
        td_password = _required_env("TDENGINE_PASSWORD")

        if db_type == "postgresql":
            # 测试 PostgreSQL 连接 - 连接到默认的 postgres 数据库
            connection = None
            cursor = None
            try:
                connection = psycopg2.connect(
                    host=host,
                    port=port,
                    user=pg_user,
                    password=pg_password,
                    database="postgres",  # 连接到默认数据库
                    connect_timeout=5,
                )
                # 执行简单查询测试
                cursor = connection.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0].split(",")[0]

                # 检查是否存在 mystocks 相关数据库
                cursor.execute("SELECT datname FROM pg_database WHERE datname LIKE 'mystocks%'")
                databases = cursor.fetchall()
                db_list = [db[0] for db in databases] if databases else []

                if db_list:
                    return ConnectionTestResponse(
                        success=True,
                        message=f"PostgreSQL 连接成功 ({version})，发现数据库: {', '.join(db_list)}",
                    )
                else:
                    return ConnectionTestResponse(
                        success=True,
                        message=f"PostgreSQL 连接成功 ({version})，但未发现 mystocks 相关数据库",
                    )
            except psycopg2.Error:
                raise
            finally:
                # 确保连接被关闭，防止连接泄漏
                _close_resource_quietly("PostgreSQL cursor", cursor)
                _close_resource_quietly("PostgreSQL connection", connection)

        elif db_type == "tdengine":
            # 测试 TDengine 连接
            connection = None
            cursor = None
            try:
                import taos

                connection = taos.connect(
                    host=host,
                    port=port,
                    user=td_user,
                    password=td_password,
                    config="/etc/taos",
                    timeout=5000,
                )
                # 执行简单查询测试
                cursor = connection.cursor()
                cursor.execute("SELECT SERVER_VERSION()")
                result = cursor.fetchone()
                version = result[0] if result and len(result) > 0 else "未知版本"

                # 检查是否存在 mystocks 相关数据库
                cursor.execute("SHOW DATABASES")
                databases = cursor.fetchall()
                db_list = [db[0] for db in databases if db and "mystocks" in db[0].lower()] if databases else []

                if db_list:
                    return ConnectionTestResponse(
                        success=True,
                        message=f"TDengine 连接成功 (版本: {version})，发现数据库: {', '.join(db_list)}",
                    )
                else:
                    return ConnectionTestResponse(
                        success=True,
                        message=f"TDengine 连接成功 (版本: {version})，但未发现 mystocks 相关数据库",
                    )
            except Exception as e:
                # TDengine 可能需要特殊处理
                error_msg = str(e)
                if "Unable to establish connection" in error_msg or "Connection refused" in error_msg:
                    return ConnectionTestResponse(
                        success=False,
                        error=f"无法连接到 TDengine 服务器 ({host}:{port})，请检查服务是否运行",
                    )
                raise
            finally:
                # 确保连接被关闭，防止连接泄漏
                _close_resource_quietly("TDengine cursor", cursor)
                _close_resource_quietly("TDengine connection", connection)

        else:
            return ConnectionTestResponse(
                success=False, error=f"不支持的数据库类型: {db_type}，仅支持 postgresql 和 tdengine"
            )

    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "could not connect to server" in error_msg:
            return ConnectionTestResponse(
                success=False,
                error=f"无法连接到 PostgreSQL 服务器 ({host}:{port})，请检查地址和端口是否正确",
            )
        elif "password authentication failed" in error_msg:
            return ConnectionTestResponse(success=False, error="PostgreSQL 认证失败，用户名或密码错误")
        else:
            return ConnectionTestResponse(success=False, error=f"PostgreSQL 连接错误: {error_msg}")

    except RuntimeError as e:
        return ConnectionTestResponse(success=False, error=str(e))

    except Exception as e:
        return ConnectionTestResponse(success=False, error=f"连接测试失败: {str(e)}")


class SystemLog(BaseModel):
    """系统日志模型"""

    id: int = Field(..., description="系统日志记录ID。")
    timestamp: str = Field(..., description="日志记录时间。")
    level: str = Field(..., description="日志级别，例如 INFO、WARNING、ERROR。")
    category: str = Field(..., description="日志分类，例如 database、api、adapter 或 system。")
    operation: str = Field(..., description="对应的操作名称。")
    message: str = Field(..., description="日志消息正文。")
    details: Optional[Dict[str, Any]] = Field(None, description="结构化日志上下文。")
    duration_ms: Optional[int] = Field(None, description="操作耗时，单位毫秒。")
    has_error: bool = Field(False, description="该日志是否代表错误或异常。")


class LogQueryResponse(BaseModel):
    """日志查询响应"""

    success: bool = Field(..., description="日志查询是否成功。")
    data: List[SystemLog] = Field(..., description="返回的系统日志列表。")
    total: int = Field(..., description="日志总记录数。")
    filtered: int = Field(..., description="按当前筛选条件命中的记录数。")
    timestamp: str = Field(..., description="本次查询响应时间。")


def get_system_logs_from_db(
    filter_errors: bool = False,
    limit: int = 100,
    offset: int = 0,
    level: Optional[str] = None,
    category: Optional[str] = None,
) -> List[SystemLog]:
    """
    从PostgreSQL监控数据库获取系统日志

    Args:
        filter_errors: 是否只返回有问题的日志 (WARNING, ERROR, CRITICAL)
        limit: 返回条数限制
        offset: 偏移量
        level: 日志级别筛选
        category: 日志分类筛选

    Returns:
        系统日志列表
    """
    conn = None
    cursor = None
    try:
        monitor_password = os.getenv("MONITOR_DB_PASSWORD") or os.getenv("POSTGRESQL_PASSWORD")
        if not monitor_password:
            raise RuntimeError("Missing MONITOR_DB_PASSWORD or POSTGRESQL_PASSWORD for log query")

        # 连接到PostgreSQL监控数据库
        conn = psycopg2.connect(
            host=os.getenv("MONITOR_DB_HOST", "localhost"),
            port=int(os.getenv("MONITOR_DB_PORT", "5432")),
            user=os.getenv("MONITOR_DB_USER", "postgres"),
            password=monitor_password,
            database=os.getenv("MONITOR_DB_NAME", "mystocks_monitoring"),
            connect_timeout=5,
        )
        cursor = conn.cursor()

        # 使用固定SQL模板 + 参数占位，避免动态拼接 WHERE 子句
        normalized_level = level.upper() if level else None

        query = """
            SELECT
                id,
                timestamp,
                COALESCE(status, 'INFO') as level,
                operation_type as category,
                operation as operation,
                COALESCE(error_message, message, '') as message,
                execution_time_ms as duration_ms,
                CASE WHEN status IN ('failed', 'error') THEN true ELSE false END as has_error
            FROM operation_log
            WHERE (%s = false OR level IN ('WARNING', 'ERROR', 'CRITICAL'))
              AND (%s IS NULL OR level = %s)
              AND (%s IS NULL OR category = %s)
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """

        query_params = [
            filter_errors,
            normalized_level,
            normalized_level,
            category,
            category,
            limit,
            offset,
        ]

        cursor.execute(query, query_params)
        rows = cursor.fetchall()

        # 转换为SystemLog对象
        logs = []
        for row in rows:
            log = SystemLog(
                id=row[0],
                timestamp=row[1].isoformat() if row[1] else datetime.now().isoformat(),
                level=row[2].upper() if row[2] else "INFO",
                category=row[3] or "system",
                operation=row[4] or "unknown",
                message=row[5] or "",
                details=None,
                duration_ms=row[6],
                has_error=row[7] if len(row) > 7 else False,
            )
            logs.append(log)

        # 获取总数
        count_query = """
            SELECT COUNT(*)
            FROM operation_log
            WHERE (%s = false OR level IN ('WARNING', 'ERROR', 'CRITICAL'))
              AND (%s IS NULL OR level = %s)
              AND (%s IS NULL OR category = %s)
        """
        count_params = [
            filter_errors,
            normalized_level,
            normalized_level,
            category,
            category,
        ]
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        return logs, total

    except Exception as e:
        logger.exception("Error fetching logs from database: %s", e)
        return [], 0
    finally:
        # 确保连接和游标被关闭，防止连接泄漏
        _close_resource_quietly("system logs cursor", cursor)
        _close_resource_quietly("system logs connection", conn)


def get_mock_system_logs(filter_errors: bool = False, limit: int = 100) -> List[SystemLog]:
    """
    生成模拟的系统日志（用于演示和数据库不可用时的备用）
    """
    mock_logs = []

    # 正常运行日志
    normal_logs = [
        SystemLog(
            id=1,
            timestamp=(datetime.now() - timedelta(minutes=5)).isoformat(),
            level="INFO",
            category="database",
            operation="数据库连接",
            message="MySQL数据库连接成功",
            details={"host": "localhost", "port": 3306},
            duration_ms=125,
            has_error=False,
        ),
        SystemLog(
            id=2,
            timestamp=(datetime.now() - timedelta(minutes=4)).isoformat(),
            level="INFO",
            category="api",
            operation="API请求",
            message="GET /api/market/quotes 请求成功",
            details={"status_code": 200, "response_time_ms": 245},
            duration_ms=245,
            has_error=False,
        ),
        SystemLog(
            id=3,
            timestamp=(datetime.now() - timedelta(minutes=3)).isoformat(),
            level="INFO",
            category="adapter",
            operation="数据获取",
            message="TDX适配器获取实时行情成功",
            details={"symbol": "000001", "records": 5},
            duration_ms=180,
            has_error=False,
        ),
        SystemLog(
            id=4,
            timestamp=(datetime.now() - timedelta(minutes=10)).isoformat(),
            level="INFO",
            category="system",
            operation="系统启动",
            message="MyStocks Backend服务启动成功",
            details={"version": "2.2.0", "port": os.getenv("BACKEND_PORT", "unknown")},
            duration_ms=0,
            has_error=False,
        ),
    ]

    # 有问题的日志
    error_logs = [
        SystemLog(
            id=5,
            timestamp=(datetime.now() - timedelta(minutes=2)).isoformat(),
            level="WARNING",
            category="database",
            operation="数据库查询",
            message="TDengine查询响应时间过长",
            details={"query": "SELECT * FROM stock_tick", "duration_ms": 3500},
            duration_ms=3500,
            has_error=True,
        ),
        SystemLog(
            id=6,
            timestamp=(datetime.now() - timedelta(minutes=1)).isoformat(),
            level="ERROR",
            category="adapter",
            operation="数据获取",
            message="AkShare适配器获取财务数据失败",
            details={"symbol": "600519", "error": "Connection timeout"},
            duration_ms=5000,
            has_error=True,
        ),
        SystemLog(
            id=7,
            timestamp=(datetime.now() - timedelta(seconds=30)).isoformat(),
            level="CRITICAL",
            category="database",
            operation="数据库连接",
            message="Redis连接失败",
            details={"host": "localhost", "port": 6379, "error": "Connection refused"},
            duration_ms=0,
            has_error=True,
        ),
        SystemLog(
            id=8,
            timestamp=(datetime.now() - timedelta(minutes=8)).isoformat(),
            level="WARNING",
            category="api",
            operation="API请求",
            message="API请求频率过高",
            details={"endpoint": "/api/market/quotes", "rate": "120 req/min"},
            duration_ms=0,
            has_error=True,
        ),
    ]

    if filter_errors:
        mock_logs = error_logs[:limit]
    else:
        # 混合正常日志和错误日志
        all_logs = normal_logs + error_logs
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        mock_logs = all_logs[:limit]

    return mock_logs


@router.get("/logs", response_model=LogQueryResponse, responses=SYSTEM_LOGS_RESPONSES)
async def get_system_logs(
    filter_errors: bool = Query(False, description="是否只显示有问题的日志"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    level: Optional[str] = Query(None, description="日志级别筛选 (INFO/WARNING/ERROR/CRITICAL)"),
    category: Optional[str] = Query(None, description="日志分类筛选 (database/api/adapter/system)"),
):
    """
    获取系统运行日志

    参数:
    - filter_errors: 是否只显示有问题的日志 (WARNING/ERROR/CRITICAL)
    - limit: 返回条数限制 (1-1000)
    - offset: 偏移量，用于分页
    - level: 日志级别筛选
    - category: 日志分类筛选

    返回:
    - 系统运行日志列表，包含时间戳、级别、分类、操作、消息等信息

    示例:
    - GET /api/system/logs - 获取所有日志
    - GET /api/system/logs?filter_errors=true - 只获取有问题的日志
    - GET /api/system/logs?level=ERROR - 只获取ERROR级别日志
    - GET /api/system/logs?category=database - 只获取数据库相关日志
    """
    try:
        # 首先尝试从数据库获取
        logs, total = get_system_logs_from_db(
            filter_errors=filter_errors,
            limit=limit,
            offset=offset,
            level=level,
            category=category,
        )

        return LogQueryResponse(
            success=True,
            data=logs,
            total=total,
            filtered=len(logs),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统日志失败: {str(e)}")


@router.get("/logs/summary", responses=SYSTEM_LOG_SUMMARY_RESPONSES)
async def get_logs_summary():
    """
    获取日志统计摘要

    返回:
    - 总日志数
    - 各级别日志数量
    - 各分类日志数量
    - 最近错误数
    """
    try:
        logs, total = get_system_logs_from_db(limit=1000)

        return build_logs_summary_payload(logs, total)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")
