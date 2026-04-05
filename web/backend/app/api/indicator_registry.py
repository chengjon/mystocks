from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Body, HTTPException, Path
from pydantic import BaseModel, Field

from app.openapi_config import COMMON_RESPONSES
from src.indicators.indicator_factory import IndicatorFactory

INDICATOR_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(prefix="/api/indicator-registry", tags=["Indicator Registry"], responses=INDICATOR_ROUTE_RESPONSES)

# Singleton Factory
_factory = None

CALCULATION_REQUEST_EXAMPLES = {
    "sma_batch_calculation": {
        "summary": "计算简单移动平均线",
        "description": "提交三条 OHLCV 数据并用 window=3 计算 SMA。",
        "value": {
            "indicator_id": "sma",
            "data": [
                {"open": 10.1, "high": 10.5, "low": 9.9, "close": 10.3, "volume": 120000},
                {"open": 10.3, "high": 10.8, "low": 10.2, "close": 10.6, "volume": 135000},
                {"open": 10.6, "high": 10.9, "low": 10.4, "close": 10.7, "volume": 142000},
            ],
            "parameters": {"window": 3},
        },
    }
}


def get_factory():
    global _factory
    if _factory is None:
        _factory = IndicatorFactory()
    return _factory


# Models
class IndicatorInfo(BaseModel):
    """指标注册表中的单个指标信息。"""

    indicator_id: str = Field(..., description="指标唯一标识。")
    indicator_name: str = Field(..., description="指标名称。")
    indicator_category: str = Field(..., description="指标分类。")
    use_case: str = Field(..., description="典型使用场景。")
    description: Optional[str] = Field(None, description="指标功能说明。")
    status: str = Field(..., description="指标当前状态。")


class CalculationRequest(BaseModel):
    indicator_id: str = Field(..., description="指标唯一标识，例如 sma 或 ema。")
    data: List[Dict[str, Any]] = Field(..., description="用于批量计算的 OHLCV 行数据列表。")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="覆盖默认配置的可选参数。")

    model_config = {
        "json_schema_extra": {
            "example": {
                "indicator_id": "sma",
                "data": [
                    {"open": 10.1, "high": 10.5, "low": 9.9, "close": 10.3, "volume": 120000},
                    {"open": 10.3, "high": 10.8, "low": 10.2, "close": 10.6, "volume": 135000},
                    {"open": 10.6, "high": 10.9, "low": 10.4, "close": 10.7, "volume": 142000},
                ],
                "parameters": {"window": 3},
            }
        }
    }


class CalculationResponse(BaseModel):
    """指标批量计算响应。"""

    indicator_id: str = Field(..., description="已执行计算的指标ID。")
    result: List[Optional[float]] = Field(..., description="按输入顺序返回的计算结果列表。")
    length: int = Field(..., description="结果列表长度。")


@router.get("/indicators", response_model=List[IndicatorInfo])
async def list_indicators():
    """List all registered indicators."""
    factory = get_factory()
    results = []
    for i_id, config in factory.registry.items():
        results.append(
            IndicatorInfo(
                indicator_id=i_id,
                indicator_name=config.get("indicator_name", "Unknown"),
                indicator_category=config.get("indicator_category", "Unknown"),
                use_case=config.get("use_case", "Unknown"),
                description=config.get("description"),
                status=config.get("status", "active"),
            )
        )
    return results


@router.get("/indicators/{indicator_id}")
async def get_indicator_details(
    indicator_id: str = Path(..., description="指标唯一标识，用于查询单个指标的详细注册配置。")
):
    """Get detailed configuration for a specific indicator."""
    factory = get_factory()
    if indicator_id not in factory.registry:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return factory.registry[indicator_id]


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_indicator(req: CalculationRequest = Body(..., openapi_examples=CALCULATION_REQUEST_EXAMPLES)):
    """Run a batch calculation."""
    factory = get_factory()

    # Convert input JSON to DataFrame
    try:
        df = pd.DataFrame(req.data)
        if df.empty:
            raise ValueError("Input data is empty")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {e}")

    # Calculate
    try:
        # Default params from registry if not provided
        config = factory.registry.get(req.indicator_id, {})
        default_params = {k: v.get("default") for k, v in config.get("parameters", {}).items()}

        # Merge params
        params = default_params.copy()
        if req.parameters:
            params.update(req.parameters)

        result_series = factory.calculate(req.indicator_id, df, **params)

        # Replace NaN with None for JSON compliance
        result_list = result_series.where(pd.notnull(result_series), None).tolist()

        return CalculationResponse(indicator_id=req.indicator_id, result=result_list, length=len(result_list))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
