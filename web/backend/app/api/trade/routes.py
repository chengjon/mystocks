"""
交易管理API路由

使用统一的Pydantic模型和APIResponse格式
"""

from typing import Any, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel

from app.openapi_config import COMMON_RESPONSES
from app.core.responses import (
    APIResponse,
    ErrorCodes,
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
    "success": True,
    "message": "获取账户信息成功",
    "request_id": "req-trade-portfolio-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "account_id": "ACC_DEMO_001",
        "account_type": "stock",
        "total_assets": "1175000.00",
        "cash": "150000.00",
        "market_value": "1025000.00",
        "frozen_cash": None,
        "total_profit_loss": "55000.00",
        "profit_loss_percent": 4.91,
        "risk_level": "low",
        "last_update": "2026-04-08T04:20:00Z",
    },
}

TRADE_POSITIONS_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "获取持仓列表成功，共2只股票",
    "request_id": "req-trade-positions-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "positions": [
            {
                "symbol": "600519.SH",
                "symbol_name": "贵州茅台",
                "quantity": 500,
                "available_quantity": 500,
                "cost_price": "1650.00",
                "current_price": "1750.00",
                "market_value": "875000.00",
                "profit_loss": "50000.00",
                "profit_loss_percent": 6.06,
                "last_update": "2026-04-08T04:20:00Z",
            },
            {
                "symbol": "000858.SZ",
                "symbol_name": "五粮液",
                "quantity": 1000,
                "available_quantity": 1000,
                "cost_price": "145.00",
                "current_price": "150.00",
                "market_value": "150000.00",
                "profit_loss": "5000.00",
                "profit_loss_percent": 3.45,
                "last_update": "2026-04-08T04:20:00Z",
            },
        ],
        "total_count": 2,
        "total_market_value": "1025000.00",
        "total_profit_loss": "55000.00",
        "total_profit_loss_percent": 5.67,
    },
}

TRADE_SIGNALS_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "获取交易信号成功",
    "request_id": "req-trade-signals-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "items": [
            {
                "symbol": "600519.SH",
                "name": "贵州茅台",
                "type": "BUY",
                "price": 1750.0,
                "time": "10:15:00",
                "strategy": "MomentumAlpha",
            },
            {
                "symbol": "000858.SZ",
                "name": "五粮液",
                "type": "SELL",
                "price": 150.0,
                "time": "10:18:00",
                "strategy": "MeanReversion",
            },
        ],
        "total": 2,
    },
}

TRADE_HISTORY_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "获取交易记录成功，共2条记录",
    "request_id": "req-trade-history-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "trades": [
            {
                "trade_id": "TRD001",
                "order_id": "ORDER001",
                "symbol": "600519.SH",
                "direction": "buy",
                "price": "1650.00",
                "quantity": 500,
                "amount": "825000.00",
                "commission": "82.50",
                "trade_time": "2026-04-08T09:35:00Z",
                "trade_type": "normal",
            },
            {
                "trade_id": "TRD002",
                "order_id": "ORDER002",
                "symbol": "000858.SZ",
                "direction": "buy",
                "price": "145.00",
                "quantity": 1000,
                "amount": "145000.00",
                "commission": "145.00",
                "trade_time": "2026-04-08T10:05:00Z",
                "trade_type": "normal",
            },
        ],
        "total_count": 2,
        "total_amount": "970000.00",
        "total_commission": "227.50",
        "page": 1,
        "page_size": 20,
    },
}

TRADE_STATISTICS_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "获取交易统计成功",
    "request_id": "req-trade-statistics-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "total_trades": 3,
        "buy_count": 2,
        "sell_count": 1,
        "position_count": 2,
        "total_buy_amount": 970000.0,
        "total_sell_amount": 100000.0,
        "total_commission": 277.5,
        "realized_profit": -870000.0,
    },
}

EXECUTE_TRADE_REQUEST_EXAMPLE = {
    "direction": "buy",
    "symbol": "600519.SH",
    "quantity": 100,
    "price": 1750.0,
}

