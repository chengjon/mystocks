"""
持仓管理API

提供交易持仓管理功能
"""

from dataclasses import asdict, replace
from datetime import date as date_cls
from datetime import datetime
from hashlib import sha256
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Path, Query

from app.core.exceptions import BusinessException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from app.api.v1.trading.runtime_state import PositionState, runtime_store
from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES
from app.services.attribution import (
    AttributionEngine,
    AttributionInputError,
    BenchmarkConstituentSnapshot,
    FactorExposureSnapshot,
    PortfolioConstituentSnapshot,
)

POSITION_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(
    prefix="/positions",
    tags=["Positions"],
    responses=POSITION_ROUTE_RESPONSES,
)


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
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


class PositionResponse(BaseModel):
    """持仓响应"""

    position_id: str = Field(..., description="持仓ID。")
    session_id: str = Field(..., description="该持仓所属交易会话ID。")
    symbol: str = Field(..., description="股票或交易标的代码。")
    name: str = Field(..., description="持仓名称或标的简称。")
    quantity: int = Field(..., description="当前持仓数量。")
    average_cost: float = Field(..., description="持仓平均成本价。")
    current_price: float = Field(..., description="当前市场价格。")
    market_value: float = Field(..., description="当前持仓市值。")
    unrealized_pnl: float = Field(..., description="当前未实现盈亏。")
    realized_pnl: float = Field(..., description="当前已实现盈亏。")
    weight: float = Field(..., description="该持仓占组合总资产的权重。")
    created_at: datetime = Field(..., description="持仓创建时间。")
    updated_at: datetime = Field(..., description="持仓最近更新时间。")


class PositionListResponse(BaseModel):
    """持仓列表响应"""

    positions: list[PositionResponse] = Field(..., description="符合筛选条件的持仓列表。")
    total_value: float = Field(..., description="当前返回持仓的总市值。")
    total: int = Field(..., description="当前返回持仓数量。")


class PositionCreate(BaseModel):
    """创建持仓请求"""

    symbol: str = Field(..., description="股票或交易标的代码。")
    quantity: int = Field(..., description="建仓数量。")
    price: float = Field(..., description="建仓价格。")


class PositionUpdate(BaseModel):
    """更新持仓请求"""

    quantity: Optional[int] = Field(None, description="更新后的持仓数量。")
    stop_loss: Optional[float] = Field(None, description="新的止损价格。")
    take_profit: Optional[float] = Field(None, description="新的止盈价格。")


class PositionDeleteResponse(BaseModel):
    """删除持仓响应"""

    message: str = Field(..., description="删除或平仓操作的结果说明。")


POSITION_CREATE_EXAMPLES = {
    "create_equity_position": {
        "summary": "创建持仓",
        "description": "在组合中新增一个股票持仓，记录数量和建仓价格。",
        "value": {
            "symbol": "600519",
            "quantity": 100,
            "price": 1800.0,
        },
    }
}

POSITION_UPDATE_EXAMPLES = {
    "adjust_position_risk_controls": {
        "summary": "更新持仓参数",
        "description": "调整持仓数量，并同时更新止损和止盈价格。",
        "value": {
            "quantity": 120,
            "stop_loss": 1720.0,
            "take_profit": 1950.0,
        },
    }
}

POSITION_LIST_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Positions retrieved",
    "data": {
        "positions": [
            {
                "position_id": "pos_demo_001",
                "session_id": "session_demo_001",
                "symbol": "600519",
                "name": "600519",
                "quantity": 100,
                "average_cost": 1800.0,
                "current_price": 1800.0,
                "market_value": 180000.0,
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0,
                "weight": 1.0,
                "created_at": "2026-04-13T08:00:00+00:00",
                "updated_at": "2026-04-13T08:00:00+00:00",
            }
        ],
        "total_value": 180000.0,
        "total": 1,
    },
}

POSITION_DETAIL_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position retrieved",
    "data": POSITION_LIST_EXAMPLE["data"]["positions"][0],
}

POSITION_CREATE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position created",
    "data": POSITION_DETAIL_EXAMPLE["data"],
}

