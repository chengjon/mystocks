from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd

from src.indicators.indicator_factory import IndicatorFactory

router = APIRouter(prefix="/api/indicator-registry", tags=["Indicator Registry"])

# Singleton Factory
_factory = None


def get_factory():
    global _factory
    if _factory is None:
        _factory = IndicatorFactory()
    return _factory


# Models
class IndicatorInfo(BaseModel):
    indicator_id: str
    indicator_name: str
    indicator_category: str
    use_case: str
    description: Optional[str]
    status: str


class CalculationRequest(BaseModel):
    indicator_id: str
    data: List[Dict[str, Any]]  # List of rows (OHLCV)
    parameters: Optional[Dict[str, Any]] = {}


class CalculationResponse(BaseModel):
    indicator_id: str
    result: List[Optional[float]]
    length: int


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
async def get_indicator_details(indicator_id: str):
    """Get detailed configuration for a specific indicator."""
    factory = get_factory()
    if indicator_id not in factory.registry:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return factory.registry[indicator_id]


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_indicator(req: CalculationRequest):
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
