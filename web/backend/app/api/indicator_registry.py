from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Body, Depends, Path

from app.core.exceptions import BusinessException
from app.core.responses import UnifiedResponse, create_unified_success_response
from pydantic import BaseModel, Field

from app.openapi_config import COMMON_RESPONSES
from src.indicators.indicator_factory import IndicatorFactory

INDICATOR_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(prefix="/api/indicator-registry", tags=["Indicator Registry"], responses=INDICATOR_ROUTE_RESPONSES)

# Singleton Factory
_factory = None


def _success_response_spec(description: str, example: object) -> dict[int, dict]:
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


INDICATOR_INFO_EXAMPLE = {
    "indicator_id": "sma.5",
    "indicator_name": "SMA",
    "indicator_category": "Unknown",
    "use_case": "Unknown",
    "description": None,
    "status": "active",
}

INDICATOR_DETAIL_EXAMPLE = {
    "indicator_id": "sma.5",
    "indicator_name": "SMA",
    "class_name": "SMAIndicator",
    "module_path": "src.indicators.implementations.trend.sma",
    "supports_streaming": True,
    "parameters": {"period": {"default": 5}},
    "required_columns": ["close"],
    "output_columns": ["sma"],
}

CALCULATION_RESPONSE_EXAMPLE = {
    "indicator_id": "sma.5",
    "result": [None, None, None, None, 10.48],
    "length": 5,
}

CALCULATION_REQUEST_EXAMPLES = {
    "sma_batch_calculation": {
        "summary": "计算简单移动平均线",
        "description": "提交五条 OHLCV 数据并用 period=5 计算 SMA。",
        "value": {
            "indicator_id": "sma.5",
            "data": [
                {"open": 10.1, "high": 10.5, "low": 9.9, "close": 10.3, "volume": 120000},
                {"open": 10.3, "high": 10.8, "low": 10.2, "close": 10.6, "volume": 135000},
                {"open": 10.6, "high": 10.9, "low": 10.4, "close": 10.7, "volume": 142000},
                {"open": 10.7, "high": 10.95, "low": 10.5, "close": 10.4, "volume": 150000},
                {"open": 10.4, "high": 10.7, "low": 10.2, "close": 10.4, "volume": 128000},
            ],
            "parameters": {"period": 5},
        },
    }
}

INDICATOR_LIST_RESPONSES = {
    **INDICATOR_ROUTE_RESPONSES,
    **_success_response_spec("指标注册表摘要列表。", [INDICATOR_INFO_EXAMPLE]),
}

INDICATOR_DETAIL_RESPONSES = {
    **INDICATOR_ROUTE_RESPONSES,
    **_success_response_spec("单个指标的注册配置详情。", INDICATOR_DETAIL_EXAMPLE),
}

INDICATOR_CALCULATE_RESPONSES = {
    **INDICATOR_ROUTE_RESPONSES,
    **_success_response_spec("指标批量计算结果。", CALCULATION_RESPONSE_EXAMPLE),
}


def get_factory() -> IndicatorFactory:
    global _factory
    if _factory is None:
        _factory = IndicatorFactory()
    return _factory


def get_indicator_factory() -> IndicatorFactory:
    return get_factory()


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
    """指标批量计算请求。"""

    indicator_id: str = Field(..., description="指标唯一标识，例如 sma 或 ema。")
    data: List[Dict[str, Any]] = Field(..., description="用于批量计算的 OHLCV 行数据列表。")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="覆盖默认配置的可选参数。")

    model_config = {
        "json_schema_extra": {
            "example": {
                "indicator_id": "sma.5",
                "data": [
                    {"open": 10.1, "high": 10.5, "low": 9.9, "close": 10.3, "volume": 120000},
                    {"open": 10.3, "high": 10.8, "low": 10.2, "close": 10.6, "volume": 135000},
                    {"open": 10.6, "high": 10.9, "low": 10.4, "close": 10.7, "volume": 142000},
                    {"open": 10.7, "high": 10.95, "low": 10.5, "close": 10.4, "volume": 150000},
                    {"open": 10.4, "high": 10.7, "low": 10.2, "close": 10.4, "volume": 128000},
                ],
                "parameters": {"period": 5},
            }
        }
    }


class CalculationResponse(BaseModel):
    """指标批量计算响应。"""

    indicator_id: str = Field(..., description="已执行计算的指标ID。")
    result: List[Optional[float]] = Field(..., description="按输入顺序返回的计算结果列表。")
    length: int = Field(..., description="结果列表长度。")


@router.get(
    "/indicators",
    response_model=UnifiedResponse[List[IndicatorInfo]],
    summary="列出已注册技术指标",
    description="返回指标注册表中的全部指标摘要，供前端配置面板、功能发现和下拉选择器读取。",
    responses=INDICATOR_LIST_RESPONSES,
)
async def list_indicators(factory: IndicatorFactory = Depends(get_indicator_factory)):
    """List all registered indicators."""
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
    return create_unified_success_response(data=results)


@router.get(
    "/indicators/{indicator_id}",
    response_model=UnifiedResponse,
    summary="查询单个指标注册配置",
    description="根据指标 ID 返回注册表中的详细配置，包括实现类、参数定义和输入输出列说明。",
    responses=INDICATOR_DETAIL_RESPONSES,
)
async def get_indicator_details(
    indicator_id: str = Path(..., description="指标唯一标识，用于查询单个指标的详细注册配置。"),
    factory: IndicatorFactory = Depends(get_indicator_factory),
):
    """Get detailed configuration for a specific indicator."""
    if indicator_id not in factory.registry:
        raise BusinessException(status_code=404, detail="Indicator not found")
    return create_unified_success_response(data=factory.registry[indicator_id])


@router.post(
    "/calculate",
    response_model=UnifiedResponse[CalculationResponse],
    summary="执行指标批量计算",
    description="接收一组 OHLCV 数据和可选参数，执行指定技术指标的批量计算并返回对齐后的结果序列。",
    responses=INDICATOR_CALCULATE_RESPONSES,
)
async def calculate_indicator(
    req: CalculationRequest = Body(..., openapi_examples=CALCULATION_REQUEST_EXAMPLES),
    factory: IndicatorFactory = Depends(get_indicator_factory),
):
    """Run a batch calculation."""

    # Convert input JSON to DataFrame
    try:
        df = pd.DataFrame(req.data)
        if df.empty:
            raise ValueError("Input data is empty")
    except Exception as e:
        raise BusinessException(status_code=400, detail=f"Invalid data format: {e}")

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

        return create_unified_success_response(
            data=CalculationResponse(indicator_id=req.indicator_id, result=result_list, length=len(result_list))
        )

    except ValueError as e:
        raise BusinessException(status_code=400, detail=str(e))
    except Exception as e:
        raise BusinessException(status_code=500, detail=str(e))
