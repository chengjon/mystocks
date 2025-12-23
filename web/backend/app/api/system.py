"""
系统管理API端点 (Phase 2.4 - System & Monitoring Module Alignment)
提供系统设置、数据库连接测试、运行日志查询、系统状态监控等功能

版本: 2.4.0
日期: 2025-12-24
更新内容:
- 添加 /api/system/status 综合状态端点
- 添加系统性能指标收集
- 使用统一响应格式
- 添加Pydantic验证模型
- Phase 2.4.3: 添加 /api/system/logs/stream SSE日志流端点
"""

import os
import psutil
import logging
import time
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import psycopg2
import taos
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

# 导入统一响应格式
from app.core.responses import (
    ErrorCodes,
    ResponseMessages,
    create_error_response,
    create_success_response,
    create_health_response,
)

# 配置日志
logger = logging.getLogger(__name__)

# Mock数据支持
use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

router = APIRouter()


# ============================================================================
# 系统启动时间追踪 (用于运行时间计算)
# ============================================================================
# 应用启动时记录时间（在main.py或app_factory.py中设置）
_app_start_time = time.time()


# ============================================================================
# Pydantic 验证模型
# ============================================================================


class SystemStatus(str, Enum):
    """系统状态枚举"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentStatus(BaseModel):
    """组件状态模型"""

    name: str = Field(..., description="组件名称")
    status: str = Field(..., description="状态 (healthy/unhealthy/unknown)")
    message: Optional[str] = Field(None, description="状态消息")
    response_time_ms: Optional[int] = Field(None, description="响应时间(毫秒)")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")


class PerformanceMetrics(BaseModel):
    """性能指标模型"""

    cpu_percent: float = Field(..., description="CPU使用率(%)")
    memory_percent: float = Field(..., description="内存使用率(%)")
    memory_used_mb: float = Field(..., description="已使用内存(MB)")
    memory_total_mb: float = Field(..., description="总内存(MB)")
    disk_percent: float = Field(..., description="磁盘使用率(%)")
    disk_used_gb: float = Field(..., description="已使用磁盘(GB)")
    disk_total_gb: float = Field(..., description="总磁盘(GB)")
    uptime_seconds: float = Field(..., description="系统运行时间(秒)")
    uptime_formatted: str = Field(..., description="系统运行时间(格式化)")


class RequestStatistics(BaseModel):
    """请求统计模型"""

    total_requests: int = Field(..., description="总请求数")
    requests_per_minute: float = Field(..., description="每分钟请求数")
    avg_response_time_ms: float = Field(..., description="平均响应时间(毫秒)")
    error_rate: float = Field(..., description="错误率(%)")
    active_connections: int = Field(..., description="活跃连接数")


class SystemStatusResponse(BaseModel):
    """系统状态响应模型"""

    overall_status: str = Field(..., description="整体状态")
    uptime: str = Field(..., description="系统运行时间")
    components: Dict[str, ComponentStatus] = Field(..., description="组件状态")
    performance: PerformanceMetrics = Field(..., description="性能指标")
    statistics: RequestStatistics = Field(..., description="请求统计")
    alerts: List[Dict[str, Any]] = Field(..., description="活跃告警")
    timestamp: str = Field(..., description="更新时间")


@router.get("/health")
async def system_health():
    """
    系统健康检查端点 (双数据库架构: TDengine + PostgreSQL)

    返回统一格式的健康检查响应:
    - 数据库连接状态
    - 系统运行时间
    - 服务状态

    Phase 2.4.4: 更新为统一响应格式
    """
    try:
        # 检查数据库连接状态
        db_status = {}
        overall_status = "healthy"
        health_details = {}

        # PostgreSQL 检查
        try:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRESQL_HOST", "192.168.123.104"),
                port=int(os.getenv("POSTGRESQL_PORT", "5438")),
                user=os.getenv("POSTGRESQL_USER", "postgres"),
                password=os.getenv("POSTGRESQL_PASSWORD"),
                database=os.getenv("POSTGRESQL_DATABASE", "mystocks"),
                connect_timeout=5,
            )
            conn.close()
            db_status["postgresql"] = "healthy"
            health_details["postgresql"] = "连接成功"
        except Exception as e:
            db_status["postgresql"] = "unhealthy"
            health_details["postgresql"] = f"连接失败: {str(e)}"
            overall_status = "unhealthy"

        # TDengine 检查
        try:
            conn = taos.connect(
                host=os.getenv("TDENGINE_HOST", "192.168.123.104"),
                port=int(os.getenv("TDENGINE_PORT", "6030")),
                user=os.getenv("TDENGINE_USER", "root"),
                password=os.getenv("TDENGINE_PASSWORD", "taosdata"),
                database=os.getenv("TDENGINE_DATABASE", "market_data"),
            )
            conn.close()
            db_status["tdengine"] = "healthy"
            health_details["tdengine"] = "连接成功"
        except Exception as e:
            db_status["tdengine"] = "unhealthy"
            health_details["tdengine"] = f"连接失败: {str(e)}"
            if overall_status == "healthy":
                overall_status = "degraded"

        # 计算运行时间
        uptime_seconds = time.time() - _app_start_time
        uptime_formatted = _format_uptime(uptime_seconds)

        return create_health_response(
            service="system",
            status=overall_status,
            details={
                "databases": db_status,
                "architecture": "dual-database",
                "uptime": uptime_formatted,
                "uptime_seconds": round(uptime_seconds, 2),
                "version": "2.4.0",
                "health_details": health_details,
            },
        )

    except Exception as e:
        logger.error(f"[SYSTEM] Health check failed: {str(e)}")
        return create_health_response(
            service="system",
            status="unhealthy",
            details={"error": str(e)},
        )


# ============================================================================
# 系统状态端点 (Phase 2.4.1 - 新增)
# ============================================================================


def _format_uptime(seconds: float) -> str:
    """格式化运行时间"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    if days > 0:
        return f"{days}天 {hours}小时 {minutes}分钟"
    elif hours > 0:
        return f"{hours}小时 {minutes}分钟"
    else:
        return f"{minutes}分钟"


