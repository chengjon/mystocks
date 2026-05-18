"""
交易管理API路由

使用统一的Pydantic模型和APIResponse格式
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel

from app.core.exceptions import BusinessException
from app.core.responses import (
    ErrorCodes,
    UnifiedResponse,
    create_error_response,
    create_unified_success_response,
)
from app.schemas.trade_schemas import (
    AccountInfo,
    Position,
    TradeHistoryItem,
)
from app.api.v1.trading.runtime_state import PositionState, SessionState, runtime_store
from app.api.trade._responses import (
    EXECUTE_TRADE_REQUEST_EXAMPLE,
    TRADE_EXECUTE_RESPONSES,
    TRADE_HEALTH_RESPONSE_EXAMPLE,
    TRADE_HISTORY_RESPONSES,
    TRADE_PORTFOLIO_RESPONSES,
    TRADE_POSITIONS_RESPONSES,
    TRADE_ROUTE_RESPONSES,
    TRADE_SIGNALS_RESPONSES,
    TRADE_STATISTICS_RESPONSES,
)

router = APIRouter(responses=TRADE_ROUTE_RESPONSES)


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


def _resolve_active_runtime_session() -> Optional[SessionState]:
    if runtime_store.current_session_id:
        session = runtime_store.get_session(runtime_store.current_session_id)
        if session is not None:
            return session
    active_sessions = runtime_store.list_sessions(status="active")
    return active_sessions[0] if active_sessions else None


def _serialize_trade_position(position: PositionState) -> dict[str, Any]:
    cost_basis = float(position.average_cost * position.quantity)
    profit_loss_percent = round((position.unrealized_pnl / cost_basis) * 100, 4) if cost_basis else 0.0
    return Position(
        symbol=position.symbol,
        symbol_name=position.name,
        quantity=position.quantity,
        available_quantity=position.quantity,
        cost_price=Decimal(str(position.average_cost)),
        current_price=Decimal(str(position.current_price)),
        market_value=Decimal(str(position.market_value)),
        profit_loss=Decimal(str(position.unrealized_pnl)),
        profit_loss_percent=profit_loss_percent,
        last_update=position.updated_at,
    ).model_dump(mode="json")


def _build_runtime_positions_payload() -> dict[str, Any]:
    positions = runtime_store.list_positions()
    total_market_value = round(sum(item.market_value for item in positions), 4)
    total_profit_loss = round(sum(item.unrealized_pnl for item in positions), 4)
    total_cost = round(sum(item.average_cost * item.quantity for item in positions), 4)
    total_profit_loss_percent = round((total_profit_loss / total_cost) * 100, 4) if total_cost else 0.0
    return {
        "positions": [_serialize_trade_position(item) for item in positions],
        "total_count": len(positions),
        "total_market_value": total_market_value,
        "total_profit_loss": total_profit_loss,
        "total_profit_loss_percent": total_profit_loss_percent,
    }


def _build_runtime_portfolio_payload() -> dict[str, Any]:
    session = _resolve_active_runtime_session()
    if session is None:
        return {"account": None}

    session_positions = runtime_store.list_positions(session_id=session.session_id)
    market_value = round(sum(item.market_value for item in session_positions), 4)
    unrealized_profit = round(sum(item.unrealized_pnl for item in session_positions), 4)
    total_profit_loss = round(session.total_pnl + unrealized_profit, 4)
    total_assets = round(session.current_capital + market_value, 4)
    profit_loss_percent = round((total_profit_loss / session.initial_capital) * 100, 4) if session.initial_capital else 0.0
    portfolio_weight = (market_value / total_assets) if total_assets else 0.0
    risk_level = "high" if portfolio_weight >= 0.8 else "medium" if portfolio_weight >= 0.5 else "low"

    account = AccountInfo(
        account_id=session.session_id,
        account_type="stock",
        total_assets=Decimal(str(total_assets)),
        cash=Decimal(str(session.current_capital)),
        market_value=Decimal(str(market_value)),
        frozen_cash=None,
        total_profit_loss=Decimal(str(total_profit_loss)),
        profit_loss_percent=profit_loss_percent,
        risk_level=risk_level,
        last_update=session.updated_at,
    )
    return {"account": account.model_dump(mode="json")}


def _build_runtime_statistics_payload() -> dict[str, Any]:
    session = _resolve_active_runtime_session()
    session_positions = runtime_store.list_positions(session_id=session.session_id) if session is not None else []
    total_buy_amount = round(sum(item.average_cost * item.quantity for item in session_positions), 4)
    statistics = TradeStatistics(
        total_trades=len(session_positions),
        buy_count=len(session_positions),
        sell_count=0,
        position_count=len(session_positions),
        total_buy_amount=total_buy_amount,
        total_sell_amount=0.0,
        total_commission=0.0,
        realized_profit=round(session.total_pnl, 4) if session is not None else 0.0,
    )
    return {
        "statistics": statistics.model_dump(mode="json"),
        "source": "trading_runtime",
    }


def _build_runtime_signals_payload(limit: int) -> dict[str, Any]:
    session = _resolve_active_runtime_session()
    if session is None:
        return {
            "items": [],
            "total": 0,
            "source": "trading_runtime",
        }

    strategy_name = session.strategy_id or "runtime_strategy"
    positions = runtime_store.list_positions(session_id=session.session_id)[:limit]
    items: list[dict[str, Any]] = []

    for position in positions:
        signal_type = "BUY"
        if position.unrealized_pnl < 0:
            signal_type = "SELL"
        elif position.unrealized_pnl == 0:
            signal_type = "HOLD"

        items.append(
            {
                "symbol": position.symbol,
                "name": position.name,
                "type": signal_type,
                "price": round(position.current_price, 4),
                "time": position.updated_at.isoformat().replace("+00:00", "Z"),
                "strategy": strategy_name,
            }
        )

    return {
        "items": items,
        "total": len(items),
        "source": "trading_runtime",
    }


def _require_active_runtime_session() -> SessionState:
    session = _resolve_active_runtime_session()
    if session is None:
        raise BusinessException(
            status_code=400,
            detail=create_error_response(
                error_code=ErrorCodes.INVALID_VALUE,
                message="当前没有活动交易会话，无法执行委托",
            ).model_dump(),
        )
    return session


def _execute_runtime_buy(*, session: SessionState, symbol: str, quantity: int, price: float) -> dict[str, Any]:
    position = runtime_store.create_position(symbol=symbol, quantity=quantity, price=price, session_id=session.session_id)
    return {
        "action": "opened",
        "position_id": position.position_id,
        "remaining_quantity": position.quantity,
        "realized_profit": 0.0,
    }


def _execute_runtime_sell(*, session: SessionState, symbol: str, quantity: int, price: float) -> dict[str, Any]:
    positions = runtime_store.list_positions(session_id=session.session_id, symbol=symbol)
    if not positions:
        raise BusinessException(
            status_code=404,
            detail=create_error_response(
                error_code=ErrorCodes.NOT_FOUND,
                message=f"未找到可卖出的持仓: {symbol}",
            ).model_dump(),
        )

    remaining_quantity = quantity
    realized_profit = 0.0
    last_position_id: Optional[str] = None
    total_available = sum(item.quantity for item in positions)

    if total_available < quantity:
        raise BusinessException(
            status_code=400,
            detail=create_error_response(
                error_code=ErrorCodes.OUT_OF_RANGE,
                message=f"可卖出数量不足: requested={quantity}, available={total_available}",
            ).model_dump(),
        )

    for position in positions:
        if remaining_quantity <= 0:
            break

        close_quantity = min(position.quantity, remaining_quantity)
        realized_delta = round((price - position.average_cost) * close_quantity, 4)
        session.current_capital = round(session.current_capital + (price * close_quantity), 4)
        session.total_pnl = round(session.total_pnl + realized_delta, 4)
        realized_profit = round(realized_profit + realized_delta, 4)
        last_position_id = position.position_id

        if close_quantity == position.quantity:
            runtime_store.positions.pop(position.position_id, None)
        else:
            position.quantity -= close_quantity
            position.market_value = round(position.quantity * position.current_price, 4)
            position.unrealized_pnl = round((position.current_price - position.average_cost) * position.quantity, 4)
            position.updated_at = datetime.now(session.updated_at.tzinfo)

        remaining_quantity -= close_quantity

    runtime_store._recalculate_session(session.session_id)  # noqa: SLF001
    remaining_positions = runtime_store.list_positions(session_id=session.session_id, symbol=symbol)
    return {
        "action": "closed" if not remaining_positions else "reduced",
        "position_id": last_position_id,
        "remaining_quantity": total_available - quantity,
        "realized_profit": realized_profit,
    }


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
            quantity = int(trade.amount or 0)
            price = Decimal(str(trade.price or 0))
            amount = Decimal(str(trade.total_cost)) if trade.total_cost is not None else price * Decimal(str(quantity))
            commission = Decimal(str(trade.commission or 0))
            total_amount += amount
            total_commission += commission
            trade_time = (
                trade.trade_date
                if isinstance(trade.trade_date, datetime)
                else datetime.combine(trade.trade_date, datetime.min.time())
            )
            trades.append(
                TradeHistoryItem(
                    trade_id=str(trade.id),
                    order_id=f"backtest-{trade.backtest_id}-{trade.id}",
                    symbol=trade.symbol,
                    direction=trade.direction,
                    price=price,
                    quantity=quantity,
                    amount=amount,
                    commission=commission,
                    trade_time=trade_time,
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
    response_model=UnifiedResponse,
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
    return create_unified_success_response(data={"status": "ok", "service": "trade"}, message="服务正常")


# ==================== Portfolio (Account Info) ====================


@router.get("/portfolio", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_PORTFOLIO_RESPONSES)
async def get_portfolio() -> UnifiedResponse[Dict[str, Any]]:
    """
    获取投资组合概览

    返回当前活动交易会话推导出的账户资产视图。
    """
    return _success_trade_response(
        message="Trade portfolio loaded from trading runtime",
        resource="portfolio",
        data=_build_runtime_portfolio_payload(),
    )


# ==================== Positions ====================


@router.get("/positions", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_POSITIONS_RESPONSES)
async def get_positions() -> UnifiedResponse[Dict[str, Any]]:
    """
    获取持仓列表

    返回与交易会话共享运行时中的当前持仓列表。
    """
    return _success_trade_response(
        message="Trade positions loaded from trading runtime",
        resource="positions",
        data=_build_runtime_positions_payload(),
    )


@router.get("/signals", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_SIGNALS_RESPONSES)
async def get_signals(limit: int = Query(20, ge=1, le=200, description="返回的交易信号数量上限，范围 1-200")) -> UnifiedResponse[Dict[str, Any]]:
    """
    获取交易信号列表

    返回基于当前交易运行时持仓派生的轻量信号列表。
    """
    return _success_trade_response(
        message="Trade signals derived from trading runtime",
        resource="signals",
        data=_build_runtime_signals_payload(limit),
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
                raise BusinessException(
                    status_code=400,
                    detail=create_error_response(
                        error_code=ErrorCodes.VALIDATION_ERROR,
                        message=f"{field_name} 格式错误，应为 YYYY-MM-DD",
                    ).model_dump(),
                ) from exc

        start_date_obj = parse_query_date(start_date, "start_date")
        end_date_obj = parse_query_date(end_date, "end_date")

        if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
            raise BusinessException(
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
    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(
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

    返回当前活动交易会话的运行时统计摘要。
    """
    return _success_trade_response(
        message="Trade statistics summarized from trading runtime",
        resource="statistics",
        data=_build_runtime_statistics_payload(),
    )