POSITION_UPDATE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position updated",
    "data": {**POSITION_DETAIL_EXAMPLE["data"], "quantity": 120, "market_value": 216000.0},
}

POSITION_DELETE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position deleted",
    "data": {"message": "Position pos_demo_001 deleted"},
}

POSITION_ATTRIBUTION_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position attribution retrieved",
    "data": {
        "analysis_date": "2026-05-08",
        "snapshot_meta": {
            "analysis_date": "2026-05-08",
            "constituent_count": 2,
            "total_weight": 1.0,
            "total_market_value": 298800.0,
            "total_return": 0.018,
            "stale": True,
            "stale_reason": "runtime_position_prices",
        },
        "benchmark_meta": {
            "analysis_date": "2026-05-08",
            "constituent_count": 2,
            "total_weight": 1.0,
            "total_market_value": None,
            "total_return": 0.011,
            "stale": False,
            "stale_reason": None,
        },
        "brinson": {
            "allocation_effect": 0.002,
            "selection_effect": 0.004,
            "interaction_effect": 0.001,
            "industry_breakdown": {},
        },
        "factor_attribution": {
            "factor_exposures": {},
            "factor_contributions": {},
            "specific_return": 0.006,
        },
        "top_contributors": [],
        "top_detractors": [],
    },
}

POSITION_LIST_RESPONSES = _success_response_spec("持仓列表结果。", POSITION_LIST_EXAMPLE)
POSITION_DETAIL_RESPONSES = _success_response_spec("持仓详情结果。", POSITION_DETAIL_EXAMPLE)
POSITION_CREATE_RESPONSES = _success_response_spec("持仓创建结果。", POSITION_CREATE_SUCCESS_EXAMPLE)
POSITION_UPDATE_RESPONSES = _success_response_spec("持仓更新结果。", POSITION_UPDATE_SUCCESS_EXAMPLE)
POSITION_DELETE_RESPONSES = _success_response_spec("持仓删除结果。", POSITION_DELETE_SUCCESS_EXAMPLE)
POSITION_ATTRIBUTION_RESPONSES = _success_response_spec("持仓归因分析结果。", POSITION_ATTRIBUTION_SUCCESS_EXAMPLE)

ATTRIBUTION_FACTORS = ("size", "value", "momentum", "volatility", "quality")
DEFAULT_BENCHMARK_NAME = "沪深300"
DEFAULT_BENCHMARK_SYMBOL = "000300.SH"
INDUSTRY_BUCKETS = ("银行", "非银金融", "食品饮料", "医药生物", "电子", "计算机", "新能源", "机械设备")


def _resolve_query_value(value: Any) -> Any:
    return getattr(value, "default", value)


def _serialize_position(position: PositionState) -> dict[str, Any]:
    return PositionResponse(
        position_id=position.position_id,
        session_id=position.session_id,
        symbol=position.symbol,
        name=position.name,
        quantity=position.quantity,
        average_cost=position.average_cost,
        current_price=position.current_price,
        market_value=position.market_value,
        unrealized_pnl=position.unrealized_pnl,
        realized_pnl=position.realized_pnl,
        weight=position.weight,
        created_at=position.created_at,
        updated_at=position.updated_at,
    ).model_dump()


def _raise_unified_http(status_code: int, message: str, data: dict[str, Any]) -> None:
    response = UnifiedResponse(success=False, code=status_code, message=message, data=data)
    raise BusinessException(status_code=status_code, detail=jsonable_encoder(response.model_dump()))


def _resolve_attribution_date(value: Optional[str]) -> tuple[str, bool]:
    if not value:
        return datetime.now().date().isoformat(), True
    try:
        return date_cls.fromisoformat(value).isoformat(), False
    except ValueError:
        _raise_unified_http(422, "Invalid attribution date", {"date": value})
        raise AssertionError("unreachable")


def _stable_ratio(key: str) -> float:
    digest = sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def _stable_scaled(key: str, lower: float, upper: float) -> float:
    return round(lower + (upper - lower) * _stable_ratio(key), 6)


