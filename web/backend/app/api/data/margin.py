"""
融资融券数据路由 (Margin Trading)
"""

from fastapi import APIRouter, Depends, Query

from app.core.security import User, get_current_user
from app.core.responses import UnifiedResponse, ok, server_error
from app.services.data_source_factory import DataSourceFactory, get_data_source_factory_dependency

router = APIRouter()


def _success_response_spec(status_code: int, description: str, example: object) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _error_response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


MARGIN_ACCOUNT_INFO_RESPONSES = {
    **_error_response_spec(
        500,
        "获取融资融券账户统计失败",
        {"success": False, "message": "获取失败", "data": None, "errors": None},
    ),
    **_success_response_spec(
        200,
        "全市场融资融券账户统计信息",
        {
            "success": True,
            "message": "success",
            "data": [
                {
                    "trade_date": "2026-04-03",
                    "financing_balance": 1543287654321.0,
                    "securities_lending_balance": 87324567890.0,
                    "financing_buy_amount": 12654321098.0,
                }
            ],
            "errors": None,
        },
    ),
}

MARGIN_DETAIL_RESPONSES = {
    **_error_response_spec(
        500,
        "获取融资融券明细失败",
        {"success": False, "message": "服务异常", "data": None, "errors": None},
    ),
    **_success_response_spec(
        200,
        "交易所融资融券明细数据",
        {
            "success": True,
            "message": "success",
            "data": [
                {
                    "trade_date": "2026-04-03",
                    "symbol": "600519",
                    "security_name": "贵州茅台",
                    "financing_balance": 325678901.0,
                    "financing_buy_amount": 18234567.0,
                    "securities_lending_balance": 1256789.0,
                }
            ],
            "errors": None,
        },
    ),
}


@router.get(
    "/margin/account-info",
    response_model=UnifiedResponse,
    summary="获取融资融券账户统计",
    description="查询全市场融资融券账户汇总指标，返回融资余额、融券余额和当日融资买入额等统计信息。",
    responses=MARGIN_ACCOUNT_INFO_RESPONSES,
)
async def get_margin_account_info(
    current_user: User = Depends(get_current_user),
    factory: DataSourceFactory = Depends(get_data_source_factory_dependency),
) -> UnifiedResponse:
    """获取全市场融资融券账户统计信息"""
    try:
        result = await factory.get_data("data", "margin/account-info", {})
        if result.get("status") == "success":
            return ok(data=result.get("data", []))
        return server_error(message="获取失败")
    except Exception as e:
        return server_error(message=str(e))


@router.get(
    "/margin/detail/sse",
    response_model=UnifiedResponse,
    summary="获取上证所融资融券明细",
    description="按交易日期查询上证所融资融券明细数据，返回证券代码、融资余额和融券余额等字段。",
    responses=MARGIN_DETAIL_RESPONSES,
)
async def get_margin_detail_sse(
    date: str = Query(..., description="需要查询的交易日期，格式为 YYYY-MM-DD。"),
    current_user: User = Depends(get_current_user),
    factory: DataSourceFactory = Depends(get_data_source_factory_dependency),
) -> UnifiedResponse:
    """获取上证所融资融券明细数据"""
    try:
        result = await factory.get_data("data", "margin/detail/sse", {"date": date})
        return ok(data=result.get("data", []))
    except Exception as e:
        return server_error(message=str(e))


@router.get(
    "/margin/detail/szse",
    response_model=UnifiedResponse,
    summary="获取深证所融资融券明细",
    description="按交易日期查询深证所融资融券明细数据，返回证券代码、融资余额和融券余额等字段。",
    responses=MARGIN_DETAIL_RESPONSES,
)
async def get_margin_detail_szse(
    date: str = Query(..., description="需要查询的交易日期，格式为 YYYY-MM-DD。"),
    current_user: User = Depends(get_current_user),
    factory: DataSourceFactory = Depends(get_data_source_factory_dependency),
) -> UnifiedResponse:
    """获取深证所融资融券明细数据"""
    try:
        result = await factory.get_data("data", "margin/detail/szse", {"date": date})
        return ok(data=result.get("data", []))
    except Exception as e:
        return server_error(message=str(e))
