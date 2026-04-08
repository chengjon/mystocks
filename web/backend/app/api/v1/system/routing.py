"""
数据路由API

提供智能数据路由选择功能
"""

from typing import Dict, Optional

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/data",
    tags=["Data Routing"],
)


DATA_ROUTING_RESPONSES = {
    200: {
        "description": "数据路由决策结果",
        "content": {
            "application/json": {
                "example": {
                    "route_selected": "tdengine",
                    "estimated_records": 1000,
                    "query_complexity": "high_frequency",
                    "recommended_strategy": "direct_query",
                }
            }
        },
    }
}

DATA_ROUTING_REQUEST_EXAMPLE = {
    "data_category": "market_data",
    "symbol": "IF9999.CCFX",
    "date_range": {"start": "2025-03-01", "end": "2025-03-31"},
}


class DataRoutingRequest(BaseModel):
    """Data routing request"""

    data_category: str = Field(
        ...,
        description="Data category (market_data|reference_data|derived_data|transaction_data|metadata)",
    )
    symbol: Optional[str] = Field(None, description="Stock symbol")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range filter")


class DataRoutingResponse(BaseModel):
    """Data routing response"""

    route_selected: str = Field(..., description="Selected database route")
    estimated_records: int = Field(..., description="Estimated record count")
    query_complexity: str = Field(..., description="Query complexity level")
    recommended_strategy: str = Field(..., description="Recommended query strategy")


@router.post(
    "/route",
    response_model=DataRoutingResponse,
    summary="Data Routing Decision",
    description="根据数据类别、标的和时间范围推断最合适的查询路由，帮助在 PostgreSQL 与 TDengine 之间做契约化选择。",
    responses=DATA_ROUTING_RESPONSES,
)
async def get_data_route(request: DataRoutingRequest = Body(..., example=DATA_ROUTING_REQUEST_EXAMPLE)):
    """
    根据数据特性和查询条件智能选择数据库路由

    Analyzes data category and query parameters to recommend optimal database routing
    strategy between PostgreSQL and TDengine.
    """
    if request.data_category in ["market_data", "derived_data"]:
        route = "tdengine"
        complexity = "high_frequency"
    else:
        route = "postgresql"
        complexity = "relational"

    return DataRoutingResponse(
        route_selected=route,
        estimated_records=1000,
        query_complexity=complexity,
        recommended_strategy="direct_query",
    )