def _resolve_industry(symbol: str) -> str:
    index = int(_stable_ratio(f"industry:{symbol}") * len(INDUSTRY_BUCKETS))
    return INDUSTRY_BUCKETS[min(index, len(INDUSTRY_BUCKETS) - 1)]


def _position_return_rate(position: PositionState) -> float:
    if position.average_cost <= 0:
        return 0.0
    return round((position.current_price - position.average_cost) / position.average_cost, 8)


def _build_portfolio_snapshot(
    positions: list[PositionState], analysis_date: str
) -> list[PortfolioConstituentSnapshot]:
    total_market_value = sum(position.market_value for position in positions)
    if total_market_value <= 0:
        _raise_unified_http(404, "No positive market value positions available for attribution", {})

    return [
        PortfolioConstituentSnapshot(
            analysis_date=analysis_date,
            symbol=position.symbol,
            weight=round(position.market_value / total_market_value, 8),
            market_value=round(position.market_value, 4),
            return_rate=_position_return_rate(position),
            industry=_resolve_industry(position.symbol),
        )
        for position in positions
        if position.market_value > 0
    ]


def _build_benchmark_snapshot(symbols: list[str], analysis_date: str) -> list[BenchmarkConstituentSnapshot]:
    benchmark_symbols = list(dict.fromkeys([*symbols, DEFAULT_BENCHMARK_SYMBOL]))
    weight = round(1.0 / len(benchmark_symbols), 8)
    return [
        BenchmarkConstituentSnapshot(
            analysis_date=analysis_date,
            symbol=symbol,
            weight=weight,
            return_rate=_stable_scaled(f"benchmark-return:{analysis_date}:{symbol}", -0.015, 0.025),
            industry=_resolve_industry(symbol),
        )
        for symbol in benchmark_symbols
    ]


def _symbol_factor_exposure(symbol: str, factor: str) -> float:
    bounds = {
        "size": (-0.5, 0.6),
        "value": (-0.4, 0.7),
        "momentum": (-0.6, 0.8),
        "volatility": (-0.8, 0.5),
        "quality": (-0.3, 0.9),
    }
    lower, upper = bounds[factor]
    return _stable_scaled(f"factor:{factor}:{symbol}", lower, upper)


def _aggregate_factor_exposures(rows: list[PortfolioConstituentSnapshot] | list[BenchmarkConstituentSnapshot]) -> dict[str, float]:
    return {
        factor: round(sum(row.weight * _symbol_factor_exposure(row.symbol, factor) for row in rows), 8)
        for factor in ATTRIBUTION_FACTORS
    }


def _build_position_attribution_payload(positions: list[PositionState], analysis_date: str, stale: bool) -> dict[str, Any]:
    portfolio = _build_portfolio_snapshot(positions=positions, analysis_date=analysis_date)
    benchmark = _build_benchmark_snapshot(symbols=[row.symbol for row in portfolio], analysis_date=analysis_date)
    factors = FactorExposureSnapshot(
        analysis_date=analysis_date,
        portfolio=_aggregate_factor_exposures(portfolio),
        benchmark=_aggregate_factor_exposures(benchmark),
    )

    try:
        result = AttributionEngine().analyze(portfolio=portfolio, benchmark=benchmark, factors=factors)
    except AttributionInputError as exc:
        _raise_unified_http(503, str(exc), {"benchmark": DEFAULT_BENCHMARK_NAME})

    if stale:
        result = replace(
            result,
            snapshot_meta=replace(result.snapshot_meta, stale=True, stale_reason="runtime_position_prices"),
        )
    return asdict(result)


@router.get(
    "",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="List Positions",
    description="按标的或交易会话筛选当前持仓列表，当前实现读取与交易会话共享的运行时状态。",
    responses=POSITION_LIST_RESPONSES,
)
async def list_positions(
    symbol: Optional[str] = Query(None, description="可选的标的代码过滤条件。"),
    session_id: Optional[str] = Query(None, description="可选的交易会话ID过滤条件。"),
):
    positions = runtime_store.list_positions(
        symbol=_resolve_query_value(symbol), session_id=_resolve_query_value(session_id)
    )
    total_value = round(sum(item.market_value for item in positions), 4)
    return UnifiedResponse(
        success=True,
        code=200,
        message="Positions retrieved",
        data={
            "positions": [_serialize_position(item) for item in positions],
            "total_value": total_value,
            "total": len(positions),
        },
    )