EXECUTE_TRADE_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "买入委托成功",
    "request_id": "req-trade-execute-001",
    "timestamp": "2026-04-08T04:20:00Z",
    "data": {
        "order_id": "ORDER_ABC123DEF456",
        "direction": "buy",
        "symbol": "600519.SH",
        "quantity": 100,
        "price": 1750.0,
        "trade_amount": 175000.0,
        "commission": 87.5,
        "total_amount": 175087.5,
        "status": "completed",
        "trade_time": "2026-04-08T04:20:00Z",
        "message": "买入成功",
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


@router.get("/portfolio", response_model=APIResponse, responses=TRADE_PORTFOLIO_RESPONSES)
async def get_portfolio():
    """
    获取投资组合概览

    返回账户总资产、可用资金、持仓市值、盈亏等信息
    """
    try:
        from datetime import datetime
        from decimal import Decimal

        positions_snapshot = [
            {"market_value": Decimal("875000.00"), "profit_loss": Decimal("50000.00")},
            {"market_value": Decimal("150000.00"), "profit_loss": Decimal("5000.00")},
        ]
        cash = Decimal("150000.00")
        market_value = sum(item["market_value"] for item in positions_snapshot)
        total_profit_loss = sum(item["profit_loss"] for item in positions_snapshot)
        total_assets = cash + market_value
        cost_basis = total_assets - total_profit_loss
        profit_loss_percent = float((total_profit_loss / cost_basis) * 100) if cost_basis > 0 else 0.0

        account_data = AccountInfo(
            account_id="ACC_DEMO_001",
            account_type="stock",
            total_assets=total_assets,
            cash=cash,
            market_value=market_value,
            frozen_cash=None,
            total_profit_loss=total_profit_loss,
            profit_loss_percent=round(profit_loss_percent, 2),
            risk_level="low",
            last_update=datetime.now(),
        )

        return create_success_response(data=account_data.model_dump(), message="获取账户信息成功")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"获取账户信息失败: {str(e)}"
            ).model_dump(),
        )


# ==================== Positions ====================


@router.get("/positions", response_model=APIResponse, responses=TRADE_POSITIONS_RESPONSES)
async def get_positions():
    """
    获取持仓列表

    返回用户当前所有持仓的详细信息，包括股票代码、数量、成本价、当前价、盈亏等
    """
    try:
        from datetime import datetime
        from decimal import Decimal

        # TODO: 实际应从数据库查询
        # 返回模拟数据用于演示
        positions = [
            Position(
                symbol="600519.SH",
                symbol_name="贵州茅台",
                quantity=500,
                available_quantity=500,
                cost_price=Decimal("1650.00"),
                current_price=Decimal("1750.00"),
                market_value=Decimal("875000.00"),
                profit_loss=Decimal("50000.00"),
                profit_loss_percent=6.06,
                last_update=datetime.now(),
            ),
            Position(
                symbol="000858.SZ",
                symbol_name="五粮液",
                quantity=1000,
                available_quantity=1000,
                cost_price=Decimal("145.00"),
                current_price=Decimal("150.00"),
                market_value=Decimal("150000.00"),
                profit_loss=Decimal("5000.00"),
                profit_loss_percent=3.45,
                last_update=datetime.now(),
            ),
        ]

        # 计算汇总数据
        total_count = len(positions)
        total_market_value = sum(p.market_value for p in positions)
        total_profit_loss = sum(p.profit_loss for p in positions)
        total_profit_loss_percent = (
            (total_profit_loss / (total_market_value - total_profit_loss)) * 100
            if total_market_value != total_profit_loss
            else 0.0
        )

        positions_response = PositionsResponse(
            positions=[p.model_dump() for p in positions],
            total_count=total_count,
            total_market_value=total_market_value,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percent=round(total_profit_loss_percent, 2),
        )

        return create_success_response(
            data=positions_response.model_dump(), message=f"获取持仓列表成功，共{total_count}只股票"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"获取持仓列表失败: {str(e)}"
            ).model_dump(),
        )


@router.get("/signals", response_model=APIResponse, responses=TRADE_SIGNALS_RESPONSES)
async def get_signals(limit: int = Query(20, ge=1, le=200, description="返回的交易信号数量上限，范围 1-200")):
    """
    获取交易信号列表

    返回用于策略/交易页面展示的信号数据。
    """
    try:
        from datetime import datetime

        signals = [
            {
                "symbol": "600519.SH",
                "name": "贵州茅台",
                "type": "BUY",
                "price": 1750.0,
                "time": datetime.now().strftime("%H:%M:%S"),
                "strategy": "MomentumAlpha",
            },
            {
                "symbol": "000858.SZ",
                "name": "五粮液",
                "type": "SELL",
                "price": 150.0,
                "time": datetime.now().strftime("%H:%M:%S"),
                "strategy": "MeanReversion",
            },
        ]

        payload = {"items": signals[:limit], "total": len(signals)}
        return create_success_response(data=payload, message="获取交易信号成功")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
                message=f"获取交易信号失败: {str(e)}",
            ).model_dump(),
        )


# ==================== Trade History ====================


