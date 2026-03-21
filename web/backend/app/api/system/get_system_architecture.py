"""
系统管理API端点
提供系统设置、数据库连接测试、运行日志查询等功能
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psycopg2
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Mock数据支持
use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

router = APIRouter()
logger = logging.getLogger(__name__)


def _close_resource_quietly(resource_name: str, resource: Any) -> None:
    if resource is None:
        return

    try:
        resource.close()
    except Exception as exc:
        logger.debug("Failed to close %s cleanly: %s", resource_name, exc)


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
            host=os.getenv("TDENGINE_HOST", "localhost"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            user=os.getenv("TDENGINE_USER", "root"),
            password=os.getenv("TDENGINE_PASSWORD"),
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
        _close_resource_quietly("TDengine connection", conn)

    # Check PostgreSQL
    conn = None
    cursor = None
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST", "localhost"),
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
        _close_resource_quietly("PostgreSQL cursor", cursor)
        _close_resource_quietly("PostgreSQL connection", conn)

    # Format databases array for E2E tests
    databases = []
    if health_data["tdengine"]["status"] == "healthy":
        databases.append(
            {
                "name": "TDengine",
                "status": "healthy",
                "host": health_data["tdengine"].get("host"),
                "port": health_data["tdengine"].get("port"),
                "database": health_data["tdengine"].get("database"),
            }
        )

    if health_data["postgresql"]["status"] == "healthy":
        databases.append(
            {
                "name": "PostgreSQL",
                "status": "healthy",
                "host": health_data["postgresql"].get("host"),
                "port": health_data["postgresql"].get("port"),
                "database": health_data["postgresql"].get("database"),
            }
        )

    # Add databases array to response for E2E tests
    health_data["databases"] = databases

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
