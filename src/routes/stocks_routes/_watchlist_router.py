"""Stocks watchlist sub-router."""

import logging
from datetime import datetime
from typing import Dict

from fastapi import APIRouter

from src.routes.stocks_routes.stocks_data_sources import check_use_mock_data, get_database_service, get_stocks_mock_data

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/watchlist")
async def add_to_watchlist(request: Dict):
    """添加到自选股"""
    try:
        stock_code = request.get("stock_code", "")
        notes = request.get("notes", "")

        logger.info("添加到自选股: %s, 备注: %s", stock_code, notes)

        if check_use_mock_data():
            logger.info("使用Mock数据源: 添加到自选股")
            mock_data = get_stocks_mock_data()
            result = mock_data["add_to_watchlist"](request)
            logger.info("Mock数据响应: 添加%s到自选股", stock_code)
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }

        logger.info("使用真实数据库: 添加到自选股")
        db_service = get_database_service()
        if db_service is None:
            return {
                "success": False,
                "message": "数据库服务暂未实现，请使用Mock数据源",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

        try:
            from src.database.database_service import db_service

            result = {"message": f"成功添加股票{stock_code}到自选股"}
            logger.info("真实数据库查询成功: 添加股票%s到自选股", stock_code)

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
        logger.error("添加到自选股失败: %s", str(e))
        return {
            "success": False,
            "message": f"添加到自选股失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.delete("/watchlist/{stock_code}")
async def remove_from_watchlist(stock_code: str):
    """从自选股移除"""
    try:
        logger.info("从自选股移除: %s", stock_code)

        if check_use_mock_data():
            logger.info("使用Mock数据源: 从自选股移除")
            mock_data = get_stocks_mock_data()
            result = mock_data["remove_from_watchlist"]({"stock_code": stock_code})
            logger.info("Mock数据响应: 从自选股移除%s", stock_code)
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }

        logger.info("使用真实数据库: 从自选股移除")
        db_service = get_database_service()
        if db_service is None:
            return {
                "success": False,
                "message": "数据库服务暂未实现，请使用Mock数据源",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

        try:
            from src.database.database_service import db_service

            result = {"message": f"成功从自选股移除股票{stock_code}"}
            logger.info("真实数据库查询成功: 从自选股移除股票%s", stock_code)

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
        logger.error("从自选股移除失败: %s", str(e))
        return {
            "success": False,
            "message": f"从自选股移除失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
