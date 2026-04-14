"""
交易管理API路由

使用统一的Pydantic模型和APIResponse格式
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel

from app.openapi_config import COMMON_RESPONSES
from app.core.responses import (
    APIResponse,
    ErrorCodes,
    UnifiedResponse,
    create_error_response,
    create_success_response,
)
from app.schemas.trade_schemas import (
    AccountInfo,
    Position,
    PositionsResponse,
    TradeHistoryItem,
    TradeHistoryResponse,
)

TRADE_ROUTE_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

router = APIRouter(responses=TRADE_ROUTE_RESPONSES)

TRADE_HEALTH_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {"status": "ok", "service": "trade"},
    "message": "服务正常",
    "request_id": "req-trade-health-001",
}

TRADE_PORTFOLIO_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 503,
    "message": "Trade portfolio service is not implemented yet",
    "request_id": "req-trade-portfolio-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "placeholder",
        "endpoint": "trade",
        "resource": "portfolio",
        "account": None,
    },
}

TRADE_POSITIONS_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 503,
    "message": "Trade positions service is not implemented yet",
    "request_id": "req-trade-positions-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "placeholder",
        "endpoint": "trade",
        "resource": "positions",
        "positions": [],
        "total_count": 0,
        "total_market_value": 0,
        "total_profit_loss": 0,
        "total_profit_loss_percent": 0.0,
    },
}

TRADE_SIGNALS_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 503,
    "message": "Trade signals service is not implemented yet",
    "request_id": "req-trade-signals-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "placeholder",
        "endpoint": "trade",
        "resource": "signals",
        "items": [],
        "total": 0,
    },
}

TRADE_HISTORY_RESPONSE_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trade history loaded from backtest trades",
    "request_id": "req-trade-history-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "available",
        "endpoint": "trade",
        "resource": "trades",
        "trades": [
            {
                "trade_id": "101",
                "order_id": "backtest-7-101",
                "symbol": "600519.SH",
                "direction": "buy",
                "price": "1750.00",
                "quantity": 100,
                "amount": "175000.00",
                "commission": "52.50",
                "trade_time": "2026-04-08T00:00:00",
                "trade_type": "backtest",
            }
        ],
        "total_count": 1,
        "total_amount": "175000.00",
        "total_commission": "52.50",
        "page": 1,
        "page_size": 20,
        "source": "backtest_trades",
    },
}

TRADE_STATISTICS_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 503,
    "message": "Trade statistics service is not implemented yet",
    "request_id": "req-trade-statistics-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "placeholder",
        "endpoint": "trade",
        "resource": "statistics",
        "statistics": None,
    },
}

EXECUTE_TRADE_REQUEST_EXAMPLE = {
    "direction": "buy",
    "symbol": "600519.SH",
    "quantity": 100,
    "price": 1750.0,
}

EXECUTE_TRADE_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 503,
    "message": "Trade execution service is not implemented yet",
    "request_id": "req-trade-execute-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "status": "placeholder",
        "endpoint": "trade",
        "resource": "execute",
        "accepted": False,
        "order": EXECUTE_TRADE_REQUEST_EXAMPLE,
    },
}


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


TRADE_PORTFOLIO_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("账户资产概览查询成功。", TRADE_PORTFOLIO_RESPONSE_EXAMPLE),
}

TRADE_POSITIONS_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("当前持仓列表查询成功。", TRADE_POSITIONS_RESPONSE_EXAMPLE),
}

TRADE_SIGNALS_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("交易信号列表查询成功。", TRADE_SIGNALS_RESPONSE_EXAMPLE),
}

TRADE_HISTORY_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("交易历史分页查询成功。", TRADE_HISTORY_RESPONSE_EXAMPLE),
}

TRADE_STATISTICS_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("交易统计指标查询成功。", TRADE_STATISTICS_RESPONSE_EXAMPLE),
}

TRADE_EXECUTE_RESPONSES = {
    **TRADE_ROUTE_RESPONSES,
    **_success_response_spec("交易委托执行成功。", EXECUTE_TRADE_RESPONSE_EXAMPLE),
}


def _placeholder_trade_response(message: str, resource: str, data: dict[str, Any]) -> UnifiedResponse[Dict[str, Any]]:
    return UnifiedResponse(
        success=False,
        code=503,
        message=message,
        data={
            "status": "placeholder",
            "endpoint": "trade",
            "resource": resource,
            **data,
        },
    )


def _success_trade_response(message: str, resource: str, data: dict[str, Any]) -> UnifiedResponse[Dict[str, Any]]:
    return UnifiedResponse(
        success=True,
        code=200,
        message=message,
        data={
            "status": "available",
            "endpoint": "trade",
            "resource": resource,
            **data,
        },
    )


def _query_trade_history(
    *,
    symbol: Optional[str],
    start_date_obj,
    end_date_obj,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    from app.core.database import SessionLocal
    from app.repositories.backtest_repository import BacktestTradeModel

    db = SessionLocal()
    try:
        query = db.query(BacktestTradeModel)

        if symbol:
            query = query.filter(BacktestTradeModel.symbol == symbol)
        if start_date_obj:
            query = query.filter(BacktestTradeModel.trade_date >= start_date_obj)
        if end_date_obj:
            query = query.filter(BacktestTradeModel.trade_date <= end_date_obj)

        total_count = query.count()
        offset = (page - 1) * page_size
        trade_rows = query.order_by(BacktestTradeModel.trade_date.desc()).offset(offset).limit(page_size).all()

        trades = []
        total_amount = Decimal("0")
        total_commission = Decimal("0")

        for trade in trade_rows:
            amount = Decimal(str(trade.amount))
            commission = Decimal(str(trade.commission))
            total_amount += amount
            total_commission += commission
            trades.append(
                TradeHistoryItem(
                    trade_id=str(trade.trade_id),
                    order_id=f"backtest-{trade.backtest_id}-{trade.trade_id}",
                    symbol=trade.symbol,
                    direction=trade.action,
                    price=Decimal(str(trade.price)),
                    quantity=trade.quantity,
                    amount=amount,
                    commission=commission,
                    trade_time=datetime.combine(trade.trade_date, datetime.min.time()),
                    trade_type="backtest",
                ).model_dump(mode="json")
            )

        return {
            "trades": trades,
            "total_count": total_count,
            "total_amount": total_amount,
            "total_commission": total_commission,
            "page": page,
            "page_size": page_size,
            "source": "backtest_trades",
        }
    finally:
        db.close()


# ==================== Health Check ====================


class HealthCheckResponse(BaseModel):
    """健康检查响应"""

    status: str
    service: str


@router.get(
    "/health",
    response_model=APIResponse,
    summary="交易服务健康检查",
    description="检查交易服务接口是否可用，并返回交易模块基础运行状态，用于前端探针和运维巡检。",
    responses={
        200: {
            "description": "交易服务运行正常",
            "content": {"application/json": {"example": TRADE_HEALTH_RESPONSE_EXAMPLE}},
        },
        500: COMMON_RESPONSES[500],
    },
)
async def health_check():
    """检查交易服务接口健康状态并返回基础服务信息。"""
    return create_success_response(data={"status": "ok", "service": "trade"}, message="服务正常")


# ==================== Portfolio (Account Info) ====================


@router.get("/portfolio", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_PORTFOLIO_RESPONSES)
async def get_portfolio() -> UnifiedResponse[Dict[str, Any]]:
    """
    获取投资组合概览

    返回交易投资组合接口的兼容占位响应，显式说明当前尚未接入真实账户资产服务。
    """
    return _placeholder_trade_response(
        message="Trade portfolio service is not implemented yet",
        resource="portfolio",
        data={"account": None},
    )


# ==================== Positions ====================


@router.get("/positions", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_POSITIONS_RESPONSES)
async def get_positions() -> UnifiedResponse[Dict[str, Any]]:
    """
    获取持仓列表

    返回交易持仓接口的兼容占位响应，显式说明当前尚未接入真实持仓查询服务。
    """
    return _placeholder_trade_response(
        message="Trade positions service is not implemented yet",
        resource="positions",
        data={
            "positions": [],
            "total_count": 0,
            "total_market_value": 0,
            "total_profit_loss": 0,
            "total_profit_loss_percent": 0.0,
        },
    )


@router.get("/signals", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_SIGNALS_RESPONSES)
async def get_signals(limit: int = Query(20, ge=1, le=200, description="返回的交易信号数量上限，范围 1-200")) -> UnifiedResponse[Dict[str, Any]]:
    """
    获取交易信号列表

    返回交易信号接口的兼容占位响应，显式说明当前尚未接入真实信号聚合服务。
    """
    return _placeholder_trade_response(
        message="Trade signals service is not implemented yet",
        resource="signals",
        data={"items": [], "total": 0},
    )


# ==================== Trade History ====================


@router.get("/trades", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_HISTORY_RESPONSES)
async def get_trades(
    symbol: Optional[str] = Query(None, description="股票代码 (可选)"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
) -> UnifiedResponse[Dict[str, Any]]:
    """
    获取交易记录列表

    支持参数校验，并优先返回当前仓库中已持久化的回测成交历史。
    """
    try:
        def parse_query_date(value: Optional[str], field_name: str):
            if value is None:
                return None
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=create_error_response(
                        error_code=ErrorCodes.VALIDATION_ERROR,
                        message=f"{field_name} 格式错误，应为 YYYY-MM-DD",
                    ).model_dump(),
                ) from exc

        start_date_obj = parse_query_date(start_date, "start_date")
        end_date_obj = parse_query_date(end_date, "end_date")

        if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.VALIDATION_ERROR,
                    message="start_date 不能晚于 end_date",
                ).model_dump(),
            )

        trade_history = _query_trade_history(
            symbol=symbol,
            start_date_obj=start_date_obj,
            end_date_obj=end_date_obj,
            page=page,
            page_size=page_size,
        )

        return _success_trade_response(
            message="Trade history loaded from backtest trades",
            resource="trades",
            data=trade_history,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"获取交易记录失败: {str(e)}"
            ).model_dump(),
        )


# ==================== Statistics ====================


class TradeStatistics(BaseModel):
    """交易统计数据"""

    total_trades: int
    buy_count: int
    sell_count: int
    position_count: int
    total_buy_amount: float
    total_sell_amount: float
    total_commission: float
    realized_profit: float


@router.get("/statistics", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_STATISTICS_RESPONSES)
async def get_statistics() -> UnifiedResponse[Dict[str, Any]]:
    """
    获取交易统计数据

    返回交易统计接口的兼容占位响应，显式说明当前尚未接入真实统计服务。
    """
    return _placeholder_trade_response(
        message="Trade statistics service is not implemented yet",
        resource="statistics",
        data={"statistics": None},
    )


# ==================== Execute Trade ====================


@router.post("/execute", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_EXECUTE_RESPONSES)
async def execute_trade(order: dict = Body(..., example=EXECUTE_TRADE_REQUEST_EXAMPLE)) -> UnifiedResponse[Dict[str, Any]]:
    """
    执行买卖交易

    接收交易指令并执行基础参数校验，当前版本返回显式标记未接入真实下单通道的兼容占位结果。

    Args:
        order: 交易信息字典，包含 type, symbol, quantity, price 等字段

    Returns:
        UnifiedResponse: 包含占位执行结果的响应
    """
    try:
        # 验证必填字段
        required_fields = ["direction", "symbol", "quantity"]
        if not all(field in order for field in required_fields):
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.VALIDATION_ERROR, message="缺少必填字段: direction, symbol, quantity"
                ).model_dump(),
            )

        direction = order.get("direction")
        if direction not in ["buy", "sell"]:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.INVALID_VALUE, message="交易方向必须是 buy 或 sell"
                ).model_dump(),
            )

        quantity = order.get("quantity")
        if quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.OUT_OF_RANGE, message="委托数量必须大于0"
                ).model_dump(),
            )

        # A股交易数量必须是100的整数倍
        if quantity % 100 != 0:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.INVALID_VALUE, message="委托数量必须是100的整数倍"
                ).model_dump(),
            )

        return _placeholder_trade_response(
            message="Trade execution service is not implemented yet",
            resource="execute",
            data={
                "accepted": False,
                "order": {
                    "direction": direction,
                    "symbol": order.get("symbol"),
                    "quantity": quantity,
                    "price": order.get("price"),
                },
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"交易执行失败: {str(e)}"
            ).model_dump(),
        )
