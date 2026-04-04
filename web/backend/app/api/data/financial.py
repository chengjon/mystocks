"""
财务数据路由 (Financial Data)
"""
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import BusinessException
from app.core.security import User, get_current_user
from app.openapi_config import COMMON_RESPONSES

router = APIRouter()


def _success_response_spec(description: str, example: dict[str, Any]) -> dict[int, dict[str, Any]]:
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


FINANCIAL_DATA_RESPONSES = {
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    **_success_response_spec(
        "股票财务报表结果",
        {
            "success": True,
            "data": [
                {
                    "report_date": "2025-12-31",
                    "report_type": "balance",
                    "total_assets": 284500000000.0,
                    "total_liabilities": 91300000000.0,
                    "shareholders_equity": 193200000000.0,
                }
            ],
            "symbol": "600519",
            "report_type": "balance",
            "period": "annual",
            "limit": 20,
        },
    ),
}


@router.get(
    "/financial",
    summary="查询股票财务报表",
    description="查询股票财务报表数据，支持报表类型、报告期间和返回条数等筛选条件。",
    responses=FINANCIAL_DATA_RESPONSES,
)
async def get_financial_data(
    symbol: str = Query(..., description="股票代码。"),
    report_type: str = Query("balance", description="财务报表类型，例如 balance、income 或 cashflow。"),
    period: str = Query("all", description="报告期间筛选，例如 annual、quarterly 或 all。"),
    limit: int = Query(20, description="单次请求返回的最大财务记录数。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()
        params = {"symbol": symbol, "report_type": report_type, "period": period, "limit": limit}
        result = await factory.get_data("data", "financial", params)
        if result.get("status") != "success":
            raise BusinessException(detail="获取财务报表失败", status_code=500, error_code="DATA_RETRIEVAL_FAILED")

        return {
            "success": True,
            "data": result.get("data", []),
            "symbol": symbol,
            "report_type": report_type,
            "period": period,
            "limit": limit,
        }
    except BusinessException:
        raise
    except Exception as error:
        raise BusinessException(
            detail=f"获取财务报表失败: {str(error)}",
            status_code=500,
            error_code="DATA_RETRIEVAL_FAILED",
        )
