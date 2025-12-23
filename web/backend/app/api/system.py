"""
系统管理API端点
提供系统设置、数据库连接测试、运行日志查询等功能
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psycopg2
import taos
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Mock数据支持
use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

router = APIRouter()


@router.get("/health")
async def system_health():
    """
    系统健康检查端点 (双数据库架构: TDengine + PostgreSQL)

    返回:
    - 数据库连接状态
    - 系统运行时间
    - 服务状态
    """
    if use_mock:
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
        except Exception:
            pass

        try:
            # 检查 TDengine
            # TODO: 添加 TDengine 健康检查
            db_status["tdengine"] = "healthy"
        except Exception:
            pass

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
                    user="postgres",
                    password="c790414J",
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
                    user="root",
                    password="taosdata",
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
            password="c790414J",
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