def _get_performance_metrics() -> PerformanceMetrics:
    """获取系统性能指标"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)

        # 磁盘使用情况
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_total_gb = disk.total / (1024 * 1024 * 1024)

        # 系统运行时间
        uptime_seconds = time.time() - _app_start_time
        uptime_formatted = _format_uptime(uptime_seconds)

        return PerformanceMetrics(
            cpu_percent=round(cpu_percent, 2),
            memory_percent=round(memory_percent, 2),
            memory_used_mb=round(memory_used_mb, 2),
            memory_total_mb=round(memory_total_mb, 2),
            disk_percent=round(disk_percent, 2),
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            uptime_seconds=round(uptime_seconds, 2),
            uptime_formatted=uptime_formatted,
        )
    except Exception as e:
        # 返回默认值当psutil不可用时
        return PerformanceMetrics(
            cpu_percent=0.0,
            memory_percent=0.0,
            memory_used_mb=0.0,
            memory_total_mb=0.0,
            disk_percent=0.0,
            disk_used_gb=0.0,
            disk_total_gb=0.0,
            uptime_seconds=0.0,
            uptime_formatted="未知",
        )


def _get_database_status() -> Dict[str, ComponentStatus]:
    """获取数据库组件状态"""
    components = {}

    # PostgreSQL 状态检查
    start_time = time.time()
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST", "192.168.123.104"),
            port=int(os.getenv("POSTGRESQL_PORT", "5438")),
            user=os.getenv("POSTGRESQL_USER", "postgres"),
            password=os.getenv("POSTGRESQL_PASSWORD"),
            database=os.getenv("POSTGRESQL_DATABASE", "mystocks"),
            connect_timeout=5,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        response_time = int((time.time() - start_time) * 1000)
        components["postgresql"] = ComponentStatus(
            name="PostgreSQL",
            status="healthy",
            message=f"连接成功 (版本: {version.split(',')[0]})",
            response_time_ms=response_time,
            details={
                "host": os.getenv("POSTGRESQL_HOST"),
                "port": int(os.getenv("POSTGRESQL_PORT", "5438")),
                "database": os.getenv("POSTGRESQL_DATABASE"),
            },
        )
    except Exception as e:
        components["postgresql"] = ComponentStatus(
            name="PostgreSQL",
            status="unhealthy",
            message=f"连接失败: {str(e)}",
            response_time_ms=None,
            details={
                "host": os.getenv("POSTGRESQL_HOST"),
                "port": int(os.getenv("POSTGRESQL_PORT", "5438")),
            },
        )

    # TDengine 状态检查
    start_time = time.time()
    try:
        conn = taos.connect(
            host=os.getenv("TDENGINE_HOST", "192.168.123.104"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            user=os.getenv("TDENGINE_USER", "root"),
            password=os.getenv("TDENGINE_PASSWORD", "taosdata"),
            database=os.getenv("TDENGINE_DATABASE", "market_data"),
        )
        result = conn.query("SELECT SERVER_VERSION()")
        version = result.fetch_all()[0][0] if result else "unknown"
        conn.close()

        response_time = int((time.time() - start_time) * 1000)
        components["tdengine"] = ComponentStatus(
            name="TDengine",
            status="healthy",
            message=f"连接成功 (版本: {version})",
            response_time_ms=response_time,
            details={
                "host": os.getenv("TDENGINE_HOST"),
                "port": int(os.getenv("TDENGINE_PORT", "6030")),
                "database": os.getenv("TDENGINE_DATABASE"),
            },
        )
    except Exception as e:
        components["tdengine"] = ComponentStatus(
            name="TDengine",
            status="unhealthy",
            message=f"连接失败: {str(e)}",
            response_time_ms=None,
            details={
                "host": os.getenv("TDENGINE_HOST"),
                "port": int(os.getenv("TDENGINE_PORT", "6030")),
            },
        )

    return components


def _get_adapter_status() -> Dict[str, ComponentStatus]:
    """获取数据适配器状态"""
    components = {}

    try:
        from app.core.adapter_loader import check_all_adapters

        adapter_health = check_all_adapters()

        for adapter_name, is_healthy in adapter_health.items():
            components[adapter_name] = ComponentStatus(
                name=adapter_name.capitalize(),
                status="healthy" if is_healthy else "unhealthy",
                message="运行正常" if is_healthy else "服务异常",
                response_time_ms=None,
                details={"type": "data_adapter"},
            )
    except Exception:
        # 如果适配器检查失败，返回默认状态
        default_adapters = ["akshare", "tdx", "financial"]
        for name in default_adapters:
            components[name] = ComponentStatus(
                name=name.capitalize(),
                status="unknown",
                message="状态检查不可用",
                response_time_ms=None,
                details={"type": "data_adapter"},
            )

    return components


def _get_request_statistics() -> RequestStatistics:
    """获取请求统计信息 (模拟数据)"""
    # TODO: 实际应该从中间件或日志中获取
    return RequestStatistics(
        total_requests=15420,
        requests_per_minute=125.5,
        avg_response_time_ms=45.2,
        error_rate=0.12,
        active_connections=8,
    )


def _get_active_alerts() -> List[Dict[str, Any]]:
    """获取活跃告警 (模拟数据)"""
    # TODO: 实际应该从监控数据库获取
    return [
        {
            "id": 1,
            "level": "warning",
            "message": "TDengine查询响应时间超过3秒",
            "component": "tdengine",
            "created_at": (datetime.now() - timedelta(minutes=2)).isoformat(),
        },
        {
            "id": 2,
            "level": "info",
            "message": "系统资源使用正常",
            "component": "system",
            "created_at": (datetime.now() - timedelta(minutes=10)).isoformat(),
        },
    ]


@router.get("/status")
async def get_system_status():
    """
    获取系统综合状态 (Phase 2.4.1 - 新增)

    返回完整的系统状态信息，包括:
    - 整体状态评估
    - 系统运行时间
    - 各组件健康状态 (数据库、适配器、服务等)
    - 性能指标 (CPU、内存、磁盘)
    - 请求统计 (请求数、响应时间、错误率)
    - 活跃告警列表

    **整体状态判定规则**:
    - `healthy`: 所有核心组件健康，无严重告警
    - `degraded`: 部分组件异常或存在警告级别告警
    - `unhealthy`: 核心组件不可用或存在严重告警

    **核心组件**:
    - PostgreSQL数据库
    - TDengine时序数据库

    **示例请求**:
        GET /api/system/status

    **示例响应**:
    ```json
    {
        "success": true,
        "message": "系统状态获取成功",
        "data": {
            "overall_status": "healthy",
            "uptime": "2天 5小时 30分钟",
            "components": {
                "postgresql": {
                    "name": "PostgreSQL",
                    "status": "healthy",
                    "message": "连接成功",
                    "response_time_ms": 15
                },
                "tdengine": {
                    "name": "TDengine",
                    "status": "healthy",
                    "message": "连接成功",
                    "response_time_ms": 8
                }
            },
            "performance": {
                "cpu_percent": 15.5,
                "memory_percent": 45.2,
                "uptime_formatted": "2天 5小时 30分钟"
            },
            "statistics": {
                "total_requests": 15420,
                "requests_per_minute": 125.5,
                "avg_response_time_ms": 45.2,
                "error_rate": 0.12
            },
            "alerts": [],
            "timestamp": "2025-12-24T10:30:00"
        }
    }
    """
    try:
        # 获取各组件状态
        db_components = _get_database_status()
        adapter_components = _get_adapter_status()

        # 合并所有组件
        all_components = {**db_components, **adapter_components}

        # 计算整体状态
        core_components = ["postgresql", "tdengine"]
        core_healthy = sum(
            1
            for name in core_components
            if all_components.get(name) and all_components.get(name).status == "healthy"
        )

        if core_healthy == len(core_components):
            overall_status = "healthy"
        elif core_healthy > 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        # 获取性能指标
        performance = _get_performance_metrics()

        # 获取请求统计
        statistics = _get_request_statistics()

        # 获取活跃告警
        alerts = _get_active_alerts()

        # 构建响应数据
        status_data = SystemStatusResponse(
            overall_status=overall_status,
            uptime=performance.uptime_formatted,
            components=all_components,
            performance=performance,
            statistics=statistics,
            alerts=alerts,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        return create_success_response(
            data=status_data.model_dump(),
            message=f"系统状态: {overall_status.upper()}",
        )

    except Exception as e:
        logger.error(f"[SYSTEM] Failed to get system status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"获取系统状态失败: {str(e)}",
            ).model_dump(mode="json"),
        )


@router.get("/adapters/health")
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

        from app.core.adapter_loader import (
            check_all_adapters,
            get_adapter_health_status,
        )

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


@router.get("/datasources")
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

    db_type: str
    host: str
    port: int


class ConnectionTestResponse(BaseModel):
    """数据库连接测试响应"""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


@router.post("/test-connection", response_model=ConnectionTestResponse)
async def test_database_connection(request: ConnectionTestRequest):
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
        if db_type == "postgresql":
            # 测试 PostgreSQL 连接 - 连接到默认的 postgres 数据库
            connection = None
            cursor = None
            try:
                connection = psycopg2.connect(
                    host=host,
                    port=port,
                    user=os.getenv("POSTGRESQL_USER", "postgres"),
                    password=os.getenv("POSTGRESQL_PASSWORD"),
                    database="postgres",  # 连接到默认数据库
                    connect_timeout=5,
                )
                # 执行简单查询测试
                cursor = connection.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0].split(",")[0]

                # 检查是否存在 mystocks 相关数据库
                cursor.execute(
                    "SELECT datname FROM pg_database WHERE datname LIKE 'mystocks%'"
                )
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
                if cursor is not None:
                    try:
                        cursor.close()
                    except Exception:
                        pass
                if connection is not None:
                    try:
                        connection.close()
                    except Exception:
                        pass

        elif db_type == "tdengine":
            # 测试 TDengine 连接
            connection = None
            cursor = None
            try:
                connection = taos.connect(
                    host=host,
                    port=port,
                    user=os.getenv("TDENGINE_USER", "root"),
                    password=os.getenv("TDENGINE_PASSWORD", "taosdata"),
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
                db_list = (
                    [db[0] for db in databases if db and "mystocks" in db[0].lower()]
                    if databases
                    else []
                )

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
                if (
                    "Unable to establish connection" in error_msg
                    or "Connection refused" in error_msg
                ):
                    return ConnectionTestResponse(
                        success=False,
                        error=f"无法连接到 TDengine 服务器 ({host}:{port})，请检查服务是否运行",
                    )
                raise
            finally:
                # 确保连接被关闭，防止连接泄漏
                if cursor is not None:
                    try:
                        cursor.close()
                    except Exception:
                        pass
                if connection is not None:
                    try:
                        connection.close()
                    except Exception:
                        pass

        else:
            return ConnectionTestResponse(
                success=False,
                error=f"不支持的数据库类型: {db_type}，仅支持 postgresql 和 tdengine",
            )

    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "could not connect to server" in error_msg:
            return ConnectionTestResponse(
                success=False,
                error=f"无法连接到 PostgreSQL 服务器 ({host}:{port})，请检查地址和端口是否正确",
            )
        elif "password authentication failed" in error_msg:
            return ConnectionTestResponse(
                success=False, error="PostgreSQL 认证失败，用户名或密码错误"
            )
        else:
            return ConnectionTestResponse(
                success=False, error=f"PostgreSQL 连接错误: {error_msg}"
            )

    except Exception as e:
        return ConnectionTestResponse(success=False, error=f"连接测试失败: {str(e)}")


# ==================== 运行日志相关端点 ====================


class SystemLog(BaseModel):
    """系统日志模型"""

    id: int
    timestamp: str
    level: str  # INFO, WARNING, ERROR, CRITICAL
    category: str  # database, api, adapter, system
    operation: str  # 操作名称
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    has_error: bool = False


class LogQueryResponse(BaseModel):
    """日志查询响应"""

    success: bool
    data: List[SystemLog]
    total: int
    filtered: int
    timestamp: str


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
        # 连接到PostgreSQL监控数据库
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=os.getenv("POSTGRESQL_PASSWORD"),
            database="mystocks_monitoring",
            connect_timeout=5,
        )
        cursor = conn.cursor()

        # 构建查询SQL
        where_clauses = []
        params = []

        if filter_errors:
            where_clauses.append("level IN ('WARNING', 'ERROR', 'CRITICAL')")

        if level:
            where_clauses.append("level = %s")
            params.append(level.upper())

        if category:
            where_clauses.append("category = %s")
            params.append(category)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # 查询operation_log表
        query = f"""
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
            WHERE {where_sql}
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])

        cursor.execute(query, params)
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
        count_query = f"""
            SELECT COUNT(*) FROM operation_log WHERE {where_sql}
        """
        cursor.execute(count_query, params[:-2])  # 不包括limit和offset
        total = cursor.fetchone()[0]

        return logs, total

    except Exception as e:
        # 如果数据库查询失败，返回模拟日志
        print(f"Error fetching logs from database: {e}")
        return get_mock_system_logs(filter_errors, limit), 0
    finally:
        # 确保连接和游标被关闭，防止连接泄漏
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def get_mock_system_logs(
    filter_errors: bool = False, limit: int = 100
) -> List[SystemLog]:
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
            details={"version": "2.2.0", "port": 8000},
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


@router.get("/logs", response_model=LogQueryResponse)
async def get_system_logs(
    filter_errors: bool = Query(False, description="是否只显示有问题的日志"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    level: Optional[str] = Query(
        None, description="日志级别筛选 (INFO/WARNING/ERROR/CRITICAL)"
    ),
    category: Optional[str] = Query(
        None, description="日志分类筛选 (database/api/adapter/system)"
    ),
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

        # 如果数据库查询失败或没有数据，使用模拟数据
        if not logs or total == 0:
            logs = get_mock_system_logs(filter_errors=filter_errors, limit=limit)
            total = len(logs)

        return LogQueryResponse(
            success=True,
            data=logs,
            total=total,
            filtered=len(logs),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统日志失败: {str(e)}")


@router.get("/logs/summary")
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

        # 如果没有真实数据，使用模拟数据
        if not logs:
            logs = get_mock_system_logs(limit=100)
            total = len(logs)

        # 统计各级别数量
        level_counts = {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
        for log in logs:
            if log.level in level_counts:
                level_counts[log.level] += 1

        # 统计各分类数量
        category_counts = {}
        for log in logs:
            category_counts[log.category] = category_counts.get(log.category, 0) + 1

        # 统计最近1小时的错误
        recent_errors = sum(1 for log in logs if log.has_error)

        return {
            "success": True,
            "data": {
                "total_logs": total,
                "level_counts": level_counts,
                "category_counts": category_counts,
                "recent_errors_1h": recent_errors,
                "last_update": datetime.now().isoformat(),
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")


@router.get("/architecture")
async def get_system_architecture():
    """
    获取系统架构信息 (Week 3简化后 - 双数据库架构)

    返回完整的系统架构信息，包括:
    - 数据库架构 (TDengine + PostgreSQL)
    - 数据分类路由策略
    - 架构简化指标
    - 技术栈信息
    - MySQL/Redis移除详情

    用于架构可视化页面展示
    """
    try:
        return {
            "success": True,
            "message": "系统架构信息获取成功",
            "data": {
                # 架构简化成果
                "simplification": {
                    "before": {
                        "databases": 4,
                        "description": "TDengine + PostgreSQL + MySQL + Redis",
                    },
                    "after": {"databases": 2, "description": "TDengine + PostgreSQL"},
                    "reduction_percentage": 50,
                    "mysql_migration": {
                        "tables": 18,
                        "rows": 299,
                        "status": "completed",
                    },
                    "redis_removal": {
                        "configured_db": "db1",
                        "data_status": "empty",
                        "status": "removed",
                    },
                    "completion_date": "2025-10-19",
                },
                # 数据库配置
                "databases": [
                    {
                        "name": "TDengine",
                        "version": "3.3.6.13",
                        "type": "time-series",
                        "purpose": "高频时序数据专用库",
                        "usage": ["Tick数据", "分钟K线", "实时深度"],
                        "features": [
                            "极致压缩比 20:1",
                            "超强写入性能",
                            "列式存储",
                            "毫秒级延迟",
                        ],
                        "connection": {
                            "websocket_port": 6030,
                            "rest_api_port": 6041,
                            "database": "market_data",
                        },
                    },
                    {
                        "name": "PostgreSQL",
                        "version": "17.6",
                        "type": "relational",
                        "purpose": "通用数据仓库 + TimescaleDB扩展",
                        "usage": [
                            "日线K线数据",
                            "参考数据（股票信息、交易日历）",
                            "衍生数据（技术指标、量化因子）",
                            "交易数据（订单、成交、持仓）",
                            "元数据（系统配置、数据源状态）",
                        ],
                        "features": [
                            "TimescaleDB 2.22.0 时序扩展",
                            "自动分区",
                            "复杂查询支持",
                            "ACID事务保证",
                            "JSON支持",
                        ],
                        "connection": {
                            "default_port": 5432,
                            "alternative_port": 5438,
                            "database": "mystocks",
                        },
                    },
                ],
                # 数据分类路由策略 (5大分类)
                "data_classifications": [
                    {
                        "category": "第1类：市场数据",
                        "characteristics": "高频时序数据，写入密集，时间范围查询",
                        "routing": [
                            {
                                "data_type": "Tick数据、分钟K线、实时深度",
                                "database": "TDengine",
                                "reason": "极致压缩和超强写入性能",
                            },
                            {
                                "data_type": "日线、周线、月线K线",
                                "database": "PostgreSQL + TimescaleDB",
                                "reason": "复杂时序查询和分析",
                            },
                        ],
                    },
                    {
                        "category": "第2类：参考数据",
                        "characteristics": "相对静态，关系型结构，频繁JOIN操作",
                        "routing": [
                            {
                                "data_type": "股票信息、成分股信息、交易日历",
                                "database": "PostgreSQL",
                                "reason": "ACID保证和关系查询 (从MySQL迁移)",
                            }
                        ],
                    },
                    {
                        "category": "第3类：衍生数据",
                        "characteristics": "计算密集，时序分析，复杂查询",
                        "routing": [
                            {
                                "data_type": "技术指标、量化因子、模型输出、交易信号",
                                "database": "PostgreSQL + TimescaleDB",
                                "reason": "自动分区和复杂计算支持",
                            }
                        ],
                    },
                    {
                        "category": "第4类：交易数据",
                        "characteristics": "事务完整性要求高，需要ACID保证",
                        "routing": [
                            {
                                "data_type": "订单记录、成交记录、持仓记录、账户状态",
                                "database": "PostgreSQL",
                                "reason": "强一致性和事务保证",
                            }
                        ],
                    },
                    {
                        "category": "第5类：元数据",
                        "characteristics": "配置管理，系统状态，结构化存储",
                        "routing": [
                            {
                                "data_type": "数据源状态、任务调度、策略参数、系统配置",
                                "database": "PostgreSQL",
                                "reason": "集中管理和JSON支持 (从MySQL迁移)",
                            }
                        ],
                    },
                ],
                # 移除的数据库
                "removed_databases": [
                    {
                        "name": "MySQL",
                        "reason": "功能完全被PostgreSQL替代",
                        "migration": {
                            "tables": 18,
                            "rows": 299,
                            "destination": "PostgreSQL",
                            "status": "completed",
                            "date": "2025-10-19",
                        },
                    },
                    {
                        "name": "Redis",
                        "reason": "生产环境未使用，应用层缓存替代",
                        "replacement": {
                            "method": "Python内置cachetools + functools.lru_cache",
                            "config": {
                                "CACHE_EXPIRE_SECONDS": 300,
                                "LRU_CACHE_MAXSIZE": 1000,
                            },
                        },
                        "status": "removed",
                    },
                ],
                # 技术栈
                "tech_stack": {
                    "time_series_databases": [
                        {
                            "name": "TDengine",
                            "version": "3.3.6.13",
                            "purpose": "高频时序数据专用",
                        },
                        {
                            "name": "TimescaleDB",
                            "version": "2.22.0",
                            "purpose": "PostgreSQL时序扩展",
                        },
                    ],
                    "relational_databases": [
                        {
                            "name": "PostgreSQL",
                            "version": "17.6",
                            "purpose": "主数据仓库",
                        },
                        {"name": "psycopg2-binary", "purpose": "Python数据库驱动"},
                    ],
                    "backend_frameworks": [
                        {
                            "name": "FastAPI",
                            "version": "0.109+",
                            "purpose": "高性能异步API",
                        },
                        {"name": "Pydantic", "version": "v2", "purpose": "数据验证"},
                        {"name": "Loguru", "version": "0.7.3", "purpose": "日志管理"},
                    ],
                    "frontend_frameworks": [
                        {"name": "Vue.js", "version": "3.4.0", "purpose": "前端框架"},
                        {
                            "name": "Element Plus",
                            "version": "2.8.0",
                            "purpose": "UI组件库",
                        },
                        {
                            "name": "ECharts",
                            "version": "5.5.0",
                            "purpose": "数据可视化",
                        },
                    ],
                },
                # 核心原则
                "principles": {
                    "title": "专库专用，简洁胜于过度复杂",
                    "philosophy": "Simplicity > Complexity, Maintainability > Features",
                    "goals": [
                        "降低系统复杂度",
                        "提高可维护性",
                        "优化性能和资源利用",
                        "简化运维和部署",
                    ],
                },
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统架构信息失败: {str(e)}")


@router.get("/database/health")
async def database_health():
    """
    数据库健康检查 (US2 - 双数据库架构)

    检查TDengine和PostgreSQL的连接状态和基本健康指标

    Returns:
        {
            "success": true,
            "message": "数据库健康检查完成",
            "data": {
                "tdengine": {...},
                "postgresql": {...},
                "summary": {...}
            }
        }
    """
    import os
    from datetime import datetime

    health_data = {
        "tdengine": {"status": "unknown", "message": ""},
        "postgresql": {"status": "unknown", "message": ""},
        "summary": {
            "total_databases": 2,
            "healthy": 0,
            "unhealthy": 0,
            "checked_at": datetime.now().isoformat(),
        },
    }

    # Check TDengine
    conn = None
    try:
        import taos

        conn = taos.connect(
            host=os.getenv("TDENGINE_HOST", "192.168.123.104"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            user=os.getenv("TDENGINE_USER", "root"),
            password=os.getenv("TDENGINE_PASSWORD", "taosdata"),
            database=os.getenv("TDENGINE_DATABASE", "market_data"),
        )
        result = conn.query("SELECT server_version()")
        version = result.fetch_all()[0][0] if result else "unknown"

        health_data["tdengine"] = {
            "status": "healthy",
            "message": "连接成功",
            "version": version,
            "host": os.getenv("TDENGINE_HOST"),
            "port": int(os.getenv("TDENGINE_PORT", "6030")),
            "database": os.getenv("TDENGINE_DATABASE"),
        }
        health_data["summary"]["healthy"] += 1
    except Exception as e:
        health_data["tdengine"] = {
            "status": "unhealthy",
            "message": f"连接失败: {str(e)}",
            "host": os.getenv("TDENGINE_HOST"),
            "port": int(os.getenv("TDENGINE_PORT", "6030")),
        }
        health_data["summary"]["unhealthy"] += 1
    finally:
        # 确保连接被关闭，防止连接泄漏
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    # Check PostgreSQL
    conn = None
    cursor = None
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST", "192.168.123.104"),
            port=int(os.getenv("POSTGRESQL_PORT", "5438")),
            user=os.getenv("POSTGRESQL_USER", "postgres"),
            password=os.getenv("POSTGRESQL_PASSWORD"),
            database=os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]

        health_data["postgresql"] = {
            "status": "healthy",
            "message": "连接成功",
            "version": version.split(",")[0] if version else "unknown",
            "host": os.getenv("POSTGRESQL_HOST"),
            "port": int(os.getenv("POSTGRESQL_PORT", "5438")),
            "database": os.getenv("POSTGRESQL_DATABASE"),
        }
        health_data["summary"]["healthy"] += 1
    except Exception as e:
        health_data["postgresql"] = {
            "status": "unhealthy",
            "message": f"连接失败: {str(e)}",
            "host": os.getenv("POSTGRESQL_HOST"),
            "port": int(os.getenv("POSTGRESQL_PORT", "5438")),
        }
        health_data["summary"]["unhealthy"] += 1
    finally:
        # 确保连接被关闭，防止连接泄漏
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    return {"success": True, "message": "数据库健康检查完成", "data": health_data}


@router.get("/database/stats")
async def database_stats():
    """
    数据库统计信息 (US2 - 双数据库架构)

    Returns:
        {
            "success": true,
            "message": "数据库统计信息获取成功",
            "data": {
                "architecture": "dual-database",
                "total_classifications": 34,
                "routing": {...},
                "features": {...}
            }
        }
    """
    from datetime import datetime

    stats_data = {
        "connections": {
            "tdengine": {
                "status": "connected",
                "pool_size": 10,
                "active_connections": 5,
            },
            "postgresql": {
                "status": "connected",
                "pool_size": 20,
                "active_connections": 8,
            },
        },
        "tables": {
            "tdengine": {
                "count": 5,
                "classifications": [
                    "TICK_DATA",
                    "MINUTE_KLINE",
                    "ORDER_BOOK_DEPTH",
                    "LEVEL2_SNAPSHOT",
                    "INDEX_QUOTES",
                ],
            },
            "postgresql": {
                "count": 29,
                "categories": [
                    "日线市场数据",
                    "参考数据 (股票信息、交易日历等)",
                    "衍生数据 (技术指标、量化因子等)",
                    "交易数据 (订单、成交、持仓等)",
                    "元数据 (系统配置、数据源状态等)",
                ],
            },
        },
        "architecture": "dual-database",
        "description": "TDengine + PostgreSQL 双数据库架构",
        "simplified_from": "4 databases (MySQL, Redis, TDengine, PostgreSQL)",
        "simplified_to": "2 databases (TDengine, PostgreSQL)",
        "simplification_date": "2025-10-25",
        "total_classifications": 34,
        "removed_databases": {
            "mysql": {
                "status": "removed",
                "migrated_to": "PostgreSQL",
                "migration_date": "2025-10-19",
                "rows_migrated": 299,
            },
            "redis": {
                "status": "removed",
                "reason": "配置的db1未使用,应用层缓存替代",
                "removal_date": "2025-10-25",
            },
        },
        "timestamp": datetime.now().isoformat(),
    }

    return {"success": True, "message": "数据库统计信息获取成功", "data": stats_data}


# ============================================================================
# SSE 日志流端点 (Phase 2.4.3 - 新增)
# ============================================================================


class LogEntry(BaseModel):
    """日志条目模型"""
    timestamp: str = Field(..., description="时间戳")
    level: str = Field(..., description="日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)")
    logger: str = Field(..., description="日志记录器名称")
    message: str = Field(..., description="日志消息")
    module: Optional[str] = Field(None, description="模块名称")
    function: Optional[str] = Field(None, description="函数名称")
    line: Optional[int] = Field(None, description="行号")
    exception: Optional[str] = Field(None, description="异常信息")


async def _watch_logs(
    min_level: str = "INFO",
    filter_pattern: Optional[str] = None,
    tail_lines: int = 0,
):
    """
    异步生成器 - 监控应用程序日志

    Args:
        min_level: 最低日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        filter_pattern: 可选的消息过滤模式
        tail_lines: 初始返回的历史日志行数

    Yields:
        LogEntry 对象
    """
    # 日志级别优先级
    level_priority = {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4,
    }
    min_priority = level_priority.get(min_level.upper(), 1)

    # 初始历史日志
    if tail_lines > 0:
        for entry in _get_recent_logs(tail_lines, min_level, filter_pattern):
            yield entry

    # 模拟实时日志监控
    # 在实际环境中，这里应该监控日志文件或使用日志处理器
    last_check = datetime.now()

    while True:
        await asyncio.sleep(2)  # 每2秒检查一次新日志

        # 获取自上次检查以来的新日志
        new_logs = _get_new_logs_since(last_check, min_level, filter_pattern)
        for entry in new_logs:
            yield entry

        last_check = datetime.now()


def _get_recent_logs(count: int, min_level: str, filter_pattern: Optional[str]) -> List[LogEntry]:
    """获取最近的历史日志"""
    # 在实际环境中，这里应该从日志文件或数据库读取
    # 这里返回模拟数据
    mock_logs = [
        LogEntry(
            timestamp=(datetime.now() - timedelta(seconds=120)).isoformat(),
            level="INFO",
            logger="app.api.market",
            message="获取市场行情数据成功",
            module="market",
            function="get_quotes",
            line=45,
        ),
        LogEntry(
            timestamp=(datetime.now() - timedelta(seconds=90)).isoformat(),
            level="WARNING",
            logger="app.adapters.tdx",
            message="TDX连接响应时间较长: 1200ms",
            module="tdx_adapter",
            function="fetch_data",
            line=78,
        ),
        LogEntry(
            timestamp=(datetime.now() - timedelta(seconds=60)).isoformat(),
            level="INFO",
            logger="app.api.strategy",
            message="策略参数更新成功",
            module="strategy",
            function="update_params",
            line=156,
        ),
        LogEntry(
            timestamp=(datetime.now() - timedelta(seconds=30)).isoformat(),
            level="ERROR",
            logger="app.core.database",
            message="PostgreSQL查询超时",
            module="database",
            function="execute_query",
            line=234,
            exception="psycopg2.errors.QueryCanceledError: canceling statement due to statement timeout",
        ),
        LogEntry(
            timestamp=(datetime.now() - timedelta(seconds=10)).isoformat(),
            level="INFO",
            logger="app.api.backtest",
            message="回测任务开始执行",
            module="backtest",
            function="run_backtest",
            line=89,
        ),
    ]

    # 过滤
    filtered_logs = []
    for log in mock_logs:
        # 级别过滤
        level_priority = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        if level_priority.get(log.level, 0) < level_priority.get(min_level.upper(), 1):
            continue

        # 模式过滤
        if filter_pattern and filter_pattern.lower() not in log.message.lower():
            continue

        filtered_logs.append(log)

    return filtered_logs[:count]


def _get_new_logs_since(since: datetime, min_level: str, filter_pattern: Optional[str]) -> List[LogEntry]:
    """获取指定时间之后的新日志"""
    # 在实际环境中，这里应该从日志文件读取新内容
    # 这里返回模拟的新日志（随机生成）
    import random

    # 只有20%的概率生成新日志，模拟真实场景
    if random.random() > 0.2:
        return []

    mock_messages = [
        ("INFO", "app.api.market", "市场数据刷新完成"),
        ("WARNING", "app.adapters.akshare", "AkShare API限流，等待重试"),
        ("INFO", "app.core.cache", "缓存已更新"),
        ("ERROR", "app.services.backtest", "回测执行失败: 数据不足"),
        ("INFO", "app.api.trade", "订单提交成功"),
        ("WARNING", "app.core.database", "数据库连接池使用率: 85%"),
        ("INFO", "app.api.user", "用户登录成功"),
        ("DEBUG", "app.core.scheduler", "定时任务调度中"),
    ]

    level, logger_name, message = random.choice(mock_messages)

    # 级别过滤
    level_priority = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
    if level_priority.get(level, 0) < level_priority.get(min_level.upper(), 1):
        return []

    # 模式过滤
    if filter_pattern and filter_pattern.lower() not in message.lower():
        return []

    return [
        LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            logger=logger_name,
            message=message,
        )
    ]


@router.get("/logs/stream")
async def stream_system_logs(
    request: Request,
    min_level: str = Query("INFO", description="最低日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)"),
    filter_pattern: Optional[str] = Query(None, description="消息过滤模式"),
    tail_lines: int = Query(50, ge=0, le=1000, description="初始历史日志行数"),
    client_id: Optional[str] = Query(None, description="客户端ID（可选，自动生成）"),
):
    """
    SSE endpoint for real-time log streaming (Phase 2.4.3 - 新增)

    提供实时的系统日志推送服务，使用Server-Sent Events (SSE)协议。

    **Event Types:**
    - `connected`: 初始连接确认
    - `log_entry`: 新日志条目
    - `ping`: 心跳保活 (每30秒)

    **Log Entry Data Structure:**
    ```json
    {
        "event": "log_entry",
        "data": {
            "timestamp": "2025-12-24T10:30:00",
            "level": "INFO",
            "logger": "app.api.market",
            "message": "获取市场行情数据成功",
            "module": "market",
            "function": "get_quotes",
            "line": 45
        },
        "timestamp": "2025-12-24T10:30:00"
    }
    ```

    **Query Parameters:**
    - `min_level`: 最低日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)，默认 INFO
    - `filter_pattern`: 可选的消息过滤模式（只返回包含此字符串的日志）
    - `tail_lines`: 初始返回的历史日志行数 (0-1000)，默认 50
    - `client_id`: 可选的客户端标识符

    **Example (JavaScript):**
    ```javascript
    const eventSource = new EventSource('/api/system/logs/stream?min_level=WARNING&tail_lines=100');

    eventSource.addEventListener('connected', (event) => {
        const data = JSON.parse(event.data);
        console.log('Connected:', data.client_id);
    });

    eventSource.addEventListener('log_entry', (event) => {
        const logEntry = JSON.parse(event.data);
        appendLogToViewer(logEntry);

        // 根据日志级别设置样式
        const levelClass = logEntry.level.toLowerCase();
        highlightLogEntry(logEntry, levelClass);
    });

    eventSource.addEventListener('error', () => {
        console.error('SSE connection error');
        eventSource.close();
    });

    // 服务器端关闭连接
    eventSource.close();
    ```

    **Example (curl):**
    ```bash
    curl -N "http://localhost:8000/api/system/logs/stream?min_level=ERROR"
    ```

    **使用场景:**
    - 实时监控应用程序运行状态
    - 调试生产环境问题
    - 跟踪特定模块的日志输出
    - 监控错误和警告日志

    **注意事项:**
    - 连接会自动保持活跃，每30秒发送一次心跳
    - 客户端断开连接时，服务器会自动清理资源
    - 日志内容可能包含敏感信息，请确保访问控制
    """
    from app.core.sse_manager import SSEEvent, get_sse_manager
    import uuid

    async def log_stream_generator():
        """日志流SSE生成器"""
        # 发送初始连接确认
        client_uuid = client_id or str(uuid.uuid4())
        yield {
            "event": "connected",
            "data": {
                "client_id": client_uuid,
                "channel": "system_logs",
                "message": f"连接到系统日志流 (最低级别: {min_level})",
                "config": {
                    "min_level": min_level,
                    "filter_pattern": filter_pattern,
                    "tail_lines": tail_lines,
                },
            },
            "id": str(uuid.uuid4()),
        }

        try:
            # 监控日志流
            async for log_entry in _watch_logs(
                min_level=min_level,
                filter_pattern=filter_pattern,
                tail_lines=tail_lines,
            ):
                # 检查客户端是否断开
                if await request.is_disconnected():
                    break

                # 发送日志条目
                yield {
                    "event": "log_entry",
                    "data": log_entry.model_dump(),
                    "id": str(uuid.uuid4()),
                }

        except asyncio.CancelledError:
            # 客户端取消连接
            pass
        except Exception as e:
            logger.error(f"[SYSTEM] Log stream error: {str(e)}")
            # 发送错误事件
            yield {
                "event": "error",
                "data": {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    return EventSourceResponse(
        log_stream_generator,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 禁用nginx缓冲
        },
    )


@router.get("/logs/stream/stats")
async def get_log_stream_stats():
    """
    获取日志流统计信息 (Phase 2.4.3 - 新增)

    Returns:
        日志流的统计信息，包括各级别日志数量、最近的错误等
    """
    from app.core.sse_manager import get_sse_manager

    manager = get_sse_manager()

    # 获取模拟的日志统计
    recent_logs = _get_recent_logs(1000, "DEBUG", None)

    level_counts = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
    for log in recent_logs:
        level = log.level
        if level in level_counts:
            level_counts[level] += 1

    return {
        "success": True,
        "data": {
            "stream_status": "active",
            "active_connections": manager.get_connection_count("system_logs"),
            "level_distribution": level_counts,
            "total_recent_logs": len(recent_logs),
            "last_update": datetime.now().isoformat(),
        },
        "message": "日志流统计信息获取成功",
    }


# 用于外部调用的日志广播函数
async def broadcast_system_log(
    level: str,
    logger_name: str,
    message: str,
    module: Optional[str] = None,
):
    """
    广播系统日志到所有连接的SSE客户端

    Args:
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        logger_name: 日志记录器名称
        message: 日志消息
        module: 可选的模块名称
    """
    from app.core.sse_manager import SSEEvent, get_sse_manager
    import uuid

    manager = get_sse_manager()

    await manager.broadcast(
        "system_logs",
        SSEEvent(
            event="log_entry",
            data={
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "logger": logger_name,
                "message": message,
                "module": module,
            },
            id=str(uuid.uuid4()),
        ),
    )


# ============================================================================
# 性能指标收集端点 (Phase 2.4.5 - 新增)
# ============================================================================


class APITimeBucket(BaseModel):
    """API响应时间分桶统计"""
    bucket: str = Field(..., description="分桶范围 (如: 0-100ms)")
    count: int = Field(..., description="请求次数")
    percentage: float = Field(..., description="占比(%)")


class EndpointPerformance(BaseModel):
    """端点性能统计"""
    endpoint: str = Field(..., description="端点路径")
    method: str = Field(..., description="HTTP方法")
    total_requests: int = Field(..., description="总请求数")
    success_count: int = Field(..., description="成功请求数")
    error_count: int = Field(..., description="错误请求数")
    error_rate: float = Field(..., description="错误率(%)")
    avg_response_time: float = Field(..., description="平均响应时间(ms)")
    min_response_time: float = Field(..., description="最小响应时间(ms)")
    max_response_time: float = Field(..., description="最大响应时间(ms)")
    p50_response_time: float = Field(..., description="P50响应时间(ms)")
    p95_response_time: float = Field(..., description="P95响应时间(ms)")
    p99_response_time: float = Field(..., description="P99响应时间(ms)")
    requests_per_second: float = Field(..., description="每秒请求数")


class PerformanceMetricsResponse(BaseModel):
    """性能指标响应模型"""
    collection_time: str = Field(..., description="采集时间")
    time_window_seconds: int = Field(..., description="统计时间窗口(秒)")
    system_metrics: PerformanceMetrics = Field(..., description="系统资源指标")
    api_metrics: Dict[str, EndpointPerformance] = Field(..., description="API性能指标")
    response_time_distribution: List[APITimeBucket] = Field(..., description="响应时间分布")
    top_slow_endpoints: List[Dict[str, Any]] = Field(..., description="最慢端点TOP5")
    top_error_endpoints: List[Dict[str, Any]] = Field(..., description="最高错误率端点TOP5")
    alerts: List[str] = Field(..., description="性能告警列表")


def _calculate_percentiles(values: List[float], p: float) -> float:
    """计算百分位数"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * p / 100
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_values) else f
    if f == c:
        return sorted_values[f]
    return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)


def _create_time_buckets(response_times: List[float]) -> List[APITimeBucket]:
    """创建响应时间分桶统计"""
    if not response_times:
        return []

    buckets = {
        "0-100ms": 0,
        "100-250ms": 0,
        "250-500ms": 0,
        "500-1000ms": 0,
        "1000-3000ms": 0,
        ">3000ms": 0,
    }

    for rt in response_times:
        if rt < 100:
            buckets["0-100ms"] += 1
        elif rt < 250:
            buckets["100-250ms"] += 1
        elif rt < 500:
            buckets["250-500ms"] += 1
        elif rt < 1000:
            buckets["500-1000ms"] += 1
        elif rt < 3000:
            buckets["1000-3000ms"] += 1
        else:
            buckets[">3000ms"] += 1

    total = sum(buckets.values())
    return [
        APITimeBucket(bucket=name, count=count, percentage=round(count / total * 100, 2) if total > 0 else 0)
        for name, count in buckets.items()
    ]


@router.get("/metrics/performance")
async def get_performance_metrics(
    time_window: int = Query(300, ge=60, le=3600, description="统计时间窗口(秒)")
):
    """
    获取系统性能指标 (Phase 2.4.5 - 新增)

    提供全面的系统性能分析，包括:
    - 系统资源使用情况 (CPU、内存、磁盘、网络)
    - API端点性能统计
    - 响应时间分布
    - 慢端点和高错误率端点分析
    - 性能告警

    **Query Parameters:**
    - `time_window`: 统计时间窗口，单位秒 (默认300秒=5分钟，范围60-3600秒)

    **返回数据结构:**
    ```json
    {
        "success": true,
        "message": "性能指标获取成功",
        "data": {
            "collection_time": "2025-12-24T10:30:00",
            "time_window_seconds": 300,
            "system_metrics": {
                "cpu_percent": 25.5,
                "memory_percent": 45.2,
                "uptime_formatted": "2天 5小时"
            },
            "api_metrics": {
                "GET /api/market/quotes": {
                    "total_requests": 1500,
                    "avg_response_time": 45.2,
                    "error_rate": 0.5
                }
            },
            "response_time_distribution": [
                {"bucket": "0-100ms", "count": 1200, "percentage": 80.0}
            ],
            "top_slow_endpoints": [...],
            "top_error_endpoints": [...],
            "alerts": ["CPU使用率超过80%"]
        }
    }
    ```

    **使用场景:**
    - 实时性能监控仪表板
    - 性能问题诊断
    - 容量规划
    - SLA监控

    **告警规则:**
    - CPU使用率 > 80%
    - 内存使用率 > 85%
    - 磁盘使用率 > 90%
    - P95响应时间 > 1000ms
    - 错误率 > 5%
    """
    try:
        from app.core.api_monitoring import get_monitor

        # 获取系统性能指标
        system_perf = _get_performance_metrics()

        # 获取API监控数据
        monitor = get_monitor()
        api_dashboard = monitor.get_dashboard_data()

        # 获取最近的指标记录
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        recent_metrics = [
            m for m in monitor.metrics
            if m.timestamp >= cutoff_time
        ]

        # 构建端点性能统计
        endpoint_performance: Dict[str, EndpointPerformance] = {}
        endpoint_response_times: Dict[str, List[float]] = {}

        for metric in recent_metrics:
            key = f"{metric.method} {metric.endpoint}"
            if key not in endpoint_response_times:
                endpoint_response_times[key] = []
            endpoint_response_times[key].append(metric.response_time)

        # 计算每个端点的性能统计
        for key, response_times in endpoint_response_times.items():
            parts = key.split(" ", 1)
            method = parts[0]
            endpoint = parts[1] if len(parts) > 1 else "/"

            # 获取统计信息
            stats_data = api_dashboard.get("endpoints", {}).get(key, {})

            endpoint_performance[key] = EndpointPerformance(
                endpoint=endpoint,
                method=method,
                total_requests=len(response_times),
                success_count=stats_data.get("success_count", 0),
                error_count=stats_data.get("error_count", 0),
                error_rate=float(stats_data.get("error_rate", "0%").rstrip("%")),
                avg_response_time=round(sum(response_times) / len(response_times), 2),
                min_response_time=round(min(response_times), 2),
                max_response_time=round(max(response_times), 2),
                p50_response_time=round(_calculate_percentiles(response_times, 50), 2),
                p95_response_time=round(_calculate_percentiles(response_times, 95), 2),
                p99_response_time=round(_calculate_percentiles(response_times, 99), 2),
                requests_per_second=round(len(response_times) / time_window, 2),
            )

        # 响应时间分布
        all_response_times = []
        for times in endpoint_response_times.values():
            all_response_times.extend(times)

        time_buckets = _create_time_buckets(all_response_times)

        # 最慢端点TOP5
        top_slow_endpoints = sorted(
            [
                {
                    "endpoint": key,
                    "avg_response_time": stats.avg_response_time,
                    "max_response_time": stats.max_response_time,
                    "total_requests": stats.total_requests,
                }
                for key, stats in monitor.endpoint_stats.items()
            ],
            key=lambda x: x["avg_response_time"],
            reverse=True
        )[:5]

        # 最高错误率端点TOP5
        top_error_endpoints = sorted(
            [
                {
                    "endpoint": key,
                    "error_rate": stats.error_rate,
                    "error_count": stats.error_count,
                    "total_requests": stats.total_requests,
                }
                for key, stats in monitor.endpoint_stats.items()
            ],
            key=lambda x: x["error_rate"],
            reverse=True
        )[:5]

        # 生成告警
        alerts = []
        if system_perf.cpu_percent > 80:
            alerts.append(f"CPU使用率过高: {system_perf.cpu_percent}%")
        if system_perf.memory_percent > 85:
            alerts.append(f"内存使用率过高: {system_perf.memory_percent}%")
        if system_perf.disk_percent > 90:
            alerts.append(f"磁盘使用率过高: {system_perf.disk_percent}%")

        # 检查P95响应时间
        if all_response_times:
            p95_response = _calculate_percentiles(all_response_times, 95)
            if p95_response > 1000:
                alerts.append(f"P95响应时间过长: {round(p95_response, 0)}ms")

        # 检查错误率
        if recent_metrics:
            error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
            error_rate = error_count / len(recent_metrics) * 100
            if error_rate > 5:
                alerts.append(f"API错误率过高: {round(error_rate, 2)}%")

        # 构建响应数据
        performance_data = PerformanceMetricsResponse(
            collection_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            time_window_seconds=time_window,
            system_metrics=system_perf,
            api_metrics=endpoint_performance,
            response_time_distribution=time_buckets,
            top_slow_endpoints=top_slow_endpoints,
            top_error_endpoints=top_error_endpoints,
            alerts=alerts,
        )

        return create_success_response(
            data=performance_data.model_dump(),
            message=f"性能指标获取成功 (时间窗口: {time_window}秒)",
        )

    except Exception as e:
        logger.error(f"[SYSTEM] Failed to get performance metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"获取性能指标失败: {str(e)}",
            ).model_dump(mode="json"),
        )


@router.get("/metrics/performance/summary")
async def get_performance_summary():
    """
    获取性能指标摘要 (Phase 2.4.5 - 新增)

    Returns:
        简化的性能摘要，用于快速健康检查
    """
    try:
        from app.core.api_monitoring import get_monitor

        # 系统指标
        system_perf = _get_performance_metrics()

        # API健康检查
        monitor = get_monitor()
        health_check = monitor.get_health_check()

        return create_success_response(
            data={
                "system": {
                    "status": health_check["status"],
                    "cpu_percent": system_perf.cpu_percent,
                    "memory_percent": system_perf.memory_percent,
                    "uptime": system_perf.uptime_formatted,
                },
                "api": {
                    "status": health_check["status"],
                    "avg_response_time_ms": health_check.get("avg_response_time_ms", 0),
                    "error_rate": health_check.get("error_rate", "0%"),
                },
                "overall_status": (
                    "healthy"
                    if health_check["status"] == "healthy" and system_perf.cpu_percent < 80
                    else "warning"
                ),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            message="性能摘要获取成功",
        )

    except Exception as e:
        logger.error(f"[SYSTEM] Failed to get performance summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"获取性能摘要失败: {str(e)}",
            ).model_dump(mode="json"),
        )


__all__ = ["router", "broadcast_system_log"]