# ==================== Execute Trade ====================


@router.post("/execute", response_model=UnifiedResponse[Dict[str, Any]], responses=TRADE_EXECUTE_RESPONSES)
async def execute_trade(order: dict = Body(..., example=EXECUTE_TRADE_REQUEST_EXAMPLE)) -> UnifiedResponse[Dict[str, Any]]:
    """
    执行买卖交易

    接收交易指令并执行基础参数校验，然后把结果回写到当前活动交易会话的运行时状态。

    Args:
        order: 交易信息字典，包含 type, symbol, quantity, price 等字段

    Returns:
        UnifiedResponse: 包含占位执行结果的响应
    """
    try:
        # 验证必填字段
        required_fields = ["direction", "symbol", "quantity"]
        if not all(field in order for field in required_fields):
            raise BusinessException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.VALIDATION_ERROR, message="缺少必填字段: direction, symbol, quantity"
                ).model_dump(),
            )

        direction = order.get("direction")
        if direction not in ["buy", "sell"]:
            raise BusinessException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.INVALID_VALUE, message="交易方向必须是 buy 或 sell"
                ).model_dump(),
            )

        quantity = order.get("quantity")
        if quantity <= 0:
            raise BusinessException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.OUT_OF_RANGE, message="委托数量必须大于0"
                ).model_dump(),
            )

        # A股交易数量必须是100的整数倍
        if quantity % 100 != 0:
            raise BusinessException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.INVALID_VALUE, message="委托数量必须是100的整数倍"
                ).model_dump(),
            )

        price = order.get("price")
        if price is None or float(price) <= 0:
            raise BusinessException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.OUT_OF_RANGE, message="委托价格必须大于0"
                ).model_dump(),
            )

        session = _require_active_runtime_session()
        normalized_symbol = str(order.get("symbol")).strip()
        execution_result = (
            _execute_runtime_buy(session=session, symbol=normalized_symbol, quantity=quantity, price=float(price))
            if direction == "buy"
            else _execute_runtime_sell(session=session, symbol=normalized_symbol, quantity=quantity, price=float(price))
        )

        return _success_trade_response(
            message="Trade order executed in trading runtime",
            resource="execute",
            data={
                "accepted": True,
                "execution_mode": "runtime",
                "session_id": session.session_id,
                "order": {
                    "direction": direction,
                    "symbol": normalized_symbol,
                    "quantity": quantity,
                    "price": float(price),
                },
                "result": execution_result,
            },
        )
    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"交易执行失败: {str(e)}"
            ).model_dump(),
        )