@router.get("/trades", response_model=APIResponse, responses=TRADE_HISTORY_RESPONSES)
async def get_trades(
    symbol: Optional[str] = Query(None, description="股票代码 (可选)"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取交易记录列表

    支持按股票代码、日期范围过滤，返回分页的交易历史记录
    """
    try:
        from datetime import datetime
        from decimal import Decimal

        # 当前实现使用内存快照数据并应用过滤条件，后续可切换数据库查询
        all_trades = [
            TradeHistoryItem(
                trade_id="TRD001",
                order_id="ORDER001",
                symbol="600519.SH",
                direction="buy",
                price=Decimal("1650.00"),
                quantity=500,
                amount=Decimal("825000.00"),
                commission=Decimal("82.50"),
                trade_time=datetime.now(),
                trade_type="normal",
            ),
            TradeHistoryItem(
                trade_id="TRD002",
                order_id="ORDER002",
                symbol="000858.SZ",
                direction="buy",
                price=Decimal("145.00"),
                quantity=1000,
                amount=Decimal("145000.00"),
                commission=Decimal("145.00"),
                trade_time=datetime.now(),
                trade_type="normal",
            ),
        ]

        # 应用过滤条件 (简化实现)
        filtered_trades = all_trades
        if symbol:
            filtered_trades = [t for t in filtered_trades if symbol in t.symbol]

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

        if start_date_obj:
            filtered_trades = [t for t in filtered_trades if t.trade_time.date() >= start_date_obj]
        if end_date_obj:
            filtered_trades = [t for t in filtered_trades if t.trade_time.date() <= end_date_obj]

        # 分页
        total = len(filtered_trades)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_trades = filtered_trades[start_idx:end_idx]

        # 计算汇总
        total_amount = sum(t.amount for t in filtered_trades)
        total_commission = sum(t.commission for t in filtered_trades)

        trade_history_response = TradeHistoryResponse(
            trades=[t.model_dump() for t in paginated_trades],
            total_count=total,
            total_amount=total_amount,
            total_commission=total_commission,
            page=page,
            page_size=page_size,
        )

        return create_success_response(
            data=trade_history_response.model_dump(), message=f"获取交易记录成功，共{total}条记录"
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


@router.get("/statistics", response_model=APIResponse, responses=TRADE_STATISTICS_RESPONSES)
async def get_statistics():
    """
    获取交易统计数据

    返回总交易次数、买卖次数、持仓数量、成交金额、手续费、已实现盈亏等统计信息
    """
    try:
        from decimal import Decimal

        trades = [
            {"direction": "buy", "amount": Decimal("825000.00"), "commission": Decimal("82.50")},
            {"direction": "buy", "amount": Decimal("145000.00"), "commission": Decimal("145.00")},
            {"direction": "sell", "amount": Decimal("100000.00"), "commission": Decimal("50.00")},
        ]

        total_trades = len(trades)
        buy_trades = [trade for trade in trades if trade["direction"] == "buy"]
        sell_trades = [trade for trade in trades if trade["direction"] == "sell"]

        total_buy_amount = sum(trade["amount"] for trade in buy_trades)
        total_sell_amount = sum(trade["amount"] for trade in sell_trades)
        total_commission = sum(trade["commission"] for trade in trades)

        realized_profit = total_sell_amount - total_buy_amount

        statistics = TradeStatistics(
            total_trades=total_trades,
            buy_count=len(buy_trades),
            sell_count=len(sell_trades),
            position_count=2,
            total_buy_amount=float(total_buy_amount),
            total_sell_amount=float(total_sell_amount),
            total_commission=float(total_commission),
            realized_profit=float(realized_profit),
        )

        return create_success_response(data=statistics.model_dump(), message="获取交易统计成功")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"获取交易统计失败: {str(e)}"
            ).model_dump(),
        )


# ==================== Execute Trade ====================


@router.post("/execute", response_model=APIResponse, responses=TRADE_EXECUTE_RESPONSES)
async def execute_trade(order: dict = Body(..., example=EXECUTE_TRADE_REQUEST_EXAMPLE)):
    """
    执行买卖交易

    接收交易指令，验证参数，模拟执行交易并返回结果

    Args:
        order: 交易信息字典，包含 type, symbol, quantity, price 等字段

    Returns:
        APIResponse: 包含交易执行结果的响应
    """
    try:
        import uuid
        from datetime import datetime

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

        # 模拟交易执行
        price = order.get("price", 0.0)
        trade_amount = quantity * price
        commission = trade_amount * 0.0005  # 手续费 0.05%

        result = {
            "order_id": f"ORDER_{uuid.uuid4().hex[:12].upper()}",
            "direction": direction,
            "symbol": order.get("symbol"),
            "quantity": quantity,
            "price": price,
            "trade_amount": trade_amount,
            "commission": round(commission, 2),
            "total_amount": round(trade_amount + commission if direction == "buy" else trade_amount - commission, 2),
            "status": "completed",
            "trade_time": datetime.now().isoformat(),
            "message": f"{'买入' if direction == 'buy' else '卖出'}成功",
        }

        return create_success_response(data=result, message=f"{'买入' if direction == 'buy' else '卖出'}委托成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=f"交易执行失败: {str(e)}"
            ).model_dump(),
        )
