"""
数据路由API

提供智能数据路由选择功能
"""

from typing import Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/data",
    tags=["Data Routing"],
)


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


@router.post("/route", response_model=DataRoutingResponse, summary="Data Routing Decision")
async def get_data_route(request: DataRoutingRequest):
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
