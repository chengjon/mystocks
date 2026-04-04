"""
龙虎榜数据路由 (Dragon Tiger)
"""
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import BusinessException
from app.core.security import User, get_current_user
from app.core.responses import UnifiedResponse, ok
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


DRAGON_TIGER_ERROR_RESPONSES = {
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

DRAGON_TIGER_DETAIL_RESPONSES = {
    **DRAGON_TIGER_ERROR_RESPONSES,
    **_success_response_spec(
        "龙虎榜明细结果",
        {
            "success": True,
            "code": 200,
            "message": "操作成功",
            "data": [
                {
                    "trade_date": "2026-04-03",
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "close": 1710.88,
                    "change_pct": 0.72,
                    "net_buy_amount": 325000000.0,
                }
            ],
            "timestamp": "2026-04-04T23:10:00Z",
            "request_id": None,
            "errors": None,
        },
    ),
}

DRAGON_TIGER_INSTITUTION_RESPONSES = {
    **DRAGON_TIGER_ERROR_RESPONSES,
    **_success_response_spec(
        "龙虎榜机构统计结果",
        {
            "success": True,
            "data": [
                {"trade_date": "2026-04-03", "buy_count": 12, "sell_count": 7, "net_amount": 486000000.0}
            ],
            "period": "近一月",
        },
    ),
}


@router.get(
    "/dragon-tiger/detail",
    response_model=UnifiedResponse,
    summary="查询龙虎榜明细",
    description="查询龙虎榜明细数据，支持按日期范围和返回条数筛选榜单结果。",
    responses=DRAGON_TIGER_DETAIL_RESPONSES,
)
async def get_dragon_tiger_detail(
    start_date: str = Query(..., description="查询开始日期，格式为 YYYY-MM-DD。"),
    end_date: str = Query(..., description="查询结束日期，格式为 YYYY-MM-DD。"),
    limit: int = Query(100, description="单次请求返回的最大龙虎榜记录数。"),
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    try:
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()
        result = await factory.get_data(
            "data",
            "dragon-tiger/detail",
            {"start_date": start_date, "end_date": end_date, "limit": limit},
        )
        return ok(data=result.get("data", []))
    except Exception as e:
        raise BusinessException(detail=f"获取龙虎榜明细失败: {str(e)}", status_code=500, error_code="DATA_RETRIEVAL_FAILED")


@router.get(
    "/dragon-tiger/institution-stats",
    summary="查询龙虎榜机构统计",
    description="返回指定观察周期内的龙虎榜机构席位买卖统计，适用于热点席位追踪和活跃度分析。",
    responses=DRAGON_TIGER_INSTITUTION_RESPONSES,
)
async def get_dragon_tiger_institution_stats(
    period: str = Query("近一月", description="统计周期，例如近一周、近一月或近三月。"),
    limit: int = Query(50, description="返回的最大统计记录数。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()
        result = await factory.get_data(
            "data",
            "dragon-tiger/institution-stats",
            {"period": period, "limit": limit},
        )
        return {"success": True, "data": result.get("data", []), "period": period}
    except Exception as e:
        raise BusinessException(
            detail=f"获取龙虎榜机构统计失败: {str(e)}",
            status_code=500,
            error_code="DATA_RETRIEVAL_FAILED",
        )