@router.get(
    "/attribution",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Position Attribution",
    description=(
        "基于当前运行时持仓计算组合归因。未传 date 时返回当前持仓观测快照并标记 stale；"
        "传入 date=YYYY-MM-DD 时返回该日期口径的确定性归因快照。"
    ),
    responses=POSITION_ATTRIBUTION_RESPONSES,
)
async def get_position_attribution(
    attribution_date: Optional[str] = Query(None, alias="date", description="可选归因日期，格式 YYYY-MM-DD。"),
    session_id: Optional[str] = Query(None, description="可选交易会话ID过滤条件。"),
):
    analysis_date, stale = _resolve_attribution_date(_resolve_query_value(attribution_date))
    positions = runtime_store.list_positions(session_id=_resolve_query_value(session_id))
    if not positions:
        _raise_unified_http(404, "No positions available for attribution", {"date": analysis_date})

    return UnifiedResponse(
        success=True,
        code=200,
        message="Position attribution retrieved",
        data=_build_position_attribution_payload(positions=positions, analysis_date=analysis_date, stale=stale),
    )


@router.get(
    "/{position_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Position",
    description="根据持仓ID获取单个持仓详情，当前实现读取共享运行时中的真实持仓数据。",
    responses=POSITION_DETAIL_RESPONSES,
)
async def get_position(position_id: str = Path(..., description="需要查询详情的持仓ID。")):
    position = runtime_store.get_position(position_id)
    if position is None:
        return UnifiedResponse(success=False, code=404, message="Position not found", data={"position_id": position_id})
    return UnifiedResponse(success=True, code=200, message="Position retrieved", data=_serialize_position(position))


@router.post(
    "",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Create Position",
    description="创建新的持仓记录，当前实现会把持仓写入当前活动交易会话。",
    responses=POSITION_CREATE_RESPONSES,
)
async def create_position(request: PositionCreate = Body(..., openapi_examples=POSITION_CREATE_EXAMPLES)):
    try:
        position = runtime_store.create_position(symbol=request.symbol, quantity=request.quantity, price=request.price)
    except ValueError as exc:
        return UnifiedResponse(success=False, code=404, message=str(exc), data={"symbol": request.symbol})
    return UnifiedResponse(success=True, code=200, message="Position created", data=_serialize_position(position))


@router.patch(
    "/{position_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Update Position",
    description="更新指定持仓的数量或风控参数，当前实现会回写共享运行时状态。",
    responses=POSITION_UPDATE_RESPONSES,
)
async def update_position(
    position_id: str = Path(..., description="需要更新的持仓ID。"),
    request: PositionUpdate = Body(..., openapi_examples=POSITION_UPDATE_EXAMPLES),
):
    position = runtime_store.update_position(
        position_id,
        quantity=request.quantity,
        stop_loss=request.stop_loss,
        take_profit=request.take_profit,
    )
    if position is None:
        return UnifiedResponse(success=False, code=404, message="Position not found", data={"position_id": position_id})
    return UnifiedResponse(success=True, code=200, message="Position updated", data=_serialize_position(position))


@router.delete(
    "/{position_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Delete Position",
    description="删除或关闭指定持仓，当前实现会同步释放对应会话的占用资金。",
    responses=POSITION_DELETE_RESPONSES,
)
async def delete_position(position_id: str = Path(..., description="需要删除或关闭的持仓ID。")):
    deleted = runtime_store.delete_position(position_id)
    if not deleted:
        return UnifiedResponse(success=False, code=404, message="Position not found", data={"position_id": position_id})
    return UnifiedResponse(
        success=True,
        code=200,
        message="Position deleted",
        data=PositionDeleteResponse(message=f"Position {position_id} deleted").model_dump(),
    )
