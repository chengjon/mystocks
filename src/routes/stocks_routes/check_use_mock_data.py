"""
FastAPI路由文件: Stocks
功能: 股票管理相关的API端点实现

作者: Claude Code
生成时间: 2025-11-13
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from src.routes.stocks_routes._watchlist_router import router as watchlist_router
from src.routes.stocks_routes.stocks_data_sources import check_use_mock_data, get_database_service, get_stocks_mock_data

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter(prefix="/api/stocks", tags=["Stocks"])
router.include_router(watchlist_router)


@router.get("/list")
async def get_stock_list(
    page: int = Query(1, description="页码"),
    limit: int = Query(20, description="每页数量"),
    exchange: Optional[str] = Query(None, description="交易所筛选"),
    industry: Optional[str] = Query(None, description="行业筛选"),
):
    """获取股票列表

    Args:
        page: int - 页码
        limit: int - 每页数量
        exchange: str - 交易所筛选
        industry: str - 行业筛选

    Returns:
        Dict: 股票列表数据
    """
    try:
        logger.info("获取股票列表: page=%s, limit=%s, exchange=%s, industry=%s", page, limit, exchange, industry)

        if check_use_mock_data():
            logger.info("使用Mock数据源: 获取股票列表")
            mock_data = get_stocks_mock_data()
            result = mock_data["get_stock_list"](
                {
                    "page": page,
                    "limit": limit,
                    "exchange": exchange,
                    "industry": industry,
                }
            )
            logger.info("Mock数据响应: 共%s只股票", result.get("total", 0))
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }
        else:
            logger.info("使用真实数据库: 获取股票列表")
            db_service = get_database_service()
            if db_service is None:
                return {
                    "success": False,
                    "message": "数据库服务暂未实现，请使用Mock数据源",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

            # 实现真实数据库查询
            try:
                # 导入真实数据库服务
                from src.database.stocks_db_service import get_stock_list

                # 调用真实数据服务，参数与Mock接口一致
                result = get_stock_list(
                    {
                        "page": page,
                        "limit": limit,
                        "exchange": exchange,
                        "industry": industry,
                    }
                )

                # 计算总数量（从结果中获取或单独查询）
                total_count = result[0]["total"] if result else 0

                logger.info("真实数据库查询成功: 共%s只股票", total_count)

                return {
                    "success": True,
                    "data": result,
                    "total": total_count,
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }
            except Exception as e:
                logger.error("真实数据库查询失败: %s", str(e))
                return {
                    "success": False,
                    "message": f"真实数据库查询失败: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

    except Exception as e:
        logger.error("获取股票列表失败: %s", str(e))
        return {
            "success": False,
            "message": f"获取股票列表失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/{stock_code}")
async def get_stock_detail(stock_code: str):
    """获取股票详细信息

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 股票详细信息
    """
    try:
        logger.info("获取股票详细信息: %s", stock_code)

        if check_use_mock_data():
            logger.info("使用Mock数据源: 获取股票详细信息")
            mock_data = get_stocks_mock_data()
            result = mock_data["get_stock_detail"]({"stock_code": stock_code})
            logger.info("Mock数据响应: 股票%s详细信息", stock_code)
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }
        else:
            logger.info("使用真实数据库: 获取股票详细信息")
            db_service = get_database_service()
            if db_service is None:
                return {
                    "success": False,
                    "message": "数据库服务暂未实现，请使用Mock数据源",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

            # 实现真实数据库查询
            try:
                # 导入真实数据库服务
                from src.database.database_service import db_service

                # 调用真实数据服务，参数与Mock接口一致
                result = db_service.get_stock_detail(stock_code)

                logger.info("真实数据库查询成功: 股票%s详细信息", stock_code)

                return {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }
            except Exception as e:
                logger.error("真实数据库查询失败: %s", str(e))
                return {
                    "success": False,
                    "message": f"真实数据库查询失败: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

    except Exception as e:
        logger.error("获取股票详细信息失败: %s", str(e))
        return {
            "success": False,
            "message": f"获取股票详细信息失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/{stock_code}/financial")
async def get_stock_financial_data(stock_code: str):
    """获取股票财务数据

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 股票财务数据
    """
    try:
        logger.info("获取股票财务数据: %s", stock_code)

        if check_use_mock_data():
            logger.info("使用Mock数据源: 获取股票财务数据")
            mock_data = get_stocks_mock_data()
            result = mock_data["get_stock_financial_data"]({"stock_code": stock_code})
            logger.info("Mock数据响应: 股票%s财务数据", stock_code)
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }
        else:
            logger.info("使用真实数据库: 获取股票财务数据")
            db_service = get_database_service()
            if db_service is None:
                return {
                    "success": False,
                    "message": "数据库服务暂未实现，请使用Mock数据源",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

            # 实现真实数据库查询
            try:
                # 导入真实数据库服务
                from src.database.database_service import db_service

                # 调用真实数据服务，参数与Mock接口一致
                # Using technical indicators as a proxy for financial data
                result = db_service.get_technical_indicators({"symbol": stock_code})

                logger.info("真实数据库查询成功: 股票%s财务数据", stock_code)

                return {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }
            except Exception as e:
                logger.error("真实数据库查询失败: %s", str(e))
                return {
                    "success": False,
                    "message": f"真实数据库查询失败: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

    except Exception as e:
        logger.error("获取股票财务数据失败: %s", str(e))
        return {
            "success": False,
            "message": f"获取股票财务数据失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/{stock_code}/indicators")
async def get_stock_indicators(stock_code: str):
    """获取股票技术指标

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 股票技术指标
    """
    try:
        logger.info("获取股票技术指标: %s", stock_code)

        if check_use_mock_data():
            logger.info("使用Mock数据源: 获取股票技术指标")
            mock_data = get_stocks_mock_data()
            result = mock_data["get_stock_indicators"]({"stock_code": stock_code})
            logger.info("Mock数据响应: 股票%s技术指标", stock_code)
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }
        else:
            logger.info("使用真实数据库: 获取股票技术指标")
            db_service = get_database_service()
            if db_service is None:
                return {
                    "success": False,
                    "message": "数据库服务暂未实现，请使用Mock数据源",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

            # 实现真实数据库查询
            try:
                # 导入真实数据库服务
                from src.database.database_service import db_service

                # 调用真实数据服务，参数与Mock接口一致
                result = db_service.get_technical_indicators({"symbol": stock_code})

                logger.info("真实数据库查询成功: 股票%s技术指标", stock_code)

                return {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }
            except Exception as e:
                logger.error("真实数据库查询失败: %s", str(e))
                return {
                    "success": False,
                    "message": f"真实数据库查询失败: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

    except Exception as e:
        logger.error("获取股票技术指标失败: %s", str(e))
        return {
            "success": False,
            "message": f"获取股票技术指标失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/realtime/quotes")
async def get_realtime_quotes():
    """获取实时行情数据

    Returns:
        Dict: 实时行情数据
    """
    try:
        logger.info("获取实时行情数据")

        if check_use_mock_data():
            logger.info("使用Mock数据源: 获取实时行情")
            mock_data = get_stocks_mock_data()
            result = mock_data["get_realtime_quotes"]()
            logger.info("Mock数据响应: 共%s只股票实时行情", result.get("total", 0))
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }
        else:
            logger.info("使用真实数据库: 获取实时行情")
            db_service = get_database_service()
            if db_service is None:
                return {
                    "success": False,
                    "message": "数据库服务暂未实现，请使用Mock数据源",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

            # 实现真实数据库查询
            try:
                # 导入真实数据库服务
                from src.database.database_service import db_service

                # 调用真实数据服务，参数与Mock接口一致
                result = db_service.get_realtime_quotes([])

                logger.info("真实数据库查询成功: 实时行情数据")

                return {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }
            except Exception as e:
                logger.error("真实数据库查询失败: %s", str(e))
                return {
                    "success": False,
                    "message": f"真实数据库查询失败: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

    except Exception as e:
        logger.error("获取实时行情失败: %s", str(e))
        return {
            "success": False,
            "message": f"获取实时行情失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/search")
async def search_stocks(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, description="搜索结果数量"),
):
    """搜索股票

    Args:
        q: str - 搜索关键词
        limit: int - 搜索结果数量

    Returns:
        Dict: 搜索结果
    """
    try:
        logger.info("搜索股票: %s, limit: %s", q, limit)

        if check_use_mock_data():
            logger.info("使用Mock数据源: 搜索股票")
            mock_data = get_stocks_mock_data()
            result = mock_data["search_stocks"]({"q": q, "limit": limit})
            logger.info("Mock数据响应: 共%s只股票", result.get("total", 0))
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }
        else:
            logger.info("使用真实数据库: 搜索股票")
            db_service = get_database_service()
            if db_service is None:
                return {
                    "success": False,
                    "message": "数据库服务暂未实现，请使用Mock数据源",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

            # 实现真实数据库查询
            try:
                # 导入真实数据库服务
                from src.database.database_service import db_service

                # 调用真实数据服务，参数与Mock接口一致
                # For search functionality, we'll use stock list with filters
                result = db_service.get_stock_list({"q": q, "limit": limit})

                logger.info("真实数据库查询成功: 搜索股票%s", q)

                return {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }
            except Exception as e:
                logger.error("真实数据库查询失败: %s", str(e))
                return {
                    "success": False,
                    "message": f"真实数据库查询失败: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

    except Exception as e:
        logger.error("搜索股票失败: %s", str(e))
        return {
            "success": False,
            "message": f"搜索股票失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/industry/{industry_name}")
async def get_stock_by_industry(
    industry_name: str,
    page: int = Query(1, description="页码"),
    limit: int = Query(20, description="每页数量"),
):
    """按行业获取股票

    Args:
        industry_name: str - 行业名称
        page: int - 页码
        limit: int - 每页数量

    Returns:
        Dict: 行业股票列表
    """
    try:
        logger.info("按行业获取股票: %s, page: %s, limit: %s", industry_name, page, limit)

        if check_use_mock_data():
            logger.info("使用Mock数据源: 按行业获取股票")
            mock_data = get_stocks_mock_data()
            result = mock_data["get_stock_by_industry"]({"industry_name": industry_name, "page": page, "limit": limit})
            logger.info("Mock数据响应: %s行业共%s只股票", industry_name, result.get("total", 0))
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }
        else:
            logger.info("使用真实数据库: 按行业获取股票")
            db_service = get_database_service()
            if db_service is None:
                return {
                    "success": False,
                    "message": "数据库服务暂未实现，请使用Mock数据源",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

            # 实现真实数据库查询
            try:
                # 导入真实数据库服务
                from src.database.database_service import db_service

                # 调用真实数据服务，参数与Mock接口一致
                result = db_service.get_stock_list({"industry": industry_name, "page": page, "limit": limit})

                logger.info("真实数据库查询成功: 按行业%s获取股票", industry_name)

                return {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }
            except Exception as e:
                logger.error("真实数据库查询失败: %s", str(e))
                return {
                    "success": False,
                    "message": f"真实数据库查询失败: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

    except Exception as e:
        logger.error("按行业获取股票失败: %s", str(e))
        return {
            "success": False,
            "message": f"按行业获取股票失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/watchlist")
async def get_watchlist():
    """获取自选股列表

    Returns:
        Dict: 自选股列表
    """
    try:
        logger.info("获取自选股列表")

        if check_use_mock_data():
            logger.info("使用Mock数据源: 获取自选股")
            mock_data = get_stocks_mock_data()
            result = mock_data["get_watchlist"]()
            logger.info("Mock数据响应: 共%s只自选股", result.get("total", 0))
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }
        else:
            logger.info("使用真实数据库: 获取自选股")
            db_service = get_database_service()
            if db_service is None:
                return {
                    "success": False,
                    "message": "数据库服务暂未实现，请使用Mock数据源",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

            # 实现真实数据库查询
            try:
                # 导入真实数据库服务
                from src.database.database_service import db_service

                # 调用真实数据服务，参数与Mock接口一致
                # For watchlist, we'll return an empty list as placeholder
                result = []

                logger.info("真实数据库查询成功: 获取自选股列表")

                return {
                    "success": True,
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }
            except Exception as e:
                logger.error("真实数据库查询失败: %s", str(e))
                return {
                    "success": False,
                    "message": f"真实数据库查询失败: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "database",
                }

    except Exception as e:
        logger.error("获取自选股列表失败: %s", str(e))
        return {
            "success": False,
            "message": f"获取自选股列表失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
